"""Run a batch of games."""


import collections
import random


from lib.gamecontext import GameContext

P1_WINS = 1
P2_WINS = 2
DRAW = 3


class Batch(GameContext):
    """A Batch will run a batch of single games."""

    def __init__(self, parent_context, bots):
        """
        Create a new Batch.

        :param config: GameConfig object.
        :param bots: List of bots to run.
        """
        super().__init__(parent_context=parent_context)
        self.bots = bots

        self.label = ""
        self.batch_info = {}  # Used by genetic.batchworker.

        self.overall_results = {P1_WINS: 0, P2_WINS: 0, DRAW: 0}
        self.num_games_played = 0
        self.total_score = {}
        return

    def run_batch(self):
        """Run this batch and return the average scores."""
        self.start_batch()

        if self.config.batch_size == 0:
            self.run_magic_batch()
        else:
            self.run_normal_batch()

        average_scores = self.process_batch_result()
        return average_scores

    def start_batch(self):
        """Start this batch."""
        # Run a single batch.
        class_ = self.config.get_game_class()
        for index, identity in enumerate(class_.identities):
            self.bots[index].clear_score()
            self.bots[index].identity = identity
            self.total_score[identity] = 0

        self.overall_results = {P1_WINS: 0, P2_WINS: 0, DRAW: 0}
        self.num_games_played = 0

        random.seed(1)
        return

    def process_game_result(self, game_num, game_info):
        """Process the result of a single game."""
        result = game_info['result']

        self.num_games_played += 1
        class_ = self.config.get_game_class()
        identities = class_.identities
        for identity in identities:
            self.total_score[identity] += game_info['scores'][identity]

        bot_name = ''
        identity_loss = ''
        if result == DRAW:
            self.log.info("Game {}: TIE".format(game_num))
        else:
            if result == P1_WINS:
                identity_loss = identities[1]
                bot_name = self.bots[0].name
            elif result == P2_WINS:
                identity_loss = identities[0]
                bot_name = self.bots[1].name
            else:
                self.log.error("Invalid result received: '{}'".format(result))
                return

            self.log.info("Game {}: '{}' WINS".
                          format(game_num, bot_name))
            if self.config.stop_on_loss == identity_loss:
                self.log.info("Stopping because {0} lost a game and "
                              "--stoponloss {0} was specified".
                              format(identity_loss))
                return

        if result not in self.overall_results:
            self.log.error("No record of {} in overall_results".format(result))
            return
        else:
            self.overall_results[result] += 1
        return

    def process_batch_result(self):
        """
        Process the results for this batch.

        :returns: List containing the average score for each bot.
        """
        # Print overall results.
        self.log.info("\nRESULTS:")
        self.log.info("Games Played: {}".format(self.num_games_played))
        self.log.info("")
        self.log.info("'{}' WINS: {}".format(self.bots[0].name,
                                             self.overall_results[P1_WINS]))
        self.log.info("'{}' WINS: {}".format(self.bots[1].name,
                                             self.overall_results[P2_WINS]))
        self.log.info("DRAW/TIE: {}".format(self.overall_results[DRAW]))
        self.log.info("")

        # Get average scores.
        if self.num_games_played > 0:
            class_ = self.config.get_game_class()
            identities = class_.identities
            avg_score = []
            for identity in identities:
                avg_score.append(
                    float(self.total_score[identity] / self.num_games_played))

            self.bots[0].score = avg_score[0]
            self.bots[1].score = avg_score[1]

            self.log.info("\nAverage Scores: '{}':{:.2f} , '{}':{:.2f}".
                          format(self.bots[0].name, avg_score[0],
                                 self.bots[1].name, avg_score[1]))

            self.log.info("AVERAGE SCORES:\n'{}':{:.2f}\n'{}':{:.2f}".
                          format(self.bots[0].name, avg_score[0],
                                 self.bots[1].name, avg_score[1]))

            return avg_score
        return [0, 0]

    def run_normal_batch(self):
        """Run normal batch of games."""
        for game_num in range(1, self.config.batch_size + 1):
            self.log.info("\n********** Running game {} **********\n".
                          format(game_num))

            game_obj = self.config.get_game_obj(parent_context=self)
            if self.config.log_games:
                game_obj.enable_file_logging()
            game_info = game_obj.run(self.bots)
            if game_info is None:
                self.log.error("Game {} failed!".format(game_num))
                return

            self.process_game_result(game_num, game_info)
        return

    def run_magic_batch(self):
        """Pseudo-batch that actually runs every possible move combination."""
        game_num = 0
        game_obj_initial = self.config.get_game_obj(parent_context=self)
        game_obj_initial.start(self.bots)

        game_queue = collections.deque()
        game_queue.append(game_obj_initial)

        try:
            while True:
                game_obj = game_queue.popleft()
                new_games = game_obj.do_turn()

                if not new_games:
                    self.log.error("No cloned games returned from do_turn() "
                                   "when running magic batch")
                    break

                for new_game_obj in new_games:
                    if new_game_obj.is_ended():
                        # A game has finished, so process the result...
                        game_num += 1
                        game_info = new_game_obj.get_result()
                        if game_info is None:
                            self.log.error("Game {} failed!".format(game_num))
                            return

                        self.process_game_result(game_num, game_info)
                    else:
                        # This game has not yet finished, so add it to the end
                        # of the queue.
                        game_queue.append(new_game_obj)
        except IndexError:
            # All games should have been run to completion.
            pass

        return
