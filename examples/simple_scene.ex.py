from fusrr.base import FusrrScene  # noqa: N999
from fusrr.base.models import Vec3
from fusrr.base.object import cube
from fusrr.base.pipeline import FusrrBuildPipeline

scene = FusrrScene("simple_scene", overwrite=True)

p = FusrrBuildPipeline("test_col2")
p.add_object(cube("cube 1", Vec3(0, 0, 0)))
p.add_object(cube("cube 2", Vec3(5, 0, 0)))
p.add_object(cube("cube 3", Vec3(10, 0, 0)))

scene.add_pipe(p)

scene.execute()
