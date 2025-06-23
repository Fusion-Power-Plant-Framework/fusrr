from pathlib import Path

from pydantic import BaseModel


class BmEUDEMOSceneState(BaseModel):
    gltf_filepath: Path | str
