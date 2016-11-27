"""Run a batch of games."""


import collections

from game.singlegame import SingleGame
from game.log import log_error


class Batch:
    """A Batch will run a batch of single games."""

    def __init__(self, config, bots):
        """Create a new Batch.

        Args:
            config: Configuration details.
            bots: List of bots to run.
        """
        self.batch_log_lines = []
        self.batch_summary_lines = []
        self.config = config
        self.bots = bots
        self.__label = ""
        self.__batch_info = {}

        # Init details used during the running of the batch.
        self.start_batch()
        return

    @property
    def label(self):
        """str: Label for this batch."""
        return self.__label

    @label.setter
    def label(self, text):
        self.__label = text
        return

    @property
    def batch_info(self):
        """dict: Dictionary containing Batch info."""
        return self.__batch_info

    @batch_info.setter
    def batch_info(self, info):
        """Set batch info dictionary."""
        self.__batch_info = info
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
        """Write the specified message to the batch log.

        Args:
            message: The text to write to the log.
        """
        self.batch_log_lines.append(message)
        return

    def log_summary(self, message):
        """Write the specified message to the batch summary.

        Args:
            message: The text to write to the summary.
        """
        self.batch_summary_lines.append(message)
        return

    def write_to_file(self, filename):
        """Write this batch log to the specified file.

        Args:
            filename: The filename of the file to write the log to.
        """

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

        # Run the batch, either using the normal batch runner or the 'magic'
        # one, depending on the 'num_games' setting.
        if (self.config['num_games'] == 0):
            self.run_magic_batch()
        else:
            self.run_normal_batch()

        average_scores = self.process_batch_result()
        return average_scores

    def start_batch(self):
        """Start this batch."""

        # Run a single batch.
        for index, identity in enumerate(['X', 'O']):
            self.bots[index].clear_score()
            self.bots[index].identity = identity

        self.overall_results = {1: 0, 2: 0, 3: 0}
        self.num_games_played = 0
        self.total_score = {'X': 0, 'O': 0}

        return

    def process_game_result(self, game_num, game_info):
        """Process the result of a single game."""
        result = game_info['result']

        self.num_games_played += 1
        self.total_score['X'] += game_info['scores']['X']
        self.total_score['O'] += game_info['scores']['O']

        if (result == 1):
            self.log_summary("Game {}: '{}' WINS".
                             format(game_num, self.bots[0].name))
            if (self.config.get('stoponloss', '') == 'O'):
                self.log_summary("Stopping because O lost a game and "
                                 "--stoponloss O was specified")
                return
        elif (result == 2):
            self.log_summary("Game {}: '{}' WINS".
                             format(game_num, self.bots[1].name))
            if (self.config.get('stoponloss', '') == 'X'):
                self.log_summary("Stopping because X lost a game and "
                                 "--stoponloss X was specified")
                return
        elif (result == 3):
            self.log_summary("Game {}: TIE".format(game_num))
        else:
            log_error("Invalid result received: '{}'".format(result))
            return

        if (result not in self.overall_results):
            log_error("No record of {} in overall_results".format(result))
            return
        else:
            self.overall_results[result] += 1

        return

    def process_batch_result(self):
        """Process the results for this batch.

        Returns:
            List containing the average score for each bot.
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
        if (self.num_games_played > 0):
            avg_score_X = float(self.total_score['X'] / self.num_games_played)
            avg_score_O = float(self.total_score['O'] / self.num_games_played)

            self.bots[0].score = avg_score_X
            self.bots[1].score = avg_score_O

            self.log_batch("\nAverage Scores: '{}':{:.2f} , '{}':{:.2f}".
                           format(self.bots[0].name, avg_score_X,
                                  self.bots[1].name, avg_score_O))

            self.log_summary("AVERAGE SCORES:\n'{}':{:.2f}\n'{}':{:.2f}".
                             format(self.bots[0].name, avg_score_X,
                                    self.bots[1].name, avg_score_O))

        return [avg_score_X, avg_score_O]

    def run_normal_batch(self):
        """Run normal batch of games."""

        for game_num in range(1, self.config['num_games'] + 1):
            self.log_batch("\n********** Running game {} **********\n".
                           format(game_num))

            game_obj = SingleGame()
            game_info = game_obj.run(self.config, self.bots)
            if (game_info is None):
                log_error("Game {} failed!".format(game_num))
                return

            game_log = game_obj.game_log
            self.log_batch(game_log)

            self.process_game_result(game_num, game_info)

        return

    def run_magic_batch(self):
        """
        This is a pseudo-batch that actually runs every possible combination of
        moves against the target bot.
        """

        game_num = 0
        game_obj_initial = SingleGame()
        game_obj_initial.start(self.config, self.bots)

        game_queue = collections.deque()
        game_queue.append(game_obj_initial)

        try:
            while(True):
                game_obj = game_queue.popleft()
                new_games = game_obj.do_turn()

                if (len(new_games) == 0):
                    log_error("No cloned games returned from do_turn() when "
                              "running magic batch")
                    break

                for new_game_obj in new_games:
                    if (new_game_obj.is_ended()):
                        # A game has finished, so process the result...
                        game_num += 1
                        game_info = new_game_obj.get_game_info()
                        if (game_info is None):
                            log_error("Game {} failed!".format(game_num))
                            return

                        game_log = new_game_obj.game_log
                        self.log_batch(game_log)

                        self.process_game_result(game_num, game_info)
                    else:
                        # This game has not yet finished, so add it to the end of the queue.
                        game_queue.append(new_game_obj)
        except IndexError:
            # All games should have been run to completion.
            pass

        return
