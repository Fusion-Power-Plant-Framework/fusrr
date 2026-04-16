from dataclasses import dataclass

from examples.process_eudemo.providers import process_params_provider
from examples.process_eudemo.scene_state import ProcessEUDEMOSceneState
from fusrr import component
from fusrr.core.config_model import Scene
from fusrr.core.vectors import Vec3
from fusrr.hooks import Designer, useDesigner, useProvider
from fusrr.modelling.blender.component import BlenderComp
from fusrr.modelling.blender.materials import (
    MaterialColour,
    MaterialValueZeroToOne,
    MetallicMaterial,
)
from fusrr.modelling.blender.tools.mesh_tools import (
    mesh_add_edges_from_points,
    mesh_revolve,
)
from fusrr.use_case.process import ProcessParams


@dataclass
class CryostatGeometry:
    width: float
    height: float
    thickness: float


class CryostatDesigner(Designer):
    def __init__(self, params: ProcessParams):
        self.params = params

    def run(self):
        r_cryostat_inboard = self.params.r_cryostat_inboard
        dr_cryostat = self.params.dr_cryostat
        z_cryostat_half_inside = self.params.z_cryostat_half_inside
        self.vars = CryostatGeometry(
            width=r_cryostat_inboard,
            height=z_cryostat_half_inside,
            thickness=dr_cryostat,
        )

        rs = [
            0,
            0,
            self.vars.width + self.vars.thickness,
            self.vars.width + self.vars.thickness,
            0,
            0,
            self.vars.width,
            self.vars.width,
        ]
        zs = [
            self.vars.height,
            self.vars.height + self.vars.thickness,
            self.vars.height + self.vars.thickness,
            -(self.vars.height + self.vars.thickness),
            -(self.vars.height + self.vars.thickness),
            -self.vars.height,
            -self.vars.height,
            self.vars.height,
        ]
        self.pts = [Vec3(x, 0, z) for x, z in zip(rs, zs, strict=True)]


@component
def Cryostat(*, scene: Scene[ProcessEUDEMOSceneState]):
    """Component to design the cryostat of a PROCESS reactor."""
    params = useProvider(process_params_provider)
    d = useDesigner(CryostatDesigner(params))

    def builder(_obj, m) -> None:
        mesh_add_edges_from_points(m, d.pts)
        mesh_revolve(m, Vec3.ZERO, Vec3.Z, scene.state.end_angle)

    return BlenderComp(
        builder=builder,
        material=MetallicMaterial(
            base_colour=MaterialColour(0.8, 0.8, 0.8, 1),
            metallicness=MaterialValueZeroToOne(0.1),
            roughness_fw_channel=MaterialValueZeroToOne(0.2),
        ),
    )
