from process.geometry.geometry_parameterisations import RectangleGeometry

from fusrr.base.entities.object import FusrrSceneObject
from fusrr.base.models import Vec3
from fusrr.base.pipeline import FusrrBuildPipeline
from fusrr.blender.mesh_tools import (
    mesh_add_edges_from_points,
    mesh_revolve,
)
from fusrr.materials.base import FusrrMaterial, MetallicMaterial
from fusrr.materials.models import MaterialColour, MaterialValueZeroToOne
from fusrr.reactor.process.process_adaptor import ProcessParams
from fusrr.reactor.process.process_component import (
    ProcessComponentCollection,
)
from fusrr.reactor.process.utils import process_rect_to_vec3_path_points


class ProcessPFCoils(ProcessComponentCollection):
    def __init__(self, reactor_params: ProcessParams):
        super().__init__("pf_coils", reactor_params)

    def setup(self, pipeline: FusrrBuildPipeline) -> None:
        bore = float(self.params.bore)
        ohcth = float(self.params.ohcth)
        ohdz = float(self.params.ohdz)
        iohcl = self.params.get("iohcl", 1)

        def _rgx_f(prefix: str, r: str) -> str:
            return rf"{prefix}.*{r}[\)|\]]*"

        def _rgx(prefix: str, n: int) -> str:
            return _rgx_f(prefix, f"{n:01}")

        number_of_coils = self.params.n_keys_with(_rgx_f("rpf", r"\d"))

        if iohcl == 0:
            number_of_coils += 1

        for coil in range(1, number_of_coils + 1):
            pipeline.add(
                ProcessPFCoil(
                    name=f"pf_{coil}",
                    geom=RectangleGeometry(
                        anchor_x=self.params.get_with(_rgx("rpf", coil)),
                        anchor_z=self.params.get_with(_rgx("zpf", coil)),
                        width=self.params.get_with(_rgx("pfdr", coil)),
                        height=self.params.get_with(_rgx("pfdz", coil)),
                    ),
                )
            )

        central_coil_geom = RectangleGeometry(
            anchor_x=bore, anchor_z=0, width=ohcth, height=ohdz
        )
        pipeline.add(ProcessCSCoil(central_coil_geom))


class ProcessPFCoil(FusrrSceneObject):
    def __init__(self, name: str, geom: RectangleGeometry):
        super().__init__(name)
        self.geom = geom

    @property
    def material(self) -> FusrrMaterial:
        return MetallicMaterial(
            object_name_override="pf_coil",
            base_colour=MaterialColour(1, 0.2, 0.2, 1),
            metallicness=MaterialValueZeroToOne(1),
            roughness=MaterialValueZeroToOne(0.2),
        )

    def prepare(self) -> None:
        self.face_path_pts = process_rect_to_vec3_path_points(self.geom)

    def construct(self, _obj, m) -> None:
        mesh_add_edges_from_points(m, self.face_path_pts)
        mesh_revolve(m, Vec3.ZERO, Vec3.Z, 360)


class ProcessCSCoil(ProcessPFCoil):
    def __init__(self, geom: RectangleGeometry):
        super().__init__("cs_coil", geom)

    @property
    def material(self) -> FusrrMaterial:
        return MetallicMaterial(
            base_colour=MaterialColour(0.9, 0.2, 1, 1),
        )
