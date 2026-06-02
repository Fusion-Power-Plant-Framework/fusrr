import math
import bpy

from examples.combined_eudemo.scene_state import LightsCameraSceneState
from fusrr import Scene, component
from fusrr.core.vectors import Vec3
from fusrr.modelling.blender import BlenderComp, BlenderTransform
from fusrr.modelling.blender.component import BlenderCompound
from fusrr.modelling.blender.tools.mesh_tools import add_plane
from fusrr.modelling.blender.tools.object_tools import add_camera, add_light


@component
def Light(transform: BlenderTransform):
    """Add a light to the scene."""

    def builder(name: str) -> bpy.types.Object:
        return add_light(
            name,
            light_type="SPOT",
            energy=10000,
            spot_angle_rad=math.pi / 2,
        )

    return BlenderComp(obj_builder=builder, transform=transform)


@component
def Lights(*, scene: Scene[LightsCameraSceneState]):
    """Add multiple lights to the scene."""
    lights = [
        Light(trans, name=f"light_{i}")
        for i, trans in enumerate(scene.state.lights)
    ]
    return BlenderCompound(lights)


@component
def Camera(*, scene: Scene[LightsCameraSceneState]):
    """Add a camera to the scene."""

    def builder(name: str) -> bpy.types.Object:
        return add_camera(name, activate_for_scene=True)

    return BlenderComp(
        obj_builder=builder,
        transform=scene.state.camera_transform,
    )


@component
def PlaneGrounding():
    """A component that adds a plane background to the scene."""

    def builder(name: str = "plane_grounding") -> bpy.types.Object:
        return add_plane(name)

    return BlenderComp(
        obj_builder=builder,
        transform=BlenderTransform(
            position=Vec3(0, 0, -25),
            scale=Vec3(100, 100, 1),
        ),
    )


@component
def PlaneBacking():
    """A component that adds a plane background to the scene."""

    def builder(name: str = "plane_backing") -> bpy.types.Object:
        return add_plane(name)

    return BlenderComp(
        obj_builder=builder,
        transform=BlenderTransform(
            position=Vec3(0, 30, 0),
            scale=Vec3(100, 100, 1),
            rotation=Vec3(math.pi / 2, 0, 0),
        ),
    )


@component
def Background():
    """A component that adds a plane background to the scene."""
    return BlenderCompound([PlaneGrounding(), PlaneBacking()])


@component
def LightsCamera():
    """A component that adds lights and a camera to the scene."""
    return BlenderCompound([Lights(), Camera(), Background()])
