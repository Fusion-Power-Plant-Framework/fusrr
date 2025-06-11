from __future__ import annotations

import inspect
from functools import wraps
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable
    from contextvars import Context

    from fusrr.new_base.project import ProjectContext
    from fusrr.new_base.scene import SceneState


class Comp:
    def __init__(self, builder: Callable[[], None] | None = None):
        self._builder = builder

    def build(self) -> None:
        if self._builder is not None:
            self._builder()
        else:
            raise NotImplementedError("Builder function is not defined.")


class ComponentConstructor:
    def __init__(
        self,
        function: Callable[..., Comp | list[FusrrComponent]],
        args: tuple[Any, ...] | None = None,
        kwargs: dict[str, Any] | None = None,
    ):
        sig = inspect.signature(function)

        self.fn = function
        self.scene_in_params = "scene" in sig.parameters

        self._args = args or ()
        self._kwargs = kwargs or {}

        if (
            self.scene_in_params
            and sig.parameters["scene"].kind
            is not inspect.Parameter.KEYWORD_ONLY
        ):
            raise TypeError(
                f"`{self.component_name}` must use reserved parameter 'scene' "
                "as a keyword-only argument, i.e.:\n"
                f"`def {self.component_name}(..., *, scene: SceneState): ...`."
            )

        if "scene" in self._kwargs:
            raise TypeError(
                f"Component `{self.component_name}` was passed "
                "reserved parameter 'scene' in its kwargs."
            )

    def __call__(
        self,
        *,
        ctx: Context | None = None,
        scene: SceneState | None = None,
    ) -> Comp | list[FusrrComponent]:
        """Calls the component function with the provided context and scene."""
        if scene is None and self.scene_in_params:
            raise ValueError(
                "Scene must be provided to the component constructor, "
                "scene is required by the component."
            )
        fn, args, kwargs = self.fn, self._args, self._kwargs.copy()
        if self.scene_in_params:
            kwargs["scene"] = scene
        if ctx:
            return ctx.run(fn, *args, **kwargs)
        return fn(*args, **kwargs)

    @property
    def component_name(self) -> str:
        return self.fn.__name__

    @property
    def _key_basis(self) -> tuple:
        """Returns a tuple of the function name and its module."""
        return (
            inspect.getfile(self.fn),
            inspect.signature(self.fn),
            self.component_name,
        )

    @property
    def stable_key(self) -> int:
        """Returns a hash that uniquely identifies this constructor
        across renders (deterministically).

        It's derived from the function file path, signature and name.
        """
        return hash(self._key_basis)


class FusrrComponent:
    def __init__(self, constructor: ComponentConstructor):
        self._constructor = constructor

    def run(self, p: ProjectContext):
        ctx = p.push_key_for_context(self._constructor.stable_key)
        scene = p.get_current_comp_scene(self._constructor.component_name)
        constructed = self._constructor(ctx=ctx, scene=scene)

        if isinstance(constructed, Comp):
            constructed.build()
        elif isinstance(constructed, list):
            for item in constructed:
                if isinstance(item, FusrrComponent):
                    item.run(p)
                else:
                    raise TypeError("List items must be FusrrComponents.")
        else:
            raise TypeError(
                "Constructor must return a Comp, FusrrComponent, or a list of FusrrComponents."
            )

        p.pop_key()


def component(
    function: Callable[..., Comp | list[FusrrComponent]],
) -> Callable[..., FusrrComponent]:
    @wraps(function)
    def wrapper(*args, **kwargs) -> FusrrComponent:
        return FusrrComponent(ComponentConstructor(function, args, kwargs))

    return wrapper
