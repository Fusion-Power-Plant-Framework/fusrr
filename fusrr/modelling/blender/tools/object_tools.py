"""Collection of functions that operate on Blender objects."""

from typing import Literal

import bpy
from numpy import isin

from fusrr.core.vectors import Vec3
from fusrr.modelling.blender.tools.scene_tools import create_object


def set_object_material(
    obj: bpy.types.Object,
    material_name: str,
    slot: int = 0,
    *,
    object_name_override: str | None = None,
) -> bpy.types.Material:
    """Applies a material to an object at a specific slot.

    This will replace the material at the slot if it exists.

    Use object_name_override to set the same material on multiple objects.

    Note:
        The material will be copied and renamed to {material_name}.{obj.name}

        However, if object_name_override is provided,
        the material will not be copied if it already exists and the name
        will be {material_name}.{object_name_override}.

    Raises:
        ValueError: If the material is not found or the slot is invalid.

    Args:
        obj:
            The object to apply the material to.
        material_name:
            The name of the material to apply.
        slot:
            The material slot to apply the material to. Defaults to 0.
        object_name_override:
            The name to override the object name in the material,
            after being applied.
            Defaults to None.
    """
    mat_name = (
        f"{material_name}.{obj.name}"
        if object_name_override is None
        else f"{material_name}.{object_name_override}"
    )

    mat = None
    if object_name_override:
        mat = bpy.data.materials.get(mat_name)
    if mat is None:
        mat = bpy.data.materials.get(material_name)
        if mat is None:
            raise ValueError(f"Material with name {material_name} not found.")

        # create a copy of the material and rename it
        # this usually happens when applying a material from the library
        # hence the copy and rename
        mat = mat.copy()
        mat.name = mat_name

    obj_mats = obj.data.materials
    if obj_mats and slot:
        if slot >= len(obj_mats):
            raise ValueError(
                f"Material slot {slot} not found on object {obj.name}.\n"
                f"Max slot: {len(obj_mats) - 1}"
            )
        obj_mats[slot] = mat
    else:
        # no slots and slot is 0
        obj_mats.append(mat)

    return mat


def add_boolean_modifier(
    obj: bpy.types.Object,
    modifier_object: bpy.types.Object,
    modifier_name: str,
    operation: Literal["INTERSECT", "UNION", "DIFFERENCE"] = "DIFFERENCE",
) -> bpy.types.Modifier:
    """Add a boolean modifier to an object.

    Args:
        obj: The object to add the modifier to.
        modifier_object: The 'cutter' object to use for the boolean operation.
        operation: The boolean operation to perform.
        modifier_name: The name of the modifier.
    """
    mod = obj.modifiers.new(modifier_name, type="BOOLEAN")
    mod.object = modifier_object
    mod.operation = operation
    return mod


def set_object_visibility(obj: bpy.types.Object, *, visibility: bool) -> None:
    """Set the visibility of an object.

    This includes the viewport and render visibility.

    Args:
        obj: The object to set the visibility of.
        visibility: The visibility state to set.
    """
    # obj.hide_viewport = not visibility
    obj.hide_render = not visibility
    obj.hide_set(not visibility)


def add_camera(name: str) -> bpy.types.Object:
    """Add a camera to the scene.

    Args:
        name: The name of the camera to add.
    """
    cam_data = bpy.data.cameras.new(name)
    cam = bpy.data.objects.new(name, cam_data)
    bpy.context.scene.collection.objects.link(cam)
    return cam


def move_camera(vec: Vec3) -> None:
    """Selects and moves the scene camera"""
    camera = bpy.data.objects["Camera"]
    camera.location = vec.tup


def copy_object_w_mesh(
    obj: bpy.types.Object,
    new_name: str | None = None,
) -> bpy.types.Object:
    """Returns a copy of an object and its mesh with a new name.

    Args:
        obj: The object to copy.
        new_name: The name of the new object. If None, the name will be
            the same as the original object with ".copy" appended.
    """
    if new_name is None:
        new_name = f"{obj.name}.copy"
    if not isinstance(obj.data, bpy.types.Mesh):
        raise TypeError(
            f"Object {obj.name} is not a mesh object. "
            "Cannot copy object with mesh."
        )
    new_mesh = obj.data.copy()
    new_mesh.name = new_name
    new_obj = create_object(new_name, mesh=new_mesh)
    new_obj.matrix_world = obj.matrix_world.copy()
    return new_obj
