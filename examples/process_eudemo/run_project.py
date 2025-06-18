from pathlib import Path

from examples.process_eudemo.components.reactor_eudemo import EUDEMO_Reactor
from examples.process_eudemo.scene import EUDEMOScene
from fusrr import SceneConfig, run_project
from fusrr.modelling.blender import BlenderProject

project_dir = Path(__file__).resolve().parent
config_dir = project_dir / "config"
output_dir = project_dir / "output"

project_config = config_dir / "Process_EUDEMO.json"
process_mfile_path = config_dir / "EUDEMO_MFILE.DAT"

run_project(
    BlenderProject(
        "Process_EUDEMO",
        root_components=[EUDEMO_Reactor(process_mfile_path)],
        # project_config=project_config,
        output_directory=output_dir,
        overwrite=True,
        default_scene=SceneConfig(
            name="scene 1", state=EUDEMOScene(start_angle=0.0, end_angle=180.0)
        ),
    ),
)
