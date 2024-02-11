from os import PathLike
from pathlib import Path

from process.io.mfile import MFile

from fusrr.base.object import FusrrSceneObject
from fusrr.reactor.process import ProcessParams
from fusrr.reactor.process.components import ProcessPFCoils, ProcessPlasma


class ProcessReactor(FusrrSceneObject):
    """..."""

    plasma: ProcessPlasma
    pf_coils: ProcessPFCoils

    def __init__(self, name: str, data_filepath: PathLike) -> None:
        self._load_data(data_filepath)
        super().__init__(name, None)

    def _load_data(self, data_filepath: PathLike) -> None:
        fp = Path(data_filepath).resolve()
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

        # add an add_all_attr_objects method to FusrrSceneObject
        self.add_object(self.plasma)
        self.add_object(self.pf_coils)
