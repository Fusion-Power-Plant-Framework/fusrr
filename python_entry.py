"""Imports Simple Example of reactor, changes location, selects/ generates and colours meshes and outputs a rendered image as PNG file"""
import bpy

def import_file(pathforfile):
    """Imports gltf file"""
    bpy.ops.import_scene.gltf(filepath= pathforfile)

def save_image(Image_pathname):
    """Saves render as PNG"""
    bpy.context.scene.render.filepath = Image_pathname 
    bpy.ops.render.render(write_still=1)

def move_location(x, y, z):
    """moves imported object"""
    bpy.context.object.location = (x, y, z)

def move_camera(x, y, z):
    """Selects and moves camera (not yet working)"""
    bpy.data.objects['Camera'].select_set(True)


importfilepath = "/home/Downloads/SimpleExample.gltf"
imagepathname = "/home/blender_venv/Image_name.png"

import_file(importfilepath)

move_location(1,2,12)

activeobject = bpy.context.scene.objects[1] #1 and 2 refers to mesh LCFS_1 and Winding_pack_1 (print(bpy.data.meshes)) 
obj1 = bpy.context.scene.objects[2]

mat = bpy.data.materials.new(name="MatName") #creates new mesh
material = bpy.data.materials.new(name="MaterialName")

activeobject.data.materials.append(mat)
obj1.data.materials.append(material)


mat.diffuse_color = (10, 3, 12, 5) #changes mesh colour
material.diffuse_color = (1, 2, 13, 4)

save_image(imagepathname )
