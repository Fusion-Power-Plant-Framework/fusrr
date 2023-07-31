"""test for python_entry"""
from pathlib import Path

import renderingpipeline.blender_tools as bt


def test_save_image(tmp_path):
    """Test to assert if render has been saved"""
    path = tmp_path / "render.png"
    bt.save_image(path)
    assert Path(path).exists()
