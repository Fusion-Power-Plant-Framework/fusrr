from process.geometry.vacuum_vessel_geometry import (
    vacuum_vessel_geometry_double_null,
    vacuum_vessel_geometry_single_null,
)
from process_eudemo.providers import process_params_provider

from fusrr.base.models import Vec3
from fusrr.blender.blender_component import BlenderComp
from fusrr.blender.mesh_tools import (
    mesh_add_edges_from_points,
    mesh_revolve,
)
from fusrr.core import component
from fusrr.hooks.base import Designer
from fusrr.hooks.hooks import useDesigner, useProvider
from fusrr.materials.base import MetallicMaterial
from fusrr.materials.models import MaterialColour
from fusrr.reactor.process import ProcessParams
from fusrr.reactor.process.process_adaptor import ProcessParams
from fusrr.reactor.process.utils import cumul_setup, cumulative_radial_build


class VacuumVesselDesigner(Designer):
    def __init__(self, reactor_params: ProcessParams):
        self.params = reactor_params

    def run(self) -> None:
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


@component
def VacuumVessel():
    """Component to design the vacuum vessel of a PROCESS reactor."""
    params = useProvider(process_params_provider)
    d = useDesigner(VacuumVesselDesigner(params))

    def builder(_obj, m) -> None:
        mesh_add_edges_from_points(m, d.pts)
        mesh_revolve(m, Vec3.ZERO, Vec3.Z, 360)

    return BlenderComp(
        builder=builder,
        material=MetallicMaterial(
            base_colour=MaterialColour(0.2, 0.0, 1, 1),
        ),
    )
