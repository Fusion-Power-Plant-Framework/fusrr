from pathlib import Path

from examples.process_eudemo.components.reactor_eudemo import EUDEMO_Reactor
from examples.process_eudemo.scene_state import ProcessEUDEMOSceneState
from fusrr import ProjectConfig, SceneConfig, run_project
from fusrr.core.config_model import SceneStateSelect
from fusrr.modelling.blender import BlenderProject

project_dir = Path(__file__).resolve().parent
config_dir = project_dir / "config"
output_dir = project_dir / "output"

project_config = config_dir / "Process_EUDEMO.json"
process_mfile_path = config_dir / "EUDEMO_MFILE.DAT"

if __name__ == "__main__":
    run_project(
        BlenderProject(
            "Process_EUDEMO",
            root_components=[EUDEMO_Reactor(process_mfile_path)],
            overwrite=True,
            output_directory=output_dir,
            project_config=ProjectConfig(
                scenes=[
                    SceneConfig(
                        name="scene 1",
                        state=ProcessEUDEMOSceneState(
                            start_angle=0.0, end_angle=180.0
                        ),
                    ),
                    SceneConfig(
                        name="scene 2",
                        state=ProcessEUDEMOSceneState(
                            start_angle=0.0, end_angle=90.0
                        ),
                        select=[
                            SceneStateSelect(
                                component="Plasma",
                                state=ProcessEUDEMOSceneState(
                                    start_angle=0.0, end_angle=360.0
                                ),
                            )
                        ],
                    ),
                ],
            ),
        ),
    )
