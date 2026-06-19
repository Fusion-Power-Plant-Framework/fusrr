from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, ParamSpec, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable


class Runnable(ABC):
    """Base class for all runnable objects."""

    @abstractmethod
    def run(self):
        """Run the runnable object."""
        raise NotImplementedError("Subclasses must implement this method.")


R = TypeVar("R", bound=Runnable)
P = ParamSpec("P")
T = TypeVar("T")


class Provided(Generic[P, T]):  # noqa: UP046
    """A class to provide instances of a specific type."""

    def __init__(self, cb: Callable[P, T]):
        self._callback = cb
        self.is_set = False

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        if self.is_set:
            raise RuntimeError(
                "This provider has already been set. "
                "`useSetProvider` can be used once to set it."
            )
        self.is_set = True
        return self._callback(*args, **kwargs)


class Designer(Runnable):
    """Base class for designers."""

    # supports cleanup

    def cleanup(self):
        """Cleanup resources after running the designer."""
        raise NotImplementedError("Subclasses must implement this method.")


D = TypeVar("D", bound=Designer)
