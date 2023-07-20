"""
Takes PROCESS (.DAT) or BLUEMIRA (.json) files and outputs parameters the same format.

"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from process.io.mfile import MFile

from renderingpipline.dictionary_basic import bluemira_param, process_param


def process_file_adaptor(input_data, filepath):
    """
    Imports data from mfile and assigns name and value

    Returns
    -------
        Dictionary containing generic parameters and their values
    """
    variables = {}
    data_obj = MFile(filename=str(filepath))
    for name_1 in input_data:
        try:
            variables[name_1] = data_obj.data[process_param[name_1]].get_scan(-1)
        except KeyError:
            continue
    return variables


def bluemira_file_adaptor(input_data, filepath):
    """
    Converts generic name into BLUEMIRA parameters to then be reassigned values and names

    Returns
    -------
        Dictionary containing generic parameters and their values
    """
    variables = {}
    with open(str(filepath), "r") as fh:
        data_obj = json.load(fh)
    for name in input_data:
        try:
            variables[name] = data_obj[bluemira_param[name]]["value"]
        except KeyError:
            continue
    return variables


@dataclass
class OutputParams:
    """DataClass to store generic output parameters

    Returns
    -------
        dataclass: listed parameters, their values + file_name which
        is optional in case of manual input for OutputParams
    """

    rmajor: float
    n_tf: float
    rminor: float
    delta_95: float
    kappa95: float
    i_single_null: float
    x1: float
    x2: float
    x3: float
    x4: float
    x5: float
    y1: float
    y2: float
    y3: float
    y4: float
    y5: float
    tfc_inleg: float
    vvblgap: float
    d_vv_in: float
    d_vv_out: float
    blnktth: float
    bore: float
    cs_rad_th: float
    precomp: float
    cs_rad_gap: float
    tftsgap: float
    thshield_ib: float
    thshldgap: float
    shldith: float
    vvblgapi: float
    blnkith: float
    fwith: float
    scrapthi: float
    rminori: float
    rminoro: float
    scraptho: float
    fwoth: float
    blnkoth: float
    vvblgapo: float
    shldoth: float
    vvtfgap: float
    thshield_ob: float
    tfth_outleg: float
    rminor_kappa: float
    vgaptop: float
    fwtth: float
    vvblgap: float
    shldtth: float
    d_vv_top: float
    vgap2: float
    thshield_vb: float
    vgap: float
    divfix: float
    shldlth: float
    d_vv_bot: float
    tftsgap: float

    file_name: Optional[str] = None

    @classmethod
    def from_file(cls, file_name: str) -> OutputParams:
        """
        Makes instance of class from file name
        and assigns values to generic parameters
        """
        file_path = Path(file_name)
        output_names = list(cls.__annotations__.keys())
        output_names.pop(output_names.index("file_name"))

        if file_name.endswith(".DAT"):
            parameters = process_file_adaptor(output_names, file_path)

        elif file_name.endswith(".json"):
            parameters = bluemira_file_adaptor(output_names, file_path)

        return cls(file_name=file_name, **parameters)
