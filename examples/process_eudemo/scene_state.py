from pydantic import BaseModel


class ProcessEUDEMOSceneState(BaseModel):
    start_angle: float
    end_angle: float
