from __future__ import annotations

from contextvars import Context, ContextVar, copy_context
from typing import TYPE_CHECKING, Any, ClassVar, Generic

from fusrr.hooks.base import P, Provided, Runnable, T

if TYPE_CHECKING:
    from collections.abc import Sequence


class CacheEntry(Generic[T]):
    def __init__(self, inst: T, deps: Sequence[Any]):
        self.inst = inst
        self.deps = deps


class _HookState:
    _frame_state: ContextVar[dict[type, CacheEntry]] = ContextVar("hook_state")
    _persistent_state: ClassVar[dict[int, CacheEntry]] = {}

    @staticmethod
    def _i_key(inst: Runnable) -> type:
        """Return the defined 'key' for the instance."""
        return inst.__class__

    @staticmethod
    def _p_key(provided: Provided) -> int:
        """Return the defined 'key' for the persistent state."""
        return id(provided)

    def _frame_get(self) -> dict[type, CacheEntry]:
        """Get the current frame's state."""
        try:
            return self._frame_state.get()
        except LookupError as e:
            raise RuntimeError(
                "No hook state is set. Use `new_hook_ctx` to create one."
            ) from e

    def frame_entry_for(self, inst: Runnable) -> CacheEntry[T] | None:
        """Return the cached instance."""
        return self._frame_get().get(self._i_key(inst))

    def set_frame_entry(
        self, inst: Runnable, deps: Sequence[Any] | None = None
    ) -> None:
        """Set the cached instance in the current frame."""
        self._frame_state.get()[self._i_key(inst)] = CacheEntry(
            inst, deps or ()
        )

    def persistent_entry_for(
        self, prov: Provided[P, T]
    ) -> CacheEntry[T] | None:
        """Return the cached instance from persistent state."""
        return self._persistent_state.get(self._p_key(prov))

    def set_persistent_entry(self, prov: Provided[P, T], inst: T) -> None:
        """Set the cached instance in the persistent state."""
        self._persistent_state[self._p_key(prov)] = CacheEntry(inst, ())

    def new_hook_ctx(self) -> Context:
        """Return the dependencies of the cached instance."""
        ctx = copy_context()
        ctx.run(self._frame_state.set, {})
        return ctx


HOOK_STATE = _HookState()
