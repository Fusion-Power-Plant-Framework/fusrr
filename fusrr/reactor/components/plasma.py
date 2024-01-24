import math
from collections.abc import Iterable

import numpy as np

from fusrr.base.object import FusrrSceneObject
from fusrr.base.scene import FusrrScene
from fusrr.base.tools import create_mesh
from fusrr.reactor.reactor_params import FusrrReactorParams


class Plasma(FusrrSceneObject):
    def __init__(self, reactor_params: FusrrReactorParams):
        # all the things here
        self.params = reactor_params
        super().__init__("Plasma", None)

    def _build(self) -> None:
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

        self.xs1 = -(r1 * np.cos(angs1) - x1)
        self.ys1 = r1 * np.sin(angs1)
        self.xs2 = -(r2 * np.cos(angs2) - x2)
        self.ys2 = r2 * np.sin(angs2)

    def _self_construct(self, scene: FusrrScene) -> None:
        for _x, _y in zip(
            (self.xs1, self.xs2), (self.ys1, self.ys2), strict=True
        ):
            self.create_mesh(_x, _y)
        scene.select_object(self.name)

    def create_mesh(
        self,
        x_coords: Iterable[float],
        y_coords: Iterable[float],
    ):
        """Create the vertices of the plasma array for plasma mesh."""
        with create_mesh(self.name) as m:
            for x, y in zip(x_coords, y_coords, strict=True):
                m.verts.new((x, y, 0))
