from process.geometry.plasma_geometry import plasma_geometry

from examples.process_eudemo.providers import process_params_provider
from examples.process_eudemo.scene_state import ProcessEUDEMOSceneState
from fusrr import Vec3, component
from fusrr.core.config_model import Scene
from fusrr.hooks import Designer, useDesigner, useProvider
from fusrr.modelling.blender import BlenderComp
from fusrr.modelling.blender.materials import (
    MaterialColour,
    PlasmaMaterial,
)
from fusrr.modelling.blender.tools.mesh_tools import (
    mesh_add_edges_from_points,
    mesh_revolve,
)
from fusrr.use_case.process import ProcessParams


class PlasmaDesigner(Designer):
    def __init__(self, params: ProcessParams):
        self.params = params

    def run(self) -> None:
        rmajor = self.params.rmajor
        rminor = self.params.rminor
        triang95 = self.params.triang95
        kappa95 = self.params.kappa95
        i_single_null = bool(self.params.i_single_null)
        i_plasma_shape = self.params.i_plasma_shape
        plasma_square = self.params.plasma_square

        pg = plasma_geometry(
            rmajor=rmajor,
            rminor=rminor,
            triang=triang95,
            kappa=kappa95,
            i_single_null=i_single_null,
            i_plasma_shape=i_plasma_shape,
            square=plasma_square,
        )

        rs_ib, rs_ob = pg.rs
        zs_ib, zs_ob = pg.zs

        self.ib_pts = [Vec3(x, 0, z) for x, z in zip(rs_ib, zs_ib, strict=True)]
        self.ob_pts = [Vec3(x, 0, z) for x, z in zip(rs_ob, zs_ob, strict=True)]


@component
def Plasma(*, scene: Scene[ProcessEUDEMOSceneState]):
    """Component to design the plasma of a PROCESS reactor."""
    params = useProvider(process_params_provider)
    d = useDesigner(PlasmaDesigner(params))

    def builder(_obj, m) -> None:
        mesh_add_edges_from_points(m, d.ib_pts)
        mesh_add_edges_from_points(m, d.ob_pts)
        mesh_revolve(m, Vec3.ZERO, Vec3.Z, scene.state.end_angle)

    return BlenderComp(
        builder=builder,
        material=PlasmaMaterial(core_colour=MaterialColour(0.8, 0.1, 0.652, 1)),
    )
