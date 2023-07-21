"""Views placeholder script
"""
import abc

import bpy

from renderingpipeline.blender_tools import camera_fix


class ViewDefault(abc.ABC):
    """Holds methods for default veiw"""

    @abc.abstractclassmethod
    def view(self):
        """Set up default view"""
        pass


class View(ViewDefault):
    """additional options for views"""

    def view(self):
        """Default view"""
        camera_fix("Camera", "Empty")

    def add_light(self, x, y, z):
        """Adds sunlight object to default view"""
        bpy.ops.object.light_add(type="SUN", location=(x, y, z))
