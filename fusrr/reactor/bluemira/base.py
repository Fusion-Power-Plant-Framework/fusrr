from pathlib import Path
from fusrr.blender.file_tools import import_gltf, save_state_to_blend_file
from fusrr.blender.scene_tools import (
    create_collection,
    get_objects_by_pattern,
    link_objects_to_collection,
)

BLUEMIRA_COMP_NAMES = {
    "Plasma": ("LCFS*",),
    "TFCoil": (
        "Casing_1_*",
        "Insulation_1*",
        "Winding_Pack_1_*",
        "TF*",
        "ITER_like_gravity_support*",
    ),
    "Cryostat": ("Cryostat*",),  # VVCryo, cryostatTS and the VV Cryo plugs
    "PFCoil": (  # PF and CS coils
        "Ground_Insulation*",
        "PFCoilSupport*",
        "Winding_Pack_[0-9]",
        "Winding_Pack_[0-9][!_]*",
        "Casing_[0-9]",
        "Casing_[0-9][!_]*",
    ),
    "Blanket": ("IBS*", "OBS*"),
    "Divertor": ("segment*",),
    "RadiationShield": (  # radiation shield and port plug
        "Body_1_*",
        "RadiationPortPlug*",
    ),
    "VacuumVessel": (  # Vacuum Vessel and VVTS
        "Body_[0-9]",
        "Body_[0-9][!_]*",
        "VVTS_1*",
    ),
}


def create_component_collections(component_regex_dict):
    for k, v in component_regex_dict.items():
        col = create_collection(k)
        for comp in v:
            link_objects_to_collection(col, get_objects_by_pattern(comp))


def get_scene(filepath):
    import_gltf(filepath)
    create_component_collections(BLUEMIRA_COMP_NAMES)
    save_state_to_blend_file(Path(f"{filepath}.blend"))
