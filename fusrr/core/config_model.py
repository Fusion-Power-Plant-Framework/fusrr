import re
from dataclasses import dataclass
from typing import Generic, Optional, Self, TypeVar

from pydantic import BaseModel

S = TypeVar("S", bound=BaseModel)


@dataclass(frozen=True)
class Scene(Generic[S]):
    name: str
    state: S


class SceneStateSelect(BaseModel, Generic[S]):
    component: str
    state: S


class SceneConfig(BaseModel, Generic[S]):
    name: str
    state: S
    select: list[SceneStateSelect[S]] | None = None

    def get_applicable_scene(self, component_name: str) -> Scene[S]:
        """Returns the state for a given component name if it exists."""
        for select in self.select or []:
            if re.fullmatch(select.component, component_name):
                return Scene(name=self.name, state=select.state)
        return Scene(name=self.name, state=self.state)


class ProjectConfig(BaseModel, Generic[S]):
    scenes: list[SceneConfig[S]]
