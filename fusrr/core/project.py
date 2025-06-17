from __future__ import annotations

from collections import deque
from os import PathLike
from pathlib import Path
from typing import TYPE_CHECKING, Generic

from fusrr.base.utils import load_json
from fusrr.core.config_model import ProjectConfig, S, SceneConfig
from fusrr.hooks._hook_state import HOOK_STATE

if TYPE_CHECKING:
    from collections.abc import Generator
    from contextvars import Context

    from fusrr.core.component import FusrrComponent


class ProjectContext(Generic[S]):
    def __init__(self):
        self._stk = deque()
        self._ctx_reg: dict[tuple[int, ...], Context] = {}
        self._current_sc: SceneConfig[S] | None = None

    def set_current_scene_config(self, scene: SceneConfig[S]) -> None:
        """Sets the current scene state for the project context."""
        self._current_sc = scene

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

    def current_scene_for(self, name: str) -> S:
        """Returns the current scene state for a given matching name."""
        if self._current_sc is None:
            raise RuntimeError("No current scene configuration set. ")
        return self._current_sc.get_applicable_state(name)


class FusrrProject(Generic[S]):
    def __init__(
        self,
        project_name: str,
        *,
        root_components: list[FusrrComponent],
        project_config: dict | PathLike | ProjectConfig[S] | None = None,
        output_directory: PathLike | None = None,
        overwrite: bool = False,
        default_scene_config: SceneConfig[S] | None = None,
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
        if config_dict is None and default_scene_config is None:
            raise ValueError("A default scene or config must be provided.")

        self.config = (
            ProjectConfig.model_validate(config_dict)
            if config_dict
            else ProjectConfig(
                scenes=[default_scene_config] if default_scene_config else []
            )
        )

    def on_start(self) -> None:
        """Initializes the project context and prepares the project."""
        pass

    def on_save_scene(self, scene: S) -> None:
        """Saves the current scene state."""
        # Here you would implement the logic to save the scene state
        # to a file or database, depending on your project requirements.
        pass

    def on_finish(self) -> None:
        """Finalizes the project, cleaning up resources."""
        # Here you would implement any cleanup logic needed for the project.
        pass


def run_project(project: FusrrProject):
    project.on_start()
    root_comps = project.root_components
    p_ctxs = [ProjectContext() for _ in root_comps]
    for scene in project.config.scenes:
        for root_comp, p_ctx in zip(root_comps, p_ctxs, strict=True):
            p_ctx.set_current_scene_config(scene)
            root_comp.run(p_ctx)
    project.on_finish()
