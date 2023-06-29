from dataclasses import asdict
from pathlib import Path

import pytest
from process.io.mfile import MFile

from extract_params import OutputParams


class Testfilein:
    def setup_method(self):
        self.results = (18, 2.9473, 16, 38.923, 7200)
        self.test = OutputParams(
            rmajor=18, rminor=2.9473, n_tf=16, bigq=38.923, tburn=7200
        )

    def test_correct_params(self):
        for (key, value), result in zip(asdict(self.test).items(), self.results):
            assert value == pytest.approx(result)

    def test_correct_params_from_file(self):
        mfile = MFile(Path(__file__).parent / "example_process_params.DAT")
        for count, (key, value) in enumerate(asdict(self.test).items()):
            if key != "file_name":
                assert value == pytest.approx((mfile.data[key]).get_scan(-1))
            else:
                assert value is None or isinstance(value, str)
