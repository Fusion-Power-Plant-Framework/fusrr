import re
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

S = TypeVar("S", bound=BaseModel)


class SceneSelectState(BaseModel, Generic[S]):
    component: str
    state: S


class SceneConfig(BaseModel, Generic[S]):
    name: str
    state: S
    select: list[SceneSelectState[S]] | None = None

    def get_applicable_state(self, component_name: str) -> S:
        """Returns the state for a given component name if it exists."""
        for select in self.select or []:
            if re.fullmatch(select.component, component_name):
                return select.state
        return self.state


class ProjectConfig(BaseModel, Generic[S]):
    scenes: list[SceneConfig[S]]
