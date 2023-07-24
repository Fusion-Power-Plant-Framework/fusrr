"""
Reactor class - builds individual components and puts them in the same scene
"""
from inspect import getmembers

import renderingpipeline.blender_tools as bt
from renderingpipeline.components import BlenderComponent


class Reactor:
    """Reactor class - methods for rendering whole reactor scenes (WIP)"""

    def __init__(self, **components):
        # Preset options, have default settings for reactor components here
        for name, comp in components.items():
            setattr(self, name, comp)

    def render(self):
        """Render reactor scene for each component"""
        to_render = dict(
            mem for mem in getmembers(self, lambda m: isinstance(m, BlenderComponent))
        )

        for mem in to_render.values():
            mem.build()  # component class has build func

    @staticmethod
    def save_image(file_name: str):
        """Saves render as PNG"""
        bt.save_image(file_name)
        # could save .gltf and .blend if wanted
