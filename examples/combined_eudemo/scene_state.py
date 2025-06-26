from pydantic import BaseModel

from fusrr.modelling.blender.transform import BlenderTransform


class LightsCameraSceneState(BaseModel):
    lights: list[BlenderTransform]
    camera_transform: BlenderTransform
