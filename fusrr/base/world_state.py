from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fusrr.base.entity.object import FusrrWorldObject
    from fusrr.base.scene import FusrrScene


class FusrrWorldState:
    def __init__(self):
        self._objs: dict[str, FusrrWorldObject] = {}
        self._scenes: dict[str, FusrrScene] = {}

    def add_object(self, obj: FusrrWorldObject):
        """Add an object to the world state."""
        if obj.name in self._objs:
            raise ValueError(f"Entity with name {obj.name} already exists.")
        self._objs[obj.name] = obj

    def add_scene(self, scene: FusrrScene):
        """Add a scene to the world state."""
        if scene.name in self._scenes:
            raise ValueError(f"Scene with name {scene.name} already exists.")
        self._scenes[scene.name] = scene
