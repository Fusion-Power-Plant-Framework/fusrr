from dataclasses import dataclass
from pathlib import Path

from kink import di

from fusrr.base.entity.object_properties import (
    CommonMeshModelProperties,
    CommonObjTransformProperties,
)
from fusrr.base.world_state import FusrrWorldState
from fusrr.blender.scene_tools import add_scene


@dataclass
class FusrrWorldSceneObjectConfig:
    """A FusrrSceneObjectsConfig is a configuration for a FusrrSceneObjects."""

    name: str

    transform: CommonObjTransformProperties | None = None
    model: CommonMeshModelProperties | None = None


@dataclass
class FusrrWorldSceneCameraConfig:
    """A FusrrSceneCameraConfig is a configuration for a FusrrSceneCamera."""

    transform: CommonObjTransformProperties | None = None
    look_at: str | None = None


@dataclass
class FusrrWorldSceneConfig:
    """A FusrrSceneConfig is a configuration for a FusrrScene."""

    name: str
    camera: FusrrWorldSceneCameraConfig
    based_on: str | None = None
    objects: list[FusrrWorldSceneObjectConfig] | None = None


class FusrrScene:
    """A FusrrScene is a specific arrangement of objects in the project,
    in a new scene.

    The scene generates an image based on its configuration.

    The scene controls the camera and may be based off other scenes.
    """

    def __init__(
        self,
        name: str,
        camera: FusrrWorldSceneCameraConfig,
        based_on: str | None = None,
        objects: list[FusrrWorldSceneObjectConfig] | None = None,
        output_directory: Path | str | None = None,
        world_state: FusrrWorldState | None = None,
    ):
        self._name = name
        self._camera_config = camera
        self._based_on = based_on
        self._objects_config = objects
        self._output_directory = (
            Path(output_directory) if output_directory else Path.cwd()
        )
        self._world_state = world_state or di[FusrrWorldState]

    @property
    def name(self) -> str:
        """The name of the scene."""
        return self._name

    def execute(self):
        """Execute this scene."""
        add_scene(self.name)
        p = self._world_state.get_object("plasma")
        p.mesh_model_props.revolve_z_deg = 360
