from dataclasses import dataclass
from pathlib import Path

from fusrr.base.entity.object_properties import (
    CommonMeshModelProperties,
    CommonObjTransformProperties,
)
from fusrr.blender.scene_tools import add_scene


@dataclass
class FusrrSceneConfigForObject:
    """A FusrrSceneObjectsConfig is a configuration for a FusrrSceneObjects."""

    name: str

    transform: CommonObjTransformProperties | None = None
    model: CommonMeshModelProperties | None = None


@dataclass
class FusrrSceneConfigForCamera:
    """A FusrrSceneCameraConfig is a configuration for a FusrrSceneCamera."""

    transform: CommonObjTransformProperties | None = None
    look_at: str | None = None


@dataclass
class FusrrSceneConfig:
    """A FusrrSceneConfig is a configuration for a FusrrScene."""

    name: str
    camera: FusrrSceneConfigForCamera
    based_on: str | None = None
    objects: list[FusrrSceneConfigForObject] | None = None


class FusrrScene:
    """A FusrrScene is a specific arrangement of objects in the project,
    in a new scene.

    The scene generates an image based on its configuration.

    The scene controls the camera and may be based off other scenes.
    """

    def __init__(
        self,
        name: str,
        camera: FusrrSceneConfigForCamera,
        based_on: str | None = None,
        objects: list[FusrrSceneConfigForObject] | None = None,
        *,
        output_directory: Path | str | None = None,
    ):
        self._name = name
        self._camera_config = camera
        self._based_on = based_on
        self._objects_config = objects
        self._output_directory = (
            Path(output_directory) if output_directory else Path.cwd()
        )

    @property
    def name(self) -> str:
        """The name of the scene."""
        return self._name

    def execute(self):
        """Execute this scene."""
        add_scene(self.name)
