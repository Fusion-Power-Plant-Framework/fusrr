from process.geometry.blanket_geometry import (
    blanket_geometry_double_null,
    blanket_geometry_single_null,
)
from process_eudemo.providers import process_params_provider

from fusrr import Comp, Designer, component
from fusrr.base.models import Vec3
from fusrr.blender.blender_component import BlenderComp
from fusrr.blender.mesh_tools import (
    mesh_add_edges_from_points,
    mesh_revolve,
)
from fusrr.hooks.hooks import useDesigner, useProvider
from fusrr.materials.base import FusrrMaterial, MetallicMaterial
from fusrr.materials.models import MaterialColour, MaterialValueZeroToOne
from fusrr.reactor.process import ProcessParams
from fusrr.reactor.process.process_component import ProcessComponent
from fusrr.reactor.process.utils import cumul_setup, cumulative_radial_build


class BlanketDesigner(Designer):
    def __init__(self, params: ProcessParams):
        self.params = params

    def run(self) -> None:
        self.i_single_null = bool(self.params.i_single_null)
        triang_95 = self.params.triang95
        blnktth = self.params.blnktth
        blnkith = self.params.blnkith
        blnkoth = self.params.blnkoth
        c_shldith = cumulative_radial_build("shldith", self.params)
        c_blnkoth = cumulative_radial_build("blnkoth", self.params)

        cumulative_upper, cumulative_lower, _, _ = cumul_setup(
            params_dict=self.params
        )

        if self.i_single_null == 1:
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

            self.pts = [Vec3(x, 0, z) for x, z in zip(rs, zs, strict=True)]

        if self.i_single_null == 0:
            bg_double_null = blanket_geometry_double_null(
                cumulative_lower=cumulative_lower,
                triang=triang_95,
                blnktth=blnktth,
                c_shldith=c_shldith,
                c_blnkoth=c_blnkoth,
                blnkith=blnkith,
                blnkoth=blnkoth,
            )

            rs_ob, rs_ib = bg_double_null.rs
            zs_ob, zs_ib = bg_double_null.zs

            self.ib_pts = [
                Vec3(x, 0, z) for x, z in zip(rs_ib, zs_ib, strict=True)
            ]
            self.ob_pts = [
                Vec3(x, 0, z) for x, z in zip(rs_ob, zs_ob, strict=True)
            ]


@component
def Blanket():
    """Component to design the blanket of a PROCESS reactor."""
    params = useProvider(process_params_provider)
    d = useDesigner(BlanketDesigner(params))

    def builder(_obj, m):
        if d.i_single_null == 1:
            mesh_add_edges_from_points(m, d.pts)
        if d.i_single_null == 0:
            mesh_add_edges_from_points(m, d.ib_pts)
            mesh_add_edges_from_points(m, d.ob_pts)
        mesh_revolve(m, Vec3.ZERO, Vec3.Z, 360)

    return BlenderComp(
        builder=builder,
        material=MetallicMaterial(
            base_colour=MaterialColour(0.0, 0.2, 1, 1),
            metallicness=MaterialValueZeroToOne(1.0),
            roughness=MaterialValueZeroToOne(0.1),
        ),
    )
