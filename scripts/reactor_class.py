"""Reactor Class WIP - begining to gather useful functions. Need to decide on structure."""
import bpy


class Reactor:
    def __init__(self, data):
        # Preset options, have default settings for reactor components here
        self.data = data

    def insert_data(self):
        # pull from adaptor
        pass

    def make_face_from_vertices(vertex_obj: str):
        """Makes a face from group of vertices

        Parameters
        ----------
        vertex_obj : object
            name of object where vertices are
        """
        bpy.data.objects[str(vertex_obj)].select_set(True)
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.edge_face_add()
        bpy.ops.object.mode_set(mode="OBJECT")


class SceneFunctions:
    def delete_cube():
        """Removes default cube if present"""

        for o in bpy.context.scene.objects:
            if o.name == "Cube":
                bpy.ops.object.select_all(action="DESELECT")
                bpy.data.objects["Cube"].select_set(True)
                bpy.ops.object.delete()
            else:
                pass

    def add_light(x, y, z):
        """adds sunlight object"""
        bpy.ops.object.light_add(type="SUN", location=(x, y, z))


class Views:
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


class RenderingOptions:
    def save_image(file_name: str):
        """Saves render as PNG"""

        bpy.context.scene.render.filepath = str(file_name)
        bpy.ops.render.render(write_still=True, use_viewport=True)


# ComponentClass, BlenderfunctionClass, ect.
