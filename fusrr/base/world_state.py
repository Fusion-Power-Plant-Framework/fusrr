from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fusrr.base.entity.entity import FusrrSceneEntity
    from fusrr.base.scene import FusrrScene


class FusrrWorldState:
    def __init__(self):
        self._entities: dict[str, FusrrSceneEntity] = {}
        self._scenes: dict[str, FusrrScene] = {}

    def add_entity(self, entity: FusrrSceneEntity):
        """Add an entity to the world state."""
        if entity.name in self._entities:
            raise ValueError(f"Entity with name {entity.name} already exists.")
        self._entities[entity.name] = entity

    def add_scene(self, scene: FusrrScene):
        """Add a scene to the world state."""
        if scene.name in self._scenes:
            raise ValueError(f"Scene with name {scene.name} already exists.")
        self._scenes[scene.name] = scene
