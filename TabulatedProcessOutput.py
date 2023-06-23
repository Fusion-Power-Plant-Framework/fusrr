"""
Extracts Data From PROCESS Output file and Stores In Data Class

Works with imported process data file but also allows manual addition of parameter values.
Currently set to 4 test parameters but can choose any attribute from .DAT file

"""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from process.io.mfile import MFile
from tabulate import tabulate


@dataclass
class OutputParams:
    rmajor: float
    rminor: float
    n_tf: float
    bigq: float
    file_name: Optional[str] = None

    @classmethod
    def from_file(cls, file_name):
        mfile_path = Path(
            file_name
        )  # insert file path here to PROCESS OUTPUT FILE .DAT
        mfile = MFile(filename=str(mfile_path))

        output_params = list(
            cls.__annotations__.keys()
        )  # Creates list to find and remove file_name from mfile data
        output_params.pop(
            output_params.index("file_name")
        )  # Removes file_name to match key values to attributes

        return cls(
            file_name=file_name,
            **{param: mfile.data[param].get_scan(-1) for param in output_params}
        )


b = OutputParams.from_file("baseline_2018_silly_MFILE.DAT")
print(b)
