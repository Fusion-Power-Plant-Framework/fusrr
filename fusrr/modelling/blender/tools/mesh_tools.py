from collections.abc import Iterable
from contextlib import contextmanager

import bpy
import numpy as np
import bmesh

from fusrr.core.vectors import Vec3


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


def mesh_add_edges_from_points(
    m: bmesh.types.BMesh,
    points: Iterable[Vec3],
    *,
    close: bool = False,
    to_face: bool = False,
):
    """Add edges to the mesh from the given points.

    If close is True, the last point will be connected to the first point.

    Args:
        m: The bmesh mesh to add the edges to.
        points: An iterable of Vec3 points.
        close: Whether to connect the last point to the first point.
        to_face: Whether to create a face from the points.
    """
    verts = [m.verts.new(p.tup) for p in points]
    m.verts.ensure_lookup_table()
    for i in range(len(verts)):
        if i == 0:
            continue
        m.edges.new((verts[i - 1], verts[i]))
    if close:
        m.edges.new((verts[-1], verts[0]))
    if to_face:
        m.faces.new(verts)


def mesh_to_face(m: bmesh.types.BMesh):
    """Create a face from the edges of the mesh.

    Args:
        m: The bmesh mesh to create the face from.
    """
    m.faces.new(m.verts)


def mesh_revolve(
    m: bmesh.types.BMesh,
    center: Vec3,
    axis: Vec3,
    rot_angle_degs: float,
    resolution: int = 50,
):
    """Revolve the edges of the mesh around the axis.

    The edges are revolved around the axis by the given angle.

    Args:
        m: The bmesh mesh to revolve.
        center: The center of the revolve.
        axis: The axis to revolve around.
        rot_angle_degs: The angle to revolve by in degrees.
        resolution: The number of steps to revolve.
    """
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
