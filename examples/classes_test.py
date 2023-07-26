"""test for view/ reactor/ component classes"""

import bpy

from renderingpipeline.adaptor import OutputParams
from renderingpipeline.components import Cryostat, PfCoils, Plasma, TFCoil
from renderingpipeline.reactor import Reactor
from renderingpipeline.views import View

input_file = OutputParams.from_file("examples/MFILE.DAT")

plasma = Plasma(input_file)
tf = TFCoil(input_file)
pf = PfCoils(input_file)
cryo = Cryostat(input_file)
reactor1 = Reactor(plasma=plasma, tfcoils=tf, pfcoils=pf, cryostat=cryo)

view = View(reactor1)
# view.highlight_plasma( '#d85319')
view.move_plasma(2, 0, 10)
view.make_3d()
# view.half_reactor('plasma')
# view.export('this')
view.tf_thick()
bpy.ops.wm.save_as_mainfile(filepath="Next")
# bpy.ops.export_scene.gltf(filepath='exports')
reactor1.save_image("View_test")


# looking_direction = camera.location - mathutils.Vector((0.0, 0.0, 0.0))
#     rot_quat = looking_direction.to_track_quat('Z', 'Y')

#     camera.rotation_euler = rot_quat.to_euler()
#     camera.location = rot_quat @ mathutils.Vector((0.0, 0.0, component))
