from __future__ import annotations

import abc
from copy import deepcopy

# from typing import Self


class FusrrSceneEntity(abc.ABC):
    """An entity in a FusrrScene, which is some object in Blender.

    This is a base class for all entities that can be added to a FusrrScene.
    """

    def __init__(self, name: str):
        """Initializes a FusrrSceneEntity."""
        self._name = name

    @property
    def name(self) -> str:
        """The name of this entity."""
        return self._name

    def replicate(self, name: str):
        """Replicates this object with a new name.

        Args:
            name:
                The name of the new object.
        """
        self = deepcopy(self)
        self._name = name
        return self

    @abc.abstractmethod
    def execute(self) -> None:
        """Execute this entity, mutating the Blender scene."""
