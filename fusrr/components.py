"""
A file that stores the blender components of the reactor
"""
import abc
from dataclasses import asdict
from typing import Iterable, List, Optional, Tuple

import bpy
import bpy_types
import numpy as np

from process.geometry.plasma_geometry import plasma_geometry
from process.geometry.cryostat_geometry import cryostat_geometry
from process.geometry.tfcoil_geometry import tfcoil_geometry_d_shape
from process.geometry.pfcoil_geometry import pfcoil_geometry
from process.geometry.vacuum_vessel_geometry import (
    vacuum_vessel_geometry_single_null,
    vacuum_vessel_geometry_double_null,
)
from process.geometry.blanket_geometry import (
    blanket_geometry_single_null,
    blanket_geometry_double_null,
)
from process.geometry.shield_geometry import (
    shield_geometry_single_null,
    shield_geometry_double_null,
)
from process.geometry.firstwall_geometry import (
    first_wall_geometry_single_null,
    first_wall_geometry_double_null,
)
from fusrr.cumulative_build import cumulative_radial_build, cumul_setup


from fusrr.adaptor import OutputParams
from fusrr.blender_tools import (
    add_empty_axes,
    array_object_rotation,
    change_to_mesh,
    component_outline,
    delete_cube,
    faces_pf_coils,
    hex_colour_to_rgba,
    join_obj,
    make_face_from_vertices,
    rect_blend,
    render_component_mesh,
    spin_extrusion,
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
FIRSTWALL = "#2740bB"

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
        """Create the PROCESS shape.

        This is an artistic take on the output PROCESS produces to make a 3D model.
        It is our best guess at what the full component would look like.
        """

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

    def select_spin(self, prefix: str, regex: str = "*"):
        """Selects component and extrudes to make 3d

        Args
        ----
            prefix (str): nabe of component
            regex (str, optional): Defaults to "*".
        """
        bpy.ops.object.select_all(action="DESELECT")
        for comp in self._select_objects(prefix, regex):
            comp.select_set(True)
        spin_extrusion()

    def hex_color_to_rgba(self, hex_color: str) -> Tuple[float, ...]:
        """Convert hex to blender's sRGB."""
        hex_color = hex_color.strip("#")
        srgb_red = int(hex_color[:2], 16) / 255
        srgb_green = int(hex_color[2:4], 16) / 255
        srgb_blue = int(hex_color[4:6], 16) / 255
        return tuple([srgb_red, srgb_green, srgb_blue, 1.0])

    def default_colour(self, colour: Optional[str] = None):
        """Create material and adds colour to shape."""
        colour_rgb = hex_colour_to_rgba(colour or PURPLE)
        for ob in self.shape.objects.values():
            mat = bpy.data.materials.new(name=type(self).__name__)
            ob.data.materials.append(mat)
            mat.diffuse_color = colour_rgb
            bpy.context.scene.view_layers.update()

    def join_objects(self, name: List[str], new_name: str):
        """Joins plotted objects into one component

        Args
        ----
            name (list): names of the objects to be joined
            new_name (str): new name of joined component
        """
        bpy.ops.object.select_all(action="DESELECT")
        for comp in name:
            bpy.data.objects[comp].select_set(True)
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.face_split_by_edges()
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.join()
        for sect in bpy.context.selected_objects:
            sect.name = new_name
        bpy.ops.object.select_all(action="DESELECT")

    def tracking_centre(
        self, component_shape
    ):  # rough estimation of distance based on rmajor
        """Uses rmajor to create rough placement for camera

        Args
        ----
            component_shape : data from named component

        Returns
        -------
            x, y, z : coordinates
        """
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
            self.select_spin(PLASMA)
            shapes.extend(self._select_objects(PLASMA))

        super().__init__(shapes, colour)

    def create_shape(self):
        """Generate coordinates for the plasma boundary arcs.

        This is an artistic take on the output PROCESS produces to make a 3D model.
        It is our best guess at what the full component would look like.
        """
        r0 = self.params.rmajor
        a = self.params.rminor
        delta95 = self.params.delta_95
        kappa95 = self.params.kappa95
        i_single_null = self.params.i_single_null

        pg = plasma_geometry(
            r_0=r0,
            a=a,
            triang_95=delta95,
            kappa_95=kappa95,
            i_single_null=i_single_null,
        )

        for _x, _y in zip((pg.rs[0], pg.rs[1]), (pg.zs[0], pg.zs[1])):
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

    def create_shape(self):
        """Create TF coils.

        This is an artistic take on the output PROCESS produces to make a 3D model.
        It is our best guess at what the full component would look like.
        """
        # Arc points
        # MDK Only 4 points now required for elliptical arcs

        tf_il = self.params.tfc_inleg
        rt = np.pi / 2
        rt2 = 2 * rt
        x1, x2, x3, x4, x5 = (
            getattr(self.params, x) for x in ("x1", "x2", "x3", "x4", "x5")
        )
        y1, y2, y3, y4, y5 = (
            getattr(self.params, y) for y in ("y1", "y2", "y3", "y4", "y5")
        )
        if y3 != 0:
            print("TF coil geometry: The value of yarc(3) is not zero, but should be.")

        rects, verts_list = tfcoil_geometry_d_shape(
            x1=x1,
            x2=x2,
            x3=x3,
            x4=x4,
            x5=x5,
            y1=y1,
            y2=y2,
            y4=y4,
            y5=y5,
            tfcth=tf_il,
            rtangle=rt,
            rtangle2=rt2,
        )
        count = 0
        for vert in verts_list:
            component_outline(vert, tf_list[count])
            count += 1

        for rec in rects:
            centre_coords = rect_blend(
                center_x=rec.center_x,
                center_z=rec.center_z,
                width=rec.width,
                height=rec.height,
            )
        component_outline(centre_coords, tf_list[4])

        for obj in tf_list:
            change_to_mesh(obj=obj)
            make_face_from_vertices(obj)

        self.tf_coil_thickness()
        self.multiple_tf_coils()

    def tf_coil_thickness(self):
        """Add some depth - beginning of making 3D TFcoils"""
        radial_thickness = self.params.tfc_inleg
        self._select_objects("Tf")
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.face_split_by_edges()
        bpy.ops.object.mode_set(mode="OBJECT")
        self._select_objects("Tf")
        bpy.ops.object.join()
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.extrude_repeat(steps=1, offset=(0, 0, radial_thickness))
        bpy.ops.object.mode_set(mode="OBJECT")
        for obj in bpy.context.selected_objects:
            obj.name = "Tf_coils"

    def multiple_tf_coils(self):
        """Adds multiple tf_coils from singular tf coil"""
        add_empty_axes(empty_name="Empty_tf")
        array_object_rotation(
            object_name="Tf_coils", empty_name="Empty_tf", no_tf=int(self.params.n_tf)
        )


class Cryostat(BlenderComponent):
    """Cryostat Component."""

    def __init__(self, params: Optional[OutputParams] = None, colour: str = CRYO_BLUE):
        self.params = params

        shapes = []
        if params is None:
            shapes.extend(self._get_bluemira_comps())
        else:
            self.create_shape()
            self.select_spin("cryostat")
            shapes.extend(self._select_objects("cryostat"))

        super().__init__(shapes, colour)

    def create_shape(self):
        """Make the outline for each of the walls of the cryostat.

        This is an artistic take on the output PROCESS produces to make a 3D model.
        It is our best guess at what the full component would look like.
        """
        rdewex = self.params.rdewex
        ddwex = self.params.ddwex
        zdewex = self.params.zdewex
        rects = cryostat_geometry(rdewex=rdewex, ddwex=ddwex, zdewex=zdewex)
        count = 0
        for rect in rects:
            coords = rect_blend(
                center_x=rect.center_x,
                center_z=rect.center_z,
                width=rect.width,
                height=rect.height,
            )
            component_outline(coords, cryo_list[count])
            count += 1

        for obj in cryo_list:
            change_to_mesh(obj=obj)

        # Makes each wall into a filled shape
        for i in cryo_list:
            make_face_from_vertices(str(i))
        self.join_objects(cryo_list, "cryostat")  # make into one object and rename


class PFCoil(BlenderComponent):
    """PF Coil Component."""

    def __init__(self, params: Optional[OutputParams] = None, colour: str = PF_BLUE):
        self.params = params

        shapes = []
        if params is None:
            shapes.extend(self._get_bluemira_comps())
        else:
            self.create_shape()
            self.select_spin("pf_coil")
            self.select_spin("central_coil")
            for name in ["pf_coil", "central_coil"]:
                shapes.extend(self._select_objects(name))

        super().__init__(shapes, colour)

    @staticmethod
    def create_mesh(
        x_coords: Iterable[float], y_coords: Iterable[float], coil_name: str
    ):
        """Create the vertices of the plasma array."""
        scene, mesh, bm = render_component_mesh(coil_name)

        for x, y in zip(x_coords, y_coords):
            bm.verts.new((x, y, 0))

        bm.to_mesh(mesh)
        bm.free()

        scene.view_layers.update()

        return mesh

    def create_shape(self):
        """Create pf coils from PROCESS' plot_proc file."""
        params_dict = {k: str(v) for k, v in asdict(self.params).items()}

        coils_r = []
        coils_z = []
        coils_dr = []
        coils_dz = []

        bore = float(params_dict["bore"])
        cs_rad_th = float(params_dict["cs_rad_th"])
        ohdz = float(params_dict["ohdz"])

        number_of_coils = 0
        for key in params_dict:
            if "rpf" in key:
                number_of_coils += 1

        # Check for Central Solenoid
        iohcl = params_dict.get("iohcl", 1)

        # If Central Solenoid present, ignore last entry in for loop
        # The last entry will be the OH coil in this case
        noc = number_of_coils + 1 if iohcl == 0 else number_of_coils

        for coil in range(1, noc + 1):
            coils_r.append(params_dict[f"rpf{coil:01}"])
            coils_z.append(params_dict[f"zpf{coil:01}"])
            coils_dr.append(params_dict[f"pfdr{coil:01}"])
            coils_dz.append(params_dict[f"pfdz{coil:01}"])

        r_points, z_points, central_coil = pfcoil_geometry(
            coils_r=coils_r,
            coils_z=coils_z,
            coils_dr=coils_dr,
            coils_dz=coils_dz,
            bore=bore,
            ohcth=cs_rad_th,
            ohdz=ohdz,
        )

        for i in range(len(coils_r)):
            pf_coil_name = f"pf_coil{i}"
            self.create_mesh(r_points[i], z_points[i], pf_coil_name)
            faces_pf_coils(pf_coil_name)

        central_coil_name = "central_coil"

        x_coords, y_coords = zip(
            *rect_blend(
                center_x=central_coil.center_x,
                center_z=central_coil.center_z,
                width=central_coil.width,
                height=central_coil.height,
            )
        )

        self.create_mesh(
            x_coords=x_coords, y_coords=y_coords, coil_name=central_coil_name
        )
        faces_pf_coils(central_coil_name)


class VacuumVessel(BlenderComponent):
    """VacuumVessel Component."""

    def __init__(
        self, params: Optional[OutputParams] = None, colour: str = VACUUMVESSEL
    ):
        self.params = params

        shapes = []
        if params is None:
            shapes.extend(self._get_bluemira_comps())
        else:
            self.create_shape()
            self.select_spin("vacuum vessel")
            shapes.extend(self._select_objects("vacuum vessel"))

        super().__init__(shapes, colour)

    def create_shape(self):
        """Create vacuum vessel shape.

        This is an artistic take on the output PROCESS produces to make a 3D model.
        It is our best guess at what the full component would look like.
        """

        params_dict = {k: str(v) for k, v in asdict(self.params).items()}
        i_single_null = self.params.i_single_null
        triang_95 = self.params.delta_95
        cumulative_upper, cumulative_lower, upper, lower = cumul_setup(
            params_dict=params_dict
        )

        # Outer side (furthest from plasma)
        radx_outer = (
            cumulative_radial_build("d_vv_out", self.params)
            + cumulative_radial_build("gapds", self.params)
        ) / 2.0
        rminx_outer = (
            cumulative_radial_build("d_vv_out", self.params)
            - cumulative_radial_build("gapds", self.params)
        ) / 2.0

        # Inner side (nearest to the plasma)
        radx_inner = (
            cumulative_radial_build("shldoth", self.params)
            + cumulative_radial_build("d_vv_in", self.params)
        ) / 2.0
        rminx_inner = (
            cumulative_radial_build("shldoth", self.params)
            - cumulative_radial_build("d_vv_in", self.params)
        ) / 2.0

        if i_single_null == 1:
            vvg_single_null = vacuum_vessel_geometry_single_null(
                cumulative_upper=cumulative_upper,
                upper=upper,
                triang=triang_95,
                radx_outer=radx_outer,
                rminx_outer=rminx_outer,
                radx_inner=radx_inner,
                rminx_inner=rminx_inner,
                cumulative_lower=cumulative_lower,
                lower=lower,
            )
            rs = vvg_single_null.rs
            zs = vvg_single_null.zs

            component_outline(list(zip(rs, zs)), "vacuum vessel")

        if i_single_null == 0:
            vvg_double_null = vacuum_vessel_geometry_double_null(
                cumulative_lower=cumulative_lower,
                lower=lower,
                radx_inner=radx_inner,
                radx_outer=radx_outer,
                rminx_inner=rminx_inner,
                rminx_outer=rminx_outer,
                triang=triang_95,
            )
            rs = vvg_double_null.rs
            zs = vvg_double_null.zs

            component_outline(list(zip(rs, zs)), "vacuum vessel")

        self.create_mesh(vacuum_vessel_parts=["vacuum vessel"])

    def create_mesh(self, vacuum_vessel_parts: List[str]):
        """Creates the face of the vacuum vessel"""
        for ob in vacuum_vessel_parts:
            change_to_mesh(ob)
        make_face_from_vertices("vacuum vessel")


class Blanket(BlenderComponent):
    """Blanket Component."""

    def __init__(self, params: Optional[OutputParams] = None, colour: str = BLANKET):
        self.params = params

        shapes = []
        if params is None:
            shapes.extend(self._get_bluemira_comps())
        else:
            self.create_shape()
            self.select_spin("blanket")
            shapes.extend(self._select_objects("blanket"))

        super().__init__(shapes, colour)

    def create_shape(self):
        """Create blanket shape.

        This is an artistic take on the output PROCESS produces to make a 3D model.
        It is our best guess at what the full component would look like.
        """
        params_dict = {k: str(v) for k, v in asdict(self.params).items()}
        i_single_null = self.params.i_single_null
        triang_95 = self.params.delta_95
        blnktth = self.params.blnktth
        blnkith = self.params.blnkith
        blnkoth = self.params.blnkoth
        c_shldith = cumulative_radial_build("shldith", self.params)
        c_blnkoth = cumulative_radial_build("blnkoth", self.params)

        cumulative_upper, cumulative_lower, _, _ = cumul_setup(params_dict=params_dict)

        if i_single_null == 1:
            # Upper blanket: outer surface
            radx_outer = (
                cumulative_radial_build("blnkoth", self.params)
                + cumulative_radial_build("vvblgapi", self.params)
            ) / 2.0
            rminx_outer = (
                cumulative_radial_build("blnkoth", self.params)
                - cumulative_radial_build("vvblgapi", self.params)
            ) / 2.0

            # Upper blanket: inner surface
            radx_inner = (
                cumulative_radial_build("fwoth", self.params)
                + cumulative_radial_build("blnkith", self.params)
            ) / 2.0
            rminx_inner = (
                cumulative_radial_build("fwoth", self.params)
                - cumulative_radial_build("blnkith", self.params)
            ) / 2.0
            bg_single_null = blanket_geometry_single_null(
                radx_outer=radx_outer,
                rminx_outer=rminx_outer,
                radx_inner=radx_inner,
                rminx_inner=rminx_inner,
                cumulative_upper=cumulative_upper,
                triang=triang_95,
                cumulative_lower=cumulative_lower,
                blnktth=blnktth,
                c_shldith=c_shldith,
                c_blnkoth=c_blnkoth,
                blnkith=blnkith,
                blnkoth=blnkoth,
            )
            rs = bg_single_null.rs
            zs = bg_single_null.zs

            component_outline(list(zip(rs, zs)), "blanket")

            blanket_parts = ["blanket"]

        if i_single_null == 0:
            bg_double_null = blanket_geometry_double_null(
                cumulative_lower=cumulative_lower,
                triang=triang_95,
                blnktth=blnktth,
                c_shldith=c_shldith,
                c_blnkoth=c_blnkoth,
                blnkith=blnkith,
                blnkoth=blnkoth,
            )
            r1 = bg_double_null.rs[0]
            r2 = bg_double_null.rs[1]
            z1 = bg_double_null.zs[0]
            z2 = bg_double_null.zs[1]

            component_outline(list(zip(r1, z1)), "outboard_blanket")
            component_outline(list(zip(r2, z2)), "inboard_blanket")

            blanket_parts = ["outboard_blanket", "inboard_blanket"]

        self.create_mesh(blanket_parts=blanket_parts)

    def create_mesh(self, blanket_parts: List[str]):
        """Creates the face of the blanket"""
        for ob in blanket_parts:
            change_to_mesh(ob)
            make_face_from_vertices(ob)
        join_obj(blanket_parts)
        for obj in bpy.context.selected_objects:
            obj.name = "blanket"


class RadiationShield(BlenderComponent):
    """Radiation shield Component."""

    def __init__(self, params: Optional[OutputParams] = None, colour: str = RADSHIELD):
        self.params = params

        shapes = []
        if params is None:
            shapes.extend(self._get_bluemira_comps())
        else:
            self.create_shape()
            self.select_spin("radiation shield")
            shapes.extend(self._select_objects("radiation shield"))

        super().__init__(shapes, colour)

    def create_shape(self):
        """Create radiation shield shape.

        This is an artistic take on the output PROCESS produces to make a 3D model.
        It is our best guess at what the full component would look like.
        """
        params_dict = {k: str(v) for k, v in asdict(self.params).items()}
        i_single_null = self.params.i_single_null
        triang_95 = self.params.delta_95
        cumulative_upper, cumulative_lower, _, _ = cumul_setup(params_dict=params_dict)

        # Side furthest from plasma
        radx_far = (
            cumulative_radial_build("shldoth", self.params)
            + cumulative_radial_build("d_vv_in", self.params)
        ) / 2.0
        rminx_far = (
            cumulative_radial_build("shldoth", self.params)
            - cumulative_radial_build("d_vv_in", self.params)
        ) / 2.0

        # Side nearest to the plasma
        radx_near = (
            cumulative_radial_build("vvblgapo", self.params)
            + cumulative_radial_build("shldith", self.params)
        ) / 2.0
        rminx_near = (
            cumulative_radial_build("vvblgapo", self.params)
            - cumulative_radial_build("shldith", self.params)
        ) / 2.0

        if i_single_null == 1:
            sg_single_null = shield_geometry_single_null(
                cumulative_upper=cumulative_upper,
                radx_far=radx_far,
                rminx_far=rminx_far,
                radx_near=radx_near,
                rminx_near=rminx_near,
                triang=triang_95,
                cumulative_lower=cumulative_lower,
            )

            rs = sg_single_null.rs
            zs = sg_single_null.zs

            component_outline(list(zip(rs, zs)), "radiation shield")

        if i_single_null == 0:
            sg_double_null = shield_geometry_double_null(
                cumulative_lower=cumulative_lower,
                radx_far=radx_far,
                radx_near=radx_near,
                rminx_far=rminx_far,
                rminx_near=rminx_near,
                triang=triang_95,
            )

            rs = sg_double_null.rs
            zs = sg_double_null.zs

            component_outline(list(zip(rs, zs)), "radiation shield")

        self.create_mesh(radiation_shield_parts=["radiation shield"])

    def create_mesh(self, radiation_shield_parts: List[str]):
        """Creates the face of the radiation shield"""
        for ob in radiation_shield_parts:
            change_to_mesh(ob)
        make_face_from_vertices("radiation shield")


class FirstWall(BlenderComponent):
    """Blanket Component."""

    def __init__(self, params: Optional[OutputParams] = None, colour: str = FIRSTWALL):
        self.params = params

        shapes = []
        if params is None:
            shapes.extend(self._get_bluemira_comps())
        else:
            self.create_shape()
            self.select_spin("first wall")
            shapes.extend(self._select_objects("first wall"))

        super().__init__(shapes, colour)

    def create_shape(self):
        """Create first wall shape.

        This is an artistic take on the output PROCESS produces to make a 3D model.
        It is our best guess at what the full component would look like.
        """
        params_dict = {k: str(v) for k, v in asdict(self.params).items()}
        i_single_null = self.params.i_single_null
        triang_95 = self.params.delta_95
        blnktth = self.params.blnktth
        tfwvt = self.params.fwtth
        fwith = self.params.fwith
        fwoth = self.params.fwoth
        c_blnkith = cumulative_radial_build("blnkith", self.params)
        c_fwoth = cumulative_radial_build("fwoth", self.params)
        cumulative_upper, cumulative_lower, _, _ = cumul_setup(params_dict=params_dict)

        if i_single_null == 1:
            # Upper first wall: outer surface
            radx_outer = (
                cumulative_radial_build("fwoth", self.params)
                + cumulative_radial_build("blnkith", self.params)
            ) / 2.0
            rminx_outer = (
                cumulative_radial_build("fwoth", self.params)
                - cumulative_radial_build("blnkith", self.params)
            ) / 2.0

            # Upper first wall: inner surface
            radx_inner = (
                cumulative_radial_build("scraplo", self.params)
                + cumulative_radial_build("fwith", self.params)
            ) / 2.0
            rminx_inner = (
                cumulative_radial_build("scraplo", self.params)
                - cumulative_radial_build("fwith", self.params)
            ) / 2.0

            fwg_single_null = first_wall_geometry_single_null(
                radx_outer=radx_outer,
                rminx_outer=rminx_outer,
                radx_inner=radx_inner,
                rminx_inner=rminx_inner,
                cumulative_upper=cumulative_upper,
                triang=triang_95,
                cumulative_lower=cumulative_lower,
                blnktth=blnktth,
                c_blnkith=c_blnkith,
                c_fwoth=c_fwoth,
                fwith=fwith,
                fwoth=fwoth,
                tfwvt=tfwvt,
            )
            rs = fwg_single_null.rs
            zs = fwg_single_null.zs

            component_outline(list(zip(rs, zs)), "first wall")

            firstwall_parts = ["first wall"]

        if i_single_null == 0:
            fwg_double_null = first_wall_geometry_double_null(
                cumulative_lower=cumulative_lower,
                triang=triang_95,
                blnktth=blnktth,
                c_blnkith=c_blnkith,
                c_fwoth=c_fwoth,
                fwith=fwith,
                fwoth=fwoth,
                tfwvt=tfwvt,
            )
            r1 = fwg_double_null.rs[0]
            r2 = fwg_double_null.rs[1]
            z1 = fwg_double_null.zs[0]
            z2 = fwg_double_null.zs[1]

            component_outline(list(zip(r1, z1)), "outboard_firstwall")
            component_outline(list(zip(r2, z2)), "inboard_firstwall")

            firstwall_parts = ["outboard_firstwall", "inboard_firstwall"]

        self.create_mesh(firstwall_parts=firstwall_parts)

    def create_mesh(self, firstwall_parts: List[str]):
        """Creates the face of the vacuum vessel"""
        for ob in firstwall_parts:
            change_to_mesh(ob)
            make_face_from_vertices(ob)
        join_obj(firstwall_parts)
        for obj in bpy.context.selected_objects:
            obj.name = "first wall"


# TODO Couldn't find a plot_divertor fn in plot_proc
class Divertor(BlenderComponent):
    """Divertor Component."""

    def __init__(self, params: Optional[OutputParams] = None, colour: str = DIVERTOR):
        self.params = params

        shapes = []
        if params is None:
            shapes.extend(self._get_bluemira_comps())
        else:
            self.create_shape()
            # for name in ["pf_coil", "central_coil"]:
            #    shapes.extend(self._select_objects(name))

        super().__init__(shapes, colour)

    def create_shape(self):
        """Create divertor shape.

        This is an artistic take on the output PROCESS produces to make a 3D model.
        It is our best guess at what the full component would look like.
        """
        raise NotImplementedError("TODO")
