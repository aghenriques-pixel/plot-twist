"""Shared test setup."""

import random

import pytest


@pytest.fixture(autouse=True)
def no_luck(monkeypatch):
    """The app rolls random.random() for chance outcomes (specs/levels-dialogue-accounts.md).
    In tests the roll is always high, so the app takes the main outcome every time and app tests
    never depend on luck. Logic tests pass their own roll to apply_action."""
    monkeypatch.setattr(random, "random", lambda: 0.99)
