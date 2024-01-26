from contextlib import contextmanager
from collections.abc import Iterable

import bpy
import numpy as np
import bmesh

from fusrr.base.models import Vec3


@contextmanager
def new_mesh(name: str):
    """Create a new mesh and object to go with it.

    Use as a context manager.
    """
    mesh = bpy.data.meshes.new(name)  # add the new mesh
    obj = bpy.data.objects.new(mesh.name, mesh)

    bpy.context.collection.objects.link(obj)

    bm = bmesh.new()

    try:
        yield bm
    finally:
        # set the object's mesh to the bmesh
        bm.to_mesh(mesh)
        bm.free()


def add_edges_to_mesh(m: bmesh.types.BMesh, points: Iterable[Vec3]):
    verts = [m.verts.new(p.tup) for p in points]
    m.verts.ensure_lookup_table()
    for i in range(len(verts)):
        if i == 0:
            continue
        m.edges.new((verts[i - 1], verts[i]))


def revolve_mesh(
    m: bmesh.types.BMesh,
    geometry: list,
    center: Vec3,
    axis: Vec3,
    rot_angle_degs: float,
    resolution: int = 100,
):
    ang = np.deg2rad(rot_angle_degs)
    bmesh.ops.spin(
        m,
        geom=geometry,
        cent=center.tup,
        axis=axis.tup,
        angle=ang,
        steps=resolution,
        use_merge=rot_angle_degs == 360,  # noqa: PLR2004
        # use_normal_flip=False,
        # use_duplicate=False,
    )


# bmesh.ops.bisect_plane(bm, geom=[], dist=0, plane_co=mathutils.Vector(), plane_no=mathutils.Vector(), use_snap_center=False, clear_outer=False, clear_inner=False)

# def spin_extrusion():
#     """Spin extrudes around y axis in blender 2Pi radians"""
#     bpy.ops.object.mode_set(mode="EDIT")
#     bpy.ops.mesh.select_all(action="SELECT")
#     bpy.ops.mesh.spin(
#         angle=2 * np.pi, steps=100, axis=(0.0, 1.0, 0.0)
#     )  # Polodial rotation
#     bpy.ops.object.mode_set(mode="OBJECT")
#     bpy.ops.object.shade_smooth()
#     bpy.ops.object.select_all(action="DESELECT")
