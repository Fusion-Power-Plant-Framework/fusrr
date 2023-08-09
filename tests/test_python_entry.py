"""test for python_entry"""
from pathlib import Path

from renderingpipeline.views import View


def test_save_image(tmp_path):
    """Test to assert if render has been saved"""
    path = tmp_path / "render.png"
    View.save_image(path)
    assert Path(path).exists()
