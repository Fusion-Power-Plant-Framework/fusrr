from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    from pathlib import Path


def load_fusrr_config(
    config_path: Path,
) -> dict[str, Any]:
    """Load a Fusrr configuration file."""
    with config_path.open() as f:
        j = json.load(f)
    # may add more functionality here
    return j  # noqa: RET504


T = TypeVar("T")


def run_list_async_concurrently(
    itr: Iterable[T], func_getter: Callable[[T], Callable]
) -> list:
    """Run a list of functions concurrently."""
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(func_getter(i)) for i in itr]
        results = []
        for future in as_completed(futures):
            results.append(future.result())  # noqa: PERF401, better exception handling
        return results
