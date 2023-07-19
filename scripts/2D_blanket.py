"""
WIP plots blanket in 2D blender view
!!! NOT WORKING AT THE MOMENT !!!

Returns
-------
Blanket shape blend file

"""
from dataclasses import asdict

import bpy
import numpy as np

import renderingpipline.utilities.blender_tools as bt
from renderingpipline.adaptor import OutputParams
from renderingpipline.utilities.process_build_tools import (
    RADIAL_BUILD,
    vertical_lower,
    vertical_upper,
)

blanket_shape = OutputParams.from_file(file_name="baseline_2018_MFILE.DAT")

blanket_shape_dict = {k: str(v) for k, v in asdict(blanket_shape).items()}


def cumul_setup(blanket_shape_dict):
    """Sets up each part of the blanket

    Parameters
    ----------
    blanket_shape_dict : dictionary
        dictionary of dataclass

    Returns
    -------
    Two dictionaries
        Upper and lower builds of blanket
    """
    upper = dict()
    cumulative_upper = dict()
    subtotal = 0
    for item in vertical_upper:
        upper[item] = blanket_shape_dict[item]
        subtotal += float(upper[item])
        cumulative_upper[item] = subtotal

    lower = dict()
    cumulative_lower = dict()
    subtotal = 0
    for item in vertical_lower:
        lower[item] = blanket_shape_dict[item]
        subtotal -= float(lower[item])
        cumulative_lower[item] = subtotal

    return cumulative_upper, cumulative_lower


cumulative_upper, cumulative_lower = cumul_setup(blanket_shape_dict=blanket_shape_dict)


def plotdh(r0, a, delta, kap):
    """Plots half a thin D-section, centred on z = 0.

    Arguments:
    ----------
        axis --> axis object to plot to
        r0 --> major radius of centre
        a --> horizontal radius
        delta --> triangularity
        kap --> elongation

    Returns:
    --------
        rs --> radial coordinates of D-section
        zs --> vertical coordinates of D-section
    """
    angs = np.linspace(0, np.pi, 50, endpoint=True)
    rs = r0 + a * np.cos(angs + delta * np.sin(1.0 * angs))
    zs = kap * a * np.sin(angs)
    return rs, zs


def plotdhgap(inpt, outpt, inthk, outthk, toppt, topthk, delta):
    """Plots half a thick D-section with a gap.

    Arguments:
    ----------
        axis --> axis object to plot to
        inpt --> inner points
        outpt --> outer points
        inthk --> inner thickness
        outthk --> outer thickness
        toppt --> top points
        topthk --> top thickness
        delta --> triangularity
        col --> color for fill

    """
    arc = np.pi / 4.0
    r01 = (inpt + outpt) / 2.0
    r02 = (inpt + inthk + outpt - outthk) / 2.0
    a1 = r01 - inpt
    a2 = r02 - inpt - inthk
    kap1 = toppt / a1
    kap2 = (toppt - topthk) / a2
    # angs = ((np.pi/2.) - arc/2.) * findgen(50)/49.
    angs = np.linspace(0.0, (np.pi / 2.0) - arc / 2.0, 50, endpoint=True)
    rs1 = r01 + a1 * np.cos(angs + delta * np.sin(angs))
    zs1 = kap1 * a1 * np.sin(angs)
    rs2 = r02 + a2 * np.cos(angs + delta * np.sin(angs))
    zs2 = kap2 * a2 * np.sin(angs)
    # angs = !pi + ((!pi/2.) - arc) * findgen(50)/49.
    angs = np.linspace(np.pi, np.pi + ((np.pi / 2.0) - arc), 50, endpoint=True)
    rs3 = r01 + a1 * np.cos(angs + delta * np.sin(angs))
    zs3 = kap1 * a1 * np.sin(angs)
    rs4 = r02 + a2 * np.cos(angs + delta * np.sin(angs))
    zs4 = kap2 * a2 * np.sin(angs)

    return rs1, rs2, rs3, rs4, zs1, zs2, zs3, zs4

    """ axis.plot(
        np.concatenate([rs1, rs2[::-1]]),
        np.concatenate([zs1, zs2[::-1]]),
        color="black",
        lw=thin,
    )
    axis.plot(
        np.concatenate([rs3, rs4[::-1]]),
        -np.concatenate([zs3, zs4[::-1]]),
        color="black",
        lw=thin,
    )
    axis.fill(
        np.concatenate([rs1, rs2[::-1]]), np.concatenate([zs1, zs2[::-1]]), color=col
    )
    axis.fill(
        np.concatenate([rs3, rs4[::-1]]), -np.concatenate([zs3, zs4[::-1]]), color=col
    ) """


def plot_blanket(blanket_shape, cumulative_upper, cumulative_lower):
    """Function to plot blanket

    Arguments:
    ----------

      axis --> axis object to plot to
      mfile_data --> MFILE.DAT object
      scan --> scan number to use

    """
    point_array = ()
    triang = blanket_shape.triang
    blnkith = blanket_shape.blnkith
    blnkoth = blanket_shape.blnkoth

    # Single null: Draw top half from output
    # Double null: Reflect bottom half to top
    i_single_null = blanket_shape.i_single_null
    if i_single_null == 1:
        # Upper blanket: outer surface
        radx = (
            cumulative_radial_build("blnkoth", blanket_shape)
            + cumulative_radial_build("vvblgapi", blanket_shape)
        ) / 2.0
        rminx = (
            cumulative_radial_build("blnkoth", blanket_shape)
            - cumulative_radial_build("vvblgapi", blanket_shape)
        ) / 2.0

        kapx = cumulative_upper["blnktth"] / rminx
        (isrs, iszs) = plotdh(radx, rminx, triang, kapx)
        point_array = point_array + ((isrs, iszs))

        # Upper blanket: inner surface
        radx = (
            cumulative_radial_build("fwoth", blanket_shape)
            + cumulative_radial_build("blnkith", blanket_shape)
        ) / 2.0
        rminx = (
            cumulative_radial_build("fwoth", blanket_shape)
            - cumulative_radial_build("blnkith", blanket_shape)
        ) / 2.0

        kapx = cumulative_upper["fwtth"] / rminx
        (osrs, oszs) = plotdh(radx, rminx, triang, kapx)
        point_array = point_array + ((osrs, oszs))

        # Plot upper blanket
        rs = np.concatenate([point_array[0], point_array[2][::-1]])
        zs = np.concatenate([point_array[1], point_array[3][::-1]])

    # Lower blanket
    blnktth = blanket_shape.blnktth
    c_shldith = cumulative_radial_build("shldith", blanket_shape)
    c_blnkoth = cumulative_radial_build("blnkoth", blanket_shape)
    divgap = cumulative_lower["divfix"]
    rs1, rs2, rs3, rs4, zs1, zs2, zs3, zs4 = plotdhgap(
        c_shldith, c_blnkoth, blnkith, blnkoth, divgap, -blnktth, triang
    )

    return rs1, rs2, rs3, rs4, zs1, zs2, zs3, zs4, isrs, iszs, osrs, oszs, rs, zs


def cumulative_radial_build(section, blanket_shape):
    """Function for calculating the cumulative radial build up to and
    including the given section.

    Arguments:
    ----------

        section --> section of the radial build to go up to
        mfile_data --> MFILE data object
        scan --> scan number to use

    Returns:
    --------
        cumulative_build --> cumulative radial build up to section given

    """
    complete = False
    cumulative_build = 0
    for item in RADIAL_BUILD:
        if item == "rminori" or item == "rminoro":
            cumulative_build += blanket_shape.rminor
        elif item == "vvblgapi" or item == "vvblgapo":
            cumulative_build += blanket_shape.vvblgap
        elif "d_vv_in" in item:
            cumulative_build += blanket_shape.d_vv_in
        elif "d_vv_out" in item:
            cumulative_build += blanket_shape.d_vv_outc_shldith

        if item == section:
            complete = True
            break

    if complete is False:
        print("radial build parameter ", section, " not found")
    return cumulative_build


#        else:
#            cumulative_build += mfile_data.data[item].get_scan(scan)

rs1, rs2, rs3, rs4, zs1, zs2, zs3, zs4, osrs, oszs, isrs, iszs, rs, zs = plot_blanket(
    blanket_shape=blanket_shape,
    cumulative_lower=cumulative_lower,
    cumulative_upper=cumulative_upper,
)


verts = list(zip(rs1, zs1))
added = list(zip(rs2[::-1], zs2[::-1]))
verts.extend(added)

verts2 = list(zip(rs3, zs3))
added = list(zip(rs4[::-1], zs4[::-1]))
verts2.extend(added)

verts3 = list(zip(osrs, oszs))
verts4 = list(zip(isrs, iszs))

verts5 = list(zip(rs, zs))


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


tf_coil_outline(verts)
# tf_coil_outline(verts2)
# tf_coil_outline(verts3)
# tf_coil_outline(verts4)
# tf_coil_outline(verts5)
bt.delete_cube()

# Save the Blender scene as a .blend file
# blend_file_path = "/home/miles/Downloads/test"
# bpy.ops.wm.save_as_mainfile(filepath=blend_file_path)
# bpy.ops.export_scene.gltf(filepath=blend_file_path)
