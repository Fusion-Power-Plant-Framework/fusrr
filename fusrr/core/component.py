from __future__ import annotations

import contextlib
import inspect
from functools import wraps
from typing import TYPE_CHECKING, Any, Generic

from fusrr.core.config_model import S, Scene
from fusrr.core.project import ProjectContext
from fusrr.hooks._hook_state import HOOK_STATE

if TYPE_CHECKING:
    from collections.abc import Callable
    from contextvars import Context

    from fusrr.core.project import ProjectContext


class Comp(Generic[S]):
    def __init__(self, *, builder: Callable[[], None] | None = None):
        self._builder = builder

    def build(self, name: str, scene: Scene[S]) -> None:  # noqa: ARG002
        if self._builder is not None:
            self._builder()
        else:
            raise NotImplementedError("Builder function is not defined.")


class Compound(Generic[S]):
    def __init__(self, components: list[FusrrComponent]):
        self.components = components

    def pre_build(self, name: str, scene: Scene[S]) -> None:
        """Builds all components in the compound."""

    def post_build(self, name: str, scene: Scene[S]) -> None:
        """Finalizes the compound after all components are built."""


CONSTRUCTOR_RETURN = Comp | Compound


class FusrrComponent(Generic[S]):
    def __init__(
        self,
        constructor: Callable[..., CONSTRUCTOR_RETURN],
        name: str | None = None,
        args: tuple[Any, ...] | None = None,
        kwargs: dict[str, Any] | None = None,
    ):
        self._constructor = constructor
        self._file = inspect.getfile(self._constructor)
        self._sig = inspect.signature(self._constructor)
        self._scene_in_params = "scene" in self._sig.parameters
        self._constructor_name = self._constructor.__name__
        self._set_name = name
        self._args = args or ()
        self._kwargs = kwargs or {}

        # Is set at the end of _run_constructor call
        self._constructed = None

        if (
            self._scene_in_params
            and self._sig.parameters["scene"].kind
            is not inspect.Parameter.KEYWORD_ONLY
        ):
            raise TypeError(
                f"`{self}` must use reserved parameter 'scene' "
                "as a keyword-only argument, i.e.:\n"
                f"`def {self}(..., *, scene: YourSceneClass): ...`."
            )
        if "name" in self._sig.parameters and self._sig.parameters[
            "name"
        ].kind in (
            inspect.Parameter.KEYWORD_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        ):
            raise TypeError(
                f"`{self}` uses reserved parameter 'name' "
                "as an argument. A component `name` can be passed "
                "to the component as a kwarg only."
            )

        if "scene" in self._kwargs:
            raise TypeError(
                f"`{self}` was passed reserved parameter 'scene' in its kwargs."
            )

    @property
    def name(self) -> str:
        return self._set_name or self._constructor_name

    @property
    def key_basis(self) -> tuple:
        """Returns the information that builds the component's key."""
        return (self._file, self._sig, self._constructor_name, self._set_name)

    @property
    def stable_key(self) -> int:
        """Returns a hash that uniquely identifies this component
        across renders (deterministically).
        """
        return hash(self.key_basis)

    @property
    def is_compound(self) -> bool:
        """Returns whether this component is a compound or not."""
        if self._constructed is None:
            raise RuntimeError(
                "The component type is not set yet and can only be "
                "determined after it has been run."
            )
        return isinstance(self._constructed, Compound)

    @property
    def constructed(self) -> CONSTRUCTOR_RETURN:
        """Returns the constructed component or compound."""
        if self._constructed is None:
            raise RuntimeError(
                "The component has not been run yet, "
                "it has not been constructed."
            )
        return self._constructed

    def _set_constructed(self, constructed: CONSTRUCTOR_RETURN) -> None:
        """Sets the type of the component based on the constructed object."""
        if not isinstance(constructed, (Comp, Compound)):
            raise TypeError(
                f"Expected Comp or Compound, got {type(constructed)}."
            )
        self._constructed = constructed

    def _run_constructor(
        self,
        *,
        ctx: Context | None = None,
        scene: Scene[S] | None = None,
    ) -> CONSTRUCTOR_RETURN:
        """Calls the component function with the provided context and scene."""
        if self._scene_in_params and scene is None:
            raise ValueError(
                "Scene must be provided to the component constructor, "
                "scene is required by the component."
            )
        fn, args, kwargs = self._constructor, self._args, self._kwargs.copy()
        if self._scene_in_params and scene:
            kwargs["scene"] = scene
        if ctx:
            constructed = ctx.run(fn, *args, **kwargs)
        else:
            constructed = fn(*args, **kwargs)
        self._set_constructed(constructed)
        return constructed

    @staticmethod
    def _run_ctx_cleanup() -> None:
        """Cleans up the context after running the component."""
        for i in HOOK_STATE.frame_used_instances():
            if hasattr(i, "cleanup"):
                with contextlib.suppress(NotImplementedError):
                    # If the instance has a cleanup method, call it
                    i.cleanup()

    def run(self, proj_ctx: ProjectContext[S]) -> None:
        """Run the component in the project context, for the current scene."""
        ctx = proj_ctx.push_key_for_context(self.stable_key)
        scene = proj_ctx.scene_for(self.name)
        constructed = self._run_constructor(ctx=ctx, scene=scene)
        # self.is_compound is set by _set_constructed in _run_constructor
        if self.is_compound:
            self._build_compound(constructed, scene, proj_ctx)  # type: ignore[call-arg]
        else:
            self._build_component(constructed, scene)  # type: ignore[call-arg]
        ctx.run(self._run_ctx_cleanup)
        proj_ctx.pop_key()

    def _build_component(self, constructed: Comp, scene: Scene[S]) -> None:
        constructed.build(self.name, scene)

    def _build_compound(
        self,
        constructed: Compound,
        scene: Scene[S],
        proj_ctx: ProjectContext[S],
    ) -> None:
        constructed.pre_build(self.name, scene)
        for comp in constructed.components:
            comp.run(proj_ctx)
        constructed.post_build(self.name, scene)

    def __repr__(self) -> str:
        return (
            f"{self.__str__()} ({self._file})\n"
            f"  Args: {self._args}\n"
            f"  Kwargs: {self._kwargs}\n"
        )

    def __str__(self) -> str:
        return (
            f"{self.name} <{self._constructor_name}>"
            if self._set_name
            else self.name
        )


def component(
    function: Callable[..., CONSTRUCTOR_RETURN],
) -> Callable[..., FusrrComponent]:
    """Construct a component."""

    @wraps(function)
    def wrapper(*args, name: str | None = None, **kwargs) -> FusrrComponent:
        return FusrrComponent(function, name, args, kwargs)

    return wrapper
