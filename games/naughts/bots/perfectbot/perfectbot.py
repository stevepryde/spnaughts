"""
This bot is designed never to lose, and also to win if it can.

Features:
- If it can see an immediate win, it will go for it.
- If it can see a way to block an immediate win for the opponent, it will
  block it (obviously it couldn't avoid a 2WW but it is designed never to
  face one)
- If it was the starting player, it will attempt to set up a 2WW.
  - If at any point it cannot see any further possible 2WWs, it will revert
    to defensive play.
- If it was not the starting player it will play defensively and attempt to
  thwart known 2WWs.
- If there are no known 2WWs on the board, it will fall through to the next
  available move from a pre-defined list in order of preference.

TODO: There are potentially more win scenarios that this bot could attempt.
      Currently it only tries one of three.

To test this bot, run it against the randombot (in both directions) with:
--batch 10000 --stoponloss X

This should be enough to detect any corner cases that slip through.

NOTE: The 'perfectbot' is not perfect. It will never lose, but it does not
      optimise its chances to win.

See minimaxbot for the optimal solution, based on the minimax algorithm with
A-B optimisation.

Neither perfectbot nor minimaxbot will lose any games against randombot, but
minimaxbot will win more games againts randombot than perfectbot will.

Perfect bot is still very useful for training AI bots, and is much faster than
minimaxbot.
"""


import random


from games.naughts.board import Board
from games.naughts.bots.naughtsbot import NaughtsBot


DEBUG = False


class PerfectBot(NaughtsBot):
    """Experimental bot that follows pre-determined rules."""

    def __init__(self):
        """Create a new PERFECTBOT."""
        super().__init__()
        self.defensive = False
        self.scenario = 0
        self.scenario_rotation = -1
        return

    def setup(self):
        """Set up this bot."""
        super().setup()

        self.defensive = False
        self.scenario = 0  # The 2WW scenario we are trying for.
        self.scenario_rotation = -1
        return

    def do_turn(self, current_board: Board):
        """Do one turn."""
        moves = current_board.get_possible_moves()

        # First, win the game if we can.
        straight_sequences = ["012", "345", "678", "036", "147", "258", "048", "246"]

        for seq in straight_sequences:
            (ours, theirs, blanks) = self.get_sequence_info(current_board, seq)
            if len(ours) == 2 and len(blanks) == 1:
                # Move into the blank for the win.
                return int(blanks[0])

        # Second, if we can't win, make sure the opponent can't win either.
        for seq in straight_sequences:
            (ours, theirs, blanks) = self.get_sequence_info(current_board, seq)
            if len(theirs) == 2 and len(blanks) == 1:
                # Move into the blank to block the win.
                return int(blanks[0])

        # If this is the first move...
        (ours, theirs, blanks) = self.get_sequence_info(current_board, "012345678")
        if not ours:
            # If we're the second player:
            if theirs:
                # Don't try anything funky to win.
                self.defensive = True

                if 4 in moves:
                    return 4

                # Otherwise take the upper left.
                return 0

            # We're starting. Try for a 2WW below.
            self.defensive = False

        their_identity = self.other_identity

        # Offensive: Try to set up a 2-way win.
        if not self.defensive:
            # Not in defensive mode. I have a limited time to set up a 2WW
            # scenario.
            if self.scenario == 0:
                # Choose a 2WW scenario at random.
                self.scenario = random.randint(1, 3)
                self.scenario_rotation = random.randint(0, 3)

            # Try to set up the scenario in all 4 rotations, but prioritise the
            # current scenario rotation.
            # Also try all scenarios, but prioritise the current one.
            rotations = [self.scenario_rotation]
            # TODO: See note below. It is risky to continue with a failed
            #       offensive scenario. Once the initial scenario fails it
            #       should immediately switch to defensive mode.
            # for n in range(4):
            #   if (n not in rotations):
            #     rotations.append(n)

            scenarios = [self.scenario]
            # TODO: I think it is probably risky to continue with a failed
            #       offensive scenario. Perhaps it should try the initial
            #       scenario, and if that fails, revert to defensive mode,
            #       and only after that should it attempt another offensive
            #       scenario.
            #
            # for n in range(1,4):
            #   if (n not in scenarios):
            #     scenarios.append(n)

            for scen in scenarios:
                for rotation in rotations:
                    b = current_board.get_rotated_board(rotation)

                    if scen == 1:
                        # Scenario 1:
                        # X_
                        # _O
                        # *_X
                        if their_identity in list(b.getat_multi("03678")):
                            # They've blocked us.
                            continue

                        if b.getat_multi("37") != "  ":
                            # Something's gone wrong with our plan.
                            continue

                        move = b.get_first_empty_space("086")
                        if move >= 0:
                            # Update the scenario rotation just in case it's
                            # not the original one.
                            self.scenario = scen
                            self.scenario_rotation = rotation

                            return self.get_unrotated_move(move, rotation)

                    elif scen == 2:
                        # Scenario 2:
                        # X_*
                        #  OX
                        #   _
                        if their_identity in list(b.getat_multi("01258")):
                            # They've blocked us.
                            continue

                        if b.getat_multi("18") != "  ":
                            # Something's gone wrong with our plan.
                            continue

                        move = b.get_first_empty_space("052")
                        if move >= 0:
                            self.scenario = scen
                            self.scenario_rotation = rotation
                            return self.get_unrotated_move(move, rotation)

                    elif scen == 3:
                        # Scenario 3 is just scenario 2 mirrored:
                        # X
                        # _O
                        # *X_
                        if their_identity in list(b.getat_multi("03678")):
                            # They've blocked us.
                            continue

                        if b.getat_multi("38") != "  ":
                            # Something's gone wrong with our plan.
                            continue

                        move = b.get_first_empty_space("076")
                        if move >= 0:
                            self.scenario = scen
                            self.scenario_rotation = rotation
                            return self.get_unrotated_move(move, rotation)

            # If we fall through to here, it means we've tried all offensive
            # moves and scanned all possible scenarios but none are left
            # available to us.

        self.defensive = True
        # Defensive: Avoid 2-way wins.
        for rotation in range(4):
            b = current_board.get_rotated_board(rotation)

            # Scenario 1:
            # X_
            # _O
            # *_X
            if b.getat_multi("03678") == "{0}   {0}".format(their_identity):
                return self.get_unrotated_move(3, rotation)

            # Scenario 2:
            # X_*
            #  OX
            #   _
            if b.getat_multi("01258") == "{0}  {0} ".format(their_identity):
                return self.get_unrotated_move(2, rotation)

            # Scenario 2 in mirrored form:
            # X
            # _O
            # *X_
            if b.getat_multi("03678") == "{0}  {0} ".format(their_identity):
                return self.get_unrotated_move(6, rotation)

            # Scenario 3:
            # NOTE: This scenario actually leaves the opponent vulnerable but
            #       we don't currently exploit this. Ironically I think if we
            #       try to exploit it we are left vulnerable instead.
            #
            # Start with 1, then play 5, then 2.
            #
            # _X*
            #  OX
            #   _
            if b.getat_multi("01258") == " {0} {0} ".format(their_identity):
                return self.get_unrotated_move(2, rotation)

            # Scenario 4:
            #
            # X _
            # _X
            # * O
            if b.getat_multi("02346") == "{0}  {0} ".format(their_identity):
                # This scenario can go two ways, so cover both.
                move = b.get_first_empty_space("62")
                return self.get_unrotated_move(move, rotation)

            # Scenario 4 mirrored:
            #
            # X_*
            #  X
            # _ O
            if b.getat_multi("01246") == "{0}  {0} ".format(their_identity):
                move = b.get_first_empty_space("26")
                return self.get_unrotated_move(move, rotation)

            # TODO: DID I MISS ANY? It should be impossible to win here.

        # Otherwise pick the first move from a series of preferred moves.
        preferred_moves_str = "402681357"
        preferred_moves = list(preferred_moves_str)
        for move in preferred_moves:
            if int(move) in moves:
                return int(move)

        # Shouldn't be here!
        raise Exception("PERFECTBOT failed!")
