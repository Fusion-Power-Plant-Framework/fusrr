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
from renderingpipeline.reactor import Reactor

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

    components = (
        "blanket",
        "cryostat",
        "divertor",
        "pfcoil",
        "plasma",
        "radiationshield",
        "tfcoil",
        "vacuumvessel",
    )

    def __init__(self, reactor: Reactor):
        self.reactor = reactor
        self._view()

    def _view(self):  # Works, want to make dist input -possibly using rmajor
        """Setup view"""
        dist = self.reactor.plasma.shape.objects[:][0].dimensions.y
        camera_fix("Camera", self.reactor.plasma.shape, dist * 8)
        self.add_light(dist)
        # Hide everything from render
        for o in bpy.context.view_layer.objects:
            o.hide_render = True

        # there is probably a better way of reshowing things?
        for view_comp in self.components:
            try:
                comp = getattr(self.reactor, view_comp).shape
            except AttributeError:
                # Component doesnt exist on reactor
                continue
            comp.hide_render = False
            for ob in comp.objects[:]:
                ob.hide_render = False

        bpy.data.objects["Sun"].hide_render = False

    def highlight_plasma(
        self, colour: str
    ):  # Not working yet, issues w/ selection and meshes
        """Selects and changes colour of plasma

        Args
        ----
            colour (str): hex number for colour
        """
        bpy.ops.object.select_all(action="DESELECT")
        comp = self.reactor.plasma.shape.objects[:][0]
        comp.select_set(True)
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
        objs = self.reactor.plasma.shape.objects[:]
        bb_max = np.array(objs[0].bound_box)
        for ob_ind in range(len(objs) - 1):
            bb_max = np.maximum(bb_max, np.array(objs[ob_ind + 1].bound_box))

        centre = np.mean(bb_max, axis=0)
        shift = np.ptp(np.stack([centre, np.array([x, y, z])]), axis=0)

        for ob in objs:
            ob.location = Vector(shift) + ob.location

    def add_light(self, dist: float):
        """Adds sunlight object to default view"""
        add_light(0, 0, dist * 10)

    def make_3d(
        self,
    ):  # work for named comps. Need to be continuous (i.e plasma) or it is wierd
        """Spins 2D render around an axis to make 3D - whole reactor"""
        for components in self.components:
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

    def tf_thick(self):
        """Add some depth - begining of making 3D TFcoils"""
        for obj in self.reactor.tfcoils.shape.objects[:]:
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
        plasma = self.reactor.plasma.shape.objects[:][0]
        dist = plasma.dimensions.y
        bpy.ops.object.select_all(action="DESELECT")
        y = 16
        for obj in key_list:
            y += -4
            add_cube(-dist * 2, y, 0)
            change_colour(colour=colour_dict[obj])
            add_text(-dist * 1.8, y, 0, rad=2, text=str(obj))
            change_colour(colour=colour_dict[obj])
        bpy.ops.object.select_all(action="DESELECT")  # may not be needed but safer
