from __future__ import annotations

from contextvars import Context, ContextVar, copy_context
from typing import TYPE_CHECKING, Any, ClassVar

if TYPE_CHECKING:
    from collections.abc import Sequence
    from fusrr.hooks.base import Provided
    from fusrr.hooks.base import P, R, Runnable, T


class CacheEntry[T]:
    def __init__(self, inst: T, deps: Sequence[Any]):
        self.inst = inst
        self.deps = deps
        self.mark_used: bool = True


class _HookState:
    _frame_state: ContextVar[dict[type, CacheEntry]] = ContextVar("hook_state")
    _persistent_cache: ClassVar[dict[int, CacheEntry]] = {}

    @staticmethod
    def _i_key(inst: Runnable) -> type:
        """Return the defined 'key' for the instance."""
        return inst.__class__

    @staticmethod
    def _p_key(provided: Provided) -> int:
        """Return the defined 'key' for the persistent state."""
        return id(provided)

    @property
    def _frame_cache(self) -> dict[type, CacheEntry]:
        """Get the current frame's state."""
        try:
            return self._frame_state.get()
        except LookupError as e:
            raise RuntimeError(
                "No hook state is set. Use `new_hook_ctx` to create one."
            ) from e

    def frame_used_instances(self) -> tuple:
        return tuple(
            [v.inst for v in self._frame_cache.values() if v.mark_used]
        )

    def frame_entry_for(self, inst: R) -> CacheEntry[R] | None:
        """Return the cached instance."""
        return self._frame_cache.get(self._i_key(inst))

    def set_frame_entry(
        self, inst: Runnable, deps: Sequence[Any] | None = None
    ) -> None:
        """Set the cached instance in the current frame."""
        self._frame_cache[self._i_key(inst)] = CacheEntry(inst, deps or ())

    def persistent_entry_for(
        self, prov: Provided[P, T]
    ) -> CacheEntry[T] | None:
        """Return the cached instance from persistent state."""
        return self._persistent_cache.get(self._p_key(prov))

    def set_persistent_entry(self, prov: Provided[P, T], inst: T) -> None:
        """Set the cached instance in the persistent state."""
        self._persistent_cache[self._p_key(prov)] = CacheEntry(inst, ())

    def new_hook_ctx(self) -> Context:
        """Return the dependencies of the cached instance."""
        ctx = copy_context()
        ctx.run(self._frame_state.set, {})
        return ctx


HOOK_STATE = _HookState()
