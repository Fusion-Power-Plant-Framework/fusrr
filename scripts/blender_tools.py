"""Useful combination of blender tools"""


import bpy


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


def camera_fix(camera: str, target: str):
    """Fixes camera to look at target

    Parameters
    ----------
    camera : bpy.data.objects[""]
    target : bpy.data.object[""]
    """
    # *Will break if object "camera" or "target" doesn't exist.
    constraint = bpy.data.objects[camera].constraints.new(type="TRACK_TO")
    constraint.target = bpy.data.objects[target]


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


def rect_blend(rectangle: object):
    """Creates rectangle

    Args:
        rectangle (object): _description_

    Returns:
        centre_cords: array
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


def change_to_mesh(object_names: list):
    """Changes plotted object to mesh

    Args:
        object_names (list): name of object in blender
    """
    bpy.ops.object.select_all(action="DESELECT")

    for i in object_names:
        bpy.data.objects[str(i)].select_set(True)

    bpy.context.view_layer.objects.active = bpy.context.scene.objects[
        str(object_names[4])
    ]
    bpy.ops.object.convert(target="MESH")
    bpy.ops.object.select_all(action="DESELECT")
