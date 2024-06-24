from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from fusrr.base.models import Vec3

if TYPE_CHECKING:
    import bpy


@dataclass
class ObjTransformProperties:
    """Common properties for object transforms."""

    center_point: Vec3 | Literal["centroid"] = Vec3.ZERO
    position: Vec3 | None = None
    rotation: Vec3 | None = None
    scale: Vec3 = Vec3.ONE

    def apply_to(self, obj: bpy.types.Object) -> None:
        """Applies the transform properties to the object."""
        if self.position is not None:
            obj.location = self.position.tup
        if self.rotation is not None:
            obj.rotation_euler = self.rotation.tup
        if self.scale != Vec3.ONE:
            obj.scale = self.scale.tup
