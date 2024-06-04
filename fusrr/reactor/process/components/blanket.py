from process.geometry.blanket_geometry import (
    blanket_geometry_double_null,
    blanket_geometry_single_null,
)

from fusrr.base.models import Vec3
from fusrr.blender.mesh_tools import (
    add_edges_to_mesh_from_points,
    revolve_mesh_edges_silhouette,
)
from fusrr.data_libs.materials import FusrrMaterialDataLabel
from fusrr.materials.base import FusrrMaterial, MetallicMaterial
from fusrr.materials.models import MaterialColour
from fusrr.reactor.process import ProcessParams
from fusrr.reactor.process.components.process_component import ProcessComponent
from fusrr.reactor.process.utils import cumul_setup, cumulative_radial_build


class ProcessBlanket(ProcessComponent):
    def __init__(self, reactor_params: ProcessParams):
        super().__init__("blanket", reactor_params)

    @property
    def material(self) -> FusrrMaterial:
        return MetallicMaterial(
            base_colour=MaterialColour(0.0, 0.2, 1, 1),
        )

    def _setup(self) -> None:
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

    def _construct(self, obj, m) -> None:
        if self.i_single_null == 1:
            add_edges_to_mesh_from_points(m, self.pts)
        if self.i_single_null == 0:
            add_edges_to_mesh_from_points(m, self.ib_pts)
            add_edges_to_mesh_from_points(m, self.ob_pts)
        revolve_mesh_edges_silhouette(m, Vec3.ZERO, Vec3.Z, 360)
