"""
Temporary dataclass structure to render 2D plasma view.

"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

from process.io.mfile import MFile
from tabulate import tabulate


# TODO: In future will use adapter class to import data, placeholder for now!
@dataclass
class PlasmaShapeParams:
    """DataClass to store Plasma params

    Returns:
        dataclass: 5 "test" parameters + file_name which is optional in case of manual
        input for OutputParams
    """

    rmajor: float
    rminor: float
    triang95: float
    kappa95: float
    i_single_null: float
    file_name: Optional[str] = None

    @classmethod
    def from_file(cls, file_name: str) -> PlasmaShapeParams:
        """Makes instance of class from file name"""

        mfile_path = Path(file_name)  # insert file path here to PROCESS OUTPUT FILE .DAT
        mfile = MFile(filename=str(mfile_path))

        output_params = list(
            cls.__annotations__.keys()
        )  # Creates list to find and remove file_name from mfile data
        output_params.pop(
            output_params.index("file_name")
        )  # Removes file_name to match key values to attributes

        return cls(
            file_name=file_name,
            **{param: mfile.data[param].get_scan(-1) for param in output_params},
        )
