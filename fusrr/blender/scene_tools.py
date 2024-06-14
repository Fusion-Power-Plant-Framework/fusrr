from collections.abc import Iterable

import bpy


def check_object_in_scene(name: str) -> bool:
    """Check if an object with the given name already exists in the scene.

    Args:
        name: The name of the object to check for.
    """
    return (
        bpy.data.objects.get(name) is not None
        and bpy.data.collections.get(name) is not None
    )


def check_collection_in_scene(name: str) -> bool:
    """Check if a collection with the given name already exists in the scene.

    Args:
        name: The name of the collection to check for.
    """
    return (
        bpy.data.objects.get(name) is not None
        and bpy.data.collections.get(name) is not None
    )


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


def deselect_all() -> None:
    """Deselect all objects in the scene."""
    bpy.ops.object.select_all(action="DESELECT")


def name_selected_object(name: str) -> None:
    """Name the selected object in the scene.

    Args:
        name: The name to give the object.
    """
    bpy.context.object.name = name
    bpy.context.object.data.name = name


def create_object(name: str):
    """Create a new object in the scene.

    Args:
        name: The name of the object to create.
    """
    deselect_all()

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


def create_collection(
    name: str, objects: Iterable[bpy.types.Object]
) -> bpy.types.Collection:
    """Create a collection and adds (links) objects to it.

    Args:
        name: The name of the collection.
        objects: The objects to add to the collection.
    """
    deselect_all()

    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    for obj in objects:
        # unlink from all other collections
        for other_col in obj.users_collection:
            other_col.objects.unlink(obj)
        col.objects.link(obj)
    return col


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
    """Create a collection and adds (links) objects to it.

    Args:
        parent_col: The parent collection.
        child_col: The child collection.
    """
    old_parent = parent_collection_of(child_col)
    old_parent.children.unlink(child_col)
    parent_col.children.link(child_col)


def clear_scene():
    """Clear the scene."""
    for m in bpy.data.meshes:
        bpy.data.meshes.remove(m)
    for o in bpy.data.objects:
        bpy.data.objects.remove(o)
    for c in bpy.data.collections:
        bpy.data.collections.remove(c)


def add_scene(name: str, *, empty: bool = False):
    """Add a new scene to the blend file.

    Note:
        This will create a new scene and make it the active scene.
        When empty is False, the new scene
        will be a full copy of the current scene.

    Args:
        name: The name of the scene.
        empty: Create an empty scene. Defaults to False.
    """
    if empty:
        bpy.ops.scene.new(type="NEW")
    else:
        bpy.ops.scene.new(type="FULL_COPY")
    bpy.context.scene.name = name


def switch_to_scene(name: str):
    """Switch to a scene by name.

    Args:
        name: The name of the scene to switch to.
    """
    bpy.context.window.scene = bpy.data.scenes[name]
