import math
from collections.abc import Iterable

import numpy as np

from fusrr.base.mesh_tools import add_edges_to_mesh, revolve_mesh, set_mesh_on
from fusrr.base.models import Vec3
from fusrr.base.object import FusrrSceneObject
from fusrr.base.scene import FusrrScene
from fusrr.reactor.reactor_params import FusrrReactorParams


class PFCoils(FusrrSceneObject):
    def __init__(self, reactor_params: FusrrReactorParams):
        # all the things here
        self.params = reactor_params
        super().__init__("pf_coils", None)

    def _setup(self) -> None:
        r0 = self.params.rmajor
        a = self.params.rminor
        delta = 1.5 * self.params.delta_95
        kappa = (1.1 * self.params.kappa95) + 0.04
        i_single_null = self.params.i_single_null

        x1 = (2.0 * r0 * (1.0 + delta) - a * (delta**2 + kappa**2 - 1.0)) / (
            2.0 * (1.0 + delta)
        )
        x2 = (2.0 * r0 * (delta - 1.0) - a * (delta**2 + kappa**2 - 1.0)) / (
            2.0 * (delta - 1.0)
        )
        r1 = 0.5 * math.sqrt(
            (a**2 * ((delta + 1.0) ** 2 + kappa**2) ** 2) / ((delta + 1.0) ** 2)
        )
        r2 = 0.5 * math.sqrt(
            (a**2 * ((delta - 1.0) ** 2 + kappa**2) ** 2) / ((delta - 1.0) ** 2)
        )
        theta1 = np.arcsin((kappa * a) / r1)
        theta2 = np.arcsin((kappa * a) / r2)
        inang = 1.0 / r1
        outang = 1.5 / r2
        if i_single_null == 0:
            angs1 = np.linspace(
                -(inang + theta1) + np.pi,
                (inang + theta1) + np.pi,
                256,
                endpoint=True,
            )
            angs2 = np.linspace(
                -(outang + theta2), (outang + theta2), 256, endpoint=True
            )
        elif i_single_null < 0:
            angs1 = np.linspace(
                -(inang + theta1) + np.pi, theta1 + np.pi, 256, endpoint=True
            )
            angs2 = np.linspace(-theta2, (outang + theta2), 256, endpoint=True)
        else:
            angs1 = np.linspace(
                -theta1 + np.pi, (inang + theta1) + np.pi, 256, endpoint=True
            )
            angs2 = np.linspace(-(outang + theta2), theta2, 256, endpoint=True)

        xs1 = -(r1 * np.cos(angs1) - x1)
        zs1 = r1 * np.sin(angs1)
        xs2 = -(r2 * np.cos(angs2) - x2)
        zs2 = r2 * np.sin(angs2)

        self.edge_1 = [Vec3(x, 0, z) for x, z in zip(xs1, zs1, strict=True)]
        self.edge_2 = [Vec3(x, 0, z) for x, z in zip(xs2, zs2, strict=True)]

    def _construct(self, scene: FusrrScene) -> None:
        obj = scene.execute_create_object(self.name)
        with set_mesh_on(obj) as m:
            add_edges_to_mesh(m, self.edge_1)
            add_edges_to_mesh(m, self.edge_2)
            revolve_mesh(m, m.edges, Vec3.ZERO, Vec3.Z, 360)
        scene.select_object(self.name)
