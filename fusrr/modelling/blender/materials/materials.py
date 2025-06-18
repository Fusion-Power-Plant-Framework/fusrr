from __future__ import annotations

from typing import TYPE_CHECKING

from fusrr.modelling.blender.data_libs.materials_lib import (
    BlenderMaterialDataLabel,
)
from fusrr.modelling.blender.materials.base import BlenderMaterial

if TYPE_CHECKING:
    from fusrr.modelling.blender.materials.value_models import (
        MaterialColour,
        MaterialValue,
        MaterialValueZeroToOne,
    )

# add all new materials to this list
__all__ = [
    "GlassMaterial",
    "MetallicMaterial",
    "PlasmaMaterial",
]


class PlasmaMaterial(BlenderMaterial):
    def __init__(
        self,
        object_name_override: str | None = None,
        core_colour: MaterialColour | None = None,
        y_colour_ramp: MaterialColour | None = None,
        z_colour_ramp: MaterialColour | None = None,
        core_fresnel: MaterialValue | None = None,
        border_colour: MaterialColour | None = None,
        plasma_emission_colour: MaterialColour | None = None,
        plasma_emission: MaterialValue | None = None,
        border_plasma_transparancy: MaterialColour | None = None,
        border_fresnel: MaterialValueZeroToOne | None = None,
    ):
        self.core_colour = core_colour
        self.y_colour_ramp = y_colour_ramp
        self.z_colour_ramp = z_colour_ramp
        self.core_fresnel = core_fresnel
        self.border_colour = border_colour
        self.plasma_emission_colour = plasma_emission_colour
        self.plasma_emission = plasma_emission
        self.border_plasma_transparancy = border_plasma_transparancy
        self.border_fresnel = border_fresnel
        super().__init__(object_name_override)

    @property
    def material_label(self) -> BlenderMaterialDataLabel:
        return BlenderMaterialDataLabel.PLASMA

    def _configure(self, mat: bpy.types.Material) -> None:
        mat.use_nodes = True

        # change the y axis colour of texture
        if self.y_colour_ramp:
            ramp_colour = mat.node_tree.nodes.get("y_axis_colour_ramp")
            ramp_colour.color_ramp.elements[1].color = self.y_colour_ramp.tup

        # change the z axis colour of texture
        if self.z_colour_ramp:
            ramp_colour = mat.node_tree.nodes.get("z_axis_colour_ramp")
            ramp_colour.color_ramp.elements[1].color = self.z_colour_ramp.tup

        # change the core colour of the plasma
        if self.core_colour:
            bsdf = mat.node_tree.nodes.get("plasma_core_colour")
            bsdf.inputs["Base Color"].default_value = self.core_colour.tup

        # change the brightness of plasma
        if self.core_fresnel:
            plasma_brightness = mat.node_tree.nodes.get("plasma_fresnel")
            plasma_brightness.inputs[0].default_value = self.core_fresnel.tup

        # change the border plasma colour
        if self.border_colour:
            bsdf = mat.node_tree.nodes.get("border_plasma_colour")
            bsdf.inputs["Base Color"].default_value = self.border_colour.tup

        # change the border plasma emission colour
        if self.plasma_emission_colour:
            emission_colour = mat.node_tree.nodes.get("border_plasma_emission")
            emission_colour.inputs[
                0
            ].default_value = self.plasma_emission_colour.tup

        # change the border plasma emission strength
        if self.plasma_emission:
            emission_strength = mat.node_tree.nodes.get(
                "border_plasma_emission"
            )
            emission_strength.inputs[1].default_value = self.plasma_emission.tup

        # change the border plasma transparancy colour
        if self.border_plasma_transparancy:
            transparancy = mat.node_tree.nodes.get(
                "border_plasma_transparent_BSDF"
            )
            transparancy.inputs[
                0
            ].default_value = self.border_plasma_transparancy.tup

        # change the border brightness of plasma
        if self.border_fresnel:
            plasma_brightness = mat.node_tree.nodes.get("plasma_fresnel")
            plasma_brightness.inputs[0].default_value = self.border_fresnel.tup


class MetallicMaterial(BlenderMaterial):
    def __init__(
        self,
        object_name_override: str | None = None,
        base_colour: MaterialColour | None = None,
        metallicness: MaterialValueZeroToOne | None = None,
        roughness: MaterialValueZeroToOne | None = None,
    ):
        self.base_colour = base_colour
        self.metallicness = metallicness
        self.roughness = roughness
        super().__init__(object_name_override)

    @property
    def material_label(self) -> BlenderMaterialDataLabel:
        return BlenderMaterialDataLabel.METALLIC

    def _configure(self, mat: bpy.types.Material) -> None:
        mat.use_nodes = True

        main_node_label = "main"

        if self.base_colour:
            bsdf = mat.node_tree.nodes.get(main_node_label)
            bsdf.inputs["Base Color"].default_value = self.base_colour.tup

        if self.metallicness:
            bsdf = mat.node_tree.nodes.get(main_node_label)
            bsdf.inputs["Metallic"].default_value = self.metallicness.tup

        if self.roughness:
            bsdf = mat.node_tree.nodes.get(main_node_label)
            bsdf.inputs["Roughness"].default_value = self.roughness.tup


class GlassMaterial(BlenderMaterial):
    def __init__(self, object_name_override: str | None = None):
        super().__init__(object_name_override)

    @property
    def material_label(self) -> BlenderMaterialDataLabel:
        return BlenderMaterialDataLabel.GLASS
