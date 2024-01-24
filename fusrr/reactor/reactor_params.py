from dataclasses import dataclass


@dataclass
class FusrrReactorParams:
    """Models the input params required for to build a FusrrReactor object."""

    rmajor: float
    n_tf: float
    rminor: float
    delta_95: float
    kappa95: float
    i_single_null: float
    x1: float
    x2: float
    x3: float
    x4: float
    x5: float
    y1: float
    y2: float
    y3: float
    y4: float
    y5: float
    tfc_inleg: float
    vvblgap: float
    d_vv_in: float
    d_vv_out: float
    blnktth: float
    bore: float
    cs_rad_th: float
    precomp: float
    cs_rad_gap: float
    tftsgap: float
    thshield_ib: float
    thshldgap: float
    shldith: float
    vvblgapi: float
    blnkith: float
    fwith: float
    scrapthi: float
    rminori: float
    rminoro: float
    scraptho: float
    fwoth: float
    blnkoth: float
    vvblgapo: float
    shldoth: float
    vvtfgap: float
    thshield_ob: float
    tfth_outleg: float
    rminor_kappa: float
    vgaptop: float
    fwtth: float
    vvblgap: float
    shldtth: float
    d_vv_top: float
    vgap2: float
    thshield_vb: float
    vgap: float
    divfix: float
    shldlth: float
    d_vv_bot: float
    tftsgap: float
    triang: float
    bore: float
    ohdz: float
    iohcl: float
    rpf1: float
    rpf2: float
    rpf3: float
    rpf4: float
    rpf5: float
    rpf6: float
    zpf1: float
    zpf2: float
    zpf3: float
    zpf4: float
    zpf5: float
    zpf6: float
    pfdr1: float
    pfdr2: float
    pfdr3: float
    pfdr4: float
    pfdr5: float
    pfdr6: float
    pfdz1: float
    pfdz2: float
    pfdz3: float
    pfdz4: float
    pfdz5: float
    pfdz6: float
    rdewex: float
    ddwex: float
    zdewex: float
    casthi: float

    # file_path: Optional[Path] = None

    # @classmethod
    # def from_file(cls, file_path: Path) -> OutputParams:
    #     """
    #     Makes instance of class from file name
    #     and assigns values to generic parameters
    #     """
    #     file_path = Path(file_path)
    #     output_names = list(cls.__annotations__.keys())
    #     output_names.pop(output_names.index("file_path"))

    #     if file_path.suffix == ".DAT":
    #         parameters = process_file_adaptor(output_names, file_path)

    #     elif file_path.suffix == ".json":
    #         parameters = bluemira_file_adaptor(output_names, file_path)

    #     return cls(file_path=file_path, **parameters)
