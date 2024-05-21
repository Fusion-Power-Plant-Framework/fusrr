from dataclasses import dataclass

from fusrr.base.models import Vec3

from fusrr.blender.mesh_tools import (
    add_edges_to_mesh_from_points,
    revolve_mesh_edges_silhouette,
)
from fusrr.reactor.process import ProcessParams
from fusrr.reactor.process.components.process_component import (
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

    def _setup(self) -> None:
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

    def _construct(self, _obj, m) -> None:
        add_edges_to_mesh_from_points(m, self.pts)
        revolve_mesh_edges_silhouette(m, Vec3.ZERO, Vec3.Z, 360)
