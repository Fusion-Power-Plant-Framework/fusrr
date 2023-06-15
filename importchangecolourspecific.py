import bpy

bpy.ops.import_scene.gltf(filepath="C:/Users/tk1837/Blender scripts/SimpleExample.gltf")

bpy.context.object.location = (1, 2, 12)

activeobject = bpy.data.objects['LCFS_1']
obj1 = bpy.context.scene.objects['Winding_pack_1']

mat = bpy.data.materials.new(name="MatName")
material = bpy.data.materials.new(name="MaterialName")

activeobject.data.materials.append(mat)
obj1.data.materials.append(material)


mat.diffuse_color = (10, 3, 12, 5)
material.diffuse_color = (1, 2, 13, 4)

#Changes location of object, generates new mesh and changes colour. Specific to SimpleExample as needed to call in names of each mesh.