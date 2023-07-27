"""Views class - WIP - will produce tf + plasma
"""
import abc

import bpy
import numpy as np
from mathutils import Vector

from renderingpipeline.blender_tools import (
    add_cube,
    add_light,
    add_text,
    camera_fix,
    half_reactor,
    spin_extrusion,
)

component_list = [  # better naming practice incoming
    "plasma",
    "pf_coil0",
    "pf_coil1",
    "pf_coil2",
    "pf_coil3",
    "pf_coil4",
    "pf_coil5",
    "central_coil",
]

tf_list = ("Tf.1", "Tf.2", "Tf.3", "Tf.4", "Tf.5")

# naming may change to become less hard-coded, currently working for key
key_list = ["Plasma", "PF Coil", "Central Coil", "TF Coil", "Cryostat"]

colour_dict = dict(
    {
        "Plasma": "#7d2f8e",
        "PF Coil": "#0072c2",
        "Central Coil": "#0072c2",
        "TF Coil": "#003688",
        "Cryostat": "#2e7ebc",
    }
)


def hex_color_to_rgba(hex_color):  # checks needed as from git
    """Converts hex to blender's sRGB"""
    hex_color = hex_color.strip("#")
    srgb_red = int(hex_color[:2], 16) / 255
    srgb_green = int(hex_color[2:4], 16) / 255
    srgb_blue = int(hex_color[4:6], 16) / 255
    return tuple([srgb_red, srgb_green, srgb_blue, 1.0])


def change_colour(colour):
    """Creates material to add colour to active objects(s)"""
    active_objects = bpy.context.selected_objects
    colour = hex_color_to_rgba(colour)
    for obj in active_objects:
        mat = bpy.data.materials.new(name=f"{obj.name} Material")
        obj.data.materials.append(mat)
        mat.diffuse_color = colour
        bpy.context.scene.view_layers.update()


class ViewBase(abc.ABC):
    """AbstractBaseClass for Views"""

    @abc.abstractmethod
    def _view(self):
        """Set up default view"""


class View(ViewBase):
    """Set up for initial view + additional options"""

    def __init__(self, reactor):
        self.reactor = reactor

        print(self.reactor)
        # reactor.render()

        self.view_component = ("plasma",)  # , "tfcoils")
        print(self.view_component)
        # print(dir(self))
        # hide all components that are not plasma
        ...
        self._view()

    def _view(self):  # Works, want to make dist input -possibly using rmajor
        """
        Default view
        """
        dist = self.reactor.plasma.shape.objects['LCFS_1'].dimensions.y
        camera_fix("Camera", "plasma", dist * 8)
        add_light(0, 0, dist * 10)

        a = self.reactor.plasma.shape.values()
        for o in bpy.context.view_layer.objects:
            if o not in a:
                o.hide_render = True

        # there is probably a better way of reshowing things?
        self.reactor.plasma.shape.hide_render = False
        for view_comp in self.view_component:
            comp = getattr(self.reactor, view_comp).shape
            for ob in comp.objects.values():
                ob.hide_render = False

    def highlight_plasma(
        self, colour
    ):  # Not working yet, issues w/ selection and meshes
        """Selects and changes colour of plasma

        Args
        ----
            colour (str): hex number for colour
        """
        bpy.ops.object.select_all(action="DESELECT")
        bpy.data.objects[component_list[0]].select_set(True)
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
        objs = list(self.reactor.plasma.shape.objects.values())
        bb_max = np.array(objs[0].bound_box)
        objs_bbs = [objs[0].bound_box]
        for ob_ind in range(len(objs) - 1):
            objs_bbs.append(np.array(objs[ob_ind + 1].bound_box))
            bb_max = np.maximum(bb_max, objs_bbs[-1])
        centre = np.mean(bb_max, axis=0)

        shift = np.ptp(np.stack([centre, np.array([x, y, z])]), axis=0)
        for ob in objs:
            ob.location = Vector(shift) + ob.location

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
            spin_extrusion(component)
        self._view()

    def half_reactor(self, face_mesh):
        """Use spin_extrusion to make 'half-doughnut' reactor
            naming of face_mesh should change to match make_3d funct
        Args:
            face_mesh (_type_): _description_
        """
        half_reactor(face_mesh)
        self._view(2, 0, 40)

    def tf_thick(self):
        """Add some depth - begining of making 3D TFcoils"""
        for sect in tf_list:
            obj = bpy.context.scene.objects.get(str(sect))
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.select_all(action="SELECT")
            bpy.ops.mesh.spin(
                angle=0.1, steps=100, axis=(0.0, 1.0, 0.0)
            )  # Currently angle/ thickness hard-coded want to become input from MFILE
            bpy.ops.object.mode_set(mode="OBJECT")
            bpy.ops.object.select_all(action="DESELECT")

    def key(self):
        """Adds 'cube key' - setup for 2D render"""
        bpy.ops.object.select_all(action="DESELECT")
        plasma = bpy.data.objects["plasma"]
        dist = plasma.dimensions.y
        bpy.ops.object.select_all(action="DESELECT")
        y = 16
        for object in key_list:
            y += -4
            add_cube(-dist * 2, y, 0)
            change_colour(colour=colour_dict[object])
            add_text(-dist * 1.8, y, 0, rad=2, text=str(object))
            change_colour(colour=colour_dict[object])
        bpy.ops.object.select_all(action="DESELECT")  # may not be needed but safer

    @staticmethod
    def export(filepath: str):  # will not work in function, need to override context
        """Save as blender file

        Args
        ----
            filepath (str): destination for file
        """
        # out = bpy.ops.wm.save_as_mainfile(filepath)
        bpy.ops.export_scene.gltf(filepath)
