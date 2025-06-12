from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar


class Runnable(ABC):
    """Base class for all runnable objects."""

    @abstractmethod
    def run(self):
        """Run the runnable object."""
        raise NotImplementedError("Subclasses must implement this method.")


R = TypeVar("R", bound=Runnable)


class Provided(Generic[R]):
    """A class to provide instances of a specific type."""


class Designer(Runnable): ...


D = TypeVar("D", bound=Designer)
