from collections.abc import Iterable
from contextlib import contextmanager

import bpy
import numpy as np
import bmesh

from fusrr.base.models import Vec3


@contextmanager
def new_mesh_for(obj: bpy.types.Object):
    """Create a new mesh for the obj.

    Use as a context manager.
    """
    mesh = obj.data

    bm = bmesh.new()

    try:
        yield bm
    finally:
        bm.normal_update()
        bm.to_mesh(mesh)
        bm.free()


@contextmanager
def update_mesh_for(obj: bpy.types.Object):
    """Update a mesh from the obj.

    Use as a context manager.
    """
    mesh = obj.data

    bm = bmesh.new()
    bm.from_mesh(mesh)

    try:
        yield bm
    finally:
        bm.normal_update()
        bm.to_mesh(mesh)
        bm.free()


def add_edges_to_mesh_from_points(
    m: bmesh.types.BMesh, points: Iterable[Vec3], *, close: bool = False
):
    verts = [m.verts.new(p.tup) for p in points]
    m.verts.ensure_lookup_table()
    for i in range(len(verts)):
        if i == 0:
            continue
        m.edges.new((verts[i - 1], verts[i]))
    if close:
        m.edges.new((verts[-1], verts[0]))


def revolve_mesh_edges_silhouette(
    m: bmesh.types.BMesh,
    center: Vec3,
    axis: Vec3,
    rot_angle_degs: float,
    resolution: int = 100,
):
    ang = np.deg2rad(rot_angle_degs)
    bmesh.ops.spin(
        m,
        geom=m.edges,
        cent=center.tup,
        axis=axis.tup,
        angle=ang,
        steps=resolution,
        use_merge=rot_angle_degs == 360,  # noqa: PLR2004
        # use_normal_flip=False,
        # use_duplicate=False,
    )


def add_empty(name: str, location: Vec3):
    """Adds an empty object to the scene."""
    bpy.ops.object.empty_add(location=location.tup)
    obj = bpy.context.object
    obj.name = name


def add_cube(name: str, location: Vec3, scale: Vec3):
    """Adds a cube to the scene."""
    bpy.ops.mesh.primitive_cube_add(location=location.tup, scale=scale.tup)
    obj = bpy.context.object
    obj.name = name
