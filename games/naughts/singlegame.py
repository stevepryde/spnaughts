"""Module for running a single game of naughts and crosses."""


from lib.gamebase import GameBase
from games.naughts import board


class SingleGame(GameBase):
    """Run a single game of naughts and crosses."""

    identities = ('X', 'O')

    def __init__(self, parent_context):
        """Create a new SingleGame object."""
        super().__init__(parent_context)
        self.game_board = None
        self.current_bot_id = 0
        return

    def is_ended(self):
        """Return True if the game has ended, otherwise False."""
        return self.game_board.is_ended()

    def clone(self):
        """Clone this instance of SingleGame."""
        cloned_game = SingleGame(self.parent_context)
        cloned_game.bots = list(self.bots)
        cloned_game.game_board = self.game_board.copy()
        cloned_game.current_bot_id = self.current_bot_id
        cloned_game.num_turns = dict(self.num_turns)
        return cloned_game

    def start(self, bots):
        """
        Start new game.

        :param bots: List of bots to run.
        """
        super().start(bots)
        self.game_board = board.Board()
        return

    def do_turn(self):
        """Process one game turn."""
        if not self.config.silent:
            self.game_board.show()

        current_bot = self.bots[self.current_bot_id]
        name = current_bot.name
        identity = current_bot.identity

        self.log.info("What is your move, '{}'?".format(name))

        # Allow for a bot to return multiple moves. This is useful for running
        # the 'omnibot' in order to train or measure other bots.
        moves = current_bot.do_turn(self.game_board.copy())

        # Update current_bot_id early, this way it will be copied to any
        # cloned games...
        if self.current_bot_id == 0:
            self.current_bot_id = 1
        else:
            self.current_bot_id = 0

        game_clones = []
        if isinstance(moves, list):
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
        """
        Apply the specified move to the current game.

        :param move: The move to apply.
        :param name: The name of the bot.
        :param identity: The player identity ('X' or 'O')
        """
        self.log.info("'{}' chose move ({})".format(name, move))
        self.log.info("")

        if move < 0 or move > 8:
            self.log.error("Bot '{}' performed a move out of range ({})".
                           format(name, move))
            return

        if self.game_board.getat(move) != ' ':
            self.log.error("Bot '{}' performed an illegal move ({})".
                           format(name, move))
            return

        self.game_board.setat(move, identity)
        self.num_turns[identity] += 1

        if not self.config.silent:
            self.game_board.show()
        return

    def get_result(self):
        """Get information about this game."""
        if len(self.bots) != 2:
            self.log.error("No bots have been set up - was this game started?")
            return

        result = self.game_board.get_game_state()

        if result == 0:
            self.log.error("Game ended with invalid state of 0 - was this "
                           "game finished?")
            return

        score_X = self.calculate_score(self.num_turns['X'], result == 1,
                                       result == 3)
        score_O = self.calculate_score(self.num_turns['O'], result == 2,
                                       result == 3)

        if result == 1:  # X wins
            self.log.info("Bot '{}' wins".format(self.bots[0].name))
            self.bots[0].process_result('WIN', score_X)
            self.bots[1].process_result('LOSS', score_O)
        elif result == 2:  # O wins
            self.log.info("Bot '{}' wins".format(self.bots[1].name))
            self.bots[0].process_result('LOSS', score_X)
            self.bots[1].process_result('WIN', score_O)
        elif result == 3:  # Tie
            self.log.info("It's a TIE")
            self.bots[0].process_result('TIE', score_X)
            self.bots[1].process_result('TIE', score_O)
        else:
            self.log.error("Game ended with invalid state ({})".format(result))
            return

        self.log.info("Scores: '{}':{:.2f} , '{}':{:.2f}".
                      format(self.bots[0].name, score_X,
                             self.bots[1].name, score_O))

        game_info = {'result': result,
                     'scores': {'X': score_X, 'O': score_O}}
        return game_info

    def calculate_score(self, num_turns, is_win, is_draw):
        """
        Calculate the 'score' for this game, from the perspective of bot 1.

        :param num_turns: The number of turns played.
        :param is_win: True if this game is a win.
        :param is_draw: True if this game is a draw.
        :returns: The game score, as float.
        """
        score = 10 - num_turns
        if not is_win:
            if is_draw:
                score = 0
            else:
                # Weight losses much more heavily than wins
                score = -score * 10
        return score
