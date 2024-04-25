from process.geometry.vacuum_vessel_geometry import (
    vacuum_vessel_geometry_single_null,
    vacuum_vessel_geometry_double_null,
)

from fusrr.base.models import Vec3
from fusrr.blender.mesh_tools import (
    add_edges_to_mesh_from_points,
    revolve_mesh_edges_silhouette,
)
from fusrr.reactor.process import ProcessParams
from fusrr.reactor.process.components.process_component import ProcessComponent
from fusrr.reactor.process.utils import cumul_setup, cumulative_radial_build


class ProcessVacuumVessel(ProcessComponent):
    def __init__(self, reactor_params: ProcessParams):
        super().__init__("vacuum_vessel", reactor_params)

    def _setup(self) -> None:
        i_single_null = bool(self.params.i_single_null)
        triang_95 = self.params.triang95
        cumulative_upper, cumulative_lower, upper, lower = cumul_setup(
            params_dict=self.params
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

        self.pts = [Vec3(x, 0, z) for x, z in zip(rs, zs, strict=True)]

    def _construct(self, _obj, m) -> None:
        add_edges_to_mesh_from_points(m, self.pts)
        revolve_mesh_edges_silhouette(m, Vec3.ZERO, Vec3.Z, 360)
