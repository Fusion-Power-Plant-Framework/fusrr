"""
Extracts Data From Two PROCESS Output files and tabulates them against one another

Comparison function works by passing in a list of two PROCESS .DAT files.
Also allows manually inputting params to store in class.
Currently set to 5 output params but can add any key from .DAT file

"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

from process.io.mfile import MFile
from tabulate import tabulate


@dataclass
class OutputParams:
    """DataClass to store output params

    Returns:
        dataclass: 5 "test" parameters + file_name which is optional in case of manual
        input for OutputParams
    """

    rmajor: float
    rminor: float
    n_tf: float
    bigq: float
    tburn: float
    file_name: Optional[str] = None

    @classmethod
    def from_file(cls, file_name: str) -> OutputParams:
        """Makes instance of class from file name"""

        mfile_path = Path(file_name)  # insert file path here to PROCESS OUTPUT FILE .DAT
        mfile = MFile(filename=str(mfile_path))

        output_params = list(
            cls.__annotations__.keys()
        )  # Creates list to find and remove file_name from mfile data
        output_params.pop(
            output_params.index("file_name")
        )  # Removes file_name to match key values to attributes
#From line 50 - 80 WIP
        def adapt_process(self):
            """Convert parameters from PROCESS dataclasses to generic format"""
            from Dictionary_Basic import process_param
            for param_name, param_value in input_data.items():
                try:    #if param found in both dict then:
                    generic_name = process_param[param_name]
                    setattr(self, generic_name, param_value)
                except KeyError:
                    pass
        
        def adapt_bluemira(self):
            """Convert parameters from BLUEMIRA dataclesses to generic format"""
            from Dictionary_Basic import bluemira_param
            for param_name, param_value in input_data.items():
                try:
                    generic_name = bluemira_param[param_name]
                    setattr(self, generic_name, param_value)
                except KeyError:
                    continue
        if MFile:

            return cls(
                file_name=file_name,
                **{param: mfile.data[adapt_process[param]].get_scan(-1) for param in output_params},
            )
        elif jsonFile:
            return cls(
            file_name=file_name,
            **{param: bluemira_data[adapt_bluemira[param]["value"]] for param in output_params},
        )
#50 - 80 is example of adaptor creating generic output for both PROCESS and BLUEMIRA, needs more work

def comparison(output_parameters: list[OutputParams]) -> str:
    """Takes list of instances and formats them comparing keys in table

    Returns
    -------
    str
        Ready to be tabulated by tabulate module
    """
    # Takes a list of instances of dataclass and makes them into dictionaries
    output_parameters = [asdict(o_p) for o_p in output_parameters]

    param_list = []
    # Creates list and pops file_name to use as headers for table
    header_list = [o_p.pop("file_name") for o_p in output_parameters]

    # Looks for same key in output_parameters list of dictionaries
    for key in output_parameters[0].keys():
        row = [key]
        for o_p in output_parameters:
            if key in o_p:
                row.append(o_p.get(key))
            else:
                row.append(None)
        param_list.append(row)
    # Tabulates the params in columns for each file
    return tabulate(
        param_list,
        headers=["Params", *header_list],
        tablefmt="fancy_outline",
        numalign="right",
    )
