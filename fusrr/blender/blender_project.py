import time
from os import PathLike
from pathlib import Path

from fusrr.blender.file_tools import save_state_to_blend_file
from fusrr.blender.scene_tools import clear_scene, deselect_all
from fusrr.core.component import _Component
from fusrr.core.project import FusrrProject
from fusrr.core.scene import SceneState
from fusrr.data_libs.materials import load_materials


class BlenderProject(FusrrProject):
    """A BlenderProject represents the state of a Blender .blend file.

    It holds the names of all objects added to the file, as well as
    methods needed to construct those objects.
    """

    def __init__(
        self,
        project_name: str,
        *,
        root_components: list[_Component],
        project_config: dict | PathLike | None = None,
        output_directory: PathLike | None = None,
        overwrite: bool = False,
        default_scene: SceneState | None = None,
    ):
        """Create a BlenderProject with a name.

        Args:
            project_name:
                The name of the Blender project.
            root_components:
                The root components of the project.
            project_config:
                The path to the project configuration file.
            output_directory:
                The directory to save the scene to.
                Defaults to the current working directory `Path.cwd()`.
            overwrite:
                Whether to overwrite the .blend file when saving,
                if it already exists.
            default_scene:
                The default scene state for the project.
        """
        super().__init__(
            project_name,
            root_components=root_components,
            project_config=project_config,
            output_directory=output_directory,
            overwrite=overwrite,
            default_scene=default_scene,
        )
        self._project_file = self._project_directory / (
            self._project_name + ".blend"
        )

    def _rename_project_file_if_exists(self) -> None:
        if self._project_file.is_file():
            new_path = self._project_file.with_stem(
                self._project_file.stem + "_" + str(int(time.time()))
            )
            Path.rename(self._project_file, new_path)

    def _delete_project_file_if_exists(self) -> None:
        if self._project_file.is_file():
            self._project_file.unlink()

    def on_start(self) -> None:
        clear_scene()
        load_materials()

    def on_finish(self) -> None:
        deselect_all()
        if self._overwrite:
            self._delete_project_file_if_exists()
        else:
            self._rename_project_file_if_exists()
        save_state_to_blend_file(self._project_file)
