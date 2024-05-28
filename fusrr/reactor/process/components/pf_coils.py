from process.geometry.geometry_parameterisations import RectangleGeometry

from fusrr.base.models import Vec3
from fusrr.base.object import FusrrSceneObject
from fusrr.base.pipeline import FusrrBuildPipeline
from fusrr.blender.mesh_tools import (
    add_edges_to_mesh_from_points,
    revolve_mesh_edges_silhouette,
)
from fusrr.data_libs.materials import FusrrMaterialDataLabel
from fusrr.materials.base import FusrrMaterial, MetallicMaterial
from fusrr.materials.models import MaterialColour, MaterialMetallic, MaterialRoughness
from fusrr.reactor.process.components.process_component import (
    ProcessComponentCollection,
)
from fusrr.reactor.process.process_adaptor import ProcessParams
from fusrr.reactor.process.utils import process_rect_to_vec3_path_points


class ProcessPFCoils(ProcessComponentCollection):
    def __init__(self, reactor_params: ProcessParams):
        super().__init__("pf_coils", reactor_params)

    def _setup(self, pipeline: FusrrBuildPipeline) -> None:
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
        self.geom = geom
        super().__init__(name)

    @property
    def material(self) -> FusrrMaterial:
        # Uncomment below code and comment the return MetallicMaterial.. to use the default option
        # mat = MetallicMaterial("pf_coil")
        # mat._material_data_label = FusrrMaterialDataLabel.METALLIC_GOLD_SHINY
        # return mat

        # returns a custom metal material
        return MetallicMaterial (
            name_suffix_override= "pf_coil",
            base_colour= MaterialColour(1, 0.2, 0.2, 1),
            metallic = MaterialMetallic(1),
            roughness= MaterialRoughness(0.2)
        )

    def _setup(self) -> None:
        self.face_path_pts = process_rect_to_vec3_path_points(self.geom)

    def _construct(self, obj, m) -> None:
        add_edges_to_mesh_from_points(m, self.face_path_pts)
        revolve_mesh_edges_silhouette(m, Vec3.ZERO, Vec3.Z, 360)


class ProcessCSCoil(ProcessPFCoil):
    def __init__(self, geom: RectangleGeometry):
        super().__init__("cs_coil", geom)

    @property
    def material(self) -> FusrrMaterial:
        mat = MetallicMaterial()
        mat._material_data_label = FusrrMaterialDataLabel.METALLIC_RED_SHINY
        return mat
