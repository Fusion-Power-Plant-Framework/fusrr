import numpy as np
from pydantic import BaseModel

from fusrr import component
from fusrr.core.component import Comp, Compound
from fusrr.core.config_model import ProjectConfig, Scene, SceneConfig
from fusrr.core.project import FusrrProject, run_project
from fusrr.core.vectors import Vec3
from fusrr.hooks.base import Designer
from fusrr.hooks.hooks import useDesigner
from fusrr.modelling.blender.component import BlenderComp
from fusrr.modelling.blender.project import BlenderProject
from fusrr.modelling.blender.tools.mesh_tools import add_cube


class SimpleSceneState(BaseModel):
    n_cubes: int
    to_scale: float


@component
def cube(scale: Vec3, location: Vec3):
    def builder(comp_name: str):
        """Builds a simple cube."""
        add_cube(
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
        vals = []
        curr_scale = 1
        dir_pts = np.linspace(1, self.n_cubes, self.n_cubes)
        locs = [Vec3.X * pt for pt in dir_pts]
        scale_pts = np.linspace(1, self.to_scale, self.n_cubes)
        scls = [Vec3.ONE * pt for pt in scale_pts]
        self.vals = list(zip(scls, locs, strict=True))
        # for i in range(self.n_cubes):
        #     scale = Vec3.ONE * curr_scale
        #     curr_scale += self.to_scale/self.n_cubes
        #     location = Vec3(i * 2.0, 0.0, 0.0)  # Example spacing
        #     direction = self.directions[i % len(self.directions)]
        #     vals.append((scale, location, direction))
        # self.vals:tuple[Vec3, Vec3] = vals


@component
def cube_curve(*, scene: Scene[SimpleSceneState]):
    d = useDesigner(
        CubeCurveDesigner(
            n_cubes=scene.state.n_cubes,
            to_scale=scene.state.to_scale,
            directions=[],
        ),
        [scene.state.n_cubes],
    )
    return Compound(
        [
            cube(name=f"cube_{i}", scale=scale, location=location)
            for i, (scale, location) in enumerate(d.vals)
        ]
    )


if __name__ == "__main__":
    run_project(
        BlenderProject(
            "Process_EUDEMO",
            root_components=[cube_curve()],
            overwrite=True,
            project_config=ProjectConfig(
                scenes=[
                    SceneConfig(
                        name="scene 1",
                        state=SimpleSceneState(n_cubes=10, to_scale=2.0),
                    ),
                    SceneConfig(
                        name="scene 2",
                        state=SimpleSceneState(n_cubes=10, to_scale=1.0),
                    ),
                    SceneConfig(
                        name="scene 3",
                        state=SimpleSceneState(n_cubes=5, to_scale=1.0),
                    ),
                ],
            ),
        ),
    )
