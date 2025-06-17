from fusrr.base.entity.object import cube
from fusrr.base.project import FusrrProject
from fusrr.core.vectors import Vec3

scene = FusrrProject("simple_scene", overwrite=True)

scene.add_entity(cube("cube 1", Vec3(0, 0, 0)))
scene.add_entity(cube("cube 2", Vec3(5, 0, 0)))
scene.add_entity(cube("cube 3", Vec3(10, 0, 0)))

scene.run()
