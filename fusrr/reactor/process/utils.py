from process.geometry.geometry_parameterisations import RectangleGeometry

from fusrr.base.models import Vec3
from fusrr.reactor.process.process_mappings import (
    RADIAL_BUILD,
    vertical_lower,
    vertical_upper,
)


def process_rect_to_vec3_path_points(geom: RectangleGeometry):
    """Return closed points in Vec3 for the rectangle."""
    x = geom.anchor_x
    z = geom.anchor_z
    dx = geom.width / 2
    dz = geom.height / 2

    tr = Vec3(x + dx, 0, z + dz)
    br = Vec3(x + dx, 0, z - dz)
    bl = Vec3(x - dx, 0, z - dz)
    tl = Vec3(x - dx, 0, z + dz)

    return [tr, br, bl, tl, tr]


def cumul_setup(params_dict):
    """Sets up each part of the blanket.

    Parameters
    ----------
    params_dict : dictionary
        dictionary of dataclass

    Returns:
    -------
    Two dictionaries
        Upper and lower builds of blanket
    """
    # TODO: improve

    upper = {}
    cumulative_upper = {}
    subtotal = 0
    for item in vertical_upper:
        upper[item] = float(params_dict[item])
        subtotal += float(upper[item])
        cumulative_upper[item] = subtotal

    lower = {}
    cumulative_lower = {}
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
    component_shape :
        Instance of dataclass

    Returns:
    -------
    Radial build section

    """
    complete = False
    cumulative_build = 0
    for item in RADIAL_BUILD:
        if item in ("rminori", "rminoro", "rminor"):
            cumulative_build += component_shape.rminor
        elif item in ("vvblgapi", "vvblgapo", "vvblgap"):
            cumulative_build += component_shape.vvblgap
        elif "d_vv_in" in item:
            cumulative_build += component_shape.d_vv_in
        elif "d_vv_out" in item:
            cumulative_build += component_shape.d_vv_out  # c_shldith
        # TODO: not sure if this works?:
        else:
            cumulative_build += getattr(component_shape, item)
        if item == section:
            complete = True
            break

    if complete is False:
        print("radial build parameter ", section, " not found")
    return cumulative_build
