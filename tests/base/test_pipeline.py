from fusrr.core.vectors import Vec3
from examples.simple_scene import cube


def test_pipeline():
    # Test currently using dummy values
    pipeline = FusrrBuildPipeline(world_state=FusrrWorldState())  # noqa: F821
    assert pipeline.entity_names() == set()
    assert pipeline.object_names() == set()
    assert pipeline.collection_names() == set()

    pipeline.add(cube("obj1", location=Vec3(0, 0, 0)))
    pipeline.add(cube("obj2", location=Vec3(5, 0, 0)))
    pipeline.add(cube("obj3", location=Vec3(10, 0, 0)))

    assert pipeline.entity_names() == {"obj1", "obj2", "obj3"}
    # assert pipeline.object_names() == {"obj1", "obj2"}
    # assert pipeline.collection_names() == {"coll1", "coll2"}

    # pipeline.execute()
