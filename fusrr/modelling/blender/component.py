from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

import bpy
import bmesh

from fusrr.core.component import Comp, Compound
from fusrr.core.config_model import S, SceneState
from fusrr.core.vectors import Vec3
from fusrr.modelling.blender.tools.mesh_tools import (
    new_mesh_for,
)
from fusrr.modelling.blender.tools.scene_tools import (
    check_collection_in_scene,
    check_object_in_scene,
    create_collection,
    create_object,
    get_collections,
    get_objects,
    link_collections,
    link_objects_to_collection,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from fusrr.modelling.blender.materials.base import BlenderMaterial


@dataclass
class BlenderTransformProperties:
    """Common properties for object transforms."""

    center_point: Vec3 | Literal["centroid"] = Vec3.ZERO
    position: Vec3 | None = None
    rotation: Vec3 | None = None
    scale: Vec3 = Vec3.ONE

    def apply_to(self, obj: bpy.types.Object) -> None:
        """Applies the transform properties to the object."""
        if self.position is not None:
            obj.location = self.position.tup
        if self.rotation is not None:
            obj.rotation_euler = self.rotation.tup
        if self.scale != Vec3.ONE:
            obj.scale = self.scale.tup


def _blender_component_name(name: str, scene_state: SceneState[S]) -> str:
    """Generates a unique name for a Blender component based on the scene state."""
    return f"{scene_state.scene_name}.{name}"


class BlenderComp(Comp[S]):
    """Base class for Blender components."""

    def __init__(
        self,
        *,
        builder: Callable[[bpy.types.Object, bmesh.types.BMesh], None],
        material: BlenderMaterial | None = None,
        transform_props: BlenderTransformProperties | None = None,
    ):
        """Initialize the Blender component with a name."""
        self._build_with_mesh = builder
        self.material = material
        self.transform_props = transform_props or BlenderTransformProperties()

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

    def build(self, name: str, scene_state: SceneState[S]) -> None:
        self.b_component_name = _blender_component_name(name, scene_state)
        if check_object_in_scene(self.b_component_name):
            raise ValueError(
                f"Object with name {self.b_component_name} already exists in the scene."
            )
        obj = create_object(self.b_component_name)
        with new_mesh_for(obj) as m:
            self.build_obj_w_mesh(obj, m)
        # apply properties
        self.transform_props.apply_to(obj)
        # apply material after constructing the object
        if self.material:
            self.material.apply_to(obj)


class BlenderCompound(Compound[S]):
    """Base class for Blender collections."""

    def _get_sub_component_names(self) -> list[str]:
        """Returns the names of sub-components, must be run in post_build only."""
        return [
            c.constructed.b_component_name
            for c in self.components
            if isinstance(c.constructed, BlenderComp)
        ]

    def _get_sub_collection_names(self) -> list[str]:
        """Returns the names of sub-compounds, must be run in post_build only."""
        return [
            c.constructed.b_collection_name
            for c in self.components
            if isinstance(c.constructed, BlenderCompound)
        ]

    def pre_build(self, name: str, scene_state: SceneState[S]) -> None:
        self.b_collection_name = _blender_component_name(name, scene_state)
        if check_collection_in_scene(self.b_collection_name):
            raise ValueError(
                f"Compound with name {self.b_collection_name} already exists in the scene."
            )
        self._this_c = create_collection(self.b_collection_name)

    def post_build(self, _name: str, _scene_state: SceneState[S]) -> None:
        # select all created objects, create a collection and add them to it
        created_objs = get_objects(set(self._get_sub_component_names()))
        link_objects_to_collection(self._this_c, created_objs)

        # get all sub-collections and link them to this collection
        sub_cs = get_collections(set(self._get_sub_collection_names()))
        for c in sub_cs:
            link_collections(self._this_c, c)
