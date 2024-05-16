from enum import Enum

import bpy

from fusrr.blender.file_tools import (
    BlenderFileDataTypes,
    append_from_blend_file,
)
from fusrr.blender.object_tools import set_object_material
from fusrr.data_libs import FUSRR_DATA_LIB_PATH

FUSRR_MATERIALS_LIB_PATH = FUSRR_DATA_LIB_PATH / "materials_lib.blend"


class FusrrMaterials(Enum):
    """Enum class for materials in the materials library."""

    PLASMA_PINK = "plasma_pink"
    METALLIC_SILVER_MATT = "metallic_silver_matt"
    METALLIC_SILVER_GLOSSY = "metallic_silver_glossy"
    METALLIC_SILVER_SHINY = "metallic_silver_shiny"
    METALLIC_GOLD_SHINY = "metallic_gold_shiny"
    METALLIC_RED_SHINY = "metallic_red_shiny"
    METALLIC_BLUE_DARK_TEXTURED = "metallic_blue_dark_textured"
    METALLIC_BLUE_LIGHT_TEXTURED = "metallic_blue_light_textured"

    def apply_to(self, obj: bpy.types.Object):
        """Applies the material to the object."""
        set_object_material(obj, self.value)


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
