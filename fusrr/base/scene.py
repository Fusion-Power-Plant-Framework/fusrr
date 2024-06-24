from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, TypedDict

import bmesh
from kink import di

from fusrr.base.entity.collection import FusrrWorldCollection
from fusrr.base.entity.object import FusrrWorldObject
from fusrr.base.models import Vec3
from fusrr.base.world_state import FusrrWorldState
from fusrr.blender.mesh_tools import mesh_add_edges_from_points
from fusrr.blender.object_tools import (
    add_boolean_modifier,
    set_object_visibility,
)
from fusrr.blender.scene_tools import get_objects, get_objects_by_pattern

if TYPE_CHECKING:
    import bpy

    from fusrr.base.entity.object_properties import ObjTransformProperties
    from fusrr.base.pipeline import FusrrBuildPipeline


@dataclass
class FusrrSceneObjectConfig:
    """A FusrrSceneObjectsConfig is a configuration for a FusrrSceneObjects."""

    name: str
    pattern: str | None = None

    slice_start: float | None = None
    slice_end: float | None = None
    slice_size: float | None = None

    visible: bool | None = None


@dataclass
class FusrrSceneCameraConfig:
    """A FusrrSceneCameraConfig is a configuration for a FusrrSceneCamera."""

    transform: ObjTransformProperties | None = None
    look_at: str | None = None


@dataclass
class FusrrSceneConfig:
    """A FusrrSceneConfig is a configuration for a FusrrScene."""

    name: str
    camera: FusrrSceneCameraConfig
    based_on: str | None = None
    objects: list[FusrrSceneObjectConfig] | None = None
    new_scene: bool = False


class FusrrScene:
    """A FusrrScene is a specific arrangement of objects in the project,
    in a new scene.

    The scene generates an image based on its configuration.

    The scene controls the camera and may be based off other scenes.
    """

    def __init__(
        self,
        name: str,
        camera: FusrrSceneCameraConfig,
        based_on: str | None = None,
        objects: list[FusrrSceneObjectConfig] | None = None,
        output_directory: Path | str | None = None,
        world_state: FusrrWorldState | None = None,
    ):
        self._name = name
        self._camera_config = camera
        self._based_on = based_on
        self._objects_config = objects
        self._output_directory = (
            Path(output_directory) if output_directory else Path.cwd()
        )
        self._world_state = world_state or di[FusrrWorldState]

    @property
    def name(self) -> str:
        """The name of the scene."""
        return self._name

    def _execute_camera(self) -> None:
        pass

    def _execute_objects(self) -> None:
        if not self._objects_config:
            return

        slice_tools = []
        for oc in self._objects_config:
            objs = (
                get_objects_by_pattern(oc.pattern)
                if oc.pattern
                else get_objects({oc.name})
            )
            if not objs:
                raise ValueError(
                    f"No objects found - "
                    f"name: {oc.name}, "
                    f"pattern: {oc.pattern}, "
                    f"scene: '{self.name}'."
                    if oc.pattern
                    else f"No object found - "
                    f"name: {oc.name}, "
                    f"scene: '{self.name}'."
                )

            for obj in objs:
                if oc.visible is not None:
                    set_object_visibility(obj, visibility=oc.visible)

                if oc.slice_start is not None or oc.slice_end is not None:
                    slice_tools.append(
                        FusrrSceneObjectCutter(
                            target_obj=obj,
                            cut_angle_deg_start=oc.slice_start,
                            cut_angle_deg_end=oc.slice_end,
                            size=oc.slice_size,
                        )
                    )
        if slice_tools:
            c = FusrrSceneToolsCollection(self.name, slice_tools=slice_tools)
            c.run()

    def execute(self):
        """Execute this scene."""
        self._execute_objects()
        self._execute_camera()


class FusrrSceneToolsCollection(FusrrWorldCollection):
    def __init__(
        self,
        scene_name: str,
        slice_tools: list[FusrrSceneObjectCutter],
    ):
        super().__init__(f"tools.{scene_name}")
        self._slice_tools = slice_tools

    def setup(self, pipeline: FusrrBuildPipeline) -> None:
        for st in self._slice_tools:
            pipeline.add(st)


class FusrrSceneObjectCutter(FusrrWorldObject):
    """A FusrrSceneObjectCutter is an object that boolean
    cuts another target object.

    """

    def __init__(
        self,
        target_obj: bpy.types.Object,
        cut_angle_deg_start: float | None = None,
        cut_angle_deg_end: float | None = None,
        size: float | None = None,
    ):
        super().__init__(f"cutter.{target_obj.name}")
        self._target_obj = target_obj
        self._start_deg = (
            cut_angle_deg_start % 360 if cut_angle_deg_start else 0
        )
        self._end_deg = cut_angle_deg_end % 360 if cut_angle_deg_end else 360
        self._size = size if size is not None else 30

        if self._end_deg <= self._start_deg:
            raise ValueError(
                f"End angle must be greater than start - "
                f"start: {self._start_deg}, "
                f"end: {self._end_deg}."
            )

    def prepare(self) -> None:
        cut_plane_poly_points = []

        cut_plane_poly_points.append(Vec3(0, 0, 0))

        # the start point
        cut_plane_poly_points.append(
            Vec3(
                math.cos(math.radians(self._start_deg)),
                math.sin(math.radians(self._start_deg)),
                0,
            )
        )

        # this only works because we're forcing end > start,
        if self._start_deg < 90 and self._end_deg > 90:  # noqa: PLR2004
            cut_plane_poly_points.append(Vec3(0, 1, 0))
        if self._start_deg < 180 and self._end_deg > 180:  # noqa: PLR2004
            cut_plane_poly_points.append(Vec3(-1, 0, 0))
        if self._start_deg < 270 and self._end_deg > 270:  # noqa: PLR2004
            cut_plane_poly_points.append(Vec3(0, -1, 0))

        # the end point
        cut_plane_poly_points.append(
            Vec3(
                math.cos(math.radians(self._end_deg)),
                math.sin(math.radians(self._end_deg)),
                0,
            )
        )

        # scale the points
        cut_plane_poly_points = [
            p * self._size - Vec3(0, 0, self._size)
            for p in cut_plane_poly_points
        ]

        self._cut_plane_poly_points = cut_plane_poly_points

    def construct(self, obj, m) -> None:
        mesh_add_edges_from_points(
            m, self._cut_plane_poly_points, close=True, to_face=True
        )

        extruded = bmesh.ops.extrude_face_region(m, geom=m.faces)
        # Get the new faces from the extruded geometry
        new_verts = [
            f for f in extruded["geom"] if isinstance(f, bmesh.types.BMVert)
        ]
        bmesh.ops.translate(
            m, vec=(Vec3.Z * self._size * 2).tup, verts=new_verts
        )

        add_boolean_modifier(
            self._target_obj,
            modifier_object=obj,
            modifier_name=self.name + "_mod",
        )

        set_object_visibility(obj, visibility=False)
