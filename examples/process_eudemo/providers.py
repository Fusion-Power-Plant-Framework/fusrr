from os import PathLike
from pathlib import Path

from process.io.mfile import MFile

from fusrr.hooks.hooks import provider
from fusrr.reactor.process.process_adaptor import ProcessParams


def provide_process_params(mfile_filepath: PathLike):
    fp = Path(mfile_filepath).resolve()
    if not fp.suffix == ".DAT":
        raise ValueError(
            f"Invalid file type: {fp.suffix}, path: {fp}. "
            "Is that a PROCESS file?"
        )
    return ProcessParams(MFile(filename=fp.as_posix()))


process_params_provider = provider(provide_process_params)
