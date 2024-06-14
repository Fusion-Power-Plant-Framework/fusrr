from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from fusrr.base.models import Vec3
from fusrr.blender.mesh_tools import mesh_revolve

if TYPE_CHECKING:
    import bpy
    import bmesh


@dataclass
class CommonObjTransformProperties:
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
        # if self.center_point == "centroid":
        #     bpy.ops.object.origin_set(type="ORIGIN_CENTER_OF_MASS", center="BOUNDS")
        # else:
        #     obj.location = self.center_point.tup


@dataclass
class CommonMeshModelProperties:
    """Common properties for object mesh models."""

    revolve_x_deg: float | None = None
    revolve_y_deg: float | None = None
    revolve_z_deg: float | None = None
    revolve_center: Vec3 = Vec3.ZERO

    def apply_to(self, m: bmesh.types.BMesh) -> None:
        """Applies the mesh model properties to the mesh."""
        if self.revolve_x_deg is not None:
            mesh_revolve(m, self.revolve_center, Vec3.X, self.revolve_x_deg)
        if self.revolve_y_deg is not None:
            mesh_revolve(m, self.revolve_center, Vec3.Y, self.revolve_y_deg)
        if self.revolve_z_deg is not None:
            mesh_revolve(m, self.revolve_center, Vec3.Z, self.revolve_z_deg)
