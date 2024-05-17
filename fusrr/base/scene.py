import time
from pathlib import Path

from fusrr.base.entity import FusrrSceneEntity
from fusrr.base.errors import SceneStopError
from fusrr.base.pipeline import FusrrBuildPipeline
from fusrr.blender.file_tools import save_state_to_blend_file
from fusrr.blender.scene_tools import clear_scene, deselect_all
from fusrr.data_libs.materials import load_materials


class FusrrScene:
    """A FusrrScene represents the state of a Blender .blend file.

    It holds the names of all objects added to the scene, as well as
    methods needed to construct those objects.

    A scene is executed in two phases, first the build phase,
    second the view phase.

    All objects added using the `add_object` and `add_pipe` methods
    are constructed during the build phase

    """

    def __init__(
        self,
        name: str,
        *,
        project_directory: Path | str | None = None,
        overwrite: bool = False,
    ):
        """Create a FusrrScene with a name.

        Args:
            name:
                The name of the scene.
            project_directory:
                The directory to save the scene to.
            overwrite:
                Whether to overwrite the .blend file when saving,
                if it already exists.
        """
        self._scene_name = name
        self._overwrite = overwrite

        self._project_directory = (
            Path(project_directory) if project_directory else Path.cwd()
        )
        self._scene_path = self._project_directory / (
            self._scene_name + ".blend"
        )

        self._pipeline = FusrrBuildPipeline()

    def _reset(self) -> None:
        clear_scene()

    def _rename_scene_file_if_exists(self) -> None:
        if self._scene_path.is_file():
            new_name = (
                str(self._project_directory / self._scene_name)
                + "_"
                + str(int(time.time()))
                + ".blend"
            )
            Path.rename(
                self._scene_path,
                new_name,
            )

    def _delete_scene_file_if_exists(self) -> None:
        if self._scene_path.is_file():
            self._scene_path.unlink()

    def add_entity(self, ent: FusrrSceneEntity):
        """Add an entity to this scene."""
        self._pipeline.add(ent)

    def save_scene(self) -> None:
        """Save the scene to a .blend file.

        The file name is the scene name with a .blend extension.
        The directory is the project directory.

        Note:
            This will rename the file if it exists, otherwise it will
            overwrite it if overwrite is set to True.
        """
        if self._overwrite:
            self._delete_scene_file_if_exists()
        else:
            self._rename_scene_file_if_exists()
        save_state_to_blend_file(self._scene_path)

    def run(self):
        """Run the FusrrScene.

        This initially clears the scene, then executes the build phase,
        saving the result to a .blend file.

        Note:
            This will modify the state of the current Blender session.
        """
        try:
            self._reset()
            load_materials()
            self._pipeline.execute()
        except SceneStopError as e:
            print(f"Stopping scene on: {e}")
        finally:
            deselect_all()
            print("saving scene...")
            self.save_scene()
