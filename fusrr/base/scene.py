import time
from collections.abc import Iterable
from os import PathLike
from pathlib import Path

import bpy
import bpy_types

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

    def __init__(
        self,
        name: str,
        *,
        project_directory: PathLike | None = None,
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
        self._scene_object_names: set[str] = set()
        self._overwrite = overwrite

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

    def _delete_scene_file_if_exists(self) -> None:
        if self._project_file_name.is_file():
            self._project_file_name.unlink()

    def _check_name_in_scene(self, name: str) -> None:
        if name in self._scene_object_names:
            raise ValueError(f"Object name {name} already exists in scene")

    def _name_selected_object(self, name: str) -> None:
        bpy.context.object.name = name
        bpy.context.object.data.name = name
        self._scene_object_names.add(name)

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
        bpy.ops.wm.save_as_mainfile(
            filepath=str(self._project_file_name),
            check_existing=False,
            copy=False,
        )

    def create_collection(  # noqa: PLR6301
        self, name: str, objects: Iterable[bpy_types.Object]
    ) -> bpy_types.Collection:
        """Create a collection and adds (links) objects to it."""
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
        for obj in objects:
            for other_col in obj.users_collection:
                other_col.objects.unlink(obj)
            if obj.name not in col.objects:
                col.objects.link(obj)
        return col

    def select_objects(self, names: set[str]) -> tuple[bpy_types.Object, ...]:
        """Select objects in the scene by name."""
        self.deselect_all()
        for name in names:
            bpy.data.objects[name].select_set(True)
        return tuple(bpy.context.selected_objects)

    def select_object(self, name: str) -> bpy_types.Object:
        """Select objects in the scene by name."""
        return self.select_objects({name})[0]

    def deselect_all(self) -> None:  # noqa: PLR6301
        """Deselect all objects in the scene."""
        bpy.ops.object.select_all(action="DESELECT")

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
        constructor(self)
        # self._name_selected_object(name)

    def execute(self):
        """Execute the FusrrScene.

        This initially clears the scene, then executes the build phase,
        saving the result to a .blend file.

        Note:
            This will modify the state of the current Blender session.
        """
        self.execute_clear_scene()
        super().execute(self)
        self.deselect_all()
        self.save_scene()
