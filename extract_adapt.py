"""
Extracts Data From PROCESS Output files and returns generic output for rendering

Mash up of extract_params and Adapter_attempt

Currently set to 5 output params but can add any key from .DAT file

"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

from process.io.mfile import MFile
import argparse

argParser = argparse.ArgumentParser()
argParser.add_argument("-fn", "--file_name", help=".DAT input file")
args = argParser.parse_args()

def adapt_process(input_data):
    """Convert parameters from PROCESS dataclasses to generic format in dictionary"""
    from Dictionary_Basic import process_param
    dd = {}
    for param_name, param_value in input_data.items():
        try:    #if param found in both dict then:
            generic_name = process_param[param_name] 
            print('gn=', generic_name)
            dd[generic_name] = param_value
        except KeyError:
            continue
    return dd

def adapt_bluemira(input_data):
    """Convert parameters from BLUEMIRA dataclesses to generic format (WIP)"""
    from Dictionary_Basic import bluemira_param
    dc = {}
    for param_name, param_value in input_data.items():
        try:
            generic_name = bluemira_param[param_name]
            dc[generic_name] = param_value
        except KeyError:
            continue
    return dc


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
        #print('output_params=', output_params)

        if MFile:
            
            proc_input = cls(file_name=file_name,
            **{param: mfile.data[param].get_scan(-1) for param in output_params},)
            process_input = asdict(proc_input)
            print('process_input =', process_input)
            generic_out = adapt_process(process_input)
            return generic_out

#        elif 
#Ongoing work: adding functionality for BLUEMIRA files



file_name = str(args.file_name)
generic_output = OutputParams.from_file(file_name)
print('final out =', generic_output)
#print statements not reqiured but useful to understand the data manipulation
