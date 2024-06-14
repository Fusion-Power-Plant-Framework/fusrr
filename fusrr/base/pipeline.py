from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Generic, TypeVar

from kink import di

from fusrr.base.entity.entity import FusrrWorldEntity
from fusrr.base.entity.object import FusrrWorldObject
from fusrr.base.scene import FusrrScene
from fusrr.base.utils import run_list_async_concurrently
from fusrr.base.world_state import FusrrWorldState
from fusrr.blender.scene_tools import deselect_all

if TYPE_CHECKING:
    from fusrr.base.entity.collection import FusrrWorldCollection

T = TypeVar("T")


class FusrrPipeline(Generic[T], abc.ABC):
    """A FusrrPipeline defines a container with a deterministic ordering."""

    def __init__(self, world_state: FusrrWorldState | None = None):
        """Construct a new build pipeline."""
        self._pipeline: list[T] = []
        self._world_state = world_state or di[FusrrWorldState]

    def add(self, ent: T):
        """Add an entity to this pipeline."""
        self._pipeline.append(ent)

    @abc.abstractmethod
    def execute(self):
        """Execute this pipeline.

        This will modify the blender scene as it goes.
        """


class FusrrBuildPipeline(FusrrPipeline[FusrrWorldEntity]):
    """A FusrrBuildPipeline defines a container with a deterministic ordering
    for constructing FusrrSceneEntity's.
    """

    @property
    def objects(self) -> list[FusrrWorldObject]:
        """Get the names of all entities in this pipeline."""
        return [
            ent for ent in self._pipeline if isinstance(ent, FusrrWorldObject)
        ]

    @property
    def collections(self) -> list[FusrrWorldCollection]:
        """Get the names of all entities in this pipeline."""
        # avoid circular imports
        from fusrr.base.entity.collection import FusrrWorldCollection

        return [
            ent
            for ent in self._pipeline
            if isinstance(ent, FusrrWorldCollection)
        ]

    def entity_names(self) -> set[str]:
        """Get the names of all entities in this pipeline."""
        return {ent.name for ent in self._pipeline}

    def object_names(self) -> set[str]:
        """Get the names of all entities in this pipeline."""
        return {ent.name for ent in self.objects}

    def collection_names(self) -> set[str]:
        """Get the names of all entities in this pipeline."""
        return {ent.name for ent in self.collections}

    def prepare(self):
        """Prepare all entities in this pipeline."""
        if not self._pipeline:
            return

        # runs all prepare methods concurrently (via futures)
        run_list_async_concurrently(self._pipeline, lambda ent: ent.prepare)

    def execute(self):
        """Execute this pipeline.

        This will execute every entity in this pipeline
        (in order), modifying the scene as it goes.
        """
        if not self._pipeline:
            return

        for ent in self._pipeline:
            ent.execute()
            deselect_all()

            if isinstance(ent, FusrrWorldObject):
                self._world_state.add_object(ent)


class FusrrViewPipeline(FusrrPipeline[FusrrScene]):
    """A FusrrViewPipeline defines a container with a deterministic ordering
    for constructing FusrrScene's.
    """

    def execute(self):
        """Execute this pipeline.

        This will execute every scene in this pipeline
        (in order), modifying the scene as it goes.
        """
        if not self._pipeline:
            return

        for scene in self._pipeline:
            scene.execute()
            deselect_all()

            self._world_state.add_scene(scene)
