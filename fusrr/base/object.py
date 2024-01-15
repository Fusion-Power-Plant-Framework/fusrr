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
    def __init__(self, name: str, constructor: OptionalConstructor):
        self.name = name
        self.constructor = constructor
        super().__init__(name + "_group")

        self._build()

    def _build(self) -> None:  # noqa: PLR6301
        return

    def _self_construct(self) -> None:
        if self.constructor is not None:
            self.constructor()

    def execute(self, scene: "FusrrScene"):
        """Executes the FusrrSceneObject."""
        scene.execute_construct_object(self.name, self._self_construct)
        super().execute(scene)


def empty_obj(x, y, z):
    """Empty object adder.

    Note: Useful for camera tracking purposes.

    """
    bpy.ops.object.empty_add(location=(x, y, z))


def cube(
    name: str, location: Vec3, size: int = 1, scale: Vec3 = Vec3.ONE
) -> FusrrSceneObject:
    """Creates a FusrrSceneObject cube.

    Args:
        name: Name of cube
        location: Location of cube
        size: Size of cube. Defaults to 1.
        scale: Scale of cube. Defaults to Vec3.ONE.
    """

    def _construct() -> None:
        bpy.ops.mesh.primitive_cube_add(location=location.tup, size=size)
        bpy.context.object.scale = scale.tup

    return FusrrSceneObject(
        name,
        _construct,
    )


def add_mesh(name, verts, faces, edges=None, col_name="Collection"):
    if edges is None:
        edges = []
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(mesh.name, mesh)
    col = bpy.data.collections[col_name]
    col.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    mesh.from_pydata(verts, edges, faces)
