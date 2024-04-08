from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from fusrr.base.frame import FusrrContextFrame

CFT = TypeVar("CFT", bound=FusrrContextFrame)

ObjConstructor = Callable[[], None]
