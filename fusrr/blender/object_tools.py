"""Collection of functions that operate on Blender objects."""

import bpy


def set_object_material(
    obj: bpy.types.Object, material_name: str, slot: int = 0
) -> bpy.types.Material:
    """Applies a material to an object at a specific.

    This will replace a material if it is already applied to the object.

    Note:
        This will raise a ValueError if the material is not found.

    Args:
        obj: The object to apply the material to.
        material_name: The name of the material to apply.
        slot: The material slot to apply the material to. Defaults to 0.
    """
    mat = bpy.data.materials.get(material_name)
    if mat is None:
        raise ValueError(f"Material with name {material_name} not found.")

    obj_mats = obj.data.materials
    if obj_mats and slot:
        if slot >= len(obj_mats):
            raise ValueError(
                f"Material slot {slot} not found on object {obj.name}.\n"
                f"Max slot: {len(obj_mats) -1}"
            )
        obj_mats[slot] = mat
    else:
        # no slots and slot is 0
        obj_mats.append(mat)

    return mat
