from os import PathLike

from process_eudemo.components.blanket import Blanket
from process_eudemo.components.cryostat import Cryostat
from process_eudemo.components.pf_coils import PFCoils
from process_eudemo.components.plasma import Plasma
from process_eudemo.components.tf_coils import TFCoils
from process_eudemo.components.vacuum_vessel import VacuumVessel
from process_eudemo.providers import process_params_provider

from fusrr import component
from fusrr.blender import BlenderCompound
from fusrr.hooks import useLatchProvider


@component
def EUDEMO_Reactor(mfile_filepath: PathLike):
    useLatchProvider(process_params_provider, mfile_filepath)

    return BlenderCompound(
        [
            Plasma(),
            Blanket(),
            VacuumVessel(),
            PFCoils(),
            TFCoils(),
            Cryostat(),
        ]
    )
