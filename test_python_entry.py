from pathlib import Path

from python_entry import save_image

imagepath = "render.png"


def test_save_image():
    """Test to assert if render has been saved"""
    assert Path(imagepath).exists() == True
