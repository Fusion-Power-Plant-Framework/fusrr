from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from fusrr.modelling.blender.tools.object_tools import set_object_material

if TYPE_CHECKING:
    import bpy

    from fusrr.modelling.blender.data_libs.materials_lib import (
        BlenderMaterialDataLabel,
    )


class BlenderMaterial(ABC):
    def __init__(self, object_name_override: str | None = None):
        """A material that is defined by a Blender material.
        This is used to apply materials that are defined in Blender files.

        Args:
            object_name_override:
                Overrides the object name when applying the material, allowing
                the same material to be applied to multiple objects.

                Defaults to None
                (each material applied will be new and unique to the object).
        """
        self._object_name_override = object_name_override

    @property
    @abstractmethod
    def material_label(self) -> BlenderMaterialDataLabel:
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
