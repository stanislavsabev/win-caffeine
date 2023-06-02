"""Test start module."""

import win_caffeine


def test_start_here():
    """Test start.here."""
    expected = 'Your code goes here!'
    actual = win_caffeine.start()
    assert actual == expected