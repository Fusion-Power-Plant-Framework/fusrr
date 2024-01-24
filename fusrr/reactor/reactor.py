from os import PathLike
from pathlib import Path

from process.io.mfile import MFile

from fusrr.base.object import FusrrSceneObject
from fusrr.reactor.adaptors.process_adaptor import process_file_adaptor
from fusrr.reactor.components.plasma import Plasma


class FusrrReactor(FusrrSceneObject):
    """A FusrrReactor is a."""

    plasma: Plasma

    def __init__(self, name: str, data_filepath: PathLike) -> None:
        self._load_data(data_filepath)
        super().__init__(name, None)

    def _load_data(self, data_filepath: PathLike) -> None:
        fp = Path(data_filepath)
        if fp.suffix == ".DAT":
            process_mfile = MFile(filename=str(fp))
            self.parames = process_file_adaptor(process_mfile)
        elif fp.suffix == ".json":
            ...
        # self.parames = bluemira_file_adaptor(output_names, file_path)

    def _build(self) -> None:
        self.plasma = Plasma(self.parames)

        # add an add_all_attr_objects method to FusrrSceneObject
        self.add_object(self.plasma)
