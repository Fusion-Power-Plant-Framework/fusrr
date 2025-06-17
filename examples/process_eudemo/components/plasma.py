from process.geometry.plasma_geometry import plasma_geometry

from examples.process_eudemo.providers import process_params_provider
from examples.process_eudemo.scene import EUDEMOScene
from fusrr import component
from fusrr.blender.blender_component import BlenderComp
from fusrr.blender.tools.mesh_tools import (
    mesh_add_edges_from_points,
    mesh_revolve,
)
from fusrr.core.vectors import Vec3
from fusrr.hooks import Designer, useDesigner, useProvider
from fusrr.materials.base import PlasmaMaterial
from fusrr.materials.models import MaterialColour
from fusrr.reactor.process import ProcessParams


class PlasmaDesigner(Designer):
    def __init__(self, params: ProcessParams):
        self.params = params

    def run(self) -> None:
        r_0 = self.params.rmajor
        a = self.params.rminor
        triang_95 = self.params.triang95
        kappa_95 = self.params.kappa95
        i_single_null = bool(self.params.i_single_null)

        pg = plasma_geometry(
            r_0=r_0,
            a=a,
            triang_95=triang_95,
            kappa_95=kappa_95,
            i_single_null=i_single_null,
        )

        rs_ib, rs_ob = pg.rs
        zs_ib, zs_ob = pg.zs

        self.ib_pts = [Vec3(x, 0, z) for x, z in zip(rs_ib, zs_ib, strict=True)]
        self.ob_pts = [Vec3(x, 0, z) for x, z in zip(rs_ob, zs_ob, strict=True)]


@component
def Plasma(*, scene: EUDEMOScene):
    """Component to design the plasma of a PROCESS reactor."""
    params = useProvider(process_params_provider)
    d = useDesigner(PlasmaDesigner(params))

    def builder(_obj, m):
        mesh_add_edges_from_points(m, d.ib_pts)
        mesh_add_edges_from_points(m, d.ob_pts)
        mesh_revolve(m, Vec3.ZERO, Vec3.Z, scene.end_angle)

    return BlenderComp(
        builder=builder,
        material=PlasmaMaterial(core_colour=MaterialColour(0.8, 0.1, 0.652, 1)),
    )
