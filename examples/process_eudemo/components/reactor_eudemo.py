from os import PathLike

from process_eudemo.components.blanket import Blanket
from process_eudemo.providers import process_params_provider

from fusrr import co_component
from fusrr.hooks import useSetCallProvider


@co_component
def EUDEMOReactor(mfile_filepath: PathLike):
    useSetCallProvider(process_params_provider, mfile_filepath)

    return [Blanket()]
