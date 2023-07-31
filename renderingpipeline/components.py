"""
A file that stores the blender components of the reactor
"""
import abc
import math
from dataclasses import asdict
from typing import Iterable, List, Optional, Tuple

import bpy
import bmesh
import bpy_types
import numpy as np
from matplotlib import patches

from renderingpipeline.adaptor import OutputParams
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
BLANKET = "#4a98c9"
DIVERTOR = "#d0e1f2"
VACUUMVESSEL = "#b7d4ea"
RADSHIELD = "#94c4df"

BLUEMIRA_COMP_NAMES = {
    "Plasma": (("LCFS", "*"),),
    "TFCoil": (
        ("Casing_1_", "*"),
        ("Insulation_1", "*"),
        ("Winding_Pack_1_", "*"),
        ("TF", "*"),
        ("ITER_like_gravity_support", "*"),
    ),
    "Cryostat": (("Cryostat", "*"),),  # VVCryo, cryostatTS and the VV Cryo plugs
    "PFCoil": (  # PF and CS coils
        ("Ground_Insulation", "*"),
        ("PFCoilSupport", "*"),
        ("Winding_Pack_", "[0-9]"),
        ("Winding_Pack_", "[0-9][!_]*"),
        ("Casing_", "[0-9]"),
        ("Casing_", "[0-9][!_]*"),
    ),
    "Blanket": (("IBS", "*"), ("OBS", "*")),
    "Divertor": (("segment", "*"),),
    "RadiationShield": (  # radiation shield and port plug
        ("Body_1_", "*"),
        ("RadiationPortPlug", "*"),
    ),
    "VacuumVessel": (  # Vacuum Vessel and VVTS
        ("Body_", "[0-9]"),
        ("Body_", "[0-9][!_]*"),
        ("VVTS_1", "*"),
    ),
}


def ellips_fill(
    a1: float = 0,
    a2: float = 0,
    b1: float = 0,
    b2: float = 0,
    x0: float = 0,
    y0: float = 0,
    ang1: float = 0,
    ang2: float = np.pi / 2,
) -> List[float]:
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
    """Base class to setup components"""

    def __init__(self, shapes: Iterable[bpy_types.Object], colour: str = PURPLE):
        delete_cube()
        self._shape_ref = self._create_collection(type(self).__name__, shapes)
        self.default_colour(colour)

    @property
    def shape(self) -> bpy_types.Collection:
        """Get the component shape references."""
        return self._shape_ref

    @abc.abstractmethod
    def create_shape(self):
        """Create the PROCESS shape."""

    def _get_bluemira_comps(self) -> List[bpy_types.Object]:
        shapes = []
        for prefix, regex in BLUEMIRA_COMP_NAMES[type(self).__name__]:
            shapes.extend(self._select_objects(prefix, regex))
        return shapes

    def _create_collection(
        self, name: str, objects: Iterable[bpy_types.Object]
    ) -> bpy_types.Collection:
        group = bpy.data.collections.new(name)
        for ob in objects:
            group.objects.link(ob)
        bpy.context.scene.collection.children.link(group)
        return group

    def _select_objects(self, prefix: str, regex: str = "*") -> Tuple[bpy_types.Object]:
        bpy.ops.object.select_all(action="DESELECT")
        bpy.ops.object.select_pattern(pattern=f"{prefix}{regex}")
        return tuple(bpy.context.selected_objects)

    def hex_color_to_rgba(self, hex_color: str) -> Tuple[float, ...]:
        """Convert hex to blender's sRGB."""
        hex_color = hex_color.strip("#")
        srgb_red = int(hex_color[:2], 16) / 255
        srgb_green = int(hex_color[2:4], 16) / 255
        srgb_blue = int(hex_color[4:6], 16) / 255
        return tuple([srgb_red, srgb_green, srgb_blue, 1.0])

    def default_colour(self, colour: Optional[str] = None):
        """Create material and adds colour to shape."""
        colour_rgb = self.hex_color_to_rgba(colour or PURPLE)
        for ob in self.shape.objects.values():
            mat = bpy.data.materials.new(name=type(self).__name__)
            ob.data.materials.append(mat)
            mat.diffuse_color = colour_rgb
            bpy.context.scene.view_layers.update()

    def tracking_centre(
        self, component_shape
    ):  # not great but gives a view that should include all components
        """Uses rmajor to make set of coordinates - Can be useful for camera tracking"""
        x, y = 0, component_shape.rmajor
        z = 6 * component_shape.rmajor
        return x, y, z


class Plasma(BlenderComponent):
    """Plasma component."""

    def __init__(self, params: Optional[OutputParams] = None, colour: str = PURPLE):
        self.params = params

        shapes = []
        if params is None:
            shapes.extend(self._get_bluemira_comps())
        else:
            self.create_shape()
            shapes.extend(self._select_objects(PLASMA))

        super().__init__(shapes, colour)

    def create_shape(self):
        """Generate coordinates for the plasma boundary arcs."""
        r0 = self.params.rmajor
        a = self.params.rminor
        delta = 1.5 * self.params.delta_95
        kappa = (1.1 * self.params.kappa95) + 0.04
        i_single_null = self.params.i_single_null

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

        for _x, _y in zip((xs1, xs2), (ys1, ys2)):
            self.create_mesh(_x, _y, name=PLASMA)
        join_obj(plasma_list)
        make_face_from_vertices(PLASMA)

    def create_mesh(
        self, x_coords: Iterable[float], y_coords: Iterable[float], name: str = "plasma"
    ):
        """Create the vertices of the plasma array for plasma mesh."""
        scene, mesh, bm = render_component_mesh(name)

        for x, y in zip(x_coords, y_coords):
            bm.verts.new((x, y, 0))

        bm.to_mesh(mesh)
        bm.free()

        scene.view_layers.update()

    @staticmethod
    def plasma_centre(x1, x2, y1, y2):
        """Calculates centre of plasma for tracking"""
        half_arr = int(len(x1) / 2)
        half_x = x1[half_arr] - x2[half_arr]
        half_y = y1[half_arr] - y2[half_arr]

        return half_x, half_y


class TFCoil(BlenderComponent):
    """TF Coil component"""

    def __init__(self, params: Optional[OutputParams] = None, colour: str = BLUE):
        self.params = params

        shapes = []
        if params is None:
            shapes.extend(self._get_bluemira_comps())
        else:
            self.create_shape()
            shapes.extend(self._select_objects("Tf"))

        super().__init__(shapes, colour)

    def create_shape(self):  # was plot_tf_coils
        """Create TF coils."""
        # Arc points
        # MDK Only 4 points now required for elliptical arcs

        tfc_inleg = self.params.tfc_inleg
        rtangle = np.pi / 2
        x1 = self.params.x1
        y1 = self.params.y1
        x2 = self.params.x2
        y2 = self.params.y2
        x3 = self.params.x3
        y3 = self.params.y3
        x4 = self.params.x4
        y4 = self.params.y4
        x5 = self.params.x5
        y5 = self.params.y5
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

        change_to_mesh(object_names=tf_list)
        for i in tf_list:
            make_face_from_vertices(i)


class Cryostat(BlenderComponent):
    """Cryostat Component."""

    def __init__(self, params: Optional[OutputParams] = None, colour: str = CRYO_BLUE):
        self.params = params

        shapes = []
        if params is None:
            shapes.extend(self._get_bluemira_comps())
        else:
            self.create_shape()
            for name in cryo_list:
                shapes.extend(self._select_objects(name))

        super().__init__(shapes, colour)

    def create_shape(self):
        """Make the outline for each of the walls of the cryostat."""
        rdewex = self.params.rdewex
        ddwex = self.params.ddwex
        zdewex = self.params.zdewex

        # Taken from plot_proc.py plotting 2D cryostat function
        rect = patches.Rectangle([rdewex, 0], ddwex, zdewex + ddwex, lw=0)
        coords = rect_blend(rectangle=rect)
        component_outline(coords, cryo_list[0])

        rect = patches.Rectangle([rdewex, 0], ddwex, -(zdewex + ddwex), lw=0)
        coords = rect_blend(rectangle=rect)
        component_outline(coords, cryo_list[1])

        rect = patches.Rectangle([0, zdewex], rdewex, ddwex, lw=0)
        coords = rect_blend(rectangle=rect)
        component_outline(coords, cryo_list[2])

        rect = patches.Rectangle([0, -zdewex], rdewex, -ddwex, lw=0)
        coords = rect_blend(rectangle=rect)
        component_outline(coords, cryo_list[3])

        change_to_mesh(object_names=cryo_list)

        # Makes each wall into a filled shape
        for i in cryo_list:
            make_face_from_vertices(str(i))



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
