from dataclasses import dataclass, fields

from process.io.mfile import MFile


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


fusrr_to_process_mapping = {
    "rmajor": "rmajor",
    "n_tf": "n_tf",
    "rminor": "rminor",
    "delta_95": "triang95",
    "kappa95": "kappa95",
    "i_single_null": "i_single_null",
    # TF Coil use
    "x1": "xarc(1)",
    "x2": "xarc(2)",
    "x3": "xarc(3)",
    "x4": "xarc(4)",
    "x5": "xarc(5)",
    "y1": "yarc(1)",
    "y2": "yarc(2)",
    "y3": "yarc(3)",
    "y4": "yarc(4)",
    "y5": "yarc(5)",
    "tfc_inleg": "tfcth",
    "d_vv_in": "d_vv_in",
    "d_vv_out": "d_vv_out",
    "blnktth": "blnktth",
    "tftort": "tftort",
    "casthi": "casthi",
    # Blanket use
    "bore": "bore",
    "cs_rad_th": "ohcth",
    "precomp": "precomp",
    "cs_rad_gap": "gapoh",
    "tftsgap": "tftsgap",
    "thshield_ib": "thshield_ib",
    "thshldgap": "gapds",
    "shldith": "shldith",
    "vvblgapi": "vvblgapi",
    "blnkith": "blnkith",
    "fwith": "fwith",
    "scrapthi": "scrapli",
    "rminori": "rminor",
    "rminoro": "rminoro",
    "scraptho": "scraplo",
    "fwoth": "fwoth",
    "blnkoth": "blnkoth",
    "vvblgapo": "vvblgapo",
    "shldoth": "shldoth",
    "vvtfgap": "gapsto",
    "thshield_ob": "thshield_ob",
    "tfth_outleg": "tfthko",
    "rminor_kappa": "rminor*kappa",
    "vgaptop": "vgaptop",
    "fwtth": "fwtth",
    "vvblgap": "vvblgap",
    "shldtth": "shldtth",
    "d_vv_top": "d_vv_top",
    "vgap2": "vgap2",
    "thshield_vb": "thshield_vb",
    "vgap": "vgap",
    "divfix": "divfix",
    "shldlth": "shldlth",
    "d_vv_bot": "d_vv_bot",
    "triang": "triang",
    # PF coil use
    "ohdz": "ohdz",
    "iohcl": "iohcl",
    "rpf1": "rpf(01)",
    "rpf2": "rpf(02)",
    "rpf3": "rpf(03)",
    "rpf4": "rpf(04)",
    "rpf5": "rpf(05)",
    "rpf6": "rpf(06)",
    "zpf1": "zpf(01)",
    "zpf2": "zpf(02)",
    "zpf3": "zpf(03)",
    "zpf4": "zpf(04)",
    "zpf5": "zpf(05)",
    "zpf6": "zpf(06)",
    "pfdr1": "pfdr01",
    "pfdr2": "pfdr02",
    "pfdr3": "pfdr03",
    "pfdr4": "pfdr04",
    "pfdr5": "pfdr05",
    "pfdr6": "pfdr06",
    "pfdz1": "pfdz01",
    "pfdz2": "pfdz02",
    "pfdz3": "pfdz03",
    "pfdz4": "pfdz04",
    "pfdz5": "pfdz05",
    "pfdz6": "pfdz06",
    "rdewex": "rdewex",
    "ddwex": "ddwex",
    "zdewex": "zdewex",
}


def process_file_adaptor(process_mfile: MFile) -> FusrrReactorParams:
    """Imports data from mfile and assigns name and value.

    Returns:
        Dictionary containing generic parameters and their values
    """
    fusrr_process_param_values = {}

    for param_label in fields(FusrrReactorParams):
        fusrr_label = param_label.name
        process_label = fusrr_to_process_mapping[fusrr_label]

        try:
            fusrr_process_param_values[fusrr_label] = process_mfile.data[
                process_label
            ].get_scan(-1)
        except KeyError:
            continue

    return FusrrReactorParams(**fusrr_process_param_values)
