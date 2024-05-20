from __future__ import annotations

import abc
from typing import TYPE_CHECKING

from fusrr.blender.object_tools import set_object_material
from fusrr.data_libs.materials import FusrrMaterialDataLabel

if TYPE_CHECKING:
    import bpy


class FusrrMaterial(abc.ABC):
    """Base class for materials used in Fusrr.

    This class should be subclassed to create new materials.
    """

    @abc.abstractmethod  # prevents the Ruff warning for no abstract methods
    def __init__(
        self,
        data_label: FusrrMaterialDataLabel,
        name_suffix_override: str | None = None,
    ):
        """Initializes the material with the given data label.

        Args:
            data_label:
                The data label to use for the material.
            name_suffix_override:
                The suffix to append to the material name.
                Defaults to None.
        """
        self._material_data_label = data_label
        self._name_suffix_override = name_suffix_override

    def _configure(self, mat: bpy.types.Material) -> None:
        """Applies the material configuration to the given material."""

    def apply(self, obj: bpy.types.Object):
        """Applies the material to the object.

        Args:
            obj: The object to apply the material to.
        """
        mat = set_object_material(
            obj,
            self._material_data_label.value,
            name_suffix_override=self._name_suffix_override,
        )
        self._configure(mat)


class PlasmaMaterial(FusrrMaterial):
    def __init__(self, name_suffix_override: str | None = None):
        super().__init__(
            FusrrMaterialDataLabel.PLASMA_PINK, name_suffix_override
        )

    def _configure(self, mat: bpy.types.Material):
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value = (0.8, 0.2, 0.8, 1)
        bsdf.inputs["Metallic"].default_value = 0.0
        bsdf.inputs["Roughness"].default_value = 0.5


class MetallicMaterial(FusrrMaterial):
    def __init__(self, name_suffix_override: str | None = None):
        super().__init__(
            FusrrMaterialDataLabel.METALLIC_GOLD_SHINY, name_suffix_override
        )
