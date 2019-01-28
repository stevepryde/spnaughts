#!/usr/bin/env python
"""
Unit test for the Naughts and Crosses board.

cd ..
python -m unittest -v test_board.py
"""


import unittest

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from games.naughts.board import Board


class BoardTest(unittest.TestCase):
    """Basic unit tests for game.board.Board."""

    def test_board(self):
        """Various unit tests for Board."""
        b = Board()

        b.data = "X--OO-OXX"

        multi = b.getat_multi("012")
        self.assertEqual(multi, "X  ", "getat_multi() with 012")

        multi = b.getat_multi("1234")
        self.assertEqual(multi, "  OO", "getat_multi() with 1234")

        multi = b.getat_multi("58712")
        self.assertEqual(multi, " XX  ", "getat_multi() with 58712")

        # Test rotated boards
        rot1 = b.get_rotated_board(1)
        self.assertEqual(rot1.data, "OOXXO-X--", "get_rotated_board() with 1 rotation")

        rot2 = b.get_rotated_board(2)
        self.assertEqual(rot2.data, "XXO-OO--X", "get_rotated_board() with 2 rotations")

        rot3 = b.get_rotated_board(3)
        self.assertEqual(rot3.data, "--X-OXXOO", "get_rotated_board() with 3 rotations")
        return
