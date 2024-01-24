from __future__ import annotations

from typing import TYPE_CHECKING
from collections.abc import Callable

if TYPE_CHECKING:
    from fusrr.base.scene import FusrrScene

Constructor = Callable[["FusrrScene"], None]
OptionalConstructor = Constructor | None
