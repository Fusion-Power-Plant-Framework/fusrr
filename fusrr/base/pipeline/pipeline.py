from __future__ import annotations

import abc
from typing import Generic, TypeVar

from kink import di

from fusrr.base.world_state import FusrrWorldState

T = TypeVar("T")


class FusrrPipeline(Generic[T], abc.ABC):
    """A FusrrPipeline defines a container with a deterministic ordering."""

    def __init__(self, world_state: FusrrWorldState | None = None):
        """Construct a new build pipeline."""
        self._pipeline: list[T] = []
        self._world_state = world_state or di[FusrrWorldState]

    def add(self, ent: T):
        """Add a `T` to this pipeline."""
        self._pipeline.append(ent)

    @abc.abstractmethod
    def execute(self):
        """Execute this pipeline.

        This will modify the blender scene as it goes.
        """
