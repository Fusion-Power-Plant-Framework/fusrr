from pathlib import Path

from fusrr.base.project import FusrrProject
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

fusrr.run()
