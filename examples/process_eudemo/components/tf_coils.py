from collections.abc import Iterable
from dataclasses import dataclass
from math import radians

import numpy as np
import bmesh
from bmesh.types import BMVert
from mathutils import Matrix, Vector
from process.geometry.tfcoil_geometry import (
    tfcoil_geometry_d_shape,
    tfcoil_geometry_rectangular_shape,
)

from examples.process_eudemo.providers import process_params_provider
from examples.process_eudemo.scene import EUDEMOScene
from fusrr import component
from fusrr.blender.blender_component import BlenderComp, BlenderCompound
from fusrr.blender.tools.mesh_tools import (
    mesh_add_edges_from_points,
)
from fusrr.core.vectors import Vec3
from fusrr.hooks import Designer, useDesigner, useProvider
from fusrr.materials.base import MetallicMaterial
from fusrr.materials.models import MaterialColour, MaterialValueZeroToOne
from fusrr.reactor.process.process_adaptor import ProcessParams


@dataclass
class TFCoilDShape:
    angle: float
    ib_leg_start: Vec3
    ib_leg_end: Vec3
    ob_leg_arch_pts: Iterable[Iterable[Vec3]]


class TFCoilsDesigner(Designer):
    def __init__(
        self, params: ProcessParams, start_angle: float, end_angle: float
    ):
        self.params = params
        self.start_angle = start_angle
        self.end_angle = end_angle

    def run(self) -> None:
        tf_ib_tk = self.params.tfc_inleg
        rt_angle = np.pi / 2
        rt_angle2 = 2 * rt_angle

        x1 = self.params["xarc(1)"]
        y1 = self.params["yarc(1)"]
        x2 = self.params["xarc(2)"]
        y2 = self.params["yarc(2)"]
        x3 = self.params["xarc(3)"]
        y3 = self.params["yarc(3)"]
        x4 = self.params["xarc(4)"]
        y4 = self.params["yarc(4)"]
        x5 = self.params["xarc(5)"]
        y5 = self.params["yarc(5)"]
        if y3 != 0:
            print(
                "TF coil geometry: The value of yarc(3) is not zero, "
                "but should be."
            )

        # Check for TF coil shape
        i_tf_shape = int(self.params.get("i_tf_shape", 1))

        if i_tf_shape == 2:  # noqa: PLR2004
            rects = tfcoil_geometry_rectangular_shape(
                x1=x1,
                x2=x2,
                x4=x4,
                x5=x5,
                y1=y1,
                y2=y2,
                y4=y4,
                y5=y5,
                tfcth=tf_ib_tk,
            )
            face_verts = None
        else:
            rects, face_verts = tfcoil_geometry_d_shape(
                x1=x1,
                x2=x2,
                x3=x3,
                x4=x4,
                x5=x5,
                y1=y1,
                y2=y2,
                y4=y4,
                y5=y5,
                tfcth=tf_ib_tk,
                rtangle=rt_angle,
                rtangle2=rt_angle2,
            )
            path_pts = []
            for face in face_verts:
                seg_pts = []
                for vert in face:
                    x, z = vert
                    seg_pts.append(Vec3(x, 0, z))
                path_pts.append(seg_pts)

            angle_per_coil = 360 / self.params["n_tf"]

            self.tf_cls = [
                TFCoilDShape(
                    angle=n * angle_per_coil,
                    ib_leg_start=Vec3(x5, 0, y1),
                    ib_leg_end=Vec3(x5, 0, y5),
                    ob_leg_arch_pts=path_pts,
                )
                for n in range(int(self.params["n_tf"]))
                if self.start_angle < n * angle_per_coil < self.end_angle
            ]


@component
def TFCoils(*, scene: EUDEMOScene):
    """Component to design the TF coils of a PROCESS reactor."""
    params = useProvider(process_params_provider)
    # designer depends on the end angle of the scene
    # add it to the useDesigner parameters
    d = useDesigner(
        TFCoilsDesigner(params, scene.start_angle, scene.end_angle),
        [scene.start_angle, scene.end_angle],
    )

    return BlenderCompound(
        [
            TFCoil(name=f"tf_{n}", cl=tf_cl)
            for n, tf_cl in enumerate(d.tf_cls, start=1)
        ]
    )


@component
def TFCoil(cl: TFCoilDShape):
    def builder(_obj, m: bmesh.types.BMesh) -> None:
        # Inner (straight) leg
        mesh_add_edges_from_points(m, [cl.ib_leg_start, cl.ib_leg_end])
        # Outer (arch) leg
        for line_seg in cl.ob_leg_arch_pts:
            mesh_add_edges_from_points(m, line_seg)

        edges = m.edges
        extruded = bmesh.ops.extrude_face_region(m, geom=edges)
        # Move extruded geometry
        translate_verts = [v for v in extruded["geom"] if isinstance(v, BMVert)]
        bmesh.ops.translate(m, vec=Vec3.Y.tup, verts=translate_verts)

        extruded = bmesh.ops.extrude_face_region(m, geom=m.faces)

        # Get the new faces from the extruded geometry
        new_faces = [
            f for f in extruded["geom"] if isinstance(f, bmesh.types.BMFace)
        ]

        # Calculate the centroid of the faces
        center = Vector((0, 0, 0))
        for f in new_faces:
            center += f.calc_center_median()
        center /= len(new_faces)

        verts = list({v for f in new_faces for v in f.verts})

        # Scale the entire mesh by its center point
        scale_factor = 1 + 0.1  # Change this to your desired scale factor
        bmesh.ops.scale(
            m,
            vec=(Vec3.ONE * scale_factor).tup,
            space=Matrix.Translation(-center),
            verts=verts,
        )

        rotation_X = Matrix.Rotation(radians(cl.angle), 4, "Z")
        bmesh.ops.rotate(
            m, cent=Vec3.ZERO.tup, matrix=rotation_X, verts=m.verts
        )

    return BlenderComp(
        builder=builder,
        material=MetallicMaterial(
            base_colour=MaterialColour(0.1, 0.1, 0.1, 1),
            roughness=MaterialValueZeroToOne(0.1),
        ),
    )
