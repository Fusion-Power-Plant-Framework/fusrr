import time
from os import PathLike
from pathlib import Path

from fusrr.core.component import FusrrComponent
from fusrr.core.config_model import ProjectConfig, S, SceneConfig
from fusrr.core.project import FusrrProject
from fusrr.modelling.blender.data_libs.materials_lib import (
    load_materials,
)
from fusrr.modelling.blender.tools.file_tools import save_state_to_blend_file
from fusrr.modelling.blender.tools.scene_tools import (
    add_scene,
    clear_scene,
    deselect_all,
)


class BlenderProject(FusrrProject[S]):
    """A BlenderProject represents the state of a Blender .blend file.

    It holds the names of all objects added to the file, as well as
    methods needed to construct those objects.
    """

    def __init__(
        self,
        project_name: str,
        *,
        root_components: list[FusrrComponent],
        project_config: dict | PathLike | ProjectConfig[S],
        output_directory: PathLike | None = None,
        overwrite: bool = False,
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
        )
        self._project_blend_file = self.project_directory / (
            self.project_name + ".blend"
        )
        self.project_directory.mkdir(exist_ok=True)

    def _rename_project_file_if_exists(self) -> None:
        if self._project_blend_file.is_file():
            new_path = self._project_blend_file.with_stem(
                self._project_blend_file.stem + "_" + str(int(time.time()))
            )
            Path.rename(self._project_blend_file, new_path)

    def _delete_project_file_if_exists(self) -> None:
        if self._project_blend_file.is_file():
            self._project_blend_file.unlink()

    def on_start(self) -> None:
        clear_scene()
        load_materials()

    def on_finish(self) -> None:
        deselect_all()
        if self.overwrite:
            self._delete_project_file_if_exists()
        else:
            self._rename_project_file_if_exists()
        save_state_to_blend_file(self._project_blend_file)

    def on_scene_start(self, scene_config: SceneConfig[S]) -> None:
        add_scene(scene_config.name, empty=True)

    def on_scene_end(self, scene_config: SceneConfig[S]) -> None:
        # render the image of the scene
        pass
