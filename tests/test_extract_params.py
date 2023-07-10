from dataclasses import asdict
from pathlib import Path

import pytest
from extract_params import OutputParams
from process.io.mfile import MFile


class TestOutputParams:
    """Test Class for extract_params"""

    def setup_method(self):
        """Setup method that is run when pytest is run"""
        self.expected_results = (18, 2.9473, 16, 38.923, 7200)
        self.observed_results = OutputParams(
            rmajor=18, rminor=2.9473, n_tf=16, bigq=38.923, tburn=7200
        )

    def test_correct_params(self):
        """Testing an attritbute of OutputParams to ensure data stored correctly"""
        assert self.observed_results.n_tf == pytest.approx(16)

    def test_correct_params_from_file(self):
        """Testing the import from MFile, ensuring all data is stored correctly"""
        mfile = MFile(Path(__file__).parent / "test_react.DAT")
        for count, (key, value) in enumerate(asdict(self.test).items()):
            if key != "file_name":
                assert value == pytest.approx((mfile.data[key]).get_scan(-1))
            else:
                assert value is None or isinstance(value, str)
