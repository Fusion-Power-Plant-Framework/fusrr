from fusrr.blender.file_tools import (
    BlenderFileDataTypes,
    append_from_blend_file,
)
from fusrr.data_libs import FUSRR_DATA_LIB_PATH

FUSRR_MATERIALS_LIB_PATH = FUSRR_DATA_LIB_PATH / "materials_lib.blend"


def load_materials():
    """Loads all materials from the materials library
    into the current bpy state.

    Note:
        This function appends materials from the materials library
        to the current bpy state.
        If a material is not applied to any object, it will not be
        saved in the final .blend file.
    """
    append_from_blend_file(
        FUSRR_MATERIALS_LIB_PATH, BlenderFileDataTypes.MATERIAL
    )
