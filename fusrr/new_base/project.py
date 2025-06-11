from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING

from fusrr.new_base.hooks._hook_state import HOOK_STATE
from fusrr.new_base.scene import SceneState

if TYPE_CHECKING:
    from contextvars import Context


class ProjectContext:
    def __init__(self, scene_state: SceneState | None = None):
        self._stk = deque()
        self._ctx_reg: dict[tuple[int, ...], Context] = {}

    def push_key_for_context(self, comp_id: int) -> Context:
        """Pushes the current context for a specific component ID."""
        self._stk.append(comp_id)
        stk_key = tuple(self._stk)
        ctx = self._ctx_reg.get(stk_key)
        if ctx is None:
            ctx = HOOK_STATE.new_hook_ctx()
            self._ctx_reg[stk_key] = ctx
        return ctx

    def pop_key(self) -> None:
        """Pops the last component ID from the stack."""
        if self._stk:
            self._stk.pop()
        else:
            raise IndexError("No component ID to pop from the stack.")

    def get_current_comp_scene(self, comp_name: str) -> SceneState:
        return SceneState(name=comp_name)
