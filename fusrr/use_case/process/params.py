import re
from typing import Any

from process.io.mfile import MFile


class ProcessParams:
    """Parameters required to build a PROCESS reactor,
    and methods to retrieve their values.
    """

    # Parameters used in radial build and vertical builds
    dr_bore: float
    """Central solenoid inboard radius."""

    dr_cs: float
    """Central solenoid thickness."""

    dr_cs_precomp: float
    """CS coil precompression structure thickness (m)."""

    dr_cs_tf_gap: float
    """Gap between central solenoid and TF coil (m) ."""

    dr_tf_inboard: float
    """Inboard TF coil thickness, (centrepost for ST) (m)."""

    dr_tf_shld_gap: float
    """Minimum metal-to-metal gap between TF coil and thermal shield (m)."""

    dr_shld_thermal_inboard: float
    """TF-VV thermal shield thickness, inboard (m)."""

    dr_shld_vv_gap_inboard: float
    """Gap between inboard vacuum vessel and thermal shield (m)."""

    dr_vv_inboard: float
    """Vacuum vessel inboard thickness (TF coil / shield) (m)."""

    dr_shld_inboard: float
    """Inboard shield thickness (m) ."""

    dr_blkt_inboard: float
    """Inboard blanket thickness (m)."""

    dr_fw_inboard: float
    """Inboard first wall thickness, initial estimate as calculated (m)."""

    dr_fw_plasma_gap_inboard: float
    """Gap between plasma and first wall, inboard side (m)."""

    dr_fw_plasma_gap_outboard: float
    """Gap between plasma and first wall, outboard side (m)."""

    dr_fw_outboard: float
    """Outboard first wall thickness, initial estimate as calculated (m)."""

    dr_blkt_outboard: float
    """Outboard blanket thickness (m)."""

    dr_shld_outboard: float
    """Outboard shield thickness (m)."""

    dr_vv_outboard: float
    """Vacuum vessel outboard thickness (TF coil / shield) (m)."""

    dr_shld_vv_gap: float
    """Gap between inboard vacuum vessel and thermal shield (m)."""

    dr_shld_thermal_outboard: float
    """TF-VV thermal shield thickness, outboard (m)."""

    dr_tf_outboard: float
    """Thickness of outboard TF coil legs."""

    dz_fw_plasma_gap: float
    """Vertical gap between top of plasma and first wall (m)."""

    dz_fw_upper: float
    """Upper first wall thickness (m)."""

    dz_blkt_upper: float
    """Top blanket thickness (m),
    = mean of inboard and outboard blanket thicknesses."""

    dr_shld_blkt_gap: float
    """Gap between vacuum vessel and blanket (m)."""

    dz_shld_upper: float
    """Upper shield thickness (m)."""

    dz_vv_upper: float
    """Vacuum vessel topside thickness (TF coil / shield) (m)."""

    dz_shld_vv_gap: float
    """Vertical gap between vacuum vessel and thermal shields (m)."""

    dz_shld_thermal: float
    """TF-VV thermal shield thickness, vertical build (m)."""

    dz_xpoint_divertor: float
    """Vertical gap between x-point and divertor (m)."""

    dz_divertor: float
    """Divertor structure vertical thickness (m)."""

    dz_shld_lower: float
    """Lower (under divertor) shield thickness (m)."""

    dz_vv_lower: float
    """Vacuum vessel underside thickness (TF coil / shield) (m)."""

    z_plasma_xpoint_upper: float
    """Vertical height of the upper plasma x-point (m)."""

    z_plasma_xpoint_lower: float
    """Vertical height of the lower plasma x-point (m)."""

    # For the blanket
    i_single_null: float
    """Switch for single null (1) or double null (0) plasma configuration."""

    # For the cryostat
    r_cryostat_inboard: float
    """Cryostat radius [m]."""

    dr_cryostat: float
    """Cryostat thickness (m)."""

    z_cryostat_half_inside: float
    """Cryostat height [m]."""

    # For PF coils
    dz_cs_full: float
    """Full height of the central solenoid (m)."""

    iohcl: float
    """Switch for existence (1) or not (0) of a central solenoid."""

    r_pf_coil_middle: float
    """Radius of PF coil i (m)."""

    z_pf_coil_middle: float
    """z (height) location of PF coil i (m)."""

    pfdr: float
    """PF coil i radial thickness (m)."""

    pfdz: float
    """PF coil i vertical thickness (m)."""

    # For building the Plasma
    rmajor: float
    """Plasma major radius."""

    rminor: float
    """Plasma minor radius."""

    triang95: float
    """Plasma triangularity at 95% surface."""

    kappa95: float
    """Plasma elongation at 95% surface ."""

    i_plasma_shape: float
    """Switch for plasma shape (0 for double arc, 1 for Sauter)."""

    plasma_square: float
    """Plasma squareness used by Sauter plasma shape"""

    # For TF coils
    r_tf_arc: list[float]
    """x location of arc point i on surface (m)."""

    z_tf_arc: list[float]
    """y location of arc point i on surface (m)."""

    i_tf_shape: float
    """Switch for TF coil toroidal shape:
        - =0  Default value :
            Picture frame coil for TART / PROCESS D-shape for non itart
        - =1  PROCESS D-shape : parametrise with 2 arcs."""

    n_tf_coils: float
    """Number of TF coils."""

    def __init__(self, process_mfile: MFile):
        self.mfile = process_mfile
        self._keys = set(process_mfile.data.keys())

    def __getattr__(self, name: str):
        return self.mfile.data[name].get_scan(-1)

    def __getitem__(self, name: str):
        return self.mfile.data[name].get_scan(-1)

    def get(self, name: str, default: Any = None):  # noqa: ANN401
        """Gets the value of the key with string s."""
        if self.has_key(name):
            return self[name]
        return default

    def get_with(self, s: str):
        """Gets the value of the key that matches (using regex)
        the pattern of string s.
        """
        k = self.get_key_with(s)
        return self[k]

    def get_key_with(self, rgx: str) -> str:
        """Gets the key that matches (using regex) the pattern of string s."""
        k = self.get_keys_with(rgx)
        if not k:
            raise KeyError(f"Key with {rgx} not found")
        return k[0]

    def get_keys_with(self, rgx: str | list[str]) -> list[str]:
        """Gets the keys that match (using regex) the pattern of string s."""
        if isinstance(rgx, str):
            rgx = [rgx]
        r = re.compile(r"^(" + "|".join(rgx) + ")$")
        return list(filter(r.match, self._keys))

    def n_keys_with(self, s: str) -> int:
        """Gets the number of keys that match (using regex)
        the pattern of string s.
        """
        return len(self.get_keys_with(s))

    def has_key(self, name: str) -> bool:
        """Checks if the key exists."""
        return name in self._keys

    def has_key_with(self, rgx: str) -> bool:
        """Checks if a key exists that matches (using regex)
        the pattern of string s.
        """
        return bool(self.get_keys_with(rgx))
