"""Useful combination of blender tools
"""

import bpy
import bmesh


def empty_obj(x, y, z):
    """Empty object adder (for camera tracking purposes)"""
    bpy.ops.object.empty_add(location=(x, y, z))


def add_light(x, y, z):
    """Adds sunlight object"""
    bpy.ops.object.light_add(type="SUN", location=(x, y, z))


def move_camera(x, y, z):
    """Selects and moves camera"""
    camera = bpy.data.objects["Camera"]
    camera.location = (x, y, z)


def camera_fix(camera: str, component: str, dist):
    """Fixes camera to look at target
    Parameters
    ----------
    camera : bpy.data.objects[""]
    component : bpy.data.object[""]
    dist (int) : distance
    """
    camera = bpy.data.objects[camera]
    constraint = camera.constraints.new(type="TRACK_TO")
    constraint.target = bpy.data.objects[component]
    camera.location = (0, 0, dist)


def delete_cube():
    """Removes default cube if present"""
    for o in bpy.context.scene.objects:
        if o.name == "Cube":
            bpy.ops.object.select_all(action="DESELECT")
            bpy.data.objects["Cube"].select_set(True)
            bpy.ops.object.delete()
        else:
            pass


def save_image(file_name: str):
    """Saves render as PNG"""
    bpy.context.scene.render.filepath = str(file_name)
    bpy.ops.render.render(write_still=True, use_viewport=True)


def join_obj(names: list):
    """Joins objects in list into one object
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
    bpy.data.objects[str(vertex_obj)].select_set(True)
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


def rect_blend(rectangle: object):
    """Makes a rectangle to be plotted in blender from rectangle patches object

    Parameters
    ----------
    rectangle : object
        from matplotlib patches

    Returns
    -------
    array
        coordinates of vertices
    """
    x_coords = []
    y_coords = []
    # Gets bottom left point
    x0 = rectangle.get_x()
    y0 = rectangle.get_y()
    x_coords.append(x0)
    y_coords.append(y0)

    # Gets bottom right point
    x1 = x0 + rectangle.get_width()
    x_coords.append(x1)
    y_coords.append(y0)

    # Top right point
    y1 = y0 + rectangle.get_height()
    x_coords.append(x1)
    y_coords.append(y1)

    # Gets top left point

    x_coords.append(x0)
    y_coords.append(y1)

    centre_coords = list(zip(x_coords, y_coords))

    return centre_coords


def rect_blend_sep(rectangle: object):
    """Makes a x and y seperated coordinate rectangle
    # ! Can just adapt rect_blend function to do this

    Parameters
    ----------
    rectangle : object
        matplotlib patches rectangle

    Returns
    -------
    tuple of lists
        x and y coords
    """
    x_coords = []
    y_coords = []
    # Gets bottom left point
    x0 = rectangle.get_x()
    y0 = rectangle.get_y()
    x_coords.append(x0)
    y_coords.append(y0)

    # Gets bottom right point
    x1 = x0 + rectangle.get_width()
    x_coords.append(x1)
    y_coords.append(y0)

    # Top right point
    y1 = y0 + rectangle.get_height()
    x_coords.append(x1)
    y_coords.append(y1)

    # Gets top left point

    x_coords.append(x0)
    y_coords.append(y1)

    return x_coords, y_coords


def change_to_mesh(object_names: list):
    """Changes spline object to mesh

    Parameters
    ----------
    object_names : list
        objects in blender scene
    """
    bpy.ops.object.select_all(action="DESELECT")

    for i in object_names:
        bpy.data.objects[str(i)].select_set(True)
    # ! Selects object 0 to be active object, must change soon
    bpy.context.view_layer.objects.active = bpy.context.scene.objects[
        str(object_names[0])
    ]
    bpy.ops.object.convert(target="MESH")
    bpy.ops.object.select_all(action="DESELECT")


def component_outline(coords, object_name: str):
    """Renders the spline of component

    Parameters
    ----------
    x_coords : numpy array
    y_coords : numpy array

    """
    curve = bpy.data.curves.new(name="Curve_test", type="CURVE")
    curve.fill_mode = "NONE"

    ob = bpy.data.objects.new(object_name, object_data=curve)
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


def render_component_mesh(name):
    """Set up + builds new mesh for component"""
    scene = bpy.context.scene
    bpy.context.view_layer.objects.active = None

    mesh = bpy.data.meshes.new(str(name))
    line_obj = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(line_obj)
    scene.view_layers.update()

    bm = bmesh.new()

    return scene, mesh, bm


def spin_extrusion(face_mesh):
    """Spin extrudes around y axis in blender 2Pi radians

    Parameters
    ----------
    face_mesh : str
        Name of face_mesh to be spun extruded
    """
    obj = bpy.context.scene.objects.get(str(face_mesh))
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.spin(
        angle=6.28319, steps=400, axis=(0.0, 1.0, 0.0)
    )  # Polodial rotation
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")


def half_reactor(face_mesh):
    """Spins Pi radians for a half reactor view

    Args
    ----
        face_mesh (str): Name of object's mesh to be spun
    """
    obj = bpy.context.scene.objects.get(str(face_mesh))
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.spin(
        angle=3.14159, steps=100, axis=(0.0, 1.0, 0.0)
    )  # Polodial rotation
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")
