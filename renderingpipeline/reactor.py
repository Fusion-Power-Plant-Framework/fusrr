"""
Reactor class - builds individual components and puts them in the same scene
"""
from inspect import getmembers

from renderingpipeline.adaptor import OutputParams
from renderingpipeline.blender_tools import save_image
from renderingpipeline.components import BlenderComponent


class Reactor:
    """Reactor class - methods for rendering whole reactor scenes (WIP)"""

    def __init__(self, **components):
        # Preset options, have default settings for reactor components here
        for name, comp in components.items():
            setattr(self, name, comp)

    @classmethod
    def reactor_from_file(cls, input_file):
        """A method to make an instance of a reactor from file

        Parameters
        ----------
        input_file : str
            Input file name of .DAT file
        """
        input_params = OutputParams.from_file(input_file)
        cdict = {}
        for component in BlenderComponent.__subclasses__():
            cdict[component.__name__.lower()] = component(input_params)

        return cls(**cdict)

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
        save_image(file_name)
        # save .gltf and .blend
