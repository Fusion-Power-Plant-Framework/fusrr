from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Generic

from fusrr.base.entity import FusrrSceneEntity
from fusrr.base.models import Vec3
from fusrr.base.types import CFT
from fusrr.blender.mesh_tools import add_cube, add_empty, new_mesh_for
from fusrr.blender.scene_tools import check_object_in_scene, create_object

if TYPE_CHECKING:
    import bpy
    import bmesh

    from fusrr.base.types import ObjConstructor
    from fusrr.materials.base import FusrrMaterial


class FusrrSceneObject(FusrrSceneEntity):
    """A FusrrSceneObject is a object that can be added to a FusrrScene."""

    def __init__(self, name: str):
        """Initializes a FusrrSceneObject."""
        super().__init__(name)
        self._setup()

    def _setup(self) -> None:
        """Setup this object, caching any necessary data."""

    @property
    def material(self) -> FusrrMaterial | None:
        """The material of this object."""
        return None

    @abc.abstractmethod
    def _construct(
        self,
        obj: bpy.types.Object,
        mesh: bmesh.types.BMesh,
    ) -> None:
        """Constructs this object in the current scene.

        bpy functions will be called during this method to construct the object.
        """
        raise NotImplementedError

    def execute(self) -> None:
        """Executes this object in the given context frame."""
        if check_object_in_scene(self.name):
            raise ValueError(
                f"Object with name {self.name} already exists in the scene."
            )
        obj = create_object(self.name)

        with new_mesh_for(obj) as m:
            self._construct(obj, m)

        # apply material after constructing the object
        mat = self.material
        if callable(mat):
            mat = mat()
        if mat is not None:
            mat.apply(obj)


class FusrrSceneObjectFromFunction(FusrrSceneObject):
    """A FusrrSceneObjectFromFunction is a FusrrSceneObject that
    is constructed from a given function.
    """

    def __init__(
        self,
        name: str,
        constructor: ObjConstructor,
    ):
        """Initializes a FusrrSceneObject."""
        self._constructor = constructor
        super().__init__(name)

    def _construct(
        self, obj: bpy.types.Object, mesh: bmesh.types.BMesh
    ) -> None:
        pass

    def execute(self) -> None:
        """Executes this object in the given context frame.

        Args:
            ctx:
                The context frame to execute this object in.
        """
        self._constructor()


class FusrrSceneObjectWithContext(FusrrSceneObject, Generic[CFT], abc.ABC):
    """A FusrrSceneObjectWithContext is a Blender object,
    that can be added to a FusrrScene,
    that uses some context during its execute phase.
    """

    def __init__(
        self,
        name: str,
        ctx: CFT,
    ):
        """Initializes a FusrrSceneObject."""
        self._ctx = ctx
        super().__init__(name)

    @property
    def ctx(self) -> CFT:
        """The context frame of this object."""
        return self._ctx

    def replicate_with_ctx(
        self, name: str, ctx: CFT
    ) -> FusrrSceneObjectWithContext[CFT]:
        """Replicates this object with a new name and context.

        Args:
            name:
                The name of the new object.
            ctx:
                The context frame of the new object.
        """
        self = self.replicate(name)
        self._ctx = ctx
        return self


def empty(name: str, location: Vec3) -> FusrrSceneObject:
    """Adds an empty object to the scene.

    Note: Useful for camera tracking purposes.

    Args:
        name: Name of empty
        location: Location of the empty
        size: Size of cube. Defaults to 1.
    """
    return FusrrSceneObjectFromFunction(name, lambda: add_empty(name, location))


def cube(name: str, location: Vec3, scale: Vec3 = Vec3.ONE) -> FusrrSceneObject:
    """Adds a cube to the scene.

    Args:
        name: Name of cube
        location: Location of cube
        scale: Scale of cube. Defaults to Vec3.ONE.
    """
    return FusrrSceneObjectFromFunction(
        name, lambda: add_cube(name, location, scale)
    )
