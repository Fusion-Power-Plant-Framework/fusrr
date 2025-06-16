import sys
from pathlib import Path

sys.path.append(Path(__file__).parent.parent.as_posix())


from process_eudemo.components.reactor_eudemo import EUDEMOReactor

from fusrr.blender.blender_project import BlenderProject
from fusrr.core.project import ProjectContext, run_project
from fusrr.core.scene import SceneState

config_dir = Path(__file__).parent / "config"

p = ProjectContext()

run_project(
    BlenderProject(
        "EUDEMO",
        root_components=[
            EUDEMOReactor(mfile_filepath=config_dir / "EUDEMO_MFILE.DAT")
        ],
        # project_config=config_dir / "process_eudemo.json",
        overwrite=True,
        default_scene=SceneState(""),
    ),
)
