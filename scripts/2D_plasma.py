"""Script to render 2D plasma from PROCESS Mfile data in blender

    Returns
    -------
    png
        image of 2D plasma

"""
import math

import bpy
import bmesh
import matplotlib.pyplot as plt
import numpy as np
from plasma_shape_params import PlasmaShapeParams

import renderingpipline.utilities.blender_tools as bt
from renderingpipline.adaptor import OutputParams

plasma_shape = OutputParams.from_file("baseline_2018_MFILE.DAT")


def plot_plasma(plasma_shape):
    """Plots the plasma boundary arcs.

    Arguments:
        axis --> axis object to plot to
    """

    r0 = plasma_shape.rmajor
    a = plasma_shape.rminor
    delta = 1.5 * plasma_shape.delta_95
    kappa = (1.1 * plasma_shape.kappa95) + 0.04
    i_single_null = plasma_shape.i_single_null

    x1 = (2.0 * r0 * (1.0 + delta) - a * (delta**2 + kappa**2 - 1.0)) / (
        2.0 * (1.0 + delta)
    )
    x2 = (2.0 * r0 * (delta - 1.0) - a * (delta**2 + kappa**2 - 1.0)) / (
        2.0 * (delta - 1.0)
    )
    r1 = 0.5 * math.sqrt(
        (a**2 * ((delta + 1.0) ** 2 + kappa**2) ** 2) / ((delta + 1.0) ** 2)
    )
    r2 = 0.5 * math.sqrt(
        (a**2 * ((delta - 1.0) ** 2 + kappa**2) ** 2) / ((delta - 1.0) ** 2)
    )
    theta1 = np.arcsin((kappa * a) / r1)
    theta2 = np.arcsin((kappa * a) / r2)
    inang = 1.0 / r1
    outang = 1.5 / r2
    if i_single_null == 0:
        angs1 = np.linspace(
            -(inang + theta1) + np.pi, (inang + theta1) + np.pi, 256, endpoint=True
        )
        angs2 = np.linspace(-(outang + theta2), (outang + theta2), 256, endpoint=True)
    elif i_single_null < 0:
        angs1 = np.linspace(
            -(inang + theta1) + np.pi, theta1 + np.pi, 256, endpoint=True
        )
        angs2 = np.linspace(-theta2, (outang + theta2), 256, endpoint=True)
    else:
        angs1 = np.linspace(
            -theta1 + np.pi, (inang + theta1) + np.pi, 256, endpoint=True
        )
        angs2 = np.linspace(-(outang + theta2), theta2, 256, endpoint=True)

    xs1 = -(r1 * np.cos(angs1) - x1)
    ys1 = r1 * np.sin(angs1)
    xs2 = -(r2 * np.cos(angs2) - x2)
    ys2 = r2 * np.sin(angs2)

    return xs1, xs2, ys1, ys2


def plasma_render(x_coords, y_coords):
    """Renders the vertices of the plasma array

    Parameters
    ----------
    x_coords : numpy array
    y_coords : numpy array

    """
    scene = bpy.context.scene
    bpy.context.view_layer.objects.active = None

    mesh = bpy.data.meshes.new("line_mesh")
    line_obj = bpy.data.objects.new("line_object", mesh)
    scene.collection.objects.link(line_obj)
    scene.view_layers.update()

    bm = bmesh.new()

    for x, y in zip(x_coords, y_coords):
        bm.verts.new((x, y, 0))

    bm.to_mesh(mesh)
    bm.free()

    scene.view_layers.update()

    return None


xs1, xs2, ys1, ys2 = plot_plasma(plasma_shape=plasma_shape)

# Finding the centre point to frame camera
half_arr = int(len(xs1) / 2)
half_x = xs1[half_arr] - xs2[half_arr]
half_y = ys1[half_arr] - ys2[half_arr]

# Rendering the outer and inner surface of the plasma
plasma_render(xs1, ys1)
plasma_render(xs2, ys2)

object_list = ["line_object", "line_object.001"]

bt.join_obj(object_list)
bt.make_face_from_vertices("line_object")
bt.delete_cube()

# Creating tracking object and lock camera
bt.empty_obj(half_x, half_y, 0)
camera = bt.move_camera(half_x, half_y, 40)
bt.camera_fix(camera="Camera", target="Empty")

# bt.save_image("Plasma")

# Save the Blender scene as a .gltf file
# blend_file_path = "ex/file/path"
# bpy.ops.export_scene.gltf(filepath = blend_file_path)
