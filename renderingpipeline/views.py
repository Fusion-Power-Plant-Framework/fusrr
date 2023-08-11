"""Views class - WIP - will produce 1 tf, plasma, pf coils, cryostat
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
    focal_length,
    hex_colour_to_rgba,
    orthographic_view,
    spin_extrusion,
)
from renderingpipeline.reactor import Reactor

# naming for key/ legend
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


def change_colour(colour):
    """Creates material to add colour to active objects(s)"""
    active_objects = bpy.context.selected_objects
    colour = hex_colour_to_rgba(colour)
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

    def _view(self):
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

        bpy.data.objects["Sun"].hide_render = True
        bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[
            0
        ].default_value = (
            1,
            1,
            1,
            1,
        )  # white viewport background
        bpy.context.scene.view_settings.gamma = (
            0  # prevents colours from becoming washed out by light
        )

    def wide_shot(self):
        """Useful positioning, moves camera + sun further away + zooms in
        -done through trial + error
        -Best in 3D renders and wide 2D shots
        """
        camera_fix("Camera", self.reactor.plasma.shape, 78)
        camera_fix("Sun", self.reactor.plasma.shape, 110)
        focal_length("Camera", 38)

    def add_light(self, dist: float):
        """Adds sunlight object to view

        Args
        ----
            dist (float): distance
        """
        add_light(0, 0, dist * 10)

    @staticmethod
    def export(filepath: str):  # Blender scene context must be correct
        """Save as blender file

        Args
        ----
            filepath (str): destination for file
        """
        bpy.ops.export_scene.gltf(filepath)

    @staticmethod
    def save_image(file_name: str):
        """Saves render as PNG"""
        bpy.context.scene.render.filepath = str(file_name)
        bpy.ops.render.render(write_still=True, use_viewport=True)


class PlasmaOptions(View):
    """Functions for altering look of plasma component"""

    def move_plasma(self, x, y, z):
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
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.delete(type="FACE")
        bpy.ops.object.mode_set(mode="OBJECT")
        change_colour(colour)


class View2D(View):
    """Cross section view of reactor"""

    def half_reactor(self):  # cuts out section of reactor
        """2D segment view
        - recommend wide_shot for framing
        """
        bpy.ops.object.select_all(action="DESELECT")
        objects = bpy.context.scene.objects
        for obj in objects:
            obj.select_set(obj.type == "MESH")
        bpy.ops.object.editmode_toggle()  # object NOT objects
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.bisect(
            plane_co=(0, 0, 1), plane_no=(0, 0, -1), clear_inner=True, clear_outer=False
        )
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.bisect(
            plane_co=(0, 0, 1), plane_no=(1, 0, 0), clear_inner=True, clear_outer=False
        )
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.bisect(
            plane_co=(0, 0, -1),
            plane_no=(0, 0, -0.99),
            clear_inner=False,
            clear_outer=True,
        )
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")
        orthographic_view()

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


class View3D(View):
    """Different 3d views"""

    def make_3d(self):
        """Spins 2D render around an axis to make 3D - whole reactor"""
        dont_spin = [
            "tfcoil",
            "cryostat",
            "blanket",
        ]  # cryo and blanket cover other components tf is not poloidal
        for seen in filter(lambda n: n not in dont_spin, self.components):
            try:
                comp = getattr(self.reactor, seen).shape
            except AttributeError:
                # Component doesnt exist on reactor
                continue
            for names in comp.objects[:]:
                names.select_set(True)
        spin_extrusion()

    def cutaway(self):
        """Removes part of the reactor to get 'cut-in' view
        - recommend wide_shot for framing
        """
        bpy.ops.object.select_all(action="DESELECT")
        objects = bpy.context.scene.objects
        for obj in objects:
            obj.select_set(obj.type == "MESH")
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.bisect(
            plane_co=(-16, 0.66, 19),
            plane_no=(-0.288, -0.186, -0.939),
            clear_inner=True,
            clear_outer=False,
            xstart=307,
            xend=557,
            ystart=295,
            yend=370,
            flip=False,
        )
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")

    def key_3d(self):  # bit messy, trial and error but looks nice in the end
        """Adds 'cube key' and sets framing
        - recommend wide_shot for framing
        """
        plasma = self.reactor.plasma.shape.objects[:][0]
        dist = plasma.dimensions.y
        bpy.ops.object.select_all(action="DESELECT")
        y = 16
        for object in key_list:
            y += -4
            add_cube(dist * 2, y, 0)
            change_colour(colour=colour_dict[object])
            add_text(dist * 2.2, y, 0, rad=1.8, text=str(object))
            change_colour(colour=colour_dict[object])
        bpy.ops.object.select_all(action="DESELECT")
