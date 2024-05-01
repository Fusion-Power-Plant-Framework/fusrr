from os import PathLike
from pathlib import Path

from process.io.mfile import MFile

from fusrr.base.pipeline import FusrrBuildPipeline
from fusrr.reactor.process import ProcessParams
from fusrr.reactor.process.components import (
    ProcessPFCoils,
    ProcessPlasma,
    ProcessVacuumVessel,
    ProcessBlanket,
    ProcessRadiationShield,
)
from fusrr.reactor.process.components.process_component import (
    ProcessComponentCollection,
)
from fusrr.reactor.process.components.tf_coils import ProcessTFCoils


class ProcessReactor(ProcessComponentCollection):
    """Models a PROCESS reactor."""

    def __init__(self, name: str, *, mfile_filepath: PathLike) -> None:
        """Create a ProcessReactor object from a PROCESS mfile."""
        super().__init__(name, self._load_mfile(mfile_filepath))

    def _load_mfile(self, mfile_filepath: PathLike) -> ProcessParams:
        fp = Path(mfile_filepath).resolve()
        if not fp.suffix == ".DAT":
            raise ValueError(
                f"Invalid file type: {fp.suffix}, path: {fp}. "
                "Is that a PROCESS file?"
            )
        return ProcessParams(MFile(filename=fp.as_posix()))

    def _setup(self, pipeline: FusrrBuildPipeline) -> None:
        pipeline.add(ProcessPlasma(self.params))
        pipeline.add(ProcessPFCoils(self.params))
        pipeline.add(ProcessTFCoils(self.params))
        pipeline.add(ProcessVacuumVessel(self.params))
        pipeline.add(ProcessBlanket(self.params))
        pipeline.add(ProcessRadiationShield(self.params))
