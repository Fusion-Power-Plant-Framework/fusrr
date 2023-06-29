import os

from python_entry import save_image

imagepath = "/home/blender_venv/Image_name.png"


def test_save_image():
    save_image(imagepath)
    assert os.path.isfile(imagepath) == True
