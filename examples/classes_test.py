"""test for view/ reactor/ component classes"""

import bpy

from renderingpipeline.adaptor import OutputParams
from renderingpipeline.components import Plasma, TFCoil
from renderingpipeline.reactor import Reactor
from renderingpipeline.views import View

input_file = OutputParams.from_file("examples/baseline_2018_MFILE.DAT")

plasma = Plasma(input_file)
tf = TFCoil(input_file)
reactor1 = Reactor(plasma=plasma, tfcoils=tf)

view = View(reactor1)
# view.highlight_plasma( '#d85319')
view.move_plasma(2, 0, 10)
# view.make_3d()
view.half_reactor()
bpy.ops.wm.save_as_mainfile(filepath="plasma")
# bpy.ops.export_scene.gltf(filepath='exports')
