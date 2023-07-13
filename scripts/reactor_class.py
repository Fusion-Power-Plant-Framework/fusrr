"""Reactor Class WIP - developing basic structure, plasma class should run fine. Making more general functions and organising componenets """
import abc
from inspect import getmembers

import bmesh
import bpy
from blender_tools import Utilities as bt


# Reactor will render whole scene
class Reactor:
    def __init__(self, **components):
        # Preset options, have default settings for reactor components here
        for name, comp in components.items():
            setattr(self, name, comp)

    def render(self, view):
        # making scene for rendering
        to_render = dict(
            mem for mem in getmembers(self, lambda m: isinstance(m, BlenderComponent))
        )

        blender_scene = bpy.context.scene
        for mem in to_render.values():
            mem.setup_scene(view)

        blender_scene.render()

    def default_scene(self):
        """Deletes any preset features"""
        bt.delete_cube()
        bpy.context.view_layer.objects.active = None  # no layers selected
        bpy.ops.object.select_all(action="DESELECT")  # no objects selected

    def get_reactor_centre(self):
        """Can be useful for camera tracking"""
        pass

    def save_image(file_name: str):
        """Saves render as PNG"""
        bpy.context.scene.render.filepath = str(file_name)
        bpy.ops.render.render(write_still=True, use_viewport=True)
        # save .gltf as well in future


class BlenderComponent(abc.ABC):  # renders individual components
    @abc.abstractmethod
    def render(self, view):
        # render individual component

        object_list = ["line_object", "line_object.001"]
        bt.join_obj(object_list)
        bt.make_face_from_vertices("line_object")

        return None

    @abc.abstractmethod
    def setup_scene(self, view, x, y, z):
        """sets up scene for a component"""

    def _delete_cube(self):
        # setup scene to render
        bt.delete_cube()

        return None

    def render_component_mesh(self):
        """sets up scene in which to build mesh + builds new mesh"""
        scene = bpy.context.scene
        bpy.context.view_layer.objects.active = None

        mesh = bpy.data.meshes.new("line_mesh")
        line_obj = bpy.data.objects.new("line_object", mesh)
        scene.collection.objects.link(line_obj)
        scene.view_layers.update()

        bm = bmesh.new()

        return scene, mesh, bm


class Plasma(BlenderComponent):  # specific parts of the plasma to plot (and render?)
    def __init__(self, x_coords, y_coords, z_coords):
        # self.shape = self._shapecreator(xcoord, zcoord)
        self.x_coords = x_coords
        self.y_coords = y_coords
        self.z_coords = z_coords

    # def render(self, view):
    #     self.setup_scene(view)
    #     # render

    def setup_scene(self):  # some of this can be moved into View/ scene as more general
        """Setup as given in 2D_plasma.py, ideally this will find its way to a more general class"""
        bpy.ops.object.empty_add(location=(self.x_coords, self.y_coords, self.z_coords))
        camera = bpy.data.objects["Camera"]
        camera.location = (self.x_coords, self.y_coords, self.z_coords + 40)
        constraint = bpy.data.objects["Camera"].constraints.new(type="TRACK_TO")
        constraint.target = bpy.data.objects["Empty"]

        object_list = [
            "line_object",
            "line_object.001",
        ]  # this bit is less general, likely need to remain in plasma class
        bt.join_obj(object_list)
        bt.make_face_from_vertices("line_object")
        bt.delete_cube()
        # self._delete_cube()
        # return super().setup_scene(view, x, y, z)

    @staticmethod
    def plot(plasma_shape):
        """Plots the plasma boundary arcs.

        Arguments:
            axis --> axis object to plot to
            mfile_data --> MFILE data object
            scan --> scan number to use
        """
        import math

        import numpy as np

        r0 = plasma_shape.rmajor
        a = plasma_shape.rminor
        delta = 1.5 * plasma_shape.delta_95
        kappa = (1.1 * plasma_shape.kappa95) + 0.04
        i_single_null = plasma_shape.i_single_null

        x1 = (2.0 * r0 * (1.0 + delta) - a * (delta**2 + kappa**2 - 1.0)) / (
            2.0 * (1.0 + delta)
        )
        x2 = (2.0 * r0 * (delta - 1.0) - a * (delta**2 + kappa**2 - 1.0)) / (
            2.0 * (delta - 1.0)
        )
        r1 = 0.5 * math.sqrt(
            (a**2 * ((delta + 1.0) ** 2 + kappa**2) ** 2) / ((delta + 1.0) ** 2)
        )
        r2 = 0.5 * math.sqrt(
            (a**2 * ((delta - 1.0) ** 2 + kappa**2) ** 2) / ((delta - 1.0) ** 2)
        )
        theta1 = np.arcsin((kappa * a) / r1)
        theta2 = np.arcsin((kappa * a) / r2)
        inang = 1.0 / r1
        outang = 1.5 / r2
        if i_single_null == 0:
            angs1 = np.linspace(
                -(inang + theta1) + np.pi, (inang + theta1) + np.pi, 256, endpoint=True
            )
            angs2 = np.linspace(
                -(outang + theta2), (outang + theta2), 256, endpoint=True
            )
        elif i_single_null < 0:
            angs1 = np.linspace(
                -(inang + theta1) + np.pi, theta1 + np.pi, 256, endpoint=True
            )
            angs2 = np.linspace(-theta2, (outang + theta2), 256, endpoint=True)
        else:
            angs1 = np.linspace(
                -theta1 + np.pi, (inang + theta1) + np.pi, 256, endpoint=True
            )
            angs2 = np.linspace(-(outang + theta2), theta2, 256, endpoint=True)

        xs1 = -(r1 * np.cos(angs1) - x1)
        ys1 = r1 * np.sin(angs1)
        xs2 = -(r2 * np.cos(angs2) - x2)
        ys2 = r2 * np.sin(angs2)

        return xs1, xs2, ys1, ys2

    def render(self):
        """Renders the vertices of the plasma array for plasma mesh

        Parameters
        ----------
        x_coords : numpy array
        y_coords : numpy array

        """
        scene, mesh, bm = self.render_component_mesh()

        for x, y in zip(self.x_coords, self.y_coords):
            bm.verts.new((x, y, 0))

        bm.to_mesh(mesh)
        bm.free()

        scene.view_layers.update()

        # print(dir(self.self))
        return None

    @staticmethod
    def plasma_centre(
        x1, x2, y1, y2
    ):  # general, should be able to apply to most components
        """calculates centre of plasma for tracking"""
        half_arr = int(len(x1) / 2)
        half_x = x1[half_arr] - x2[half_arr]
        half_y = y1[half_arr] - y2[half_arr]

        return half_x, half_y


class tfCoil(BlenderComponent):
    import numpy as np

    rtangle = np.pi / 2

    def __innit__(self, ect):
        self.ect = ect

    def tf_coil_outline(self, coords):
        """Renders the spline of the tf coil

        Parameters
        ----------
        x_coords : numpy array
        y_coords : numpy array

        """
        curve = bpy.data.curves.new(name="Curve_test", type="CURVE")
        curve.fill_mode = "NONE"

        ob = bpy.data.objects.new(name="TestObject", object_data=curve)
        scene = bpy.context.scene
        scene.collection.objects.link(ob)
        bpy.context.view_layer.objects.active = None

        spline = curve.splines.new(type="POLY")
        spline.points.add(len(coords) - 1)
        for i, point in enumerate(spline.points):
            point.co[0:2] = coords[i]

        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.view_layer.objects.active = ob
        ob.select_set(True)

        return None

    def ellips_fill(self, a1=0, a2=0, b1=0, b2=0, x0=0, y0=0, ang1=0, ang2=rtangle):
        """Fills the space between two concentric ellipse sectors.

        Arguments

        axis: plot object
        a1, a2, b1, b2 horizontal and vertical radii to be filled
        x0, y0 coordinates of centre of the ellipses
        ang1, ang2 are the polar angles of the start and end

        """
        import numpy as np

        angs = np.linspace(ang1, ang2, endpoint=True)
        r1 = ((np.cos(angs) / a1) ** 2 + (np.sin(angs) / b1) ** 2) ** (-0.5)
        xs1 = r1 * np.cos(angs) + x0
        ys1 = r1 * np.sin(angs) + y0
        angs = np.linspace(ang2, ang1, endpoint=True)
        r2 = ((np.cos(angs) / a2) ** 2 + (np.sin(angs) / b2) ** 2) ** (-0.5)
        xs2 = r2 * np.cos(angs) + x0
        ys2 = r2 * np.sin(angs) + y0
        verts = list(zip(xs1, ys1))
        verts.extend(list(zip(xs2, ys2)))
        endpoint = verts[-1:]
        verts.extend(endpoint)

        return verts


# Default view + different options
class View(abc.ABC):
    @abc.abstractmethod
    def view(self, view, x, y, z):
        """Sets default view"""
        bt.empty_obj(x, y, z)
        bt.move_camera(x, y, z + 40)
        bt.camera_fix(camera="Camera", target="Empty")


class View1(View):
    def add_light(self, x, y, z):
        """adds sunlight object to default view"""
        bpy.ops.object.light_add(type="SUN", location=(x, y, z))
