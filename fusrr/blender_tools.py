"""Useful combination of blender tools
"""

from pathlib import Path
from typing import Iterable

import bpy
import bmesh
import bpy_types
import mathutils
import numpy as np


def empty_obj(x, y, z):
    """Empty object adder (for camera tracking purposes)"""
    bpy.ops.object.empty_add(location=(x, y, z))


def add_cube(x, y, z):
    """Adds cube to scene - used in 2D key

    Args
    ----
        x (int): x coord
        y (int): y coord
        z (int): z coord
    """
    bpy.ops.mesh.primitive_cube_add(location=(x, y, z))


def add_light(x, y, z, name="Sun", remove_lights=True):
    """Adds sunlight object"""
    if remove_lights:
        bpy.ops.object.select_by_type(type="LIGHT")
        for ob in bpy.context.selected_objects:
            bpy.data.objects.remove(ob, do_unlink=True)
        bpy.ops.object.select_all(action="DESELECT")

    # Create light datablock
    light_data = bpy.data.lights.new(name="light-data", type="SUN")
    light_data.energy = 1

    # Create new object, pass the light data
    light_object = bpy.data.objects.new(name=name, object_data=light_data)
    light_object.location = (x, y, z)

    # Link object to collection in context
    bpy.data.collections["Collection"].objects.link(light_object)


def add_text(x, y, z, rad, text: str):
    """Adds text to blender scene

    Args
    ----
        x (int): x coordinate
        y (int): y coordinate
        z (int): z coordinate
        rad (int): font radius/ size
        text (str): word/ component
    """
    bpy.ops.object.text_add(radius=rad, location=(x, y, z))
    ob = bpy.context.object
    ob.data.body = text


def move_camera(x, y, z):
    """Selects and moves camera"""
    camera = bpy.data.objects["Camera"]
    camera.location = (x, y, z)


def orthographic_view():
    """Changes camera settings to an orthographic (flat) rendering view"""
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = None
    camera = bpy.data.objects["Camera"]
    bpy.context.view_layer.objects.active = camera
    bpy.context.object.data.type = "ORTHO"
    bpy.context.object.data.ortho_scale = 80


def camera_fix(camera: str, target: bpy_types.Collection, dist):
    """Fixes camera to look at target
    Parameters
    ----------
    camera : bpy.data.objects[""]  Most likely: ["Camera"]
    component : bpy.data.object[""]
    dist (int) : distance
    """
    camera = bpy.data.objects[camera]
    constraint = camera.constraints.new(type="TRACK_TO")
    constraint.target = target.objects[:][0]
    camera.location = (0, 0, dist)


def camera_frame():  # looks good for 3D, can cut off some of 2D
    """
    Frames the 3D object in the camera
    - to change angle use camera tracking + location
    """
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            ctx = bpy.context.copy()  # ctx provides right context for blender
            ctx["area"] = area  # - makes a copy of data and then throws it away
            ctx["region"] = area.regions[-1]
            bpy.ops.view3d.view_selected(ctx)  # points view
        else:
            raise Exception("Blender area is not setup for this camera frame")
    bpy.ops.view3d.camera_to_view_selected(ctx)  # points camera


def delete_cube():
    """Removes default cube if present"""
    objs = bpy.data.objects
    cube = objs.get("Cube", None)
    if cube:
        objs.remove(cube, do_unlink=True)


def save_blender_file(filepath: Path | str):
    """Save blender file"""
    filepath = Path(filepath)

    if filepath.suffix != ".blend":
        filepath = Path(f"{filepath}.blend")

    if not filepath.is_absolute():
        filepath = Path(Path.cwd() / filepath)
    bpy.ops.wm.save_as_mainfile(filepath=filepath.as_posix())


def join_obj(names: list):
    """Joins objects in list into one object
    Combined object is named as the first object in the list of names
    Parameters
    ----------
    names : list
        strings of names of objects wanted to be joined
    """
    bpy.ops.object.select_all(action="DESELECT")
    for obj_name in names:
        selected_objects = bpy.data.objects.get(str(obj_name))
        selected_objects.select_set(True)

    bpy.context.view_layer.objects.active = bpy.context.scene.objects[str(names[0])]
    bpy.ops.object.join()


def make_face_from_vertices(vertex_obj: str):
    """Makes a face from group of vertices
    Parameters
    ----------
    vertex_obj : object
        name of object where vertices are
    """
    bpy.ops.object.select_all(action="DESELECT")
    bpy.data.objects[vertex_obj].select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.edge_face_add()
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")


def faces_pf_coils(vertex_obj: str):
    """Makes a face from group of vertices
    Parameters
    ----------
    vertex_obj : object
        name of object where vertices are
    """
    bpy.ops.object.select_all(action="DESELECT")
    line_object = bpy.context.scene.objects.get(str(vertex_obj))
    if line_object is not None:
        line_object.select_set(True)
        bpy.context.view_layer.objects.active = line_object
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.edge_face_add()
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")
    else:
        print("No object selected")


def rect_blend(center_x: float, center_z: float, width: float, height: float):
    """Makes a rectangle to be plotted in blender

    Parameters
    ----------
    center_x : float
    center_z : float
    width : float
    height : float

    Returns
    -------
    centre_coords : list
        coordinates of vertices
    """
    x_coords = []
    y_coords = []
    # Gets bottom left point
    x0 = center_x
    y0 = center_z
    x_coords.append(x0)
    y_coords.append(y0)

    # Gets bottom right point
    x1 = x0 + width
    x_coords.append(x1)
    y_coords.append(y0)

    # Top right point
    y1 = y0 + height
    x_coords.append(x1)
    y_coords.append(y1)

    # Gets top left point
    x_coords.append(x0)
    y_coords.append(y1)

    centre_coords = list(zip(x_coords, y_coords))

    return centre_coords


def change_to_mesh(obj: object):
    """Changes spline object to mesh

    Parameters
    ----------
    object_names : list
        object in blender scene
    """
    bpy.ops.object.select_all(action="DESELECT")
    bpy.data.objects[obj].select_set(True)
    bpy.context.view_layer.objects.active = bpy.context.scene.objects[str(obj)]
    bpy.ops.object.convert(target="MESH")
    bpy.ops.object.select_all(action="DESELECT")


def component_outline(coords: Iterable[float], name: str = "component"):
    """Renders the spline of component

    Parameters
    ----------
    x_coords : numpy array
    y_coords : numpy array

    """
    curve = bpy.data.curves.new(name=f"{name}_curve", type="CURVE")
    curve.fill_mode = "NONE"

    ob = bpy.data.objects.new(name, object_data=curve)
    scene = bpy.context.scene
    scene.collection.objects.link(ob)
    bpy.context.view_layer.objects.active = None

    spline = curve.splines.new(type="POLY")
    spline.points.add(len(coords) - 1)
    for i, point in enumerate(spline.points):
        point.co[0:2] = coords[i]

    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)


def render_component_mesh(name):
    """Set up + builds new mesh for component

    Args
    ----
        name (str): name of mesh

    Returns
    -------
        blender information for new mesh
    """
    scene = bpy.context.scene
    bpy.context.view_layer.objects.active = None

    mesh = bpy.data.meshes.new(name)
    line_obj = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(line_obj)
    scene.view_layers.update()

    bm = bmesh.new()

    return scene, mesh, bm


def spin_extrusion():
    """Spin extrudes around y axis in blender 2Pi radians"""
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.spin(
        angle=2 * np.pi, steps=100, axis=(0.0, 1.0, 0.0)
    )  # Polodial rotation
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.shade_smooth()
    bpy.ops.object.select_all(action="DESELECT")


def half_reactor():
    """Spins radians for a cut away reactor view

    Args
    ----
        face_mesh (str): Name of object's mesh to be spun
    """
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.spin(
        angle=-4.14159, steps=100, axis=(0.0, 1.0, 0.0)
    )  # Polodial rotation
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.shade_smooth()
    bpy.ops.object.select_all(action="DESELECT")


def focal_length(camera: str, length):
    """Changes the camera focal length
        note: longer fl = smaller FOV (i.e. more zoom)

    Args
    ----
        camera (str): name of the camera
        length (int): focal length in mm
    """
    bpy.data.cameras[camera].lens = length


def hex_colour_to_rgba(hex_colour) -> tuple[float, ...]:
    """Converts hex to blender's sRGB

    Args
    ----
        hex_color (str): hex colour code

    Returns
    -------
        tuple : blender colour code
    """
    hex_colour = hex_colour.strip("#")
    srgb_red = int(hex_colour[:2], 16) / 255
    srgb_green = int(hex_colour[2:4], 16) / 255
    srgb_blue = int(hex_colour[4:6], 16) / 255
    return tuple([srgb_red, srgb_green, srgb_blue, 1.0])


def pi_rotation(set_comp: str):
    """Moves camera about a fixed point by 180 degrees

    Args
    ----
        set_comp (str): setup component i.e. Camera, Sun, Light
    """
    object = bpy.data.objects[str(set_comp)]
    looking_direction = object.location - mathutils.Vector((0.0, 0.0, 0.0))
    rot_quat = looking_direction.to_track_quat("-Z", "Z")
    object.rotation_euler = rot_quat.to_euler("XYZ")
    object.location = rot_quat @ mathutils.Vector((0.0, 0.0, 80))


def add_empty_axes(empty_name: str):
    """Aim of this function is to create an empty axes centred on the origin"""
    bpy.context.view_layer.objects.active = None
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    for obj in bpy.context.selected_objects:
        obj.name = empty_name
    bpy.context.view_layer.objects.active = None
    for obj in bpy.context.selected_objects:
        obj.select_set(False)


def array_object_rotation(object_name: str, empty_name: str, no_tf: int):
    """The aim of this function will to be able to replicate an object around an axis"""
    mod_name = "Tf_mod"
    angle_gap = 2 * np.pi / no_tf
    bpy.data.objects[object_name].select_set(True)
    bpy.context.view_layer.objects.active = bpy.context.scene.objects[object_name]
    bpy.ops.object.modifier_add(type="ARRAY")
    for obj in bpy.context.selected_objects:
        mod = obj.modifiers.get("Array")
        mod.name = mod_name
    bpy.context.object.modifiers[mod_name].count = no_tf
    bpy.context.object.modifiers[mod_name].offset_object = bpy.data.objects[empty_name]
    bpy.context.object.modifiers[mod_name].use_object_offset = True
    bpy.context.object.modifiers[mod_name].use_relative_offset = False
    bpy.data.objects[object_name].select_set(False)
    bpy.context.view_layer.objects.active = None
    bpy.data.objects[empty_name].select_set(True)
    bpy.context.view_layer.objects.active = bpy.context.scene.objects[empty_name]
    bpy.context.object.rotation_euler[1] = angle_gap


def import_gltf(filepath: str):
    """Import from gltf"""
    bpy.ops.import_scene.gltf(filepath=filepath)


def export_gltf(filepath: str):
    """Export to gltf"""
    bpy.ops.export_scene.gltf(filepath)
