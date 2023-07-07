"""
Extracts Data From PROCESS or BLUEMIRA output file and renames parameters to make them generic for rendering

"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional
from process.io.mfile import MFile
import argparse
import json

argParser = argparse.ArgumentParser()
argParser.add_argument("-fn", "--file_name", help="input file")
args = argParser.parse_args()

def adapt_process(input_data):
    """Convert parameters from PROCESS dictionary to generic param names"""
    from Dictionary_Basic import process_param
    dd = {}
    for param_name, param_value in input_data.items():
        try:   #if param found in both dict then reassigns name
            generic_name = process_param[param_name] 
            dd[generic_name] = param_value
        except KeyError:
            continue
    return dd

def adapt_bluemira(input_data):
    """Convert parameters from BLUEMIRA dictionary to generic param names"""
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

        mfile_path = Path(file_name)  # insert file path here to PROCESS OUTPUT FILE .DAT
        mfile = MFile(filename=str(mfile_path))

        output_params = list(cls.__annotations__.keys())  # Creates list to find and remove file_name from mfile data
        output_params.pop(output_params.index("file_name"))  # Removes file_name to match key values to attributes

        proc_input = cls(file_name=file_name,**{param: mfile.data[param].get_scan(-1) for param in output_params},)
        process_input = asdict(proc_input)
        generic_out = adapt_process(process_input)
        return generic_out

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
        
        a = {}
        # extracting the output paramters dictionary from json file
        for param in output_params:
            a[param] = jsondata[str(param)]["value"]
        return cls(file_name=file_name, **a)
        

file_name = str(args.file_name)

if file_name.endswith('.json'): #for bm files convert to dictionary and adapt
    blue_input = BlueOutputParams.from_blue_file(file_name)
    bluemira_input = asdict(blue_input)
    generic_output = adapt_bluemira(bluemira_input)
elif file_name.endswith('.DAT'): #adapt for process
    generic_output = OutputParams.from_file(file_name)
 
