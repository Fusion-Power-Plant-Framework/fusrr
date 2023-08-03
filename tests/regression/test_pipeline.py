"""Regression tests for entire rendering pipeline."""
from pathlib import Path

from renderingpipeline.reactor import Reactor
from renderingpipeline.views import View


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

    reactor1 = Reactor.reactor_from_file(input_file_path=input_file_path)

    view = View(reactor1)
    view.tf_thick()
    view.key()

    # Save "view_test.png" in temporary test dir
    view.save_image(tmp_path / "view_test")

    # Check .png has been produced
    png_exists = len(list(tmp_path.glob("*.png"))) > 0
    assert png_exists
