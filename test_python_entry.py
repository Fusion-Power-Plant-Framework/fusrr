"""Test to locate png in specified directory. Ensure no other pngs in file or the test will always pass."""
import os

from python_entry import save_image

imagepath = "render.png"


def test_save_image():
    save_image(imagepath)
    assert os.path.isfile(imagepath) == True
