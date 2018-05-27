"""Game Runner for the genetic algorithm."""


import json
import time


from lib.runners.gamerunnerbase import GameRunnerBase
from lib.runners.genetic.processor import Processor, ProcessorMP

MAX_SCORE = 7.0


class GeneticRunner(GameRunnerBase):
    """Genetic Runner. This is the main genetic algorithm."""

    def __init__(self):
        """Create new GeneticRunner."""
        super().__init__()
        self.enable_console_logging()
        self.bots = []
        self.genetic_bot_index = 0
        self.genetic_index = 0
        self.genetic_name = None
        self.genetic_class = None
        return

    def setup(self):
        """Set up the genetic runner."""
        self.genetic_index = 0

        # Determine which bot is genetic.
        self.bots = self.bot_manager.create_bots()
        if not self.bots[0].genetic:
            self.genetic_index = 1
        elif self.bots[1].genetic:
            # Both bots are genetic - this is not allowed.
            self.log.critical(
                "GENETICRUNNER: Both bots are genetic. "
                "Only first bot will use the genetic algorithm"
            )
            self.genetic_index = 0

        # Store the name of the genetic bot.
        # This is used to generate new ones.
        self.genetic_name = self.bots[self.genetic_index].name
        self.genetic_class = self.bot_manager.get_bot_class(self.genetic_name)
        return

    def run(self):
        """Run the games."""
        start_time = time.monotonic()

        self.setup()
        genetic_bot = self.bots[self.genetic_index]
        other_bot = self.bots[0 if self.genetic_index == 1 else 1]

        if not genetic_bot.genetic:
            self.log.critical("GENETICRUNNER: Neither bot is a genetic bot!")
            return

        selected_samples = []
        score_threshold = -999  # This will be reset after first round.

        processor = ProcessorMP(
            context=self, bot=other_bot, genetic_index=self.genetic_index
        )

        for gen in range(self.config.num_generations):
            self.log.info("--------------------------")
            self.log.info("Generation '{}':".format(str(gen)))

            # Set up the genetic bot pool.
            if selected_samples:
                new_samples = self.generate_samples(selected_samples, gen)
            else:
                new_samples = self.generate_original_samples(gen)

            genetic_pool = []
            for batch in processor.run(
                samples=new_samples,
                generation_index=gen,
                score_threshold=score_threshold,
            ):
                # Collect scores.
                sample = self.bot_manager.create_bot_from_class(self.genetic_class)
                sample.from_dict(batch.info["bot_data"])
                # sample.score = batch.info['genetic_score']
                genetic_pool.append(sample)

            # Sort the pool based on score, in descending order.
            sorted_pool = sorted(genetic_pool, key=lambda bot: bot.score, reverse=True)

            selected_samples = self.select_samples(sorted_pool)

            selected_scores = []
            selected_recipes = []
            for sample in selected_samples:
                # Check if this is one of the top for this bot.
                self.config.top_bots.check(self.bots[self.genetic_index].name, sample)

                score = sample.score
                if score > score_threshold:
                    score_threshold = score

                selected_scores.append("{:.3f}".format(score))
                selected_recipes.append("[{:.3f}]: '{}'".format(score, sample.recipe))

            self.log.info(
                "Generation {} highest scores: [{}]".format(
                    gen, ", ".join(selected_scores)
                )
            )

            # Write winning recipes to a file.
            with self.open_unique_file(
                prefix="winning_recipes_GEN{:04d}".format(gen)
            ) as f:
                bot_list = [x.to_dict() for x in selected_samples]
                json.dump(bot_list, f)

        end_time = time.monotonic()
        duration = end_time - start_time
        self.log.info("Completed in {:.2f} seconds".format(duration))
        return

    def generate_samples(self, input_samples, generation):
        """Generate the required number of genetic samples.

        This takes some input samples and uses them to generate a range of
        mutated samples based on these originals. If no originals are provided,
        this will create random samples from scratch.

        :param input_samples: List of input samples.
        :param generation: The generation number.
        """
        for sample in input_samples:
            # Yield the original samples as well. This allows the original
            # samples to compete with the offspring, and guards against the
            # scenario where all offspring are less-advantaged.
            yield sample

            for s in range(1, self.config.num_samples):
                bot_obj = self.bot_manager.create_bot_from_class(self.genetic_class)

                if not bot_obj:
                    self.log.critical(
                        "Error instantiating bot '{}'".format(bot_obj.genetic_name)
                    )
                    return

                # Name it using the generation and sample number.
                bot_obj.name = "{}-{}-{}".format(self.genetic_name, generation, s)

                bot_obj.from_dict(sample.to_dict())
                bot_obj.mutate()
                yield bot_obj
        return

    def generate_original_samples(self, generation):
        """Generate samples from scratch."""
        # Start from scratch, just create random bots.
        # NOTE: if --top is specified, create bots from the top recipes.
        top_index = 0
        botname = self.bots[self.genetic_index].name
        top_data = None
        if self.config.use_top_bots:
            top_data = self.config.top_bots.get_top_bot_data(botname)
        for s in range(1, self.config.num_samples + 1):
            bot_obj = self.bot_manager.create_bot_from_class(self.genetic_class)

            if not bot_obj:
                self.log.critical(
                    "Error instantiating bot '{}'".format(self.genetic_name)
                )
                return

            # Name it using the generation and sample number.
            # This is generation 0.
            bot_obj.name = "{}-{}-{}".format(self.genetic_name, generation, s)

            if self.config.use_top_bots and top_data:
                if top_index >= len(top_data):
                    # Out of range: Just repeat the first one.
                    bot_obj.from_dict(top_data[0])
                else:
                    bot_obj.from_dict(top_data[top_index])
                    top_index += 1
            else:
                bot_obj.create()

            yield bot_obj
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
