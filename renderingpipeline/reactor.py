"""
Reactor Class WIP - developing basic structure, plasma class and tf class working.
Need to impliment proper structure to use Reactor class and tidy rendering functions.
"""
import abc
import math
from inspect import getmembers

import bpy
import blender_tools as bt
import bmesh
import components
import numpy as np
from matplotlib import patches


def ellips_fill(a1=0, a2=0, b1=0, b2=0, x0=0, y0=0, ang1=0, ang2=np.pi / 2):
    """Fills the space between two concentric ellipse sectors.

    Arguments
    ---------
    axis: plot object
    a1, a2, b1, b2 horizontal and vertical radii to be filled
    x0, y0 coordinates of centre of the ellipses
    ang1, ang2 are the polar angles of the start and end

    """
    angs = np.linspace(ang1, ang2, endpoint=True)
    r1 = ((np.cos(angs) / a1) ** 2 + (np.sin(angs) / b1) ** 2) ** (-0.5)
    xs1 = r1 * np.cos(angs) + x0
    ys1 = r1 * np.sin(angs) + y0
    angs = np.linspace(ang2, ang1, endpoint=True)
    r2 = ((np.cos(angs) / a2) ** 2 + (np.sin(angs) / b2) ** 2) ** (-0.5)
    xs2 = r2 * np.cos(angs) + x0
    ys2 = r2 * np.sin(angs) + y0
    verts = list(zip(xs1, ys1))
    verts.extend(list(zip(xs2, ys2)))
    endpoint = verts[-1:]
    verts.extend(endpoint)

    return verts


class Reactor:
    """Reactor class - methods for rendering whole reactor scenes (WIP)"""

    def __init__(self, **components):
        # Preset options, have default settings for reactor components here
        for name, comp in components.items():
            setattr(self, name, comp)

    def render(self, view):
        """Render whole reactor scene"""
        to_render = dict(
            mem for mem in getmembers(self, lambda m: isinstance(m, BlenderComponent))
        )

        blender_scene = bpy.context.scene
        for mem in to_render.values():
            mem.setup_scene(view)
        # setup camera after scene
        blender_scene.render()

    @staticmethod
    def save_image(file_name: str):
        """Saves render as PNG"""
        bt.save_image(file_name)
        # possibly save .gltf as well in future
