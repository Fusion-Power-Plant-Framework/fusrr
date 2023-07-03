"""Takes input MFILE from process and uses major radius to control "test sphere"

    Returns
    -------
    png
        Image of sphere
    """

import argparse

import bpy

from extract_params import OutputParams

argParser = argparse.ArgumentParser()
argParser.add_argument("-fn", "--file_name", help=".DAT input file")
args = argParser.parse_args()


# Creating the test sphere at the centre of the space
sphere_loc = (0, 0, 0)


def get_maj_rad(file_name):
    """Gets major radius from MFILE, to use to set sphere radius and camera distance

    Parameters
    ----------
    file_name : str
        .DAT file

    Returns
    -------
    float
        Major Radius (m)
    """
    major_rad = OutputParams.from_file(str(file_name)).rmajor

    return major_rad


def test_sphere(major_rad):
    """Creates Sphere and lighting for space

    Parameters
    ----------
    major_rad : float
        Major Radius(m)
    """
    bpy.ops.object.light_add(type="SUN", location=(20, 10, 10))

    bpy.ops.mesh.primitive_ico_sphere_add(radius=major_rad, location=sphere_loc)


def move_camera(distance):
    """Selects and moves camera"""
    camera = bpy.data.objects["Camera"]
    camera.location = (2 * distance, 2 * distance, 15)

    return camera


def empty_obj():
    """Tracking empty object to make sure camera is framed correctly

    Returns
    -------
    object
        1D point object for tracking
    """
    bpy.ops.object.empty_add(location=sphere_loc)
    empty = bpy.context.active_object

    return empty


def track_obj(camera, empty):
    """Constraining camera to tracking object

    Parameters
    ----------
    camera : object
        camera
    empty : object
        1D tracking point
    """
    constraint = camera.constraints.new(type="TRACK_TO")
    constraint.target = empty


def delete_cube():
    """Goodbye default cube"""
    bpy.ops.object.select_all(action="DESELECT")
    bpy.data.objects["Cube"].select_set(True)
    bpy.ops.object.delete()


def save_image(file_name):
    """Saves render as PNG"""

    bpy.context.scene.render.filepath = f"test {file_name}"
    bpy.ops.render.render(write_still=True, use_viewport=True)


# Can be adjusted by user.

file_name = str(args.file_name)
delete_cube()
maj_rad = get_maj_rad(file_name=file_name)
test_sphere(major_rad=maj_rad)
empty = empty_obj()
camera = move_camera(maj_rad)
track_obj(camera=camera, empty=empty)
save_image(file_name=file_name)
