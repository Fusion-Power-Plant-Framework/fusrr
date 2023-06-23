from dataclasses import dataclass
from pathlib import Path

from process.io.mfile import MFile
from tabulate import tabulate


@dataclass
class OutputParams:
    rmajor: float
    rminor: float
    no_of_tfcoils: float
    bigq: float

    def tab(self, set2):
        paramtable = [
            ["Output Parameters", "Data Set 1", "Data Set 2"],
            ["rmajor", self.rmajor, set2.rmajor],
            ["rminor", self.rminor, set2.rminor],
            ["no_of_tfcoils", self.no_of_tfcoils, set2.no_of_tfcoils],
            ["Q", self.bigq, set2.bigq],
        ]

        output_table = tabulate(paramtable)
        print(output_table)


def get_data(file_name=".DAT file"):
    mfile_path = Path(file_name)  # insert file path here to PROCESS OUTPUT FILE .DAT
    mfile = MFile(filename=str(mfile_path))
    rmajor = mfile.data["rmajor"].get_scan(-1)
    rminor = mfile.data["rminor"].get_scan(-1)
    no_of_tfcoils = mfile.data["n_tf"].get_scan(-1)
    bigq = mfile.data["bigq"].get_scan(-1)

    return rmajor, rminor, no_of_tfcoils, bigq


rmajor, rminor, no_of_tfcoils, bigq = get_data("silly_data.DAT")
Instance1 = OutputParams(rmajor, rminor, no_of_tfcoils, bigq)
rmajor, rminor, no_of_tfcoils, bigq = get_data("baseline_2018_MFILE.DAT")
Instance2 = OutputParams(rmajor, rminor, no_of_tfcoils, bigq)
Instance1.tab(Instance2)
