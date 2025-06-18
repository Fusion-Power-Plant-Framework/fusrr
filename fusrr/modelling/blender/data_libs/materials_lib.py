from enum import Enum

from fusrr.modelling.blender.data_libs import BLENDER_DATA_LIBS_PATH
from fusrr.modelling.blender.tools.file_tools import (
    BlenderFileDataTypes,
    append_from_blend_file,
)

MATERIALS_LIB_PATH = BLENDER_DATA_LIBS_PATH / "materials_lib.blend"


class BlenderMaterialDataLabel(Enum):
    """Enum class for materials in the materials_lib.blend library."""

    PLASMA = "plasma"
    METALLIC = "metallic"
    METALLIC_BLUE_DARK_TEXTURED = "metallic_textured"
    GLASS = "glass"


def load_materials():
    """Loads all materials from the materials library
    into the current bpy state.

    Note:
        This function appends materials from the materials library
        to the current bpy state.
        If a material is not applied to any object, it will not be
        saved in the final .blend file.
    """
    append_from_blend_file(MATERIALS_LIB_PATH, BlenderFileDataTypes.MATERIAL)
