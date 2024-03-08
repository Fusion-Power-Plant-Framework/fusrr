from os import PathLike
from pathlib import Path

from process.io.mfile import MFile

from fusrr.base.object import FusrrSceneObject
from fusrr.reactor.process import ProcessParams
from fusrr.reactor.process.components import ProcessPFCoils, ProcessPlasma
from fusrr.reactor.process.components.tf_coils import ProcessTFCoils


class ProcessReactor(FusrrSceneObject):
    """Models a PROCESS reactor."""

    plasma: ProcessPlasma
    pf_coils: ProcessPFCoils
    tf_coils: ProcessTFCoils

    def __init__(self, name: str, mfile_filepath: PathLike) -> None:
        """Create a ProcessReactor object from a PROCESS mfile."""
        self._load_mfile(mfile_filepath)
        super().__init__(name)

    def _load_mfile(self, mfile_filepath: PathLike) -> None:
        fp = Path(mfile_filepath).resolve()
        if not fp.suffix == ".DAT":
            raise ValueError(
                f"Invalid file type: {fp.suffix}, path: {fp}. "
                "Is that a PROCESS file?"
            )
        process_mfile = MFile(filename=fp.as_posix())
        self.params = ProcessParams(process_mfile)

    def _setup(self) -> None:
        self.plasma = ProcessPlasma(self.params)
        self.pf_coils = ProcessPFCoils(self.params)
        self.tf_coils = ProcessTFCoils(self.params)

        # add an add_all_attr_objects method to FusrrSceneObject
        self.add_object(self.plasma)
        self.add_object(self.pf_coils)
        self.add_object(self.tf_coils)
