from collections.abc import Callable

import bpy
import bmesh

from fusrr.base.entity.object_properties import ObjTransformProperties
from fusrr.blender.mesh_tools import (
    new_mesh_for,
)
from fusrr.blender.scene_tools import (
    check_collection_in_scene,
    check_object_in_scene,
    create_collection,
    create_object,
    get_collections,
    get_objects,
    link_collections,
    link_objects_to_collection,
)
from fusrr.core.component import Comp, Compound
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

    def build(self, name: str) -> None:
        if check_object_in_scene(name):
            raise ValueError(
                f"Object with name {name} already exists in the scene."
            )
        obj = create_object(name)
        with new_mesh_for(obj) as m:
            self.build_obj_w_mesh(obj, m)

        # apply properties
        self.transform_props.apply_to(obj)
        # apply material after constructing the object
        if self.material:
            self.material.apply_to(obj)


class BlenderCompound(Compound):
    """Base class for Blender collections."""

    def pre_build(self, name: str) -> None:
        if check_collection_in_scene(name):
            raise ValueError(
                f"Compund with name {name} already exists in the scene."
            )
        self._this_c = create_collection(name)

    def post_build(self, _name: str) -> None:
        # select all created objects, create a collection and add them to it
        created_objs = get_objects(
            set(self.component_names(include_compounds=False))
        )
        link_objects_to_collection(self._this_c, created_objs)

        # get all sub-collections and link them to this collection
        sub_cs = get_collections(set(self.sub_compound_names()))
        for c in sub_cs:
            link_collections(self._this_c, c)
