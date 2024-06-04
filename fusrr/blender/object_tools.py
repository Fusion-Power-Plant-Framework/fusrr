"""Collection of functions that operate on Blender objects."""

import bpy


def set_object_material(
    obj: bpy.types.Object,
    material_name: str,
    slot: int = 0,
    *,
    object_name_override: str | None = None,
) -> bpy.types.Material:
    """Applies a material to an object at a specific slot.

    This will replace the material at the slot if it exists.

    Use name_suffix_override to set the same material on multiple objects.

    Note:
        The material will be copied and renamed to {material_name}.{obj.name}

        However, if name_suffix_override is provided,
        the material will not be copied if it already exists and the name
        will be {material_name}.{name_suffix_override}.

    Raises:
        ValueError: If the material is not found or the slot is invalid.

    Args:
        obj:
            The object to apply the material to.
        material_name:
            The name of the material to apply.
        slot:
            The material slot to apply the material to. Defaults to 0.
        name_suffix_override:
            The suffix to append to the material name.
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
        mat = mat.copy()
        mat.name = mat_name

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
