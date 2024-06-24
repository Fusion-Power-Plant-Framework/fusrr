from __future__ import annotations

from typing import TYPE_CHECKING

from fusrr.base.entity.entity import FusrrWorldEntity
from fusrr.base.entity.object import FusrrWorldObject
from fusrr.base.pipeline.pipeline import FusrrPipeline
from fusrr.base.utils import run_list_async_concurrently
from fusrr.blender.scene_tools import deselect_all

if TYPE_CHECKING:
    from fusrr.base.entity.collection import FusrrWorldCollection


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
