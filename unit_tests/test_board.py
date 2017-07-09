#!/usr/bin/env python
"""
Unit test for the Naughts and Crosses board.

cd ..
python -m unittest -v test_board.py
"""


import unittest

import game.board as board
from bots.bot_base import Bot


class BoardTest(unittest.TestCase):
    """Basic unit tests for game.board.Board."""

    def test_board(self):
        """Various unit tests for Board."""
        b = board.Board()

        b.data = 'X--OO-OXX'

        multi = b.getat_multi('012')
        self.assertEqual(multi, 'X  ', "getat_multi() with 012")

        multi = b.getat_multi('1234')
        self.assertEqual(multi, '  OO', "getat_multi() with 1234")

        multi = b.getat_multi('58712')
        self.assertEqual(multi, ' XX  ', "getat_multi() with 58712")

        # Test rotated boards
        rot1 = b.get_rotated_board(1)
        self.assertEqual(rot1.data, 'OOXXO-X--',
                         "get_rotated_board() with 1 rotation")

        rot2 = b.get_rotated_board(2)
        self.assertEqual(rot2.data, 'XXO-OO--X',
                         "get_rotated_board() with 2 rotations")

        rot3 = b.get_rotated_board(3)
        self.assertEqual(rot3.data, '--X-OXXOO',
                         "get_rotated_board() with 3 rotations")

        # Also test robot base methods that interact with boards.
        base_robot = Bot()
        self.assertEqual(base_robot.get_unrotated_move(1, 3), 5,
                         "get_unrotated_move(1) with 3 rotations")
        self.assertEqual(base_robot.get_unrotated_move(1, 2), 7,
                         "get_unrotated_move(1) with 2 rotations")
        self.assertEqual(base_robot.get_unrotated_move(1, 1), 3,
                         "get_unrotated_move(1) with 1 rotation")

        return
