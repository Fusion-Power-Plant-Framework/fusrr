"""brocess"""

from renderingpipeline.adaptor import OutputParams
from renderingpipeline.blender_tools import import_gltf, save_blender_file
from renderingpipeline.components import Cryostat, PFCoil, Plasma, TFCoil
from renderingpipeline.reactor import Reactor
from renderingpipeline.views import Comparison, View

input_file = OutputParams.from_file("examples/EUDEMO_MFILE.DAT")

plasma = Plasma(input_file)
tf = TFCoil(input_file)
pf = PFCoil(input_file)

reactor1 = Reactor(plasma=plasma, tfcoil=tf, pfcoil=pf)
view = Comparison(reactor1)
view.comparison()


import_gltf("examples/EUDEMO.gltf")
plasma = Plasma()
tf = TFCoil()
pf = PFCoil()
cryo = Cryostat()
reactor2 = Reactor(plasma=plasma, tfcoil=tf, pfcoil=pf)

image = View(reactor2)
view.comparison_shot()

image.save_image("brocess")
save_blender_file("Comparisons")

# Changes to be made to comparison function in views.py:
#   def comparison(self):
# """Set up for comparing two reactors
# - Makes 1 reactor a single object and moves it to own collection
# """
# bpy.ops.object.select_all(action="DESELECT")
# bpy.ops.object.select_by_type(type="MESH")
# bpy.ops.object.join()
# for sect in bpy.context.selected_objects:
#     sect.name = "reactor1"
# bpy.data.objects["reactor1"].location = (40, 0, 0)
# bpy.ops.object.select_all(action="DESELECT")
# bpy.data.objects["Tf_coils"].location = (40, 0, 0)
# bpy.data.objects["Empty_tf"].location = (40, 0, 0)
# move_to_collection("reactor1", "Reactor1")  # can change for name to be input
# bpy.ops.object.move_to_collection(collection_index=0, is_new=False)
# bpy.ops.object.select_all(action="DESELECT")

# This will allow for tf coil rendering in comparison view
