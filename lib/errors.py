"""Exceptions."""


class GameError(Exception):
    """Generic game error."""

    pass


class GameCreateError(GameError):
    """An error occurred creating game."""

    pass


class BotError(Exception):
    """Generic bot error."""

    pass


class BotCreateError(BotError):
    """An error occurred creating bot."""

    pass

