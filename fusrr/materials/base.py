from __future__ import annotations

import abc
from typing import TYPE_CHECKING

from fusrr.blender.object_tools import set_object_material
from fusrr.data_libs.materials import FusrrMaterialDataLabel

if TYPE_CHECKING:
    import bpy

    from fusrr.materials.models import MaterialColour, MaterialValueZeroToOne


class FusrrMaterial(abc.ABC):
    """Base class for materials used in Fusrr.

    This class should be subclassed to create new materials.
    """

    def __init__(self, object_name_override: str | None = None):
        """Initializes the material with the given data label.

        Args:
            object_name_override:
                Overrides the object name when applying the material, allowing
                the same material to be applied to multiple objects.

                Defaults to None
                (each material applied will be new and unique to the object).
        """
        self._object_name_override = object_name_override

    @property
    @abc.abstractmethod
    def material_label(self) -> FusrrMaterialDataLabel:
        """The material label for this material."""

    def _configure(self, mat: bpy.types.Material) -> None:
        """Applies the material configuration to the given material."""

    def apply_to(self, obj: bpy.types.Object):
        """Applies the material to the object.

        Args:
            obj: The object to apply the material to.
        """
        mat = set_object_material(
            obj,
            self.material_label.value,
            object_name_override=self._object_name_override,
        )
        self._configure(mat)


class PlasmaMaterial(FusrrMaterial):
    def __init__(
        self,
        object_name_override: str | None = None,
        base_colour: MaterialColour | None = None,
        colour_ramp: MaterialColour | None = None,
    ):
        self.base_colour = base_colour
        self.colour_ramp = colour_ramp
        super().__init__(object_name_override)

    @property
    def material_label(self) -> FusrrMaterialDataLabel:
        return FusrrMaterialDataLabel.PLASMA

    def _configure(self, mat: bpy.types.Material) -> None:
        mat.use_nodes = True

        if self.base_colour:
            bsdf = mat.node_tree.nodes.get("Core Plasma Color")
            bsdf.inputs["Base Color"].default_value = self.base_colour.tup

        # testing how to change color ramp inputs
        if self.colour_ramp:
            ramp_colour = mat.node_tree.nodes.get("Color Ramp Y Axis")
            ramp_colour.color_ramp.elements[1].color = self.colour_ramp.tup


class MetallicMaterial(FusrrMaterial):
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
    def material_label(self) -> FusrrMaterialDataLabel:
        return FusrrMaterialDataLabel.METALLIC

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


class GlassMaterial(FusrrMaterial):
    def __init__(self, object_name_override: str | None = None):
        super().__init__(object_name_override)

    @property
    def material_label(self) -> FusrrMaterialDataLabel:
        return FusrrMaterialDataLabel.GLASS
