from fusrr.base import FusrrScene  # noqa: N999
from fusrr.base.models import Vec3
from fusrr.base.object import cube

scene = FusrrScene("test")

scene.add_object(cube("cube 1", Vec3(0, 0, 0)))
scene.add_object(cube("cube 2", Vec3(5, 0, 0)))
scene.add_object(cube("cube 3", Vec3(10, 0, 0)))

scene.execute()
