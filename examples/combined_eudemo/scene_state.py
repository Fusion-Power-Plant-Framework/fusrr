from pydantic import BaseModel

from fusrr.modelling.blender.transform import BlenderTransform


class CombinedLCSState(BaseModel):
    lights: list[BlenderTransform]
    camera_transform: BlenderTransform
