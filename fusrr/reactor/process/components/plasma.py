from process.geometry.plasma_geometry import plasma_geometry

from fusrr.base.models import Vec3
from fusrr.blender.mesh_tools import (
    add_edges_to_mesh_from_points,
    revolve_mesh_edges_silhouette,
)
from fusrr.materials.base import FusrrMaterial, PlasmaMaterial
from fusrr.reactor.process import ProcessParams
from fusrr.reactor.process.components.process_component import ProcessComponent


class ProcessPlasma(ProcessComponent):
    def __init__(self, reactor_params: ProcessParams):
        super().__init__("plasma", reactor_params)

    @property
    def material(self) -> FusrrMaterial:
        return PlasmaMaterial()

    def _setup(self) -> None:
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

    def _construct(self, obj, m) -> None:
        add_edges_to_mesh_from_points(m, self.ib_pts)
        add_edges_to_mesh_from_points(m, self.ob_pts)
        revolve_mesh_edges_silhouette(m, Vec3.ZERO, Vec3.Z, 360)
