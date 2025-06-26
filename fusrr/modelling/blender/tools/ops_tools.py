import bpy

from fusrr.core.vectors import Vec3


def translate_selected(translation: Vec3):
    """Translate the selected objects by the given delta.

    Args:
        translation: The translation vector.
    """
    bpy.ops.transform.translate(value=translation.tup)
