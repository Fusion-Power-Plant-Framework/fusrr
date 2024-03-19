from process.geometry.geometry_parameterisations import RectangleGeometry

from fusrr.base.mesh_tools import (
    add_edges_to_mesh_from_points,
    new_mesh_for,
    revolve_mesh_edges_silhouette,
)
from fusrr.base.models import Vec3
from fusrr.base.object import FusrrSceneObject, empty
from fusrr.base.scene import FusrrScene
from fusrr.reactor.process.components.process_component import ProcessComponent
from fusrr.reactor.process.process_adaptor import ProcessParams
from fusrr.reactor.process.utils import process_rect_to_vec3_path


class ProcessPFCoils(ProcessComponent):
    def __init__(self, reactor_params: ProcessParams):
        super().__init__("pf_coils", reactor_params)

    def _setup(self) -> None:
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
            self.add_object(
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
            anchor_x=bore, anchor_z=(-ohdz / 2), width=ohcth, height=ohdz
        )
        self.add_object(ProcessCSCoil(central_coil_geom))


class ProcessPFCoil(FusrrSceneObject):
    def __init__(self, name: str, geom: RectangleGeometry):
        self.geom = geom
        super().__init__(name)

    def _setup(self) -> None:
        self.face_path_pts = process_rect_to_vec3_path(self.geom)

    def _construct(self, scene: FusrrScene) -> None:
        obj = scene.execute_create_object(self.name)
        with new_mesh_for(obj) as m:
            add_edges_to_mesh_from_points(m, self.face_path_pts)
            revolve_mesh_edges_silhouette(m, Vec3.ZERO, Vec3.Z, 360)
        scene.select_object(self.name)


class ProcessCSCoil(ProcessPFCoil):
    def __init__(self, geom: RectangleGeometry):
        super().__init__("cs_coil", geom)
