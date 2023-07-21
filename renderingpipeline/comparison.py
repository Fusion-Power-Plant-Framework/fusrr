"""
Extracts Data From Two PROCESS Output files and tabulates them against one another

Comparison function works by passing in a list of two PROCESS .DAT files.
Also allows manually inputting params to store in class.
Currently set to 5 output params but can add any key from .DAT file

"""
from __future__ import annotations

from process.io.mfile import MFile
from tabulate import tabulate


def comparison(output_parameters) -> str:
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
