"""
Extracts Data From Two PROCESS Output files and tabulates them against one another

Comparison function works by passing in a list of two PROCESS .DAT files.
Also allows manually inputting params to store in class.
Currently set to 5 output params but can add any key from .DAT file

"""
from dataclasses import asdict, dataclass
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
    tburn: float
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


def comparison(two_files=list):
    # Creates the two instances to compare and converts to dictionary
    process1 = asdict(OutputParams.from_file(two_files[0]))
    process2 = asdict(OutputParams.from_file(two_files[1]))

    param_list = []
    header_list = []

    # Appends to header list and removes the file name from params
    header_list.append(process1.pop("file_name"))
    header_list.append(process2.pop("file_name"))

    # Looks for same key in both outputs to match
    for key in process1.keys():
        if key in process2:
            param_list.append([key, process1.get(key), process2.get(key)])
        else:
            pass

    # Tabulates the params in columns for each file
    return tabulate(
        param_list,
        headers=["Params", header_list[0], header_list[1]],
        tablefmt="fancy_outline",
        numalign="right",
    )
