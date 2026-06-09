from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from fusrr.modelling.blender.transform import BlenderTransform


class LightsCameraSceneState(BaseModel):
    lights: list[BlenderTransform]
    camera_transform: BlenderTransform
