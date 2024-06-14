import time
from pathlib import Path

from fusrr.base.entity.entity import FusrrSceneEntity
from fusrr.base.errors import SceneStopError
from fusrr.base.pipeline import FusrrBuildPipeline, FusrrViewPipeline
from fusrr.base.scene import FusrrScene
from fusrr.base.utils import load_fusrr_config
from fusrr.blender.file_tools import save_state_to_blend_file
from fusrr.blender.scene_tools import clear_scene, deselect_all
from fusrr.data_libs.materials import load_materials


class FusrrProject:
    """A FusrrProject represents the state of a Blender .blend file.

    It holds the names of all objects added to the file, as well as
    methods needed to construct those objects.

    The execution of a project split into two phases:
      1. A build phase,
      2. A view phase.
    """

    def __init__(
        self,
        project_name: str,
        *,
        project_directory: Path | str | None = None,
        config_path: Path | str | None = None,
        overwrite: bool = False,
    ):
        """Create a FusrrScene with a name.

        Args:
            project_name:
                The name of the Fusrr project.
            project_directory:
                The directory to save the scene to.
                Defaults to the current working directory `Path.cwd()`.
            config_path:
                The path to the project configuration file.
            overwrite:
                Whether to overwrite the .blend file when saving,
                if it already exists.
        """
        self._project_name = project_name
        self._project_directory = (
            Path(project_directory) if project_directory else Path.cwd()
        )
        self._project_path = self._project_directory / (
            self._project_name + ".blend"
        )

        self._config_path = Path(config_path) if config_path else None
        self._config = (
            load_fusrr_config(self._config_path) if self._config_path else None
        )

        self._overwrite = overwrite

        self._build_pipeline = FusrrBuildPipeline()
        self._view_pipeline = FusrrViewPipeline()

    @property
    def project_name(self) -> str:
        """The name of the project."""
        return self._project_name

    @property
    def project_directory(self) -> Path:
        """The directory of the project."""
        return self._project_directory

    def _reset(self) -> None:
        clear_scene()

    def _rename_project_file_if_exists(self) -> None:
        if self._project_path.is_file():
            new_path = self._project_path.with_stem(
                self._project_path.stem + "_" + str(int(time.time()))
            )
            Path.rename(self._project_path, new_path)

    def _delete_project_file_if_exists(self) -> None:
        if self._project_path.is_file():
            self._project_path.unlink()

    def add_entity(self, *ent: FusrrSceneEntity):
        """Add an entity(ies) to the project."""
        for e in ent:
            self._build_pipeline.add(e)

    def add_scene(self, *scene: FusrrScene):
        """Add an entity(ies) to the project."""
        for s in scene:
            self._view_pipeline.add(s)

    def save(self) -> None:
        """Save the project to a .blend file.

        The file name is `self.project_name` with a .blend extension.
        The directory is `self.project_directory`.

        Note:
            This will rename the file if it exists, otherwise it will
            overwrite it if `self._overwrite` is `True`.
        """
        if self._overwrite:
            self._delete_project_file_if_exists()
        else:
            self._rename_project_file_if_exists()
        save_state_to_blend_file(self._project_path)

    def run(self):
        """Runs the project.

        This is the main blocking call that runs the project.

        This happens in two phases, the prepare phase and the view phase.

        During the prepare phase, the `prepare()` method for every object added
        is called. This is where any calculations or setup are done.

        During the view phase, each s...

        This initially clears the scene, then executes the build phase,
        saving the result to a .blend file.

        Note:
            This will modify the state of the current Blender session.
        """
        self._build_pipeline.prepare()

        completed_successfully = False
        try:
            self._reset()
            load_materials()
            self._build_pipeline.execute()
        except SceneStopError as e:
            print(f"Stopping scene on: {e}")
        else:
            completed_successfully = True
        finally:
            deselect_all()
            print("saving scene...")
            if not completed_successfully:
                print("Errors occurred during the run.")
            self.save()
