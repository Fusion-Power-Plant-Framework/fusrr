"""Views class - WIP - will produce tf + plasma
"""
import abc

import bpy

from renderingpipeline.adaptor import OutputParams
from renderingpipeline.blender_tools import camera_fix, half_reactor, spin_extrusion
from renderingpipeline.components import Plasma, TFCoil
from renderingpipeline.reactor import Reactor


def hex_color_to_rgba(hex_color):  # checks needed as from git
    """Converts hex to blender's sRGB"""
    hex_color = hex_color[1:]
    red = int(hex_color[:2], 16)
    srgb_red = red / 255

    green = int(hex_color[2:4], 16)
    srgb_green = green / 255

    blue = int(hex_color[4:6], 16)
    srgb_blue = blue / 255

    tup = tuple([srgb_red, srgb_green, srgb_blue, 1.0])

    return tup


def change_colour(colour):
    """Creates material to add colour to active objects(s)"""
    active_objects = bpy.context.selected_objects
    colour = hex_color_to_rgba(colour)
    print(colour)
    for object in active_objects:
        mat = bpy.data.materials.new(name="MatName")
        object.data.materials.append(mat)
        mat.diffuse_color = colour
        bpy.context.scene.view_layers.update()


class ViewDefault(abc.ABC):
    """Holds methods for default veiw"""

    @abc.abstractclassmethod
    def __init__(self):
        pass

    @abc.abstractclassmethod
    def _view(self):
        """Set up default view"""
        pass


class View(ViewDefault):
    """Set up for initial view + additional options"""

    def __init__(self, reactor):
        self.reactor = reactor

        print(self.reactor)
        reactor.render()

        self.view_component = ("plasma", "tfcoils")
        print(self.view_component)
        # print(dir(self))
        # hide all components that are not plasma
        ...
        self._view(5, 1, 0)

    def _view(self, x, y, z):  # Works, want to do better tracking
        """
        Default view - working example - want to create bbetter method for tracking
        """
        bpy.ops.object.empty_add(location=(x, y, z))
        camera_fix("Camera", "Empty")
        camera = bpy.data.objects["Camera"]
        camera.location = (x, y, z + 55)

    def highlight_plasma(
        self, colour
    ):  # Not working yet, issues w/ selection and meshes
        """Selects and changes colour of plasma

        Args
        ----
            colour (str): hex number for colour
        """
        bpy.ops.object.select_all(action="DESELECT")
        bpy.data.objects["line_object"].select_set(True)
        bpy.ops.object.mode_set(mode="EDIT")  # blender likes 'EDIT' VScode does not
        bpy.ops.mesh.delete(type="FACE")
        bpy.ops.object.mode_set(mode="OBJECT")
        change_colour(colour)

    def move_plasma(self, x, y, z):  # this works, not sure how useful it is
        """Selects and moves plasma

        Args
        ----
            x : coords
            y : coords
            z : coords
        """
        bpy.ops.object.select_all(action="DESELECT")
        plasma = bpy.data.objects["line_object"]
        plasma.location = (x, y, z)

    def add_light(self, x, y, z):
        """Adds sunlight object to default view"""
        self.view()
        bpy.ops.object.light_add(type="SUN", location=(x, y, z))

    def make_3d(self):  # this works, but currenly only selecting plasma
        """Spins 2D render around an axis to make 3D - whole reactor"""
        spin_extrusion("line_object")
        self._view(2, 0, 40)

    def half_reactor(self):
        """Use spin_excursion to make a half reactor view -needs changes"""
        half_reactor("line_object")
        self._view(2, 0, 40)

    @staticmethod
    def export(filepath: str):  # this is not yet working
        """Save as blender file

        Args
        ----
            filepath (str): destination for file
        """
        override = bpy.context.copy()
        override["selected_objects"] = list(bpy.context.scene.objects)
        with bpy.context.temp_override(**override):
            bpy.ops.wm.save_as_mainfile(filepath)


input_file = OutputParams.from_file("examples/baseline_2018_MFILE.DAT")

plasma = Plasma(input_file)
tf = TFCoil(input_file)
reactor1 = Reactor(plasma=plasma, tfcoils=tf)

view = View(reactor1)
# view.highlight_plasma( '#d85319')
view.move_plasma(2, 0, 10)
# view.make_3d()
view.half_reactor()
View.export("plasma_tf_view")
# bpy.ops.wm.save_as_mainfile(filepath="plasma")
