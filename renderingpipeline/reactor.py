"""
Reactor Class WIP - developing basic structure, plasma class and tf class working.
Need to impliment proper structure to use Reactor class and tidy rendering functions.
"""
from inspect import getmembers

import bpy
import blender_tools as bt
from components import *


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
