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

    def tab(self):
        paramtable = [
            ["Output Parameters", "Value"],
            ["rmajor", self.rmajor],
            ["rminor", self.rminor],
            ["no_of_tfcoils", self.no_of_tfcoils],
            ["Q", self.bigq],
        ]

        table1 = tabulate(paramtable)
        print(table1)


""" DataSet1 = OutputParams(12,10,7,2) # test data
DataSet1.tab() """

mfile_path = Path("silly_data.DAT")  # insert file path here to PROCESS OUTPUT FILE .DAT
mfile = MFile(filename=str(mfile_path))
rmajor = mfile.data["rmajor"].get_scan(-1)
rminor = mfile.data["rminor"].get_scan(-1)
no_of_tfcoils = mfile.data["n_tf"].get_scan(-1)
bigq = mfile.data["bigq"].get_scan(-1)

DataSet2 = OutputParams(rmajor, rminor, no_of_tfcoils, bigq)
DataSet2.tab()
