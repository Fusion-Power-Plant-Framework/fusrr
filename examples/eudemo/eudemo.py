from pathlib import Path

from fusrr.base.entity.object_properties import ObjTransformProperties
from fusrr.base.models import Vec3
from fusrr.base.project import FusrrProject
from fusrr.base.scene import (
    FusrrScene,
    FusrrSceneCameraConfig,
    FusrrSceneObjectConfig,
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
base_angle = 180
fusrr.add_scene(
    FusrrScene(
        "expose_plasma",
        camera=FusrrSceneCameraConfig(
            transform=ObjTransformProperties(
                position=Vec3(0, 0, 10),
            ),
            look_at="plasma",
        ),
        objects=[
            FusrrSceneObjectConfig(
                name="cryostat",
                slice_start=base_angle - 80,
                slice_end=base_angle + 80,
            ),
            FusrrSceneObjectConfig(
                name="vacuum_vessel",
                slice_start=base_angle - 35,
                slice_end=base_angle + 35,
            ),
            FusrrSceneObjectConfig(
                name="blanket",
                slice_start=base_angle - 20,
                slice_end=base_angle + 20,
            ),
            FusrrSceneObjectConfig(
                name="pf_coils",
                pattern="(pf_*)|(cs_coil)$",
                slice_start=base_angle - 35,
                slice_end=base_angle + 35,
            ),
            FusrrSceneObjectConfig(
                name="tf_coils",
                pattern="tf_coil_d_(8|9|10|11|12)$",
                visible=False,
            ),
        ],
    )
)
fusrr.run()
