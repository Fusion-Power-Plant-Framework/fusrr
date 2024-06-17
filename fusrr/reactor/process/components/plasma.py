from process.geometry.plasma_geometry import plasma_geometry

from fusrr.base.models import Vec3
from fusrr.blender.mesh_tools import mesh_add_edges_from_points
from fusrr.materials.base import FusrrMaterial, PlasmaMaterial
from fusrr.materials.models import MaterialColour
from fusrr.reactor.process import ProcessParams
from fusrr.reactor.process.process_component import ProcessComponent


class ProcessPlasma(ProcessComponent):
    def __init__(self, reactor_params: ProcessParams):
        super().__init__("plasma", reactor_params)

    @property
    def material(self) -> FusrrMaterial:
        return PlasmaMaterial(
            # testing the colour of the plasma
            base_colour=MaterialColour(0.7, 0.01, 0.01, 1),
            colour_ramp=MaterialColour(0.1, 0.1, 0.9, 1),
        )

    def prepare(self) -> None:
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

        # todo: temp
        self._mesh_model_props.revolve_z_deg = 360

    def construct(self, _obj, m) -> None:
        mesh_add_edges_from_points(m, self.ib_pts)
        mesh_add_edges_from_points(m, self.ob_pts)
