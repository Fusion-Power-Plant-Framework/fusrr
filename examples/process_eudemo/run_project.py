import sys
from pathlib import Path

from fusrr import SceneState, run_project
from fusrr.blender import BlenderProject

sys.path.append(Path(__file__).resolve().parent.parent.as_posix())

from process_eudemo.components.reactor_eudemo import EUDEMO_Reactor

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
        default_scene=SceneState(""),
    ),
)
