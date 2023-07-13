"""Script to render 2D plasma from PROCESS Mfile data in blender

    Returns
    -------
    .gltf file
        polodial cross section of Tf coil

"""
import math

import bpy
import bmesh
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import patches
from Tf_coil_dict import arc_points

import renderingpipline.utilities.blender_tools as bt
from renderingpipline.adaptor import OutputParams

# TODO: Some imports manual need fixing!
tf_coil_shape = OutputParams.from_file(file_name="baseline_2018_MFILE.DAT")
rtangle = np.pi / 2
i_tf_sup = int(1)
tfcth = tf_coil_shape.tfcth


def tf_coil_outline(coords):
    """Renders the spline of the tf coil

    Parameters
    ----------
    x_coords : numpy array
    y_coords : numpy array

    """
    curve = bpy.data.curves.new(name="Curve_test", type="CURVE")
    curve.fill_mode = "NONE"

    ob = bpy.data.objects.new(name="TestObject", object_data=curve)
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

    return None


def ellips_fill(a1=0, a2=0, b1=0, b2=0, x0=0, y0=0, ang1=0, ang2=rtangle):
    """Fills the space between two concentric ellipse sectors.

    Arguments

    axis: plot object
    a1, a2, b1, b2 horizontal and vertical radii to be filled
    x0, y0 coordinates of centre of the ellipses
    ang1, ang2 are the polar angles of the start and end

    """
    angs = np.linspace(ang1, ang2, endpoint=True)
    r1 = ((np.cos(angs) / a1) ** 2 + (np.sin(angs) / b1) ** 2) ** (-0.5)
    xs1 = r1 * np.cos(angs) + x0
    ys1 = r1 * np.sin(angs) + y0
    angs = np.linspace(ang2, ang1, endpoint=True)
    r2 = ((np.cos(angs) / a2) ** 2 + (np.sin(angs) / b2) ** 2) ** (-0.5)
    xs2 = r2 * np.cos(angs) + x0
    ys2 = r2 * np.sin(angs) + y0
    verts = list(zip(xs1, ys1))
    verts.extend(list(zip(xs2, ys2)))
    endpoint = verts[-1:]
    verts.extend(endpoint)

    return verts


def plot_tf_coils(tf_coil_shape):
    """Function to plot TF coils

    Arguments:
        axis --> axis object to plot to
        mfile_data --> MFILE.DAT object
        scan --> scan number to use

    """
    # Arc points
    # MDK Only 4 points now required for elliptical arcs
    x1 = tf_coil_shape.x1
    y1 = tf_coil_shape.y1
    x2 = tf_coil_shape.x2
    y2 = tf_coil_shape.y2
    x3 = tf_coil_shape.x3
    y3 = tf_coil_shape.y3
    x4 = tf_coil_shape.x4
    y4 = tf_coil_shape.y4
    x5 = tf_coil_shape.x5
    y5 = tf_coil_shape.y5
    if y3 != 0:
        print("TF coil geometry: The value of yarc(3) is not zero, but should be.")

    x0 = x2
    y0 = y1
    a1 = x2 - x1
    b1 = y2 - y1
    a2 = a1 + tfcth
    b2 = b1 + tfcth
    verts = ellips_fill(
        a1=a1,
        a2=a2,
        b1=b1,
        b2=b2,
        x0=x0,
        y0=y0,
        ang1=rtangle,
        ang2=2 * rtangle,
    )
    tf_coil_outline(verts)
    # Outboard upper arc
    x0 = x2
    y0 = 0
    a1 = x3 - x2
    b1 = y2
    a2 = a1 + tfcth
    b2 = b1 + tfcth
    verts = ellips_fill(a1=a1, a2=a2, b1=b1, b2=b2, x0=x0, y0=y0, ang1=0, ang2=rtangle)
    tf_coil_outline(verts)
    # Inboard lower arc
    x0 = x4
    y0 = y5
    a1 = x4 - x5
    b1 = y5 - y4
    a2 = a1 + tfcth
    b2 = b1 + tfcth
    verts = ellips_fill(
        a1=a1, a2=a2, b1=b1, b2=b2, x0=x0, y0=y0, ang1=-rtangle, ang2=-2 * rtangle
    )
    tf_coil_outline(verts)
    # Outboard lower arc
    x0 = x4
    y0 = 0
    a1 = x3 - x2
    b1 = -y4
    a2 = a1 + tfcth
    b2 = b1 + tfcth
    verts = ellips_fill(a1=a1, a2=a2, b1=b1, b2=b2, x0=x0, y0=y0, ang1=0, ang2=-rtangle)
    tf_coil_outline(verts)
    # Vertical leg
    # Bottom left corner
    rect = patches.Rectangle([x5 - tfcth, y5], tfcth, (y1 - y5), lw=0, facecolor="cyan")
    centre_coords = bt.rect_blend(rect)
    tf_coil_outline(centre_coords)


plot_tf_coils(tf_coil_shape=tf_coil_shape)


# Rendering the outer and inner surface of the plasma

# TODO: Naming to be automated
object_list = [
    "TestObject",
    "TestObject.001",
    "TestObject.002",
    "TestObject.003",
    "TestObject.004",
]

bt.change_to_mesh(object_names=object_list)
for i in object_list:
    bt.make_face_from_vertices(str(i))


bt.delete_cube()

# Creating tracking object and lock camera
# bt.empty_obj(10, 5, 0)
# camera = bt.move_camera(10, 5, 40)
# bt.camera_fix(camera="Camera", target="Empty")

# bt.save_image("tf_coil")


# Save the Blender scene as a .blend file
# blend_file_path = "/home/miles/Downloads/test"
# bpy.ops.wm.save_as_mainfile(filepath=blend_file_path)
# bpy.ops.export_scene.gltf(filepath=blend_file_path)
