import time
from os import PathLike
from pathlib import Path

import bpy

from fusrr.base.pipeline import FusrrBuildPipeline
from fusrr.base.types import Constructor


class FusrrScene(FusrrBuildPipeline):
    """A FusrrScene represents the state of a Blender .blend file.

    It holds the names of all objects added to the scene, as well as
    methods needed to construct those objects.

    A scene is executed in two phases, first the build phase,
    second the view phase.

    All objects added using the `add_object` and `add_pipe` methods
    are constructed during the build phase

    """

    def __init__(self, name: str, project_directory: PathLike | None = None):
        """Create a FusrrScene with a name."""
        self._scene_name = name
        self._scene_object_names: set[str] = set()

        self._project_directory = (
            Path(project_directory) if project_directory else Path.cwd()
        )
        self._project_file_name = Path(
            str(self._project_directory / self._scene_name) + ".blend"
        )
        super().__init__()

        self._setup()

    def _setup(self) -> None:
        self.execute_clear_scene()

    def _rename_scene_file_if_exists(self) -> None:
        if self._project_file_name.is_file():
            new_name = (
                str(self._project_file_name.parent / self._scene_name)
                + "_"
                + str(int(time.time()))
                + ".blend"
            )
            Path.rename(
                self._project_file_name,
                new_name,
            )

    def save_scene(self) -> None:
        """Save the scene to a .blend file."""
        self._rename_scene_file_if_exists()
        bpy.ops.wm.save_as_mainfile(
            filepath=str(self._project_file_name),
            check_existing=False,
            copy=False,
        )

    def _check_name_in_scene(self, name: str) -> None:
        if name in self._scene_object_names:
            raise ValueError(f"Object name {name} already exists in scene")

    def _name_selected_object(self, name: str) -> None:
        bpy.context.object.name = name
        bpy.context.object.data.name = name
        self._scene_object_names.add(name)

    def execute_clear_scene(self):
        """Clear the scene."""
        for m in bpy.data.meshes:
            bpy.data.meshes.remove(m)
        for o in bpy.data.objects:
            bpy.data.objects.remove(o)
        for c in bpy.data.collections:
            bpy.data.collections.remove(c)
        self._scene_object_names.clear()

    def execute_construct_object(self, name: str, constructor: Constructor):
        """Construct an object in the scene."""
        self._check_name_in_scene(name)
        constructor()
        self._name_selected_object(name)

    def execute(self):
        """Execute the FusrrScene."""
        super().execute(self)
        self.save_scene()
