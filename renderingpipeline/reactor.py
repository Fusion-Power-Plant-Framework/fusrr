"""
Reactor class - builds individual components and puts them in the same scene
"""
from inspect import getmembers

from renderingpipeline.adaptor import OutputParams
from renderingpipeline.components import BlenderComponent


class Reactor:
    """Reactor class - methods for rendering whole reactor scenes (WIP)"""

    def __init__(self, **components):
        # Preset options, have default settings for reactor components here
        for name, comp in components.items():
            setattr(self, name, comp)

    @classmethod
    def reactor_from_file(cls, input_file_path):
        """A method to make an instance of a reactor from file

        Parameters
        ----------
        input_file : str
            Input file name of .DAT file
        """
        reactor_params = OutputParams.from_file(input_file_path)
        cdict = {}
        for component in BlenderComponent.__subclasses__():
            try:
                cdict[component.__name__.lower()] = component(reactor_params)
            except NotImplementedError:
                continue

        return cls(**cdict)

    def render(self):
        """Render reactor scene for each component"""
        to_render = dict(
            mem for mem in getmembers(self, lambda m: isinstance(m, BlenderComponent))
        )

        for mem in to_render.values():
            mem.build()  # component class has build func
