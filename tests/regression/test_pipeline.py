"""Regression tests for entire rendering pipeline."""
from renderingpipeline.adaptor import OutputParams
from renderingpipeline.components import Plasma, TFCoil, PfCoils, Cryostat
from renderingpipeline.reactor import Reactor
from renderingpipeline.views import View
from pathlib import Path
import pytest


def test_pipelines(tmp_path):
    """Run full render pipelines using Process and Bluemira inputs files.

    Parameters
    ----------
    tmp_path : PosixPath
        Temporary directory to save rendered images to.
    """
    # TODO parameterise with Bluemira input file too.
    data_dir = Path(__file__).parent / "data"
    input_file_path = data_dir / "EUDEMO_MFILE.DAT"

    input_file = OutputParams.from_file(str(input_file_path))

    reactor1 = Reactor(
        plasma=Plasma(input_file),
        tfcoils=TFCoil(input_file),
        pfcoils=PfCoils(input_file),
        cryostat=Cryostat(input_file),
    )

    view = View(reactor1)
    view.tf_thick()
    view.key()

    # Save "view_test.png" in temporary test dir
    reactor1.save_image(tmp_path / "view_test")

    # Check .png has been produced
    png_exists = len(list(tmp_path.glob("*.png"))) > 0
    assert png_exists
