from fusrr.mapping import RADIAL_BUILD, vertical_lower, vertical_upper


def cumul_setup(params_dict):
    """Sets up each part of the blanket

    Parameters
    ----------
    blanket_shape_dict : dictionary
        dictionary of dataclass

    Returns
    -------
    Two dictionaries
        Upper and lower builds of blanket
    """
    upper = dict()
    cumulative_upper = dict()
    subtotal = 0
    for item in vertical_upper:
        upper[item] = float(params_dict[item])
        subtotal += float(upper[item])
        cumulative_upper[item] = subtotal

    lower = dict()
    cumulative_lower = dict()
    subtotal = 0
    for item in vertical_lower:
        lower[item] = float(params_dict[item])
        subtotal -= float(lower[item])
        cumulative_lower[item] = subtotal

    return cumulative_upper, cumulative_lower, upper, lower


def cumulative_radial_build(section, component_shape):
    """Function for calculating the cumulative radial build up to and
    including the given section.


    Parameters
    ----------
    section :
        Section being built
    blanket_shape :
        Instance of dataclass

    Returns
    -------
    Radial build section

    """
    complete = False
    cumulative_build = 0
    for item in RADIAL_BUILD:
        if item == "rminori" or item == "rminoro" or item == "rminor":
            cumulative_build += component_shape.rminor
        elif item == "vvblgapi" or item == "vvblgapo" or item == "vvblgap":
            cumulative_build += component_shape.vvblgap
        elif "d_vv_in" in item:
            cumulative_build += component_shape.d_vv_in
        elif "d_vv_out" in item:
            cumulative_build += component_shape.d_vv_out  # c_shldith
        # TODO not sure if this works?:
        else:
            cumulative_build += getattr(component_shape, item)
        if item == section:
            complete = True
            break

    if complete is False:
        print("radial build parameter ", section, " not found")
    return cumulative_build
