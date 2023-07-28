"""Test for view/ reactor/ component classes - rendering 2D/ 3D basic reactors"""


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
view.tf_thick()
view.key()
reactor1.save_image("View_test")

# view.make_3d()

# bpy.ops.wm.save_as_mainfile(filepath="Next")
# bpy.ops.export_scene.gltf(filepath='exports')
