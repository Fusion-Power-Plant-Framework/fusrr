from pathlib import Path

from fusrr.base.scene import FusrrScene
from fusrr.reactor.process import ProcessReactor

scene = FusrrScene("simple_scene", overwrite=True)
scene.add_entity(
    ProcessReactor("EUDEMO", mfile_filepath=Path.cwd() / "EUDEMO_MFILE.DAT")
)

scene.run()
