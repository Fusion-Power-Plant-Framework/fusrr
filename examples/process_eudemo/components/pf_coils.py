from process.geometry.geometry_parameterisations import RectangleGeometry

from examples.process_eudemo.providers import process_params_provider
from examples.process_eudemo.scene_state import ProcessEUDEMOSceneState
from fusrr import Vec3, component
from fusrr.core.config_model import Scene
from fusrr.hooks import Designer, useDesigner, useProvider
from fusrr.modelling.blender import BlenderComp, BlenderCompound
from fusrr.modelling.blender.materials import (
    MaterialColour,
    MaterialValueZeroToOne,
    MetallicMaterial,
)
from fusrr.modelling.blender.tools.mesh_tools import (
    mesh_add_edges_from_points,
    mesh_revolve,
)
from fusrr.use_case.process import (
    ProcessParams,
    process_rect_to_vec3_path_points,
)


class PFCoilsDesigner(Designer):
    """Designer for the PF coils of a PROCESS reactor."""

    def __init__(self, params: ProcessParams):
        self.params = params

    def run(self) -> None:
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

        self.pf_coils_geom = [
            RectangleGeometry(
                anchor_x=self.params.get_with(_rgx("rpf", coil)),
                anchor_z=self.params.get_with(_rgx("zpf", coil)),
                width=self.params.get_with(_rgx("pfdr", coil)),
                height=self.params.get_with(_rgx("pfdz", coil)),
            )
            for coil in range(1, number_of_coils + 1)
        ]

        self.central_coil_geom = RectangleGeometry(
            anchor_x=bore, anchor_z=0, width=ohcth, height=ohdz
        )


@component
def PFCoils():
    """Component to design the PF coils of a PROCESS reactor."""
    params = useProvider(process_params_provider)
    d = useDesigner(PFCoilsDesigner(params))

    comps = [
        PFCoil(name=f"pf_{i}", geom=geom)
        for i, geom in enumerate(d.pf_coils_geom, start=1)
    ]
    comps.append(CSCoil(name="cs", geom=d.central_coil_geom))

    return BlenderCompound(comps)


def _coil_builder(geom: RectangleGeometry, angle: float):
    """Helper function to build a coil component."""

    def builder(_obj, m):
        face_path_pts = process_rect_to_vec3_path_points(geom)
        mesh_add_edges_from_points(m, face_path_pts, close=True)
        mesh_revolve(m, Vec3.ZERO, Vec3.Z, angle)

    return builder


@component
def PFCoil(geom: RectangleGeometry, *, scene: Scene[ProcessEUDEMOSceneState]):
    return BlenderComp(
        builder=_coil_builder(geom, scene.state.end_angle),
        material=MetallicMaterial(
            base_colour=MaterialColour(1.0, 0.2, 0.2, 1),
            metallicness=MaterialValueZeroToOne(1.0),
            roughness=MaterialValueZeroToOne(0.2),
        ),
    )


@component
def CSCoil(geom: RectangleGeometry, *, scene: Scene[ProcessEUDEMOSceneState]):
    return BlenderComp(
        builder=_coil_builder(geom, scene.state.end_angle),
        material=MetallicMaterial(
            base_colour=MaterialColour(0.9, 0.2, 1, 1),
            metallicness=MaterialValueZeroToOne(1.0),
            roughness=MaterialValueZeroToOne(0.2),
        ),
    )
