from contextlib import contextmanager
from tkinter.tix import Tree

import bpy
import bmesh


@contextmanager
def create_mesh(name: str):
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


# def render_component_mesh(name):
#     """Set up + builds new mesh for component

#     Args
#     ----
#         name (str): name of mesh

#     Returns
#     -------
#         blender information for new mesh
#     """
#     scene = bpy.context.scene
#     bpy.context.view_layer.objects.active = None

#     mesh = bpy.data.meshes.new(name)
#     line_obj = bpy.data.objects.new(name, mesh)
#     scene.collection.objects.link(line_obj)
#     scene.view_layers.update()

#     bm = bmesh.new()

#     return scene, mesh, bm
