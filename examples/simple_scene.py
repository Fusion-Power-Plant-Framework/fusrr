from fusrr.base.models import Vec3
from fusrr.base.object import cube
from fusrr.base.scene import FusrrScene

scene = FusrrScene("simple_scene", overwrite=True)

scene.add_entity(cube("cube 1", Vec3(0, 0, 0)))
scene.add_entity(cube("cube 2", Vec3(5, 0, 0)))
scene.add_entity(cube("cube 3", Vec3(10, 0, 0)))

scene.run()
