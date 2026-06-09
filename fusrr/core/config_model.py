from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Generic, TypeVar

from pydantic import BaseModel

S = TypeVar("S", bound=BaseModel)


@dataclass(frozen=True)
class Scene(Generic[S]):
    name: str
    state: S


class SceneStateSelect(BaseModel, Generic[S]):
    component: str
    state: S | list[S | None]


class SceneConfig(BaseModel, Generic[S]):
    name: str
    state: S | list[S]
    select: list[SceneStateSelect[S]] | None = None

    def get_applicable_scene(
        self,
        component_name: str,
        arr_select_id: int | None = None,
    ) -> Scene[S]:
        """Returns the state for a given component name if it exists."""
        ss = self.state
        for select in self.select or []:
            if re.fullmatch(select.component, component_name):
                ss = select.state

        if isinstance(ss, list):
            if arr_select_id is None:
                raise ValueError(
                    "arr_select_id must be set to access "
                    "array based scene data. Are you using run_project?"
                )
            ss = ss[arr_select_id]

        if ss is None:
            raise RuntimeError(
                f"Scene state for component '{component_name}' "
                f"and index {arr_select_id} is None."
            )

        return Scene(name=self.name, state=ss)


class ProjectConfig(BaseModel, Generic[S]):
    scenes: list[SceneConfig[S]]
