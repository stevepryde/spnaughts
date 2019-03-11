"""Game Runner for the genetic algorithm."""

import itertools
import json
import os
import time
from typing import Callable, Iterator, List, Optional, Tuple

from lib.botfactory import BotFactory
from lib.gameconfig import GameConfig
from lib.gamefactory import GameFactory
from lib.gameplayer import GamePlayer
from lib.runners.gamerunnerbase import GameRunnerBase
from lib.runners.genetic.processor import Processor, ProcessorMP, ProcessorRabbit
from lib.runners.genetic.rabbit import RabbitManager
from lib.support.botdb import BotDB, ConnectionFailure


class GeneticRunner(GameRunnerBase):
    """Genetic Runner. This is the main genetic algorithm."""

    def __init__(self, config: GameConfig) -> None:
        """Create new GeneticRunner."""
        super().__init__(config)
        self.db = None
        if config.botdb:
            try:
                self.db = BotDB()
            except ConnectionFailure:
                self.log.warning(
                    "Error connecting to MongoDB. BotDB will be disabled for this run."
                )
                self.db = None

        self.use_rabbit = config.use_rabbit
        self.wild_samples = config.wild_samples

        self.bots = []  # type: List[GamePlayer]
        self.genetic_bot_index = 0
        self.genetic_index = 0
        self.genetic_name = ""
        self.bot_factory = BotFactory(context=self, bot_config=self.config.get_bot_config())
        self.rabbit = RabbitManager() if self.use_rabbit else None
        return

    def setup(self) -> None:
        """Set up the genetic runner."""
        self.genetic_index = 0

        # Determine which bot is genetic.
        self.bots = self.bot_factory.create_bots()
        if not self.bots[0].genetic:
            self.genetic_index = 1
        elif self.bots[1].genetic:
            # Both bots are genetic - this is not allowed.
            self.log.critical(
                "GENETICRUNNER: Both bots are genetic. Only first bot will use the genetic algorithm"
            )
            self.genetic_index = 0

        # Store the name of the genetic bot.
        # This is used to generate new ones.
        self.genetic_name = self.bots[self.genetic_index].name
        return

    def run(self) -> None:
        """Run the games."""
        start_time = time.monotonic()

        self.setup()
        genetic_bot = self.bots[self.genetic_index]
        other_bot = self.bots[0 if self.genetic_index == 1 else 1]

        if not genetic_bot.genetic:
            self.log.critical("GENETICRUNNER: Neither bot is a genetic bot!")
            return

        selected_samples = []  # type: List[GamePlayer]
        last_scores = []  # type: List[Tuple[str, float]]
        score_threshold = -999.0  # This will be reset after first round.

        if self.rabbit and self.rabbit.enabled:
            processor = ProcessorRabbit(
                context=self,
                other_bot=other_bot,
                genetic_index=self.genetic_index,
                batch_config=self.config.get_batch_config(),
                rabbit=self.rabbit,
            )
            self.log.info("Using RabbitMQ processor")
        else:
            processor = ProcessorMP(  # type: ignore
                context=self,
                other_bot=other_bot,
                genetic_index=self.genetic_index,
                batch_config=self.config.get_batch_config(),
            )
            self.log.info("Using MP processor")

        for gen in range(self.config.num_generations):
            self.log.info("--------------------------")
            self.log.info("Generation '{}':".format(str(gen)))

            # Set up the genetic bot pool.
            if selected_samples:
                new_samples = self.generate_samples(selected_samples, gen)
            else:
                new_samples = self.generate_original_samples(gen, count=self.config.num_samples)

            if self.wild_samples:
                new_samples = itertools.chain(
                    new_samples, self.generate_original_samples(gen, count=self.wild_samples)
                )

            genetic_pool = []
            for batch_result in processor.run(
                samples=new_samples, generation_index=gen, score_threshold=score_threshold
            ):
                sample = self.bot_factory.create_bot(self.genetic_name)
                sample.from_dict(batch_result["bot_data"])
                sample.score = batch_result["genetic_score"]
                genetic_pool.append(sample)

                win = ""
                if sample.score > score_threshold:
                    win = "*"

                self.log.debug(
                    "Completed batch for sample {:5d} :: score = {:.3f} {}".format(
                        batch_result["sample"], sample.score, win
                    )
                )

            # Sort the pool based on score, in descending order.
            filtered_pool = list(filter(lambda bot: bot.score > score_threshold, genetic_pool))

            if not filtered_pool:
                self.log.info(
                    "Generation {} :: No improvement - will generate more samples".format(gen)
                )
                for bot_id, score in last_scores:
                    self.log.info("SCORE {} :: {}".format(score, bot_id))
                continue

            pool_count = len(filtered_pool)
            sample_count = len(selected_samples)
            if pool_count < sample_count:
                filtered_pool.extend(selected_samples[: sample_count - pool_count])

            sorted_pool = sorted(filtered_pool, key=lambda bot: bot.score, reverse=True)

            selected_samples = self.select_samples(sorted_pool)

            selected_scores = []
            last_scores = []
            for sample in selected_samples:
                # Check if this is one of the top for this bot.
                bot_name = self.bots[self.genetic_index].name

                score = sample.score
                if score > score_threshold:
                    score_threshold = score

                selected_scores.append("{:.3f}".format(score))

                # Add to DB, if enabled.
                if self.db:
                    bot_id = self.db.insert_bot(bot_name, sample.to_dict(), score)
                    self.log.info("SCORE {} :: {}".format(score, bot_id))
                    last_scores.append((bot_id, score))

            self.log.info(
                "Generation {} highest scores: [{}]".format(gen, ", ".join(selected_scores))
            )
            with open(os.path.join(self.path, "scores.csv"), "a") as f:
                f.write("{},{}\n".format(gen, selected_scores[0]))

        end_time = time.monotonic()
        duration = end_time - start_time
        self.log.info("Completed in {:.2f} seconds".format(duration))
        return

    def generate_samples(
        self, input_samples: List[GamePlayer], generation: int
    ) -> Iterator[GamePlayer]:
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

            for _ in range(1, self.config.num_samples):
                bot_obj = self.bot_factory.create_bot(self.genetic_name)

                sample_data = sample.to_dict()
                bot_obj.from_dict(sample_data)
                assert bot_obj.to_dict() == sample_data, "New sample not identical to old sample!"
                bot_obj.mutate()
                if bot_obj.to_dict() == sample_data:
                    self.log.warning("Sample did not mutate")
                yield bot_obj
        return

    def generate_original_samples(self, generation: int, count: int) -> Iterator[GamePlayer]:
        """Generate samples from scratch."""
        # Start from scratch, just create random bots.
        class_ = GameFactory(self).get_game_class(self.config.game)
        for _ in range(1, count + 1):
            bot_obj = self.bot_factory.create_bot(self.genetic_name)

            if not bot_obj:
                self.log.critical("Error instantiating bot '{}'".format(self.genetic_name))
                return

            bot_obj.create(game_info=class_.get_game_info())

            yield bot_obj
        return

    def select_samples(self, sorted_pool: List[GamePlayer]) -> List[GamePlayer]:
        """Select samples from the given pool."""
        # TODO: allow custom selector, to test various selection criteria.

        keep = int(self.config.keep_samples)
        if keep > len(sorted_pool):
            keep = len(sorted_pool)

        # Get samples.
        # For now, just get the top n scoring samples.
        return sorted_pool[:keep]
