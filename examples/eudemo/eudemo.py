from pathlib import Path

from fusrr.base.entity.object_properties import (
    CommonMeshModelProperties,
    CommonObjTransformProperties,
)
from fusrr.base.models import Vec3
from fusrr.base.project import FusrrProject
from fusrr.base.scene import (
    FusrrScene,
    FusrrSceneConfigForCamera,
    FusrrSceneConfigForObject,
)
from fusrr.reactor.process import ProcessReactor

fusrr = FusrrProject(
    "EUDEMO",
    config_path=Path.cwd() / "config.json",
    overwrite=True,
)
fusrr.add_entity(
    ProcessReactor(
        "EUDEMO",
        mfile_filepath=Path.cwd() / "EUDEMO_MFILE.DAT",
    )
)
fusrr.add_scene(
    FusrrScene(
        "test1",
        camera=FusrrSceneConfigForCamera(
            transform=CommonObjTransformProperties(
                position=Vec3(0, 0, 10),
            ),
            look_at="plasma",
        ),
        objects=[
            FusrrSceneConfigForObject(
                name="plasma",
                model=CommonMeshModelProperties(
                    revolve_z_deg=270,
                ),
            ),
        ],
    )
)
fusrr.run()
