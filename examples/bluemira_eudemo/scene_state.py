from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from pathlib import Path


class BmEUDEMOSceneState(BaseModel):
    gltf_filepath: Path | str
