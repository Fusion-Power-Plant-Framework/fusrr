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
base_angle = 0
cryostat_cut = 120
vv_cut = 60
b_cut = vv_cut - 30
pf_cut = vv_cut
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
                slice_start=base_angle - cryostat_cut,
                slice_end=base_angle + cryostat_cut,
                visible=False,
            ),
            FusrrSceneObjectConfig(
                name="vacuum_vessel",
                slice_start=base_angle - vv_cut,
                slice_end=base_angle + vv_cut,
            ),
            FusrrSceneObjectConfig(
                name="blanket",
                slice_start=base_angle - b_cut,
                slice_end=base_angle + b_cut,
            ),
            FusrrSceneObjectConfig(
                name="pf_coils",
                pattern="(pf_*)|(cs_coil)$",
                slice_start=base_angle - pf_cut,
                slice_end=base_angle + pf_cut,
            ),
            FusrrSceneObjectConfig(
                name="tf_coils",
                pattern="tf_coil_d_(1|2|3|18|17|16)$",
                visible=False,
            ),
        ],
    )
)
fusrr.run()
