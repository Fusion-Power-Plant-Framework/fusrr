from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Any

from fusrr.hooks._hook_state import HOOK_STATE
from fusrr.hooks.base import D, P, Provided, T

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence


def _are_equal(x: Any, y: Any) -> bool:  # noqa: ANN401
    """Check if two objects are equal."""
    if type(x) is not type(y):
        return False

    # Check via the `==` operator if possible
    if hasattr(x, "__eq__"):
        with contextlib.suppress(Exception):
            return x == y

    # Fallback to identity check
    return x is y


def _deps_should_run(
    deps_a: Sequence[Any] | None, deps_b: Sequence[Any] | None
) -> bool:
    """Check if two dependency lists are equal."""
    if deps_a is None or deps_b is None:
        return True
    if len(deps_a) != len(deps_b):
        return True
    return not all(
        _are_equal(a, b) for a, b in zip(deps_a, deps_b, strict=True)
    )


def useDesigner(designer: D, deps: Sequence[Any] | None = ()) -> D:
    entry = HOOK_STATE.frame_entry_for(designer)
    if entry is None or _deps_should_run(entry.deps, deps):
        designer.run()
        HOOK_STATE.set_frame_entry(designer, deps)
        return designer
    return entry.inst


def provider(prov: Callable[P, T]) -> Provided[P, T]:
    return Provided(prov)


def useLatchProvider(
    provider: Provided[P, T], *args: P.args, **kwargs: P.kwargs
):
    """Set a provider instance by calling it with the given arguments."""
    entry = HOOK_STATE.persistent_entry_for(provider)
    if entry is None:
        inst = provider(*args, **kwargs)
        HOOK_STATE.set_persistent_entry(provider, inst)


def useProvider(provider: Provided[P, T]) -> T:
    """Use a provided instance."""
    entry = HOOK_STATE.persistent_entry_for(provider)
    if entry is None:
        raise RuntimeError(
            "This provider has not been set yet. "
            "`useSetProvider` must be called on it first."
        )
    return entry.inst
