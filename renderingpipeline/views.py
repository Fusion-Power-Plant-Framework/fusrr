"""Views class - WIP - will produce tf + plasma
"""
import abc

import bpy

from renderingpipeline.blender_tools import (
    add_light,
    camera_fix,
    half_reactor,
    spin_extrusion,
)


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

        self.view_component = (
            "plasma",
            "pf_coil0",
            "pf_coil1",
            "pf_coil2",
            "pf_coil3",
            "pf_coil4",
            "pf_coil5",
            "central_coil",
        )
        # print(dir(self))
        # hide all components that are not plasma
        ...
        self._view(5, 1, 0)

    def _view(self):  # Works, want to make dist input -possibly using rmajor
        """
        Default view
        """
        dist = 90
        camera_fix("Camera", "plasma", dist)
        add_light(0, 0, dist + 30)

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

    def make_3d(
        self,
    ):  # work for named comps. Need to be continuous (i.e plasma) or it is wierd
        """Spins 2D render around an axis to make 3D - whole reactor"""
        for components in self.view_component:
            component = str(components)
            print("component =", component)
            spin_extrusion(component)
        self._view(2, 0, 40)

    def half_reactor(self, face_mesh):  # naming of face_meshes needs improving
        """Use spin_excursion to make a half reactor view -needs changes"""
        half_reactor(face_mesh)
        self._view(2, 0, 40)

    def tf_thick(self):
        """Add some depth - begining of making 3D TFcoils"""
        tf_list = ("Tf.1", "Tf.2", "Tf.3", "Tf.4", "Tf.5")  # naming will change
        for sect in tf_list:
            obj = bpy.context.scene.objects.get(str(sect))
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.select_all(action="SELECT")
            bpy.ops.mesh.spin(
                angle=0.1, steps=100, axis=(0.0, 1.0, 0.0)
            )  # Polodial rotation
            bpy.ops.object.mode_set(mode="OBJECT")
            bpy.ops.object.select_all(action="DESELECT")

    @staticmethod
    def export(filepath: str):  # will not work in function, need to override context
        """Save as blender file

        Args
        ----
            filepath (str): destination for file
        """
        # out = bpy.ops.wm.save_as_mainfile(filepath)
        bpy.ops.export_scene.gltf(filepath)
