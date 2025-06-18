from os import PathLike

from examples.process_eudemo.components.blanket import Blanket
from examples.process_eudemo.components.cryostat import Cryostat
from examples.process_eudemo.components.pf_coils import PFCoils
from examples.process_eudemo.components.plasma import Plasma
from examples.process_eudemo.components.tf_coils import TFCoils
from examples.process_eudemo.components.vacuum_vessel import VacuumVessel
from examples.process_eudemo.providers import process_params_provider
from fusrr import component
from fusrr.hooks import useSetProvider
from fusrr.modelling.blender import BlenderCompound


@component
def EUDEMO_Reactor(mfile_filepath: PathLike):
    useSetProvider(process_params_provider, mfile_filepath)

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
