"""Module for running a single game of naughts and crosses and returning some
basic information about the game.
"""


from game.log import log_error
import game.board as board


class SingleGame:
    """Run a single game of naughts and crosses."""

    def __init__(self):
        """Create a new SingleGame object."""
        self.game_log_lines = []
        self.config = None
        self.bots = []
        self.game_board = None
        self.current_bot_id = 0
        self.num_turns = {'O': 0, 'X': 0}
        return

    @property
    def game_log(self):
        """str: The full game log"""
        return "\n".join(self.game_log_lines)

    def is_ended(self):
        """Returns True if the game has ended, otherwise False."""
        return self.game_board.is_ended()

    def log_game(self, message):
        """Write the specified message to the game log.

        Args:
            message:  String to write to the game log.
        """
        if (self.config and not self.config.get('silent')):
            print(message)

        self.game_log_lines.append(message)
        return

    def clone(self):
        """Clone this instance of SingleGame.

        Returns:
            New SingleGame instance that is a clone of this one.
        """
        cloned_game = SingleGame()
        cloned_game.game_log_lines = list(self.game_log_lines)
        cloned_game.config = self.config
        cloned_game.bots = list(self.bots)
        cloned_game.game_board = self.game_board.copy()
        cloned_game.current_bot_id = self.current_bot_id
        cloned_game.num_turns = dict(self.num_turns)
        return cloned_game

    def start(self, config, bots):
        """Start new game.

        Args:
            config: Dictionary containing game config.
            bots: List of bots to run.
        """
        self.config = config
        self.bots = []

        for bot in bots:
            bot.setup()
            self.bots.append(bot)

        self.game_board = board.Board()
        self.log_game("START GAME")
        self.current_bot_id = 0
        self.num_turns = {'O': 0, 'X': 0}
        return

    def do_turn(self):
        """Process one game turn."""
        if (not self.config.get('silent')):
            self.game_board.show()

        current_bot = self.bots[self.current_bot_id]
        name = current_bot.name
        identity = current_bot.identity

        self.log_game("What is your move, '{}'?".format(name))

        # Allow for a bot to return multiple moves. This is useful for running
        # the 'omnibot' in order to train or measure other bots.
        moves = current_bot.do_turn(self.game_board)

        # Update current_bot_id early, this way it will be copied to any
        # cloned games...
        if (self.current_bot_id == 0):
            self.current_bot_id = 1
        else:
            self.current_bot_id = 0

        game_clones = []
        if (type(moves) is list):
            for move in moves:
                # clone this game.
                cloned_game = self.clone()

                # apply move to clone.
                cloned_game.apply_move(int(move), name, identity)

                # append to game_clones
                game_clones.append(cloned_game)
        else:
            # Single move only.
            self.apply_move(int(moves), name, identity)

            # This will not affect the standard game runner.
            # The omnibot runner should use the returned list of games and
            # discard the one that was used to call do_turn().
            game_clones = [self]

        return game_clones

    def apply_move(self, move, name, identity):
        """Apply the specified move to the current game.

        Args:
            move (int): The move to apply.
            name (str): The name of the bot.
            identity (str): The player identity ('X' or 'O')

        """

        self.log_game("'{}' chose move ({})".format(name, move))
        self.log_game("")

        if (move < 0 or move > 8):
            log_error("Bot '{}' performed a move out of range ({})".
                      format(name, move))
            return

        if (self.game_board.getat(move) != ' '):
            log_error("Bot '{}' performed an illegal move ({})".
                      format(name, move))
            return

        self.game_board.setat(move, identity)
        self.num_turns[identity] += 1

        if (not self.config.get('silent')):
            self.game_board.show()

        return

    def run(self, config, bots):
        """Run this game.

        Args:
            config: Configuration details.
            bots: List of bots.

        Returns:
            Dictionary containing game info.
        """
        self.start(config, bots)

        while (not self.is_ended()):
            self.do_turn()

        game_info = self.get_game_info()
        return game_info

    def get_game_info(self):
        """Get information about this game.

        Returns:
            Dictionary containing game info.
        """
        if (len(self.bots) != 2):
            log_error("No bots have been set up - was this game started?")
            return

        result = self.game_board.get_game_state()

        if (result == 0):
            log_error("Game ended with invalid state of 0 - was this game "
                      "finished?")
            return

        score_X = self.calculate_score(self.num_turns['X'], result == 1,
                                       result == 3)
        score_O = self.calculate_score(self.num_turns['O'], result == 2,
                                       result == 3)

        if (result == 1):  # X wins
            self.log_game("Bot '{}' wins".format(self.bots[0].name))
            self.bots[0].process_result('WIN', score_X)
            self.bots[1].process_result('LOSS', score_O)
        elif (result == 2):  # O wins
            self.log_game("Bot '{}' wins".format(self.bots[1].name))
            self.bots[0].process_result('LOSS', score_X)
            self.bots[1].process_result('WIN', score_O)
        elif (result == 3):  # Tie
            self.log_game("It's a TIE")
            self.bots[0].process_result('TIE', score_X)
            self.bots[1].process_result('TIE', score_O)
        else:
            log_error("Game ended with invalid state ({})".format(result))
            return

        self.log_game("Scores: '{}':{:.2f} , '{}':{:.2f}".
                      format(self.bots[0].name, score_X,
                             self.bots[1].name, score_O))

        game_info = {'result': result,
                     'scores': {'X': score_X, 'O': score_O}}
        return game_info

    def calculate_score(self, num_turns, is_win, is_draw):
        """Calculate the 'score' for this game, from the perspective of bot 1.

        Args:
            num_turns: The number of turns played.
            is_win: True if this game is a win.
            is_draw: True if this game is a draw.

        Returns:
            The game score, as float.
        """
        score = 10 - num_turns
        if (not is_win):
            if (is_draw):
                score = 0
            else:
                # Weight losses much more heavily than wins
                score = -score * 10

        return score
