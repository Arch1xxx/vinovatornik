"""Виноваторник: назовёт виноватого, не связанного с вашей проблемой."""

from .engine import BlameError, Verdict, blame

__version__ = "0.1.1"

__all__ = ["BlameError", "Verdict", "blame", "__version__"]
