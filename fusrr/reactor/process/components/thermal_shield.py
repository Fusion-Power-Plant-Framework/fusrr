from process.geometry.shield_geometry import (
    shield_geometry_single_null,
    shield_geometry_double_null,
)

from fusrr.base.models import Vec3
from fusrr.blender.mesh_tools import (
    add_edges_to_mesh_from_points,
    revolve_mesh_edges_silhouette,
)
from fusrr.reactor.process import ProcessParams
from fusrr.reactor.process.components.process_component import ProcessComponent
from fusrr.reactor.process.utils import cumul_setup, cumulative_radial_build


class ProcessThermalShield(ProcessComponent):
    def __init__(self, reactor_params: ProcessParams):
        super().__init__("thermal_shield", reactor_params)

    def _setup(self) -> None:
        i_single_null = bool(self.params.i_single_null)
        triang_95 = self.params.triang95
        cumulative_upper, cumulative_lower, upper, lower = cumul_setup(
            params_dict=self.params
        )

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

        self.pts = [Vec3(x, 0, z) for x, z in zip(rs, zs, strict=True)]

    def _construct(self, _obj, m) -> None:
        add_edges_to_mesh_from_points(m, self.pts)
        # revolve_mesh_edges_silhouette(m, Vec3.ZERO, Vec3.Z, 360)
