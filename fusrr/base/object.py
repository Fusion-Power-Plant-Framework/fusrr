from typing import TYPE_CHECKING

import bpy
import numpy as np
import bmesh
import bpy_types
import mathutils

from fusrr.base.models import Vec3
from fusrr.base.pipeline import FusrrBuildPipeline
from fusrr.base.types import OptionalConstructor

if TYPE_CHECKING:
    from fusrr.base.scene import FusrrScene


class FusrrSceneObject(FusrrBuildPipeline):
    """A FusrrSceneObject is a object that can be added to a FusrrScene."""

    def __init__(self, name: str, constructor: OptionalConstructor):
        self.name = name
        self.constructor = constructor
        super().__init__(name)

        self._setup()

    def _setup(self) -> None:  # noqa: PLR6301
        return

    def _construct(self, scene: "FusrrScene") -> None:
        if self.constructor is not None:
            self.constructor(scene)

    def execute(self, scene: "FusrrScene"):
        """Executes the FusrrSceneObject."""
        scene.execute_construct_object(self.name, self._construct)
        super().execute(scene)


def empty(name: str, location: Vec3, size: int = 1) -> FusrrSceneObject:
    """Adds an empty object to the scene.

    Note: Useful for camera tracking purposes.

    Args:
        name: Name of empty
        location: Location of the empty
        size: Size of cube. Defaults to 1.
    """

    def _construct(_scene: "FusrrScene") -> None:
        bpy.ops.object.empty_add(location=location.tup, size=size)

    return FusrrSceneObject(
        name,
        _construct,
    )


def cube(
    name: str, location: Vec3, size: int = 1, scale: Vec3 = Vec3.ONE
) -> FusrrSceneObject:
    """Adds a cube to the scene.

    Args:
        name: Name of cube
        location: Location of cube
        size: Size of cube. Defaults to 1.
        scale: Scale of cube. Defaults to Vec3.ONE.
    """

    def _construct(_scene: "FusrrScene") -> None:
        bpy.ops.mesh.primitive_cube_add(location=location.tup, size=size)
        bpy.context.object.scale = scale.tup

    return FusrrSceneObject(
        name,
        _construct,
    )


# def add_mesh(name, verts, faces, edges=None, col_name="Collection"):
#     if edges is None:
#         edges = []
#     mesh = bpy.data.meshes.new(name)
#     obj = bpy.data.objects.new(mesh.name, mesh)
#     col = bpy.data.collections[col_name]
#     col.objects.link(obj)
#     bpy.context.view_layer.objects.active = obj
#     mesh.from_pydata(verts, edges, faces)
