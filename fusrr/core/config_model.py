import re
from dataclasses import dataclass
from typing import Generic, Optional, Self, TypeVar

from pydantic import BaseModel

S = TypeVar("S", bound=BaseModel)


@dataclass(frozen=True)
class SceneState(Generic[S]):
    scene_name: str
    state: S


class SceneStateSelect(BaseModel, Generic[S]):
    component: str
    state: S


class SceneConfig(BaseModel, Generic[S]):
    name: str
    state: S
    select: list[SceneStateSelect[S]] | None = None

    def get_applicable_state(self, component_name: str) -> SceneState[S]:
        """Returns the state for a given component name if it exists."""
        for select in self.select or []:
            if re.fullmatch(select.component, component_name):
                return SceneState(scene_name=self.name, state=select.state)
        return SceneState(scene_name=self.name, state=self.state)


class ProjectConfig(BaseModel, Generic[S]):
    scenes: list[SceneConfig[S]]
