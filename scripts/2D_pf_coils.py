"""
Plots polodial cross section of PF coils in blender

Returns
-------
blend file of pf coils
"""

from dataclasses import asdict

import bpy
import bmesh
from matplotlib import patches

import renderingpipline.utilities.blender_tools as bt
from renderingpipline.adaptor import OutputParams

pf_coil_shape = OutputParams.from_file("baseline_2018_MFILE.DAT")
pf_coil_shape_dict = {k: str(v) for k, v in asdict(pf_coil_shape).items()}


def plasma_render(x_coords, y_coords):
    """Renders the vertices of the plasma array

    Parameters
    ----------
    x_coords : numpy array
    y_coords : numpy array

    """
    bpy.ops.object.select_all(action="DESELECT")
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

    return mesh


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


def plot_pf_coils(pf_coil_shape_dict):
    """Plots pf coils

    Parameters
    ----------
    pf_coil_shape_dict : dictionary
    """
    coils_r = []
    coils_z = []
    coils_dr = []
    coils_dz = []
    coil_text = []

    # Number of coils (1 is OH coil)
    number_of_coils = 0
    for key in pf_coil_shape_dict.keys():
        if "rpf" in key:
            number_of_coils += 1

    bore = float(pf_coil_shape_dict["bore"])
    ohcth = float(pf_coil_shape_dict["ohcth"])
    ohdz = float(pf_coil_shape_dict["ohdz"])

    # Check for Central Solenoid
    if "iohcl" in pf_coil_shape_dict:
        iohcl = pf_coil_shape_dict["iohcl"]
    else:
        iohcl = 1

    # If Central Solenoid present, ignore last entry in for loop
    # The last entry will be the OH coil in this case
    if iohcl == 0:
        noc = number_of_coils + 1
    else:
        noc = number_of_coils

    for coil in range(1, noc + 1):
        coils_r.append(pf_coil_shape_dict["rpf{:01}".format(coil)])
        coils_z.append(pf_coil_shape_dict["zpf{:01}".format(coil)])
        coils_dr.append(pf_coil_shape_dict["pfdr{:01}".format(coil)])
        coils_dz.append(pf_coil_shape_dict["pfdz{:01}".format(coil)])
        coil_text.append(str(coil + 1))

    for i in range(len(coils_r)):
        print(i)
        r_1 = float(coils_r[i]) - 0.5 * float(coils_dr[i])
        z_1 = float(coils_z[i]) - 0.5 * float(coils_dz[i])
        r_2 = float(coils_r[i]) - 0.5 * float(coils_dr[i])
        z_2 = float(coils_z[i]) + 0.5 * float(coils_dz[i])
        r_3 = float(coils_r[i]) + 0.5 * float(coils_dr[i])
        z_3 = float(coils_z[i]) + 0.5 * float(coils_dz[i])
        r_4 = float(coils_r[i]) + 0.5 * float(coils_dr[i])
        z_4 = float(coils_z[i]) - 0.5 * float(coils_dz[i])
        r_5 = float(coils_r[i]) - 0.5 * float(coils_dr[i])
        z_5 = float(coils_z[i]) - 0.5 * float(coils_dz[i])

        r_points = [r_1, r_2, r_3, r_4, r_5]
        z_points = [z_1, z_2, z_3, z_4, z_5]

        plasma_render(r_points, z_points)
        if i > 0:
            bt.faces_pf_coils(f"line_object.00{i}")

        else:
            bt.faces_pf_coils("line_object")

    central_coil = patches.Rectangle([bore, (-ohdz / 2)], ohcth, ohdz)
    print(central_coil)

    x_coords, y_coords = bt.rect_blend_sep(central_coil)

    plasma_render(x_coords=x_coords, y_coords=y_coords)
    bt.faces_pf_coils("line_object.006")


plot_pf_coils(pf_coil_shape_dict=pf_coil_shape_dict)


bt.delete_cube()

# blend_file_path = "/home/miles/Downloads/test"
# bpy.ops.export_scene.gltf(filepath=blend_file_path)
# bpy.ops.wm.save_as_mainfile(filepath=blend_file_path)
