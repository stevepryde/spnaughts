"""Game Runner for the genetic algorithm."""


import multiprocessing
import random


from lib.batch import Batch
from lib.runners.gamerunnerbase import GameRunnerBase
from lib.runners.genetic.batchworker import BatchWorker

MAX_SCORE = 7.0


class GeneticRunner(GameRunnerBase):
    """Genetic Runner. This is the main genetic algorithm."""

    def __init__(self):
        """Create new GeneticRunner."""
        super().__init__()
        self.enable_console_logging()
        self.bots = []
        self.genetic_bot_index = 0
        self.standard_mutations = 0
        self.genetic_index = 0
        self.genetic_name = None
        self.genetic_pool = []

        self.num_threads = multiprocessing.cpu_count() - 2
        if self.num_threads < 1:
            self.num_threads = 1

        self.log.info("Using {} threads...".format(self.num_threads))
        return

    def setup(self):
        """Set up the genetic runner."""
        self.genetic_index = 0
        self.standard_mutations = 20

        # Determine which bot is genetic.
        self.bots = self.bot_manager.create_bots()
        if not self.bots[0].genetic:
            self.genetic_index = 1
        elif self.bots[1].genetic:
            # Both bots are genetic - this is not allowed.
            self.log.critical("GENETICRUNNER: Both bots are genetic. "
                              "Only first bot will use the genetic algorithm")
            self.genetic_index = 0

        # Store the name of the genetic bot.
        # This is used to generate new ones.
        self.genetic_name = self.bots[self.genetic_index].name
        return

    def run(self):
        """Run the games."""
        self.setup()

        if not self.bots[self.genetic_index].genetic:
            self.log.critical("GENETICRUNNER: Neither bot is a genetic bot!")
            return

        selected_samples = []
        score_threshold = -999  # This will be reset after first round.

        for gen in range(self.config.num_generations):
            self.log.info("--------------------------")
            self.log.info("Generation '{}':".format(str(gen)))

            # Set up the genetic bot pool.
            self.generate_samples(selected_samples, gen)

            self.log.info("Standard Mutations: '{}'".
                          format(self.standard_mutations))

            # Set up the batch queue and worker threads.
            batch_queue = multiprocessing.JoinableQueue()
            threads = []
            for _ in range(self.num_threads):
                thr = BatchWorker(batch_queue, score_threshold)
                thr.start()
                threads.append(thr)

            for s in range(len(self.genetic_pool)):
                bot_list = []
                for index in [0, 1]:
                    if index == self.genetic_index:
                        bot_list.append(self.genetic_pool[s])
                    else:
                        bot_list.append(self.bots[index])

                batch = Batch(parent_context=self, bots=bot_list)
                batch.label = "Gen {} - Sample {}".format(gen, s)
                batch.batch_info = {'generation': gen,
                                    'sample': s,
                                    'index': self.genetic_index}
                batch_queue.put(batch)

            # Wait for all batches to process...
            batch_queue.join()

            # Tell the threads to stop.
            for _ in range(self.num_threads):
                batch_queue.put(None)

            # Join threads and process scores.
            scores = {}
            for thr in threads:
                thr.join()
                scores.update(thr.scores)

            # First get a dict of just the score we want.
            bot_scores = {}
            for s, score_list in scores.items():
                genetic_score = score_list[self.genetic_index]

                # Set the score in the bot object.
                self.genetic_pool[s].score = genetic_score
                bot_scores[s] = genetic_score

            # Sort the pool based on score, in descending order.
            sorted_pool = sorted(self.genetic_pool,
                                 key=lambda bot: bot.score,
                                 reverse=True)

            selected_samples = self.select_samples(sorted_pool)

            selected_scores = []
            selected_recipes = []
            for sample in selected_samples:
                # Check if this is one of the top for this bot.
                score = sample.score
                self.config.top_bots.check(self.bots[self.genetic_index].name,
                                           sample.recipe,
                                           score)

                if score > score_threshold:
                    score_threshold = score

                selected_scores.append("{:.3f}".format(score))
                selected_recipes.append("[{:.3f}]: '{}'".
                                        format(score, sample.recipe))

            self.log.info("Generation {} highest scores: [{}]".
                          format(gen, ', '.join(selected_scores)))

            # Also log recipes of winning bots:
            self.log.debug("Generation '{}': Winning bot recipes:\n{}".
                           format(gen, "\n".join(selected_recipes)))
        return

    def generate_samples(self, input_samples, generation):
        """Generate the required number of genetic samples.

        This takes some input samples and uses them to generate a range of
        mutated samples based on these originals. If no originals are provided,
        this will create random samples from scratch.

        :param input_samples: List of input samples.
        :param generation: The generation number.
        """
        if not input_samples:
            return self.generate_original_samples(generation)

        # Add the samples first. This allows the original samples to compete
        # with the offspring, and guards against the scenario where all
        # offspring are less-advantaged.
        self.genetic_pool = list(input_samples)

        for sample in input_samples:
            sample_recipe = sample.recipe

            # Experimental:
            # If the sample had fewer mutations than the current standard,
            # lower the standard number, and vice versa.
            sample_mutations = sample.get_metadata('mutations')
            if sample_mutations is None:
                sample_mutations = self.standard_mutations

            self.standard_mutations += \
                int((sample_mutations - self.standard_mutations) * 0.3)

            if self.standard_mutations < 1:
                self.standard_mutations = 1

            mutation_range = self.standard_mutations * 2.0
            min_mutations = self.standard_mutations - int(mutation_range / 2.0)

            if min_mutations < 1:
                min_mutations = 1

            if mutation_range < 2:
                mutation_range = 2

            for s in range(1, self.config.num_samples):
                bot_obj = self.bot_manager.create_bot(self.genetic_name)

                if not bot_obj:
                    self.log.critical("Error instantiating bot '{}'".
                                      format(bot_obj.genetic_name))
                    return

                # Name it using the generation and sample number.
                bot_obj.name = "{}-{}-{}".format(self.genetic_name,
                                                 generation, s)

                # Mutate the recipe.
                num_mutations = random.randint(min_mutations,
                                               min_mutations + mutation_range)

                mutated_recipe = sample_recipe
                mutated_recipe = bot_obj.mutate_recipe(mutated_recipe,
                                                       num_mutations)

                bot_obj.create_from_recipe(mutated_recipe)
                bot_obj.set_metadata('mutations', num_mutations)
                self.genetic_pool.append(bot_obj)
        return

    def generate_original_samples(self, generation):
        """Generate samples from scratch."""
        # Start from scratch, just create random bots.
        self.genetic_pool = []

        # NOTE: if --top is specified, create bots from the top recipes.
        top_index = 0
        botname = self.bots[self.genetic_index].name
        top_recipes = self.config.top_bots.get_top_recipe_list(botname)
        for s in range(1, self.config.num_samples + 1):
            bot_obj = self.bot_manager.create_bot(self.genetic_name)

            if not bot_obj:
                self.log.critical("Error instantiating bot '{}'".
                                  format(self.genetic_name))
                return

            # Name it using the generation and sample number.
            # This is generation 0.
            bot_obj.name = "{}-{}-{}".format(self.genetic_name,
                                             generation, s)

            if self.config.use_top_bots and top_recipes:
                if top_index >= len(top_recipes):
                    # Out of range: Just repeat the first one.
                    bot_obj.create_from_recipe(top_recipes[0])
                else:
                    bot_obj.create_from_recipe(top_recipes[top_index])
                    top_index += 1
            else:
                bot_obj.create()
            self.genetic_pool.append(bot_obj)
        return

    def select_samples(self, sorted_pool):
        """Select samples from the given pool."""
        # TODO: allow custom selector, to test various selection criteria.

        keep = int(self.config.keep_samples)
        if keep > len(sorted_pool):
            keep = len(sorted_pool)

        # Get samples.
        # For now, just get the top n scoring samples.
        return sorted_pool[:keep]
