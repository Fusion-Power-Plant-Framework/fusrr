from collections.abc import Iterable

import numpy as np
from process.geometry.tfcoil_geometry import (
    tfcoil_geometry_d_shape,
    tfcoil_geometry_rectangular_shape,
)

from fusrr.base.mesh_tools import add_edges_to_mesh_from_points, new_mesh_for
from fusrr.base.models import Vec3
from fusrr.base.object import FusrrSceneObject
from fusrr.base.scene import FusrrScene
from fusrr.reactor.process.components.process_component import ProcessComponent
from fusrr.reactor.process.process_adaptor import ProcessParams


class ProcessTFCoils(ProcessComponent):
    def __init__(self, reactor_params: ProcessParams):
        super().__init__("tf_coils", reactor_params)

    def _setup(self):
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
                "TF coil geometry: The value of yarc(3) is not zero, but should be."
            )

        # Check for TF coil shape
        i_tf_shape = int(self.params.get("i_tf_shape", 1))

        if i_tf_shape == 2:
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
            self.add_object(
                ProcessTFCoilD(
                    name="tf_coil_d",
                    ib_leg_start=Vec3(x5, 0, y1),
                    ib_leg_end=Vec3(x5, 0, y5),
                    ob_leg_arch_pts=path_pts,
                )
            )

    def _construct(self, scene: FusrrScene) -> None:
        # empty for the parent component, for now
        scene.execute_create_object(self.name)


class ProcessTFCoilD(FusrrSceneObject):
    def __init__(
        self,
        name: str,
        ib_leg_start: Vec3,
        ib_leg_end: Vec3,
        ob_leg_arch_pts: Iterable[Iterable[Vec3]],
    ):
        self.ib_leg_start = ib_leg_start
        self.ib_leg_end = ib_leg_end
        self.ob_leg_arch_pts = ob_leg_arch_pts
        super().__init__(name)

    def _construct(self, scene: FusrrScene) -> None:
        obj = scene.execute_create_object(self.name)
        with new_mesh_for(obj) as m:
            # Inner (straight) leg
            add_edges_to_mesh_from_points(
                m, [self.ib_leg_start, self.ib_leg_end]
            )
            # Outer (arch) leg
            for line_seg in self.ob_leg_arch_pts:
                add_edges_to_mesh_from_points(m, line_seg)
