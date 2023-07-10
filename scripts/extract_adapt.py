"""
Takes PROCESS (.DAT) or BLUEMIRA (.json) files and outputs parameters the same format.

"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from process.io.mfile import MFile
import argparse
import json

argParser = argparse.ArgumentParser()
argParser.add_argument("-fn", "--file_name", help="input file")
args = argParser.parse_args()

def adapt_bluemira(input_data):
    """Converts generic name into BLUEMIRA parameters for use in class method"""
    from Dictionary_Basic import bluemira_param
    blue_out = []
    for param_name in input_data:
        blue_name = bluemira_param[param_name]
        blue_out.append(blue_name)
    return blue_out


@dataclass
class OutputParams:
    """DataClass to store generic output parameters

    Returns:
        dataclass: listed parameters + file_name which is optional in case of manual
        input for OutputParams
    """

    rmajor: float
    No_TF: float
    file_name: Optional[str] = None

    @classmethod
    def from_file(cls, file_name: str) -> OutputParams:
        """Makes instance of class from file name and assigns values to generic parameters"""
        file_path = Path(file_name) 
        output_names = list(cls.__annotations__.keys())
        output_names.pop(output_names.index("file_name"))

        variables = {}
        if file_name.endswith(".DAT"):
            from Dictionary_Basic import process_param
            data_obj = MFile(filename=str(file_path))
            for name_1 in output_names:
               try:
                    variables[name_1] = data_obj.data[process_param[name_1]].get_scan(-1)
               except KeyError:
                   continue
            
        elif file_name.endswith(".json"):
            with open(str(file_path), "r") as fh:
                data_obj = json.load(fh)
            program_names = adapt_bluemira(output_names)
            for name_1, name_2 in zip(output_names, program_names):
                try:
                    variables[name_1] = data_obj[name_2]["value"]
                except KeyError:
                    continue

        return cls(file_name=file_name, **variables)


file_name = str(args.file_name)
generic_output = OutputParams.from_file(file_name)
print('generic_output=', generic_output)
 
