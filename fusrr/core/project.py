from __future__ import annotations

from collections import deque
from os import PathLike
from pathlib import Path
from typing import TYPE_CHECKING, Generator

from fusrr.base.utils import load_json
from fusrr.core.scene import SceneState
from fusrr.hooks._hook_state import HOOK_STATE

if TYPE_CHECKING:
    from contextvars import Context

    from fusrr.core.component import _Component


class ProjectContext:
    def __init__(self):
        self._stk = deque()
        self._ctx_reg: dict[tuple[int, ...], Context] = {}
        self._current_scene: SceneState | None = None

    def set_current_scene(self, scene: SceneState) -> None:
        """Sets the current scene state for the project context."""
        self._current_scene = scene

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

    def current_scene_for(self, name: str) -> SceneState:
        """Returns the current scene state for a given matching name."""
        return SceneState(name)


class FusrrProject:
    def __init__(
        self,
        project_name: str,
        *,
        root_components: list[_Component],
        project_config: dict | PathLike | None = None,
        output_directory: PathLike | None = None,
        overwrite: bool = False,
        default_scene: SceneState | None = None,
    ):
        self._project_name = project_name
        self._root_components = root_components
        self._project_directory = (
            Path(output_directory) if output_directory else Path.cwd()
        )
        self._config = (
            load_json(project_config)
            if isinstance(project_config, PathLike)
            else project_config
            if isinstance(project_config, dict)
            else None
        )
        self._overwrite = overwrite

        self._default_scene = default_scene

        if self._config is None and self._default_scene is None:
            raise ValueError("A default scene or config must be provided.")

    def next_scene(self) -> Generator[SceneState]:
        """Generates the next scene state for the project."""
        if self._default_scene:
            yield self._default_scene
        else:
            # Here you would implement logic to
            # generate scenes based on the project configuration.
            # For now, we yield an empty SceneState.
            yield SceneState("default_scene")

    def on_start(self) -> None:
        """Initializes the project context and prepares the project."""
        pass

    def on_save_scene(self, scene: SceneState) -> None:
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
    rcs = project._root_components
    p_ctxs = [ProjectContext() for _ in rcs]
    for scene in project.next_scene():
        for rc, p_ctx in zip(rcs, p_ctxs, strict=True):
            p_ctx.set_current_scene(scene)
            rc.run(p_ctx)
    project.on_finish()
