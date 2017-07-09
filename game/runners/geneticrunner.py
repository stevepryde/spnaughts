"""Game Runner for the genetic algorithm"""


import datetime
import multiprocessing
import os
import random


from game.batch import Batch
from game.botmanager import BotManager
from game.log import log_critical, log_error, log_info
from game.runners.gamerunnerbase import GameRunnerBase
from game.support.topbots import TopBots

MAX_SCORE = 7.0


class BatchWorker(multiprocessing.Process):
    """Worker class for a single 'thread'."""

    def __init__(self, batch_queue, score_threshold):
        """Create new BatchWorker object.

        Args:
            batch_queue: collections.deque() object containing batches to run.
            score_threshold: Maximum score to beat.
        """
        super().__init__()

        self.batch_queue = batch_queue
        self.manager = multiprocessing.Manager()
        self.__scores = self.manager.dict()
        self.score_threshold = score_threshold
        return

    @property
    def scores(self):
        """Get the bot scores."""
        return self.__scores

    def run(self):
        """Run batches until the queue is empty."""
        try:
            while (True):
                batch = self.batch_queue.get()

                # The game runner signals the end of the queue by enqueuing
                # 'None'.
                if (batch is None):
                    break

                info = batch.batch_info
                sample = info['sample']
                gen = info['generation']
                log_path = info['log_path']
                bot_index = info['index']

                batch_scores = batch.run_batch()
                if (batch_scores is not None):
                    self.__scores[sample] = batch_scores

                if (batch.config.get('loggames')):
                    # Write batch log to a file.
                    gen_path = os.path.join(log_path, "Gen{}".format(gen))
                    sample_log_path = os.path.join(gen_path,
                                                   "sample_{}_batch_log.log".
                                                   format(sample))

                    try:
                        os.makedirs(gen_path, exist_ok=True)
                        batch.write_to_file(sample_log_path)
                    except OSError as e:
                        log_error("Error creating batch log path '{}': {}".
                                  format(gen_path, str(e)))

                win = ""
                score = batch_scores[bot_index]
                if (score > self.score_threshold):
                    win = "*"

                print("Completed batch for sample {:5d} :: score = {:.3f} {}".
                      format(sample, score, win))

                self.batch_queue.task_done()
        except KeyboardInterrupt:
            log_info("Cancelled")

        return


class GeneticRunner(GameRunnerBase):
    """Genetic Runner. This is the main genetic algorithm."""

    def __init__(self):
        """Create new GeneticRunner."""
        super().__init__()

        self.config = None
        self.bots = None
        self.genetic_bot_index = 0
        self.standard_mutations = 0
        self.genetic_index = 0
        self.genetic_name = None
        self.game_log_path = None
        self.genetic_pool = []

        self.num_threads = multiprocessing.cpu_count() - 2
        if (self.num_threads < 1):
            self.num_threads = 1

        log_info("Using {} threads...".format(self.num_threads))
        self.run_log_file = None
        return

    def log_genetic(self, message):
        """Write the specified message to the genetic runner log.

        Args:
            message: The text to write to the log.
        """
        print(message)
        return

    def log_run(self, message):
        """Write the specified run to the genetic runner log file.

        Args:
            message: The text to write to the log.
        """

        if (self.run_log_file):
            try:
                with open(self.run_log_file, 'at') as logfile:
                    logfile.write("{}\n".format(message))
            except IOError as e:
                log_critical("Error writing to run log file '{}': {}".
                             format(self.run_log_file, str(e)))
        return

    def setup(self, config, bots):
        """Set up the genetic runner.

        Args:
            config: The configuration details.
            bots: List of bots to set up.
        """

        self.config = config
        self.bots = bots
        self.genetic_index = 0
        self.standard_mutations = 20

        # Determine which bot is genetic.
        if (not bots[0].genetic):
            self.genetic_index = 1
        elif (bots[1].genetic):
            # Both bots are genetic - this is not allowed.
            log_critical("GENETICRUNNER: Both bots are genetic. Only first "
                         "bot will use the genetic algorithm")
            self.genetic_index = 0

        # Store the name of the genetic bot.
        # This is used to generate new ones.
        self.genetic_name = self.bots[self.genetic_index].name

        # Set up logging.
        log_base_dir = self.config['log_base_dir']

        ts = str(datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S%f'))
        self.game_log_path = os.path.join(log_base_dir,
                                          "genetic_{}_{}_{}".
                                          format(self.bots[0].name,
                                                 self.bots[1].name,
                                                 ts))

        if (os.path.exists(self.game_log_path)):
            log_critical("Path '{}' already exists!".format(
                self.game_log_path))
            return

        try:
            os.mkdir(self.game_log_path)
        except IOError as e:
            log_critical("Error creating log directory '{}': {}".
                         format(self.game_log_path, str(e)))
            return

        self.run_log_file = os.path.join(self.game_log_path,
                                         "genetic_run_log.log")
        return

    def generate_samples(self, input_samples, generation):
        """Generate the required number of genetic samples for the given
        generation.

        Args:
            input_samples: List of input samples.
            generation: The generation number.
        """

        self.genetic_pool = []

        manager = BotManager()

        if (not input_samples):
            # Start from scratch, just create random bots.
            # NOTE: The original bot is discarded (for convenience).

            # NOTE: if --top is specified, create bots from the top recipes.
            top_index = 0
            botname = self.bots[self.genetic_index].name
            top_recipes = self.config['toplist'].get_top_recipe_list(botname)
            for s in range(1, self.config['num_samples'] + 1):
                bot_obj = manager.create_bot(self.genetic_name)

                if (not bot_obj):
                    log_critical("Error instantiating bot '{}'".
                                 format(self.genetic_name))
                    return

                # Name it using the generation and sample number.
                # This is generation 0.
                bot_obj.name = "{}-{}-{}".format(self.genetic_name,
                                                 generation, s)

                if (self.config.get('use_top_bots') and top_recipes):
                    if (top_index >= len(top_recipes)):
                        # Out of range: Just repeat the first one.
                        bot_obj.create_from_recipe(top_recipes[0])
                    else:
                        bot_obj.create_from_recipe(top_recipes[top_index])
                        top_index += 1
                else:
                    bot_obj.create(self.config)
                self.genetic_pool.append(bot_obj)
            return

        # Input samples given. Generate new ones.
        self.genetic_pool.extend(input_samples)

        for sample in input_samples:
            sample_recipe = sample.recipe

            # Experimental:
            # If the sample had fewer mutations than the current standard,
            # lower the standard number, and vice versa.
            sample_mutations = sample.get_metadata('mutations')
            if (sample_mutations is None):
                sample_mutations = self.standard_mutations

            self.standard_mutations += \
                int((sample_mutations - self.standard_mutations) * 0.3)

            if (self.standard_mutations < 1):
                self.standard_mutations = 1

            mutation_range = self.standard_mutations * 2.0
            min_mutations = self.standard_mutations - int(mutation_range / 2.0)

            if (min_mutations < 1):
                min_mutations = 1

            if (mutation_range < 2):
                mutation_range = 2

            for s in range(1, self.config['num_samples']):
                bot_obj = manager.create_bot(self.genetic_name)

                if (not bot_obj):
                    log_critical("Error instantiating bot '{}'".
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

    def select_samples(self, sorted_pool):
        """Select samples from the given pool.

        Args:
            sorted_pool: Sorted list of samples.
        """

        # TODO: allow custom selector, to test various selection criteria.

        keep = int(self.config.get('keep_samples', 1))
        if (keep > len(sorted_pool)):
            keep = len(sorted_pool)

        # Get samples.
        # For now, just get the top n scoring samples.
        return sorted_pool[:keep]

    def run(self, config, bots):
        """Run the games.

        Args:
            config: The configuration details.
            bots: List of bots to run.
        """
        self.setup(config, bots)

        if (not bots[self.genetic_index].genetic):
            log_critical("GENETICRUNNER: Neither bot is a genetic bot!")
            return

        selected_samples = []

        toplist = TopBots(config['data_path'])
        self.config['toplist'] = toplist
        score_threshold = -999  # This will be reset after first round.

        for gen in range(config['num_generations']):
            self.log_genetic("--------------------------")
            self.log_genetic("Generation '{}':".format(str(gen)))

            # Set up the genetic bot pool.
            self.generate_samples(selected_samples, gen)

            self.log_genetic("Standard Mutations: '{}'".
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
                    if (index == self.genetic_index):
                        bot_list.append(self.genetic_pool[s])
                    else:
                        bot_list.append(self.bots[index])

                batch = Batch(self.config, bot_list)
                batch.label = "Gen {} - Sample {}".format(gen, s)
                batch.batch_info = {'generation': gen,
                                    'sample': s,
                                    'log_path': self.game_log_path,
                                    'index': self.genetic_index
                                    }
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
                toplist.check(bots[self.genetic_index].name, sample.recipe,
                              score)

                if (score > score_threshold):
                    score_threshold = score

                selected_scores.append("{:.3f}".format(score))
                selected_recipes.append("[{:.3f}]: '{}'".
                                        format(score, sample.recipe))

            self.log_genetic("Generation {} highest scores: [{}]".
                             format(gen, ', '.join(selected_scores)))

            # Also log recipes of winning bots:
            self.log_run("Generation '{}': Winning bot recipes:\n{}".
                         format(gen, "\n".join(selected_recipes)))

        return
