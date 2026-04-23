import numpy as np
import bpy
from pydantic import BaseModel

from fusrr import component
from fusrr.core.config_model import ProjectConfig, Scene, SceneConfig
from fusrr.core.project import run_project
from fusrr.core.vectors import Vec3
from fusrr.hooks.base import Designer
from fusrr.hooks.hooks import useDesigner
from fusrr.modelling.blender.component import BlenderComp, BlenderCompound
from fusrr.modelling.blender.project import BlenderProject
from fusrr.modelling.blender.tools.mesh_tools import add_cube


class SimpleSceneState(BaseModel):
    n_cubes: int
    to_scale: float


@component
def cube(scale: Vec3, location: Vec3):
    """Builds a simple cube."""

    def builder(comp_name: str) -> bpy.types.Object:
        return add_cube(
            name=comp_name,
            scale=scale,
            location=location,
        )

    return BlenderComp(obj_builder=builder)


class CubeCurveDesigner(Designer):
    def __init__(self, n_cubes: int, to_scale: float, directions: list[str]):
        self.n_cubes = n_cubes
        self.to_scale = to_scale
        self.directions = directions

    def run(self):
        """Designs a curve of cubes."""
        # Generate scales linearly from 1 to self.to_scale
        scales = np.linspace(1, self.to_scale, self.n_cubes)
        # Compute x positions so cubes are spaced by their scale (no overlap)
        positions = []
        x = 1.0
        for s in scales:
            x += s
            positions.append(x)
            x += s

        # Generate y positions using a sinusoidal wave
        amplitude = 5.0  # adjust as needed
        frequency = 2 * np.pi / max(1, self.n_cubes - 1)
        y_positions = [
            amplitude * np.sin(i * frequency) for i in range(self.n_cubes)
        ]

        # Build the (scale, location) pairs
        self.vals = [
            (Vec3.ONE * s, Vec3(x, y, 0.0))
            for s, x, y in zip(scales, positions, y_positions, strict=False)
        ]


@component
def cube_curve(*, scene: Scene[SimpleSceneState]):
    """Creates a curve of cubes."""
    d = useDesigner(
        CubeCurveDesigner(
            n_cubes=scene.state.n_cubes,
            to_scale=scene.state.to_scale,
            directions=[],
        ),
        [scene.state.n_cubes, scene.state.to_scale],
    )
    comps = [
        cube(name=f"cube_{i}", scale=scale, location=location)
        for i, (scale, location) in enumerate(d.vals, start=1)
    ]
    return BlenderCompound(comps)


if __name__ == "__main__":
    run_project(
        BlenderProject(
            "simple_scene",
            root_components=[cube_curve()],
            overwrite=True,
            project_config=ProjectConfig(
                scenes=[
                    SceneConfig(
                        name="scene 1",
                        state=SimpleSceneState(n_cubes=20, to_scale=0.5),
                    ),
                    SceneConfig(
                        name="scene 2",
                        state=SimpleSceneState(n_cubes=50, to_scale=10.0),
                    ),
                ],
            ),
        ),
    )
