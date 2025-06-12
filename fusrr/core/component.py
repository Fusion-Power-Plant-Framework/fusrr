from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from functools import wraps
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from fusrr.core.project import ProjectContext

if TYPE_CHECKING:
    from collections.abc import Callable
    from contextvars import Context

    from fusrr.core.project import ProjectContext
    from fusrr.core.scene import SceneState


class Comp:
    def __init__(self, builder: Callable[[], None] | None = None):
        self._builder = builder

    def build(self) -> None:
        if self._builder is not None:
            self._builder()
        else:
            raise NotImplementedError("Builder function is not defined.")


_CT = TypeVar("_CT", bound=Comp | list["FusrrComponent"])


class _ComponentConstructor(Generic[_CT]):
    def __init__(
        self,
        function: Callable[..., _CT],
        args: tuple[Any, ...] | None = None,
        kwargs: dict[str, Any] | None = None,
    ):
        self.fn = function
        self.file = inspect.getfile(self.fn)
        self.sig = inspect.signature(self.fn)
        self.scene_in_params = "scene" in self.sig.parameters
        self.args = args or ()
        self.kwargs = kwargs or {}

        self._ad_id: int | None = None

        if (
            self.scene_in_params
            and self.sig.parameters["scene"].kind
            is not inspect.Parameter.KEYWORD_ONLY
        ):
            raise TypeError(
                f"`{self}` must use reserved parameter 'scene' "
                "as a keyword-only argument, i.e.:\n"
                f"`def {self}(..., *, scene: SceneState): ...`."
            )
        if "scene" in self.kwargs:
            raise TypeError(
                f"`{self}` was passed reserved parameter 'scene' in its kwargs."
            )

    def __call__(
        self, *, ctx: Context | None = None, scene: SceneState | None = None
    ) -> _CT:
        """Calls the component function with the provided context and scene."""
        if scene is None and self.scene_in_params:
            raise ValueError(
                "Scene must be provided to the component constructor, "
                "scene is required by the component."
            )
        fn, args, kwargs = self.fn, self.args, self.kwargs.copy()
        if self.scene_in_params:
            kwargs["scene"] = scene
        if ctx:
            return ctx.run(fn, *args, **kwargs)
        return fn(*args, **kwargs)

    def set_ad_id(self, ad_id: int) -> None:
        """Sets the ad_id, used when the component is part of a list."""
        if self._ad_id:
            raise RuntimeError("Cannot set ad_id more than once")
        self._ad_id = ad_id

    @property
    def component_name(self) -> str:
        return self.fn.__name__

    @property
    def key_basis(self) -> tuple:
        """Returns the information that builds the component's key."""
        return (self.file, self.sig, self.component_name, self._ad_id)

    @property
    def stable_key(self) -> int:
        """Returns a hash that uniquely identifies this constructor
        across renders (deterministically).

        It's derived from the function file path, signature and name.
        """
        return hash(self.key_basis)

    def __repr__(self) -> str:
        return (
            f"{self.component_name} <{self.file}>\n"
            f"  Args: {self.args}\n"
            f"  Kwargs: {self.kwargs}\n"
        )

    def __str__(self) -> str:
        return self.component_name


class _Component(ABC, Generic[_CT]):
    def __init__(self, constructor: _ComponentConstructor[_CT]):
        self._constructor = constructor

    def run(self, project: ProjectContext) -> None:
        """Run the component in the project context, for the current scene."""
        cstr = self._constructor
        ctx = project.push_key_for_context(cstr.stable_key)
        scene = project.current_scene_for(cstr.component_name)
        self._render_with_project(project, cstr(ctx=ctx, scene=scene))
        project.pop_key()

    def run_scene(self, scene: SceneState) -> None:
        """Run the component in the scene, context free."""
        self._render_with_scene(scene, self._constructor(scene=scene))

    @abstractmethod
    def _render_with_project(self, p: ProjectContext, constructed: _CT) -> None:
        """Renders the constructed component."""
        raise NotImplementedError("Subclasses must implement _render method.")

    @abstractmethod
    def _render_with_scene(self, s: SceneState, constructed: _CT) -> None:
        """Renders the constructed component."""
        raise NotImplementedError("Subclasses must implement _render method.")

    def __repr__(self) -> str:
        return self._constructor.__repr__()

    def __str__(self) -> str:
        return self._constructor.__str__()


class FusrrComponent(_Component[Comp]):
    def _inject_iter_id(self, iter_id: int):
        self._constructor.set_ad_id(iter_id)

    def _render_with_project(
        self, _p: ProjectContext, constructed: Comp
    ) -> None:
        constructed.build()

    def _render_with_scene(self, _s: SceneState, constructed: Comp) -> None:
        constructed.build()


class FusrrCompoundComponent(_Component[list[FusrrComponent]]):
    def _render_with_project(
        self, p: ProjectContext, constructed: list[FusrrComponent]
    ) -> None:
        iter_id = 0
        for fc in constructed:
            fc._inject_iter_id(iter_id)  # noqa: SLF001
            fc.run(p)

    def _render_with_scene(
        self, s: SceneState, constructed: list[FusrrComponent]
    ) -> None:
        iter_id = 0
        for fc in constructed:
            fc._inject_iter_id(iter_id)  # noqa: SLF001
            fc.run_scene(s)


def component(
    function: Callable[..., Comp],
) -> Callable[..., FusrrComponent]:
    """Construct a component."""

    @wraps(function)
    def wrapper(*args, **kwargs) -> FusrrComponent:
        return FusrrComponent(_ComponentConstructor(function, args, kwargs))

    return wrapper


def co_component(
    function: Callable[..., list[FusrrComponent]],
) -> Callable[..., FusrrCompoundComponent]:
    """Construct a component that returns others a list of components."""

    @wraps(function)
    def wrapper(*args, **kwargs) -> FusrrCompoundComponent:
        return FusrrCompoundComponent(
            _ComponentConstructor(function, args, kwargs)
        )

    return wrapper
