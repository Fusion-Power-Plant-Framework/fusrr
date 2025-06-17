from pydantic import BaseModel


class EUDEMOScene(BaseModel):
    start_angle: float
    end_angle: float
