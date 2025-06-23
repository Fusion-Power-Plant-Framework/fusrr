from pathlib import Path

from examples.bluemira_eudemo.components.reactor import (
    Bluemira_PowerPlant_EUDEMO,
)
from examples.bluemira_eudemo.scene_state import BmEUDEMOSceneState
from fusrr import ProjectConfig, SceneConfig, run_project
from fusrr.modelling.blender import BlenderProject

project_dir = Path(__file__).resolve().parent
config_dir = project_dir / "config"
data_dir = project_dir / "data"
output_dir = project_dir / "output"

project_config = config_dir / "Bluemira_EUDEMO.json"

if __name__ == "__main__":
    run_project(
        BlenderProject(
            "Bluemira_EUDEMO",
            root_components=[Bluemira_PowerPlant_EUDEMO()],
            overwrite=True,
            output_directory=output_dir,
            project_config=ProjectConfig(
                scenes=[
                    SceneConfig(
                        name="scene-1",
                        state=BmEUDEMOSceneState(
                            gltf_filepath=data_dir / "eudemo.gltf"
                        ),
                    ),
                    SceneConfig(
                        name="scene-2",
                        state=BmEUDEMOSceneState(
                            gltf_filepath=data_dir / "eudemo_half.gltf"
                        ),
                    ),
                ],
            ),
        ),
    )
