"""
A file that stores the blender components of the reactor
"""
import abc
import math
from dataclasses import asdict

import bpy
import bmesh
import numpy as np
from matplotlib import patches

from renderingpipeline.blender_tools import (
    change_to_mesh,
    component_outline,
    delete_cube,
    faces_pf_coils,
    join_obj,
    make_face_from_vertices,
    rect_blend,
    rect_blend_sep,
    render_component_mesh,
)

tf_list = ["Tf.1", "Tf.2", "Tf.3", "Tf.4", "Tf.5"]
plasma_list = ["plasma", "plasma.001"]
cryo_list = [
    "Upper_Outer_wall",
    "Lower_Outer_wall",
    "Upper_wall",
    "Lower_wall",
]
PLASMA = "plasma"

PURPLE = "#7d2f8e"  # plasma purple
BLUE = "#003688"  # tf blue
CRYO_BLUE = "#2e7ebc"
PF_BLUE = "#0072c2"


def ellips_fill(a1=0, a2=0, b1=0, b2=0, x0=0, y0=0, ang1=0, ang2=np.pi / 2):
    """Fills the space between two concentric ellipse sectors.

    Arguments
    ---------
    axis: plot object
    a1, a2, b1, b2 horizontal and vertical radii to be filled
    x0, y0 coordinates of centre of the ellipses
    ang1, ang2 are the polar angles of the start and end

    """
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


class BlenderComponent(abc.ABC):
    """Stores default functions for blender setup and renderings"""

    def scene(self):
        """Sets up scene"""
        scene = bpy.context.scene
        mesh = bpy.data.meshes.new("line_mesh")
        line_obj = bpy.data.objects.new("line_object", mesh)
        scene.collection.objects.link(line_obj)
        scene.view_layers.update()

        bm = bmesh.new()

        return scene, mesh, bm

    def tracking_centre(
        self, component_shape
    ):  # not great but gives a view that should include all components
        """Uses rmajor to make set of coordinates - Can be useful for camera tracking"""
        x, y = 0, component_shape.rmajor
        z = 6 * component_shape.rmajor
        return x, y, z

    def frame(self):
        """Sets up camera for rendering"""
        delete_cube()

    def hex_color_to_rgba(self, hex_color):  # checks needed as from git
        """Converts hex to blender's sRGB"""
        hex_color = hex_color[1:]
        red = int(hex_color[:2], 16)
        srgb_red = red / 255

        green = int(hex_color[2:4], 16)
        srgb_green = green / 255

        blue = int(hex_color[4:6], 16)
        srgb_blue = blue / 255
        colour = tuple([srgb_red, srgb_green, srgb_blue, 1.0])

        return colour

    def default_colour(self, colour):
        """Creates material to add colour to active objects(s)"""
        bpy.ops.object.select_all(action="SELECT")
        active_objects = bpy.context.selected_objects
        # h = input('Enter hex: ').lstrip('#')
        # RGB = (tuple(int(h[i:i+2], 16) for i in (0, 2, 4)))
        if colour is None:
            colour = self.hex_color_to_rgba(PURPLE)
        else:
            colour = self.hex_color_to_rgba(colour)
        for object in active_objects:
            try:
                mat = bpy.data.materials.new(name="MatName")
                object.data.materials.append(mat)
                mat.diffuse_color = colour
                bpy.context.scene.view_layers.update()
            except AttributeError:
                continue


class Plasma(BlenderComponent):
    """Contains methods for plotting and rendering different parts of the plasma"""

    def __init__(self, plasma_shape):
        self.plasma_shape = plasma_shape

    @staticmethod
    def create_shape(plasma_shape):
        """Generates coordinates for the plasma boundary arcs

        Arguments:
        ---------
            plasma_shape: input values for componets
        """
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

    def render(self, x_coords, y_coords):
        """Renders the vertices of the plasma array for plasma mesh

        Parameters
        ----------
        x_coords : numpy array
        y_coords : numpy array

        """
        scene, mesh, bm = render_component_mesh(PLASMA)

        for x, y in zip(x_coords, y_coords):
            bm.verts.new((x, y, 0))

        bm.to_mesh(mesh)
        bm.free()

        scene.view_layers.update()
        return None

    @staticmethod
    def plasma_centre(x1, x2, y1, y2):
        """Calculates centre of plasma for tracking"""
        half_arr = int(len(x1) / 2)
        half_x = x1[half_arr] - x2[half_arr]
        half_y = y1[half_arr] - y2[half_arr]

        return half_x, half_y

    def setup_scene(self):
        """Sets up cameras and objects for rendering"""
        self.frame()
        join_obj(plasma_list)
        make_face_from_vertices(PLASMA)

    def build(self):
        """Combines above functions to plot, track and render plasma"""
        xs1, xs2, ys1, ys2 = self.create_shape(self.plasma_shape)
        self.render(xs1, ys1)
        self.render(xs2, ys2)
        self.setup_scene()
        self.default_colour(colour=None)


class TFCoil(BlenderComponent):
    """Contains method for plotting and rendering tf coils"""

    def __init__(self, tf_coil_shape):
        self.tf_coil_shape = tf_coil_shape

    def create_shape(self):  # was plot_tf_coils
        """Function to plot TF coils
        Arguments:
        --------
            axis --> axis object to plot to
            mfile_data --> MFILE.DAT object
            scan --> scan number to use
        """
        # Arc points
        # MDK Only 4 points now required for elliptical arcs

        tfc_inleg = self.tf_coil_shape.tfc_inleg
        rtangle = np.pi / 2
        x1 = self.tf_coil_shape.x1
        y1 = self.tf_coil_shape.y1
        x2 = self.tf_coil_shape.x2
        y2 = self.tf_coil_shape.y2
        x3 = self.tf_coil_shape.x3
        y3 = self.tf_coil_shape.y3
        x4 = self.tf_coil_shape.x4
        y4 = self.tf_coil_shape.y4
        x5 = self.tf_coil_shape.x5
        y5 = self.tf_coil_shape.y5
        if y3 != 0:
            print("TF coil geometry: The value of yarc(3) is not zero, but should be.")

        x0 = x2
        y0 = y1
        a1 = x2 - x1
        b1 = y2 - y1
        a2 = a1 + tfc_inleg
        b2 = b1 + tfc_inleg
        verts = ellips_fill(
            a1=a1,
            a2=a2,
            b1=b1,
            b2=b2,
            x0=x0,
            y0=y0,
            ang1=rtangle,
            ang2=2 * rtangle,
        )
        component_outline(verts, tf_list[0])
        # Outboard upper arc
        x0 = x2
        y0 = 0
        a1 = x3 - x2
        b1 = y2
        a2 = a1 + tfc_inleg
        b2 = b1 + tfc_inleg
        verts = ellips_fill(
            a1=a1, a2=a2, b1=b1, b2=b2, x0=x0, y0=y0, ang1=0, ang2=rtangle
        )
        component_outline(verts, tf_list[1])
        # Inboard lower arc
        x0 = x4
        y0 = y5
        a1 = x4 - x5
        b1 = y5 - y4
        a2 = a1 + tfc_inleg
        b2 = b1 + tfc_inleg
        verts = ellips_fill(
            a1=a1, a2=a2, b1=b1, b2=b2, x0=x0, y0=y0, ang1=-rtangle, ang2=-2 * rtangle
        )
        component_outline(verts, tf_list[2])
        # Outboard lower arc
        x0 = x4
        y0 = 0
        a1 = x3 - x2
        b1 = -y4
        a2 = a1 + tfc_inleg
        b2 = b1 + tfc_inleg
        verts = ellips_fill(
            a1=a1, a2=a2, b1=b1, b2=b2, x0=x0, y0=y0, ang1=0, ang2=-rtangle
        )
        component_outline(verts, tf_list[3])
        # Vertical leg
        # Bottom left corner
        rect = patches.Rectangle(
            [x5 - tfc_inleg, y5], tfc_inleg, (y1 - y5), lw=0, facecolor="cyan"
        )
        centre_coords = rect_blend(rect)
        component_outline(centre_coords, tf_list[4])

    def setup_scene(self):
        """Sets up scene and objects for rendering"""
        x, y, z = self.tracking_centre(self.tf_coil_shape)
        self.frame()

        change_to_mesh(object_names=tf_list)
        for i in tf_list:
            make_face_from_vertices(str(i))

    def build(self):
        """Plots tracks and renders tf coils"""
        self.create_shape()
        self.setup_scene()
        self.default_colour(colour=BLUE)


class Cryostat(BlenderComponent):
    """Cryostat Component

    Parameters
    ----------
    Params :
        An instance of OutputParams dataclass
    """

    def __init__(self, params):
        self.params = params

    def _cryo_outline(self):
        """Makes the outline for each of the walls of the cryostat"""
        rdewex = self.params.rdewex
        ddwex = self.params.ddwex
        zdewex = self.params.zdewex

        # Taken from plot_proc.py plotting 2D cryostat function
        rect = patches.Rectangle([rdewex, 0], ddwex, zdewex + ddwex, lw=0)
        coords = rect_blend(rectangle=rect)
        component_outline(coords, object_name=cryo_list[0])

        rect = patches.Rectangle([rdewex, 0], ddwex, -(zdewex + ddwex), lw=0)
        coords = rect_blend(rectangle=rect)
        component_outline(coords, object_name=cryo_list[1])

        rect = patches.Rectangle([0, zdewex], rdewex, ddwex, lw=0)
        coords = rect_blend(rectangle=rect)
        component_outline(coords, object_name=cryo_list[2])

        rect = patches.Rectangle([0, -zdewex], rdewex, -ddwex, lw=0)
        coords = rect_blend(rectangle=rect)
        component_outline(coords, object_name=cryo_list[3])

        change_to_mesh(object_names=cryo_list)

        # Makes each wall into a filled shape
        for i in cryo_list:
            make_face_from_vertices(str(i))

    def build(self):
        """Build method to render the component"""
        self._cryo_outline()
        self.scene()
        self.default_colour(colour=CRYO_BLUE)


class PfCoils(BlenderComponent):
    """Contains methods for plotting and rendering Pf_coils

    Parameters
    ----------
    BlenderComponent : instance
        Inherits other general methods for components
    """

    def __init__(self, pf_coil_shape) -> None:
        self.pf_coil_shape = pf_coil_shape

    # TODO: pf_coil_render is identical to plasma render, move it to component class!
    @staticmethod
    def pf_coil_render(x_coords, y_coords, coil_name):
        """Renders the vertices of the plasma array

        Parameters
        ----------
        x_coords : numpy array
        y_coords : numpy array

        """
        bpy.ops.object.select_all(action="DESELECT")
        scene = bpy.context.scene
        bpy.context.view_layer.objects.active = None

        # Creates new line_mesh object
        mesh = bpy.data.meshes.new("line_mesh")
        line_obj = bpy.data.objects.new(str(coil_name), mesh)
        scene.collection.objects.link(line_obj)
        scene.view_layers.update()

        # Using bmesh allows the editing of existing meshes to be updated
        bm = bmesh.new()

        for x, y in zip(x_coords, y_coords):
            bm.verts.new((x, y, 0))

        bm.to_mesh(mesh)
        bm.free()

        scene.view_layers.update()

        return mesh

    def plot_pf_coils(self):
        """Plots pf coils from PROCESS' plot_proc file"""
        pf_coil_shape_dict = {k: str(v) for k, v in asdict(self.pf_coil_shape).items()}

        coils_r = []
        coils_z = []
        coils_dr = []
        coils_dz = []
        coil_text = []

        number_of_coils = 0
        for key in pf_coil_shape_dict.keys():
            if "rpf" in key:
                number_of_coils += 1

        bore = float(pf_coil_shape_dict["bore"])
        cs_rad_th = float(pf_coil_shape_dict["cs_rad_th"])
        ohdz = float(pf_coil_shape_dict["ohdz"])

        # Check for Central Solenoid
        if "iohcl" in pf_coil_shape_dict:
            iohcl = pf_coil_shape_dict["iohcl"]
        else:
            iohcl = 1

        # If Central Solenoid present, ignore last entry in for loop
        # The last entry will be the OH coil in this case
        if iohcl == 0:
            noc = number_of_coils + 1
        else:
            noc = number_of_coils

        for coil in range(1, noc + 1):
            coils_r.append(pf_coil_shape_dict["rpf{:01}".format(coil)])
            coils_z.append(pf_coil_shape_dict["zpf{:01}".format(coil)])
            coils_dr.append(pf_coil_shape_dict["pfdr{:01}".format(coil)])
            coils_dz.append(pf_coil_shape_dict["pfdz{:01}".format(coil)])
            coil_text.append(str(coil + 1))

        for i in range(len(coils_r)):
            r_1 = float(coils_r[i]) - 0.5 * float(coils_dr[i])
            z_1 = float(coils_z[i]) - 0.5 * float(coils_dz[i])
            r_2 = float(coils_r[i]) - 0.5 * float(coils_dr[i])
            z_2 = float(coils_z[i]) + 0.5 * float(coils_dz[i])
            r_3 = float(coils_r[i]) + 0.5 * float(coils_dr[i])
            z_3 = float(coils_z[i]) + 0.5 * float(coils_dz[i])
            r_4 = float(coils_r[i]) + 0.5 * float(coils_dr[i])
            z_4 = float(coils_z[i]) - 0.5 * float(coils_dz[i])
            r_5 = float(coils_r[i]) - 0.5 * float(coils_dr[i])
            z_5 = float(coils_z[i]) - 0.5 * float(coils_dz[i])

            r_points = [r_1, r_2, r_3, r_4, r_5]
            z_points = [z_1, z_2, z_3, z_4, z_5]

            pf_coil_name = f"pf_coil{i}"
            self.pf_coil_render(r_points, z_points, pf_coil_name)
            faces_pf_coils(pf_coil_name)

        central_coil = patches.Rectangle([bore, (-ohdz / 2)], cs_rad_th, ohdz)
        central_coil_name = "central_coil"
        x_coords, y_coords = rect_blend_sep(central_coil)

        self.pf_coil_render(
            x_coords=x_coords, y_coords=y_coords, coil_name=central_coil_name
        )
        faces_pf_coils(central_coil_name)

    def setup_scene(self):
        """Sets up scene and objects for rendering"""
        x, y, z = self.tracking_centre(self.pf_coil_shape)
        self.frame()  # Tracking works but is wonky

    def build(self):
        """Plots tracks and renders tf coils"""
        self.plot_pf_coils()
        self.setup_scene()
        self.default_colour(colour=PF_BLUE)


# class Blanket(BlenderComponent):
