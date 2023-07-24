"""Views placeholder script
"""
import abc

import bpy

from renderingpipeline.adaptor import OutputParams
from renderingpipeline.blender_tools import camera_fix


class ViewDefault(abc.ABC):
    """Holds methods for default veiw"""

    @abc.abstractclassmethod
    def view(self):
        """Set up default view"""
        pass


class View(ViewDefault):
    """additional options for views"""

    def __init__(self, reactor1):
        reactor1.params: OutputParams

    @staticmethod
    def view():
        """
        Default view - very much hard coded needs to change
        - just getting working example
        """
        bpy.ops.object.empty_add(location=(5, 1, 0))
        camera_fix("Camera", "Empty")
        camera = bpy.data.objects["Camera"]
        camera.location = (5, 1, 55)

    def add_light(self, x, y, z):
        """Adds sunlight object to default view"""
        bpy.ops.object.light_add(type="SUN", location=(x, y, z))
