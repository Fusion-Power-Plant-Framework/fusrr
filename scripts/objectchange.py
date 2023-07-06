import bpy

bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
bpy.context.object.location.xy = (1, 2)

activeobject = bpy.context.active_object
mat = bpy.data.materials.new(name="MatName")
activeobject.data.materials.append(mat)
bpy.context.object.active_material.diffuse_color = (1, 2, 4, 1)
