from collections.abc import Callable

import bpy
import bmesh

from fusrr.base.entity.object_properties import ObjTransformProperties
from fusrr.blender.mesh_tools import (
    new_mesh_for,
)
from fusrr.blender.scene_tools import (
    check_object_in_scene,
    create_object,
)
from fusrr.core.component import Comp
from fusrr.materials.base import FusrrMaterial


class BlenderComp(Comp):
    """Base class for Blender components."""

    def __init__(
        self,
        builder: Callable[[bpy.types.Object, bmesh.types.BMesh], None],
        material: FusrrMaterial | None = None,
        transform_props: ObjTransformProperties | None = None,
    ):
        """Initialize the Blender component with a name."""
        self._build_with_mesh = builder
        self.material = material
        self.transform_props = transform_props or ObjTransformProperties()

    def build_obj_w_mesh(
        self,
        obj: bpy.types.Object,
        mesh: bmesh.types.BMesh,
    ) -> None:
        """Constructs this object in the current scene.

        bpy functions will be called during this method to construct the object.
        """
        if self._build_with_mesh:
            self._build_with_mesh(obj, mesh)
        else:
            raise NotImplementedError

    def build(self) -> None:
        if check_object_in_scene(self.name):
            raise ValueError(
                f"Object with name {self.name} already exists in the scene."
            )
        obj = create_object(self.name)

        with new_mesh_for(obj) as m:
            self.build_obj_w_mesh(obj, m)

            # apply properties
            self.transform_props.apply_to(obj)

        # apply material after constructing the object
        mat = self.material
        if callable(mat):
            mat = mat()
        if mat is not None:
            mat.apply_to(obj)
