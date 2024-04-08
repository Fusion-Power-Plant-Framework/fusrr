from process.geometry.geometry_parameterisations import RectangleGeometry

from fusrr.base.models import Vec3


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
