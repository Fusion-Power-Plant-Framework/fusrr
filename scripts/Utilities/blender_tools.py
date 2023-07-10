"""Useful combination of blender tools. """


import bpy


def empty_obj(x, y, z):
    """Empty object adder (for camera tracking purposes)"""
    bpy.ops.object.empty_add(location=(x, y, z))


def add_light(x, y, z):
    """adds sunlight object"""
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
