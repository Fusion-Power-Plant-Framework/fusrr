from enum import Enum
from pathlib import Path

import bpy


class BlenderFileDataTypes(Enum):
    """Data types that can be saved/read to/from a .blend file."""

    BRUSH = "Brush"
    IMAGE = "Image"
    MATERIAL = "Material"
    MESH = "Mesh"
    OBJECT = "Object"
    PALETTE = "Palette"
    SCENE = "Scene"
    TEXTURE = "Texture"
    WORLD = "World"

    def access_from_bpy_lib(self, bpy_lib):
        """Access the data type from the bpy library."""
        plural_suffix = "s"
        if (
            self is BlenderFileDataTypes.MESH
            or self is BlenderFileDataTypes.BRUSH
        ):
            plural_suffix = "es"
        return getattr(bpy_lib, self.value.lower() + plural_suffix)


def save_state_to_blend_file(path: Path) -> None:
    """Save the bpy scene state to a .blend file.

    Args:
        path: The path to save the scene to.
    """
    bpy.ops.wm.save_as_mainfile(
        filepath=path.as_posix(),
        check_existing=False,
        copy=False,
    )


def append_from_blend_file(
    path: Path,
    data_type: BlenderFileDataTypes,
):
    """Load materials from the materials library."""
    files = []
    with bpy.data.libraries.load(path.as_posix()) as (data_from, _data_to):
        files = [
            {"name": data_name}
            for data_name in data_type.access_from_bpy_lib(data_from)
        ]
    dt_dir = (path / data_type.value).as_posix()
    bpy.ops.wm.append(directory=dt_dir, files=files)
