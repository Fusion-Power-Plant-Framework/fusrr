import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

from tabulate import tabulate


@dataclass
class BlueOutputParams:
    """DataClass to store output params

    Returns
    -------
    _Dataclass: 5 "test" parameters + file name (optional)_
        _description_
    """

    R_0: float
    r_fw_ob_in: float
    n_TF: float
    q_95: float
    tau_e: float
    file_name: Optional[str] = None

    @classmethod
    def from_blue_file(cls, file_name):
        """Makes instance of class from file name"""
        file_path = Path(file_name)
        # opening json file here and loading data

        with open(str(file_path), "r") as fh:
            jsondata = json.load(fh)
        # listing attributes of data class and removing the file_name which is not present in json file
        output_params = list(cls.__annotations__.keys())
        output_params.pop(output_params.index("file_name"))

        # creating an empty dictionary to help with nested dictionary
        a = {}

        # extracting the output paramters dictionary from json file
        for param in output_params:
            a[param] = jsondata[str(param)]["value"]

        return cls(file_name=file_name, **a)


def comparison(output_parameters: list[BlueOutputParams]) -> str:
    """Takes a list of instances and compares them in table format

    Parameters
    ----------
    output_parameters : list[BlueOutputParams]
        _list of instances

    Returns
    -------
    str
        ready to be tabluated
    """
    # Making an instance of the class of test json file
    output_parameters = [asdict(o_p) for o_p in output_parameters]
    # Creates a list of headers by popping the file_name from params
    header_list = [o_p.pop("file_name") for o_p in output_parameters]
    # Creates a param list to format the data values into
    param_list = []

    for key in output_parameters[0].keys():
        row = [key]
        for o_p in output_parameters:
            if key in o_p:
                row.append(o_p.get(key))
            else:
                row.append(None)
        param_list.append(row)
    return tabulate(
        param_list, headers=["Params", *header_list], tablefmt="fancy_outline"
    )
