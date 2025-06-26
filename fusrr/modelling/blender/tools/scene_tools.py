import re
from collections.abc import Iterable
from os import PathLike
from pathlib import Path
from typing import Literal

import bpy

from fusrr.core.vectors import Vec3


def check_object_in_scene(name: str) -> bool:
    """Check if an object with the given name already exists in the scene.

    Args:
        name: The name of the object to check for.
    """
    return bpy.data.objects.get(name) is not None


def check_collection_in_scene(name: str) -> bool:
    """Check if a collection with the given name already exists in the scene.

    Args:
        name: The name of the collection to check for.
    """
    return bpy.data.collections.get(name) is not None


def select_objects(names: set[str]) -> tuple[bpy.types.Object, ...]:
    """Select objects in the scene by name.

    Args:
        names: The names of the objects to select.
    """
    deselect_all()
    for name in names:
        obj = get_object_f(name)
        obj.select_set(True)
    return tuple(bpy.context.selected_objects)


def select_object(name: str) -> bpy.types.Object:
    """Select a single object in the scene by name.

    Args:
        name: The name of the object to select.
    """
    return select_objects({name})[0]


def select_and_activate_object(name: str) -> bpy.types.Object:
    """Select a single object in the scene by name
    and make it the active object.

    Args:
        name: The name of the object to select and activate.
    """
    obj = select_object(name)
    bpy.context.view_layer.objects.active = obj
    return obj


def select_all():
    """Select all objects in the scene."""
    return bpy.ops.object.select_all(action="SELECT")


def deselect_all():
    """Deselect all objects in the scene."""
    return bpy.ops.object.select_all(action="DESELECT")


def name_selected_object(name: str) -> None:
    """Name the selected object in the scene.

    Args:
        name: The name to give the object.
    """
    if bpy.context.object is None or bpy.context.object.data is None:
        raise ValueError("No object is selected.")
    bpy.context.object.name = name
    bpy.context.object.data.name = name


def create_object(
    name: str, *, mesh: bpy.types.Mesh | None = None
) -> bpy.types.Object:
    """Create a new object in the scene.

    Args:
        name: The name of the object to create.
        mesh: The mesh to use for the object. If None, a new mesh will be created.
    """
    deselect_all()

    if mesh is None:
        mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def get_object(name: str) -> bpy.types.Object | None:
    """Get an object by name.

    Args:
        name: The name of the object to get.
    """
    return bpy.data.objects.get(name)


def get_object_f(name: str) -> bpy.types.Object:
    """Get an object by name.

    Raises:
        ValueError: If the object is not found.

    Args:
        name: The name of the object to get.
    """
    o = get_object(name)
    if o is None:
        raise ValueError(f"Object with name {name} not found.")
    return o


def get_objects(names: set[str]) -> list[bpy.types.Object]:
    """Get objects by name.

    Args:
        names: The names of the objects to get.
    """
    rtn = []
    for name in names:
        obj = get_object(name)
        if obj is not None:
            rtn.append(obj)
    return rtn


def get_objects_by_pattern(pattern: str) -> list[bpy.types.Object]:
    """Get all objects whose name matches the given pattern.

    Args:
        pattern: The regular expression pattern to match.

    Returns:
        A list of matching objects.
    """
    return [obj for obj in bpy.data.objects if re.match(pattern, obj.name)]


def get_object_by_pattern(pattern: str) -> bpy.types.Object | None:
    """Get a single object whose name matches the given pattern.

    Args:
        pattern: The regular expression pattern to match.

    Returns:
        The first matching object, or None if no match is found.
    """
    matches = get_objects_by_pattern(pattern)
    if not matches:
        return None
    if len(matches) > 1:
        raise ValueError(f"Multiple objects match the pattern: {pattern}")
    return matches[0]


def get_object_by_pattern_f(pattern: str) -> bpy.types.Object:
    """Get a single object whose name matches the given pattern.

    Raises:
        ValueError: If no object is found or if multiple objects match the pattern.

    Args:
        pattern: The regular expression pattern to match.
    """
    obj = get_object_by_pattern(pattern)
    if obj is None:
        raise ValueError(f"No object matches the pattern: {pattern}")
    return obj


def get_collection(name: str) -> bpy.types.Collection | None:
    """Get a collection by name.

    Args:
        name: The name of the collection to get.
    """
    return bpy.data.collections.get(name)


def get_collection_f(name: str) -> bpy.types.Collection:
    """Get a collection by name.

    Raises:
        ValueError: If the collection is not found.

    Args:
        name: The name of the collection to get.
    """
    c = get_collection(name)
    if c is None:
        raise ValueError(f"Collection with name {name} not found.")
    return c


def get_collections(names: set[str]) -> tuple[bpy.types.Collection, ...]:
    """Select objects in the scene by name.

    Args:
        names: The names of the collections to get.
    """
    cols = []
    for name in names:
        col = get_collection_f(name)
        cols.append(col)
    return tuple(cols)


def create_collection(name: str) -> bpy.types.Collection:
    """Create a collection and adds (links) objects to it.

    Args:
        name: The name of the collection.
        objects: The objects to add to the collection.
    """
    deselect_all()

    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col


def select_collection_objects(col: bpy.types.Collection):
    """Select all objects in a collection."""
    for obj in col.objects:
        obj.select_set(True)


def select_collection_all_objects(col_name: str):
    """Select all objects in a collection and make the first one active."""
    col = get_collection_f(col_name)
    for obj in col.all_objects:
        obj.select_set(True)


def link_objects_to_collection(
    col: bpy.types.Collection,
    objects: Iterable[bpy.types.Object],
):
    """Link objects to a collection.

    Args:
        col: The collection to link the objects to.
        objects: The objects to link to the collection.
    """
    for obj in objects:
        # unlink from all other collections
        for other_col in obj.users_collection:
            other_col.objects.unlink(obj)
        col.objects.link(obj)


def parent_collection_of(
    child_coll: bpy.types.Collection,
) -> bpy.types.Collection:
    """Get the parent collection of a collection.

    Args:
        child_coll: The child collection to get the parent of.
    """
    all_collections = bpy.data.collections
    for c in all_collections:
        if child_coll.name in c.children:
            return c
    return bpy.context.scene.collection


def link_collections(
    parent_col: bpy.types.Collection,
    child_col: bpy.types.Collection,
):
    """Adds (links) child_col to parent_col.

    Args:
        parent_col: The parent collection.
        child_col: The child collection.
    """
    old_parent = parent_collection_of(child_col)
    old_parent.children.unlink(child_col)
    parent_col.children.link(child_col)


def remove_collection_if_exists(name: str):
    """Remove a collection by name.

    Args:
        name: The name of the collection to remove.
    """
    col = get_collection(name)
    if col is not None:
        remove_collection(col)


def remove_collection(col: bpy.types.Collection):
    """Remove a collection from the scene.

    Args:
        col: The collection to remove.
    """
    bpy.data.collections.remove(col)


def remove_object_if_exists(name: str):
    """Remove an object by name.

    Args:
        name: The name of the object to remove.
    """
    obj = get_object(name)
    if obj is not None:
        remove_object(obj)


def remove_object(obj: bpy.types.Object):
    """Remove an object from the scene.

    Args:
        obj: The object to remove.
    """
    bpy.data.objects.remove(obj)


def clear_scene():
    """Clear the scene."""
    for m in bpy.data.meshes:
        bpy.data.meshes.remove(m)
    for o in bpy.data.objects:
        bpy.data.objects.remove(o)
    for c in bpy.data.collections:
        bpy.data.collections.remove(c)


def add_scene(name: str, *, empty: bool = False, linked_copy: bool = False):
    """Add a new scene to the blend file.

    Note:
        This will create a new scene and make it the active scene.
        When empty is False, the new scene
        will be a full copy of the current scene.

    Args:
        name:
            The name of the scene.
        empty:
            Create an empty scene. Defaults to False.
        linked_copy:
            Create a linked copy of the current scene.
            Defaults to False.

    """
    if empty:
        bpy.ops.scene.new(type="EMPTY")
    elif linked_copy:
        bpy.ops.scene.new(type="LINK_COPY")
    else:
        bpy.ops.scene.new(type="FULL_COPY")
    # renames the new (now context) scene
    bpy.context.scene.name = name


def switch_to_scene(name: str):
    """Switch to a scene by name.

    Args:
        name: The name of the scene to switch to.
    """
    bpy.context.window.scene = bpy.data.scenes[name]


def import_gltf(
    gltf_path: Path | str,
    *,
    objs_name_prefix: str | None = None,
    scale: Vec3 | None = None,
) -> None:
    """Imports gltf file"""
    deselect_all()
    bpy.ops.import_scene.gltf(filepath=Path(gltf_path).resolve().as_posix())
    if scale is not None:
        bpy.ops.transform.resize(
            value=scale.tup,
            orient_type="GLOBAL",
            orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            orient_matrix_type="GLOBAL",
        )
    if objs_name_prefix is not None:
        for obj in bpy.context.selected_objects:
            obj.name = f"{objs_name_prefix}.{obj.name}"
    deselect_all()


def render_scene(
    scene_name: str,
    output_path: PathLike | str,
    *,
    res: tuple[int, int] = (1920, 1080),
    file_format: Literal[
        "BMP",  # BMP.Output image in bitmap format.
        "IRIS",  # Iris.Output image in SGI IRIS format.
        "PNG",  # PNG.Output image in PNG format.
        "JPEG",  # JPEG.Output image in JPEG format.
        "JPEG2000",  # JPEG 2000.Output image in JPEG 2000 format.
        "TARGA",  # Targa.Output image in Targa format.
        "TARGA_RAW",  # Targa Raw.Output image in uncompressed Targa format.
        "CINEON",  # Cineon.Output image in Cineon format.
        "DPX",  # DPX.Output image in DPX format.
        "OPEN_EXR_MULTILAYER",  # OpenEXR MultiLayer.Output image in multilayer OpenEXR format.
        "OPEN_EXR",  # OpenEXR.Output image in OpenEXR format.
        "HDR",  # Radiance HDR.Output image in Radiance HDR format.
        "TIFF",  # TIFF.Output image in TIFF format.
        "WEBP",  # WebP.Output image in WebP format.
        "FFMPEG",  # FFmpeg Video.
    ] = "JPEG",
    engine: Literal[
        "BLENDER_EEVEE_NEXT", "BLENDER_WORKBENCH", "CYCLES"
    ] = "BLENDER_EEVEE_NEXT",
    samples: int = 10,
):
    """Render the current scene to an image file.

    Args:
        output_path: The path to save the rendered image.
        scene_name: The name of the scene to render. Defaults to "RenderScene".
    """
    if not bpy.context.scene.camera:
        print("Attempting to render with no camera set in the scene.")
        return

    bpy.context.scene.render.filepath = (
        Path(output_path / Path(scene_name)).resolve().as_posix()
    )
    bpy.context.scene.render.resolution_x = res[0]
    bpy.context.scene.render.resolution_y = res[1]
    bpy.context.scene.render.image_settings.file_format = file_format

    bpy.context.scene.render.engine = engine  # type: ignore
    bpy.context.scene.cycles.samples = samples
    bpy.context.scene.cycles.preview_samples = samples
    bpy.context.scene.eevee.taa_samples = samples
    bpy.context.scene.eevee.taa_render_samples = samples

    bpy.ops.render.render("INVOKE_DEFAULT", write_still=True)
