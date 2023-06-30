"""Imports Simple Example of reactor, changes location, selects/ generates and colours meshes and outputs a rendered image as PNG file"""
import bpy

def import_file(pathforfile):
    """Imports gltf file"""
    bpy.ops.import_scene.gltf(filepath= pathforfile)

def object_change(obj_1,obj_2):
    """Selects active object, creates new meshes and assigns colours
    obj_x = name/number of desired object"""
    activeobject = bpy.context.scene.objects[obj_1] #1 and 2 refers to mesh LCFS_1 and Winding_pack_1 (print(bpy.data.meshes)) 
    obj1 = bpy.context.scene.objects[obj_2]

    mat = bpy.data.materials.new(name="MatName")
    material = bpy.data.materials.new(name="MaterialName")

    activeobject.data.materials.append(mat)
    obj1.data.materials.append(material)


    mat.diffuse_color = (10, 3, 12, 5)
    material.diffuse_color = (1, 2, 13, 4)

def save_image(Image_pathname):
    """Saves render as PNG"""
    object_change(1, 2)
    bpy.context.scene.render.filepath = Image_pathname 
    bpy.ops.render.render(write_still=1)

def move_location(x, y, z):
    """moves imported object"""
    bpy.context.object.location = (x, y, z)

def move_camera(x, y, z):
    """Selects and moves camera"""
    camera = bpy.data.objects['Camera']
    camera.location = (x, y, z)

def delete_cube():
    """Goodbye default cube"""
    bpy.ops.object.select_all(action = 'DESELECT')
    bpy.data.objects['Cube'].select_set(True)
    bpy.ops.object.delete()

importfilepath = "/home/Downloads/SimpleExample.gltf"
imagepathname = "render.png"

import_file(importfilepath)
delete_cube()
move_camera(15, -20, 20)
move_location(1,2,12)

save_image(imagepathname )
