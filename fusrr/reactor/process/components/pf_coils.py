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
                    r=self.params.get_with(_rgx("rpf", coil)),
                    z=self.params.get_with(_rgx("zpf", coil)),
                    dr=self.params.get_with(_rgx("pfdr", coil)),
                    dz=self.params.get_with(_rgx("pfdz", coil)),
                )
            )

        central_coil_geom = RectangleGeometry(
            anchor_x=bore, anchor_z=(-ohdz / 2), width=ohcth, height=ohdz
        )
        self.add_object(ProcessCSCoil(central_coil_geom))

    def _construct(self, scene: FusrrScene) -> None:
        scene.execute_create_object(self.name)


class ProcessPFCoil(FusrrSceneObject):
    def __init__(self, name: str, r: float, z: float, dr: float, dz: float):
        self.r = r
        self.z = z
        self.dr = dr / 2
        self.dz = dz / 2
        super().__init__(name, None)

    def _setup(self) -> None:
        tr = Vec3(self.r + self.dr, 0, self.z + self.dz)
        br = Vec3(self.r + self.dr, 0, self.z - self.dz)
        bl = Vec3(self.r - self.dr, 0, self.z - self.dz)
        tl = Vec3(self.r - self.dr, 0, self.z + self.dz)

        self.face_pts = [tr, br, bl, tl, tr]

    def _construct(self, scene: FusrrScene) -> None:
        obj = scene.execute_create_object(self.name)
        with new_mesh_for(obj) as m:
            add_edges_to_mesh_from_points(m, self.face_pts)
            revolve_mesh_edges_silhouette(m, Vec3.ZERO, Vec3.Z, 360)
        scene.select_object(self.name)


class ProcessCSCoil(FusrrSceneObject):
    def __init__(self, geom: RectangleGeometry):
        self.geom = geom
        super().__init__("cs_coil", None)

    def _setup(self) -> None:
        x = self.geom.anchor_x
        z = self.geom.anchor_z
        dx = self.geom.width / 2
        dz = self.geom.height / 2

        tr = Vec3(x + dx, 0, z + dz)
        br = Vec3(x + dx, 0, z - dz)
        bl = Vec3(x - dx, 0, z - dz)
        tl = Vec3(x - dx, 0, z + dz)

        self.rec_pts = [tr, br, bl, tl, tr]

    def _construct(self, scene: FusrrScene) -> None:
        obj = scene.execute_create_object(self.name)
        with new_mesh_for(obj) as m:
            add_edges_to_mesh_from_points(m, self.rec_pts)
            revolve_mesh_edges_silhouette(m, Vec3.ZERO, Vec3.Z, 360)
        scene.select_object(self.name)
