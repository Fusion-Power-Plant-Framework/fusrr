from __future__ import annotations

import abc
from typing import TYPE_CHECKING

from fusrr.blender.object_tools import set_object_material
from fusrr.data_libs.materials import FusrrMaterialDataLabel

if TYPE_CHECKING:
    import bpy


class FusrrMaterial:
    def __init__(self, data_label: FusrrMaterialDataLabel):
        self.material_data_label = data_label

    def configure(self, mat: bpy.types.Material):
        pass

    def apply(self, obj: bpy.types.Object):
        mat = set_object_material(obj, self.material_data_label.value)
        self.configure(mat)


class PlasmaMaterial(FusrrMaterial):
    def __init__(self):
        super().__init__(FusrrMaterialDataLabel.PLASMA_PINK)

    def configure(self, mat: bpy.types.Material):
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value = (0.8, 0.2, 0.8, 1)
        bsdf.inputs["Metallic"].default_value = 0.0
        bsdf.inputs["Roughness"].default_value = 0.5


class MetallicMaterial(FusrrMaterial):
    def __init__(self):
        super().__init__(FusrrMaterialDataLabel.METALLIC_GOLD_SHINY)
