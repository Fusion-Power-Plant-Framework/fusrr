from pathlib import Path

import bpy

from examples.bluemira_eudemo.scene_state import BmEUDEMOSceneState
from fusrr import Scene, Vec3, component
from fusrr.hooks import Designer, useDesigner
from fusrr.modelling.blender.component import BlenderComp, BlenderCompound
from fusrr.modelling.blender.materials.base import BlenderMaterial
from fusrr.modelling.blender.materials.materials import (
    MetallicMaterial,
    PlasmaMaterial,
)
from fusrr.modelling.blender.materials.value_models import MaterialColour
from fusrr.modelling.blender.tools.object_tools import copy_object_w_mesh
from fusrr.modelling.blender.tools.scene_tools import (
    get_object_by_pattern_f,
    get_objects_by_pattern,
    import_gltf,
    remove_object,
    remove_object_if_exists,
)


@component
def GLTFComp(
    *,
    comp_pattern: str,
    comp_mat: BlenderMaterial,
    scene: Scene[BmEUDEMOSceneState],
):
    """GLTF component."""

    def obj_builder(comp_name: str) -> bpy.types.Object:
        """Builds the GLTF object."""
        pat = rf"^gltf\.{scene.name}\.{comp_pattern}$"
        return copy_object_w_mesh(
            get_object_by_pattern_f(pat), new_name=comp_name
        )

    return BlenderComp(
        obj_builder=obj_builder,
        material=comp_mat,
    )


class PowerPlantGLTFLoader(Designer):
    """Power Plant Loader component."""

    def __init__(self, gltf_filepath: Path | str, scene_name: str):
        self.gltf_filepath = gltf_filepath
        self.scene_name = scene_name
        self.objs_name_prefix = f"gltf.{self.scene_name}"

    def run(self):
        """Load the power plant model."""
        import_gltf(
            self.gltf_filepath,
            objs_name_prefix=self.objs_name_prefix,
            scale=Vec3.ONE * 1000,
        )

    def cleanup(self):
        """Cleanup resources after loading the power plant model."""
        # No specific cleanup needed for the GLTF import in this case.
        imported_objs = get_objects_by_pattern(rf"^{self.objs_name_prefix}\..*")
        for obj in imported_objs:
            remove_object(obj)


@component
def Bluemira_PowerPlant_EUDEMO(*, scene: Scene[BmEUDEMOSceneState]):
    """Bluemira Power Plant EUDEMO component."""
    useDesigner(
        PowerPlantGLTFLoader(scene.state.gltf_filepath, scene.name),
        [scene.state.gltf_filepath, scene.name],
    )
    return BlenderCompound(
        [
            GLTFComp(
                name="bm_thermal_shield",
                comp_pattern="Thermal_Shield",
                comp_mat=MetallicMaterial(
                    base_colour=MaterialColour(0.7, 0.7, 0.7, 1),
                ),
            ),
            GLTFComp(
                name="bm_blanket_ib",
                comp_pattern="Blanket.*IB",
                comp_mat=MetallicMaterial(
                    base_colour=MaterialColour(0.8, 0.6, 0.2, 1),
                ),
            ),
            GLTFComp(
                name="bm_blanket_ob",
                comp_pattern="Blanket_mat_Homogenised_HCPB_2015_v3_OB",
                comp_mat=MetallicMaterial(
                    base_colour=MaterialColour(0.8, 0.6, 0.2, 1),
                ),
            ),
            GLTFComp(
                name="bm_tf_coil",
                comp_pattern="TFCoil_mat_Toroidal_Field_Coil_2015",
                comp_mat=MetallicMaterial(
                    base_colour=MaterialColour(0.1, 0.1, 0.5, 1),
                ),
            ),
            GLTFComp(
                name="bm_poloidal_coils",
                comp_pattern="Poloidal_Coils_mat_Poloidal_Field_Coil",
                comp_mat=MetallicMaterial(
                    base_colour=MaterialColour(0.2, 0.5, 0.2, 1),
                ),
            ),
            GLTFComp(
                name="bm_coil_structures",
                comp_pattern="Coil_Structures_mat_SS316_LN",
                comp_mat=MetallicMaterial(
                    base_colour=MaterialColour(0.5, 0.5, 0.5, 1),
                ),
            ),
            GLTFComp(
                name="bm_cryostat",
                comp_pattern="Cryostat_mat_SS316_LN",
                comp_mat=MetallicMaterial(
                    base_colour=MaterialColour(0.6, 0.6, 0.7, 1),
                ),
            ),
            GLTFComp(
                name="bm_radiation_shield",
                comp_pattern="RadiationShield_mat_SS316_LN",
                comp_mat=MetallicMaterial(
                    base_colour=MaterialColour(0.7, 0.7, 0.8, 1),
                ),
            ),
            GLTFComp(
                name="bm_radiation_shield_plugs",
                comp_pattern="RadiationShield",
                comp_mat=MetallicMaterial(
                    base_colour=MaterialColour(0.8, 0.8, 0.9, 1),
                ),
            ),
            GLTFComp(
                name="bm_plasma",
                comp_pattern="Plasma",
                comp_mat=PlasmaMaterial(
                    core_colour=MaterialColour(0.8, 0.1, 0.652, 1)
                ),
            ),
            GLTFComp(
                name="bm_vv",
                comp_pattern="VacuumVessel.*",
                comp_mat=MetallicMaterial(
                    base_colour=MaterialColour(0.2, 0.0, 1, 1),
                ),
            ),
            GLTFComp(
                name="bm_divertor",
                comp_pattern="Divertor.*",
                comp_mat=MetallicMaterial(
                    base_colour=MaterialColour(0.2, 0.0, 1, 1),
                ),
            ),
        ]
    )
