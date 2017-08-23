"""Run a batch of games."""


import collections
import random

from lib.log import log_error


class Batch:
    """A Batch will run a batch of single games."""

    def __init__(self, config, bots):
        """
        Create a new Batch.

        :param config: GameConfig object.
        :param bots: List of bots to run.
        """
        self.config = config
        self.bots = bots

        self.batch_log_lines = []
        self.batch_summary_lines = []
        self.label = ""
        self.batch_info = {}

        self.overall_results = {1: 0, 2: 0, 3: 0}
        self.num_games_played = 0
        self.total_score = {}
        return

    @property
    def batch_log(self):
        """str: Get the batch log as a string."""
        return "\n".join(self.batch_log_lines)

    @property
    def batch_summary(self):
        """str: Get the batch summary as a string."""
        return "\n".join(self.batch_summary_lines)

    def log_batch(self, message):
        """Write the specified message to the batch log."""
        self.batch_log_lines.append(message)
        return

    def log_summary(self, message):
        """Write the specified message to the batch summary."""
        self.batch_summary_lines.append(message)
        return

    def write_to_file(self, filename):
        """Write this batch log to the specified file."""
        try:
            with open(filename, 'wt') as batch_log_file:
                batch_log_file.write(self.batch_summary)
                batch_log_file.write("\n\nFULL LOG:\n")
                batch_log_file.write(self.batch_log)

        except IOError as e:
            log_error("Error writing batch log file '{}': {}".
                      format(filename, str(e)))
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

        self.overall_results = {1: 0, 2: 0, 3: 0}
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
        if result == 3:
            self.log_summary("Game {}: TIE".format(game_num))
        else:
            if result == 1:
                identity_loss = identities[1]
                bot_name = self.bots[0].name
            elif result == 2:
                identity_loss = identities[1]
                bot_name = self.bots[1].name
            else:
                log_error("Invalid result received: '{}'".format(result))
                return

            self.log_summary("Game {}: '{}' WINS".
                             format(game_num, bot_name))
            if self.config.stop_on_loss == identity_loss:
                self.log_summary("Stopping because {0} lost a game and "
                                 "--stoponloss {0} was specified".
                                 format(identity_loss))
                return

        if result not in self.overall_results:
            log_error("No record of {} in overall_results".format(result))
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
        self.log_summary("\nRESULTS:")
        self.log_summary("Games Played: {}".format(self.num_games_played))
        self.log_summary("")
        self.log_summary("'{}' WINS: {}".format(self.bots[0].name,
                                                self.overall_results[1]))
        self.log_summary("'{}' WINS: {}".format(self.bots[1].name,
                                                self.overall_results[2]))
        self.log_summary("DRAW/TIE: {}".format(self.overall_results[3]))
        self.log_summary("")

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

            self.log_batch("\nAverage Scores: '{}':{:.2f} , '{}':{:.2f}".
                           format(self.bots[0].name, avg_score[0],
                                  self.bots[1].name, avg_score[1]))

            self.log_summary("AVERAGE SCORES:\n'{}':{:.2f}\n'{}':{:.2f}".
                             format(self.bots[0].name, avg_score[0],
                                    self.bots[1].name, avg_score[1]))

            return avg_score
        return [0, 0]

    def run_normal_batch(self):
        """Run normal batch of games."""
        for game_num in range(1, self.config.batch_size + 1):
            self.log_batch("\n********** Running game {} **********\n".
                           format(game_num))

            game_obj = self.config.get_game_obj()
            game_info = game_obj.run(self.bots)
            if game_info is None:
                log_error("Game {} failed!".format(game_num))
                return

            self.log_batch(game_obj.get_game_log())
            self.process_game_result(game_num, game_info)
        return

    def run_magic_batch(self):
        """Pseudo-batch that actually runs every possible move combination."""
        game_num = 0
        game_obj_initial = self.config.get_game_obj()
        game_obj_initial.start(self.bots)

        game_queue = collections.deque()
        game_queue.append(game_obj_initial)

        try:
            while True:
                game_obj = game_queue.popleft()
                new_games = game_obj.do_turn()

                if not new_games:
                    log_error("No cloned games returned from do_turn() when "
                              "running magic batch")
                    break

                for new_game_obj in new_games:
                    if new_game_obj.is_ended():
                        # A game has finished, so process the result...
                        game_num += 1
                        game_info = new_game_obj.get_result()
                        if game_info is None:
                            log_error("Game {} failed!".format(game_num))
                            return

                        self.log_batch(new_game_obj.get_game_log())
                        self.process_game_result(game_num, game_info)
                    else:
                        # This game has not yet finished, so add it to the end
                        # of the queue.
                        game_queue.append(new_game_obj)
        except IndexError:
            # All games should have been run to completion.
            pass

        return
