from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

import bpy
import bmesh

from fusrr.core.component import Comp, Compound
from fusrr.core.config_model import S, Scene
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
from fusrr.modelling.blender.transform import BlenderTransform

if TYPE_CHECKING:
    from collections.abc import Callable

    from fusrr.modelling.blender.materials.base import BlenderMaterial


def _blender_component_name(name: str, scene: Scene[S]) -> str:
    """Generates a unique name for a Blender component based on the scene state."""
    return f"{scene.name}.{name}"


class BlenderComp(Comp[S]):
    """Base class for Blender components."""

    def __init__(
        self,
        *,
        builder: Callable[[bpy.types.Object, bmesh.types.BMesh], None]
        | None = None,
        obj_builder: Callable[[str], bpy.types.Object] | None = None,
        material: BlenderMaterial | None = None,
        transform: BlenderTransform | None = None,
    ):
        """Initialize the Blender component with a name."""
        self._build_with_mesh = builder
        self._obj_builder = obj_builder
        self.material = material
        self.transform = transform or BlenderTransform()

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

    def build_obj(self, comp_name: str) -> bpy.types.Object:
        """Builds the object without a mesh.

        This is used when the object is created without a mesh,
        for example, when using an external model.
        """
        if self._obj_builder:
            return self._obj_builder(comp_name)
        raise NotImplementedError(
            "No object builder provided, cannot build object without mesh."
        )

    def build(self, name: str, scene: Scene[S]) -> None:
        b_component_name = _blender_component_name(name, scene)
        if check_object_in_scene(b_component_name):
            raise ValueError(
                f"Object with name {b_component_name} already exists in the scene."
            )
        obj = None
        with contextlib.suppress(NotImplementedError):
            obj = self.build_obj(b_component_name)
        if obj is None:
            with contextlib.suppress(NotImplementedError):
                obj_instance = create_object(b_component_name)
                with new_mesh_for(obj_instance) as m:
                    self.build_obj_w_mesh(obj_instance, m)
                obj = obj_instance
        if obj is None:
            raise ValueError(
                f"No builder provided for {name}, could not be built."
            )
        # apply properties
        self.transform.apply_to(obj)
        # apply material after constructing the object
        if self.material:
            self.material.apply_to(obj)
        self.b_component_name = b_component_name


class BlenderCompound(Compound[S]):
    """Base class for Blender collections."""

    def _get_sub_component_names(self) -> list[str]:
        """Returns the names of sub-components, must be run in post_build only."""
        return [
            c.built.b_component_name
            for c in self.components
            if isinstance(c.built, BlenderComp)
        ]

    def _get_sub_collection_names(self) -> list[str]:
        """Returns the names of sub-compounds, must be run in post_build only."""
        return [
            c.built.b_collection_name
            for c in self.components
            if isinstance(c.built, BlenderCompound)
        ]

    def pre_build(self, name: str, scene: Scene[S]) -> None:
        b_collection_name = _blender_component_name(name, scene)
        if check_collection_in_scene(b_collection_name):
            raise ValueError(
                f"Compound with name {b_collection_name} "
                "already exists in the scene."
            )
        self._this_c = create_collection(b_collection_name)
        self.b_collection_name = b_collection_name
        super().pre_build(name, scene)

    def post_build(self, name: str, scene: Scene[S]) -> None:
        # select all created objects, create a collection and add them to it
        created_objs = get_objects(set(self._get_sub_component_names()))
        link_objects_to_collection(self._this_c, created_objs)

        # get all sub-collections and link them to this collection
        sub_cs = get_collections(set(self._get_sub_collection_names()))
        for c in sub_cs:
            link_collections(self._this_c, c)
        super().post_build(name, scene)
