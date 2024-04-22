from __future__ import annotations

from typing import TYPE_CHECKING

from fusrr.blender.scene_tools import deselect_all

if TYPE_CHECKING:
    from fusrr.base.collection import FusrrSceneCollection
    from fusrr.base.entity import FusrrSceneEntity
    from fusrr.base.object import FusrrSceneObject


class FusrrBuildPipeline:
    """A FusrrBuildPipeline defines a container with a deterministic ordering
    for constructing FusrrSceneEntity's.
    """

    def __init__(self):
        """Construct a new build pipeline."""
        self._pipeline: list[FusrrSceneEntity] = []

    def add(self, ent: FusrrSceneEntity):
        """Add an entity to this pipeline."""
        self._pipeline.append(ent)

    @property
    def objects(self) -> list[FusrrSceneObject]:
        """Get the names of all entities in this pipeline."""
        from fusrr.base.object import FusrrSceneObject

        return [
            ent for ent in self._pipeline if isinstance(ent, FusrrSceneObject)
        ]

    @property
    def collections(self) -> list[FusrrSceneCollection]:
        """Get the names of all entities in this pipeline."""
        from fusrr.base.collection import FusrrSceneCollection

        return [
            ent
            for ent in self._pipeline
            if isinstance(ent, FusrrSceneCollection)
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


# class FusrrViewPipeline(FusrrPipeline):
