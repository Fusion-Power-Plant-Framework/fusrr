from __future__ import annotations

from collections import deque
from os import PathLike
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import BaseModel

from fusrr.core.config_model import ProjectConfig, S, Scene, SceneConfig
from fusrr.core.errors import SceneStopError
from fusrr.core.utils import load_json
from fusrr.hooks._hook_state import HOOK_STATE

if TYPE_CHECKING:
    from contextvars import Context

    from fusrr.core.component import FusrrComponent


class ProjectContext[S]:
    def __init__(
        self,
        *,
        ptx_id: int | None = None,
        initial_scene_config: SceneConfig[S] | None = None,
    ):
        """Initializes the project context with an empty stack
        and context registry.
        """
        self.ptx_id = ptx_id
        self._stk = deque()
        self._ctx_reg: dict[tuple[int, ...], Context] = {}
        self._cur_scene_config = initial_scene_config

    def set_scene_config(self, scene: SceneConfig[S]) -> None:
        """Sets the current scene state for the project context."""
        self._cur_scene_config = scene

    def push_key_for_context(self, key: int) -> Context:
        """Pushes the current context for a specific component ID."""
        self._stk.append(key)
        stk_key = tuple(self._stk)
        ctx = self._ctx_reg.get(stk_key)
        if ctx is None:
            ctx = HOOK_STATE.new_hook_ctx()
            self._ctx_reg[stk_key] = ctx
        return ctx

    def pop_key(self) -> None:
        """Pops the last component key from the stack."""
        if self._stk:
            self._stk.pop()
        else:
            raise IndexError("No component ID to pop from the stack.")

    def scene_for(self, name: str) -> Scene[S] | None:
        """Returns the current scene data for a given matching name."""
        if self._cur_scene_config is None:
            return None
        return self._cur_scene_config.get_applicable_scene(name, self.ptx_id)


class FusrrProject[S]:
    def __init__(
        self,
        project_name: str,
        *,
        root_components: list[FusrrComponent],
        project_config: dict | PathLike | ProjectConfig[S] | SceneConfig[S] | S,
        output_directory: PathLike | None = None,
        overwrite: bool = False,
    ):
        self.project_name = project_name
        self.root_components = root_components
        self.project_directory = (
            Path(output_directory) if output_directory else Path.cwd()
        )
        self.overwrite = overwrite

        config_dict = (
            load_json(project_config)
            if isinstance(project_config, PathLike)
            else project_config
            if isinstance(project_config, dict)
            else None
        )
        if config_dict:
            self.config = ProjectConfig.model_validate(config_dict)
        elif isinstance(project_config, ProjectConfig):
            self.config = project_config
        elif isinstance(project_config, SceneConfig):
            self.config = ProjectConfig(
                scenes=[project_config],
            )
        elif isinstance(project_config, BaseModel):
            self.config = ProjectConfig(
                scenes=[SceneConfig[S](name=project_name, state=project_config)]
            )
        else:
            raise ValueError(
                "project_config must be a dictionary, PathLike, "
                "ProjectConfig, SceneConfig, or a Pydantic model instance."
            )

    def on_start(self) -> None:
        """Initializes the project context and prepares the project."""

    def on_scene_start(self, scene_config: SceneConfig[S]) -> None:
        """Saves the current scene state."""

    def on_scene_end(self, scene_config: SceneConfig[S]) -> None:
        """Saves the current scene state."""

    def on_finish(self) -> None:
        """Finalizes the project, cleaning up resources."""


def run_project(project: FusrrProject):
    """Runs a FusrrProject, executing all root components in the defined scenes.

    Each root component is given an independent ProjectContext,
    meaning all hooks used by sub-components are isolated to
    contexts of the root components.
    """
    completed_successfully = False
    project.on_start()
    root_comps = project.root_components
    p_ctxs = [ProjectContext(ptx_id=i) for i, _ in enumerate(root_comps)]
    try:
        for scene_cfg in project.config.scenes:
            print(f"Running scene: {scene_cfg.name}")
            project.on_scene_start(scene_cfg)
            for root_comp, p_ctx in zip(root_comps, p_ctxs, strict=True):
                p_ctx.set_scene_config(scene_cfg)
                root_comp.run(p_ctx)
            project.on_scene_end(scene_cfg)
    except SceneStopError as e:
        print(f"SceneStopError raised: {e}")
    else:
        completed_successfully = True
    finally:
        if not completed_successfully:
            print("Errors occurred during the run.")
        project.on_finish()
