"""Imports Simple Example of reactor, changes location, selects/ generates and colours meshes and outputs a rendered PNG file"""
import bpy

bpy.ops.import_scene.gltf(filepath="")
bpy.context.object.location = (1, 2, 12)

activeobject = bpy.context.scene.objects[1] #1 and 2 refers to mesh LCFS_1 and Winding_pack_1 (print(bpy.data.meshes)) 
obj1 = bpy.context.scene.objects[2]

mat = bpy.data.materials.new(name="MatName")
material = bpy.data.materials.new(name="MaterialName")

activeobject.data.materials.append(mat)
obj1.data.materials.append(material)


mat.diffuse_color = (10, 3, 12, 5)
material.diffuse_color = (1, 2, 13, 4)

bpy.context.scene.render.filepath = '/home/hannah/blender_venv/NameofPNG' #Saves render as PNG
bpy.ops.render.render(write_still=1)
