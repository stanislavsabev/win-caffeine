"""Test start module."""

import pytest
from win_caffeine import gui


def test_start_here():
    """Test start.here."""
    expected = 0
    actual = gui.run()
    assert actual == expected
