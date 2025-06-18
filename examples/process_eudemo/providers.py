from os import PathLike
from pathlib import Path

from process.io.mfile import MFile

from fusrr.hooks import provider
from fusrr.use_case.process import ProcessParams


def _load_process_params(mfile_filepath: PathLike) -> ProcessParams:
    """Loads the PROCESS params from a .DAT file."""
    fp = Path(mfile_filepath).resolve()
    if not fp.suffix == ".DAT":
        raise ValueError(
            f"Invalid file type: {fp.suffix}, path: {fp}. "
            "Is that a PROCESS file?"
        )
    return ProcessParams(MFile(filename=fp.as_posix()))


process_params_provider = provider(_load_process_params)
