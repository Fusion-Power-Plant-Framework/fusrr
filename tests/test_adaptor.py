"""test for adaptor"""

from renderingpipline.adaptor import (
    OutputParams,
    bluemira_file_adaptor,
    process_file_adaptor,
)

# test to see if generic outputs are the same
# test to see if dictionary is returned
# check that an error is given if not .DAT or .json


def test_from_file():
    """Test to assert if dictionary is produced"""
    output = OutputParams.from_file("scripts/baseline_2018_MFILE.DAT")
    assert type(output) is dict == True
