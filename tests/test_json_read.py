import json
from dataclasses import asdict
from pathlib import Path

import pytest

from extract_bluemira_params import BlueOutputParams


class Testfilein:
    def setup_method(self):
        self.test = BlueOutputParams(R_0=9, r_fw_ob_in=12.1, n_TF=18, q_95=3.5, tau_e=3)

    def test_params_from_file(self):
        file_path = Path(__file__).parent / "example_params.json"
        with open(str(file_path), "r") as fh:
            json_test = json.load(fh)

        for count, (key, value) in enumerate(asdict(self.test).items()):
            if key != "file_name":
                assert value == pytest.approx((json_test[str(key)]["value"]))
            else:
                assert value is None or isinstance(value, str)
