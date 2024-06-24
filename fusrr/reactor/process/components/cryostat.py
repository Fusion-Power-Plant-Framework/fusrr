from dataclasses import dataclass

from fusrr.base.models import Vec3
from fusrr.blender.mesh_tools import (
    mesh_add_edges_from_points,
    mesh_revolve,
)
from fusrr.materials.base import FusrrMaterial, GlassMaterial, MetallicMaterial
from fusrr.materials.models import MaterialColour, MaterialValueZeroToOne
from fusrr.reactor.process import ProcessParams
from fusrr.reactor.process.process_component import (
    ProcessComponent,
)


@dataclass
class CryostatGeometry:
    width: float
    height: float
    thickness: float


class ProcessCryostat(ProcessComponent):
    def __init__(self, reactor_params: ProcessParams):
        super().__init__("cryostat", reactor_params)

    @property
    def material(self) -> FusrrMaterial:
        return MetallicMaterial(
            base_colour=MaterialColour(0.8, 0.8, 0.8, 1),
            metallicness=MaterialValueZeroToOne(0.1),
            roughness=MaterialValueZeroToOne(0.6),
        )

    def prepare(self) -> None:
        rdewex = self.params.rdewex
        ddwex = self.params.ddwex
        zdewex = self.params.zdewex
        self.vars = CryostatGeometry(
            width=rdewex, height=zdewex, thickness=ddwex
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

    def construct(self, _obj, m) -> None:
        mesh_add_edges_from_points(m, self.pts)
        mesh_revolve(m, Vec3.ZERO, Vec3.Z, 360)
