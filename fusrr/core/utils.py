from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    from os import PathLike


def load_json(config_path: PathLike) -> dict[str, Any]:
    """Load a Fusrr configuration file."""
    with Path(config_path).open() as f:
        return json.load(f)


T = TypeVar("T")


def run_list_async_concurrently[T](
    itr: Iterable[T], func_getter: Callable[[T], Callable]
) -> list:
    """Run a list of functions concurrently."""
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(func_getter(i)) for i in itr]
        results = []
        for future in as_completed(futures):
            results.append(future.result())  # noqa: PERF401, better exception handling
        return results
