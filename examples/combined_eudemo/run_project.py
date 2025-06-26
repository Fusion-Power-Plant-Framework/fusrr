import math
from pathlib import Path

from examples.bluemira_eudemo.components.reactor import (
    Bluemira_PowerPlant_EUDEMO,
)
from examples.bluemira_eudemo.run_project import data_dir as bm_data_dir
from examples.bluemira_eudemo.scene_state import BmEUDEMOSceneState
from examples.combined_eudemo.lights_camera import LightsCamera
from examples.combined_eudemo.scene_state import LightsCameraSceneState
from examples.process_eudemo.components.reactor_eudemo import EUDEMO_Reactor
from examples.process_eudemo.run_project import process_mfile_path
from examples.process_eudemo.scene_state import ProcessEUDEMOSceneState
from fusrr import ProjectConfig, SceneConfig, run_project
from fusrr.core.config_model import SceneStateSelect
from fusrr.core.vectors import Vec3
from fusrr.modelling.blender import BlenderProject
from fusrr.modelling.blender.transform import BlenderTransform

project_dir = Path(__file__).resolve().parent
output_dir = project_dir / "output"

# an idea for the future: create multiple cameras in the LightsCamera component,
# subclass BlenderProject and write a new on_scene_finish hook to render each
# camera in the scene

if __name__ == "__main__":
    run_project(
        BlenderProject(
            "Combined_EUDEMO",
            root_components=[
                Bluemira_PowerPlant_EUDEMO(),
                EUDEMO_Reactor(process_mfile_path, translation=Vec3(50, 0, 0)),
                LightsCamera(),
            ],
            overwrite=True,
            output_directory=output_dir,
            project_config=ProjectConfig(
                scenes=[
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
                            LightsCameraSceneState(
                                lights=[
                                    BlenderTransform(
                                        position=Vec3(0, -50, 20)
                                        + Vec3(-5 + x * 10, 0, -10 + z * 5),
                                        rotation=Vec3(math.pi / 3, 0, 0),
                                    )
                                    for x in range(2)
                                    for z in range(2)
                                ],
                                camera_transform=BlenderTransform(
                                    position=Vec3(0, -75, -5),
                                    rotation=Vec3(math.pi / 2, 0, 0),
                                ),
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
