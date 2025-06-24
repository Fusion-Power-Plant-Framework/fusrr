from pathlib import Path

from examples.bluemira_eudemo.components.reactor import (
    Bluemira_PowerPlant_EUDEMO,
)
from examples.bluemira_eudemo.run_project import data_dir as bm_data_dir
from examples.bluemira_eudemo.scene_state import BmEUDEMOSceneState
from examples.process_eudemo.components.reactor_eudemo import EUDEMO_Reactor
from examples.process_eudemo.run_project import process_mfile_path
from examples.process_eudemo.scene_state import ProcessEUDEMOSceneState
from fusrr import ProjectConfig, SceneConfig, run_project
from fusrr.core.config_model import SceneStateSelect
from fusrr.modelling.blender import BlenderProject

project_dir = Path(__file__).resolve().parent
output_dir = project_dir / "output"


if __name__ == "__main__":
    run_project(
        BlenderProject(
            "Combined_EUDEMO",
            root_components=[
                Bluemira_PowerPlant_EUDEMO(),
                EUDEMO_Reactor(process_mfile_path),
            ],
            overwrite=True,
            output_directory=output_dir,
            project_config=ProjectConfig(
                scenes=[
                    SceneConfig(
                        name="scene 1",
                        state=[
                            BmEUDEMOSceneState(
                                gltf_filepath=bm_data_dir / "eudemo.gltf"
                            ),
                            ProcessEUDEMOSceneState(
                                start_angle=0,
                                end_angle=360,
                            ),
                        ],
                    ),
                    SceneConfig(
                        name="scene 2",
                        state=[
                            BmEUDEMOSceneState(
                                gltf_filepath=bm_data_dir / "eudemo_half.gltf"
                            ),
                            ProcessEUDEMOSceneState(
                                start_angle=0,
                                end_angle=180,
                            ),
                        ],
                        select=[
                            SceneStateSelect(
                                component="Plasma",
                                state=[
                                    None,
                                    ProcessEUDEMOSceneState(
                                        start_angle=0,
                                        end_angle=360,
                                    ),
                                ],
                            )
                        ],
                    ),
                ],
            ),
        ),
    )
