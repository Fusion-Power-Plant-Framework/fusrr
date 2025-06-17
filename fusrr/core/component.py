from __future__ import annotations

import inspect
from functools import wraps
from typing import TYPE_CHECKING, Any, Generic

from fusrr.core.config_model import S
from fusrr.core.project import ProjectContext

if TYPE_CHECKING:
    from collections.abc import Callable
    from contextvars import Context

    from fusrr.core.project import ProjectContext


class Comp:
    def __init__(self, *, builder: Callable[[], None] | None = None):
        self._builder = builder

    def build(self, name: str) -> None:  # noqa: ARG002
        if self._builder is not None:
            self._builder()
        else:
            raise NotImplementedError("Builder function is not defined.")


class Compound:
    def __init__(self, components: list[FusrrComponent]):
        self.components = components

    def component_names(self, *, include_compounds=True) -> list[str]:
        """Returns the names of all components in the compound."""
        return [
            comp.name
            for comp in self.components
            if include_compounds or comp.is_compound is False
        ]

    def sub_compound_names(self) -> list[str]:
        """Returns the names of all sub-compounds in the compound."""
        return [
            comp.name for comp in self.components if comp.is_compound is True
        ]

    def pre_build(self, name: str) -> None:
        """Builds all components in the compound."""

    def post_build(self, name: str) -> None:
        """Finalizes the compound after all components are built."""


COMPONENT_RETURN = Comp | Compound


class FusrrComponent(Generic[S]):
    def __init__(
        self,
        function: Callable[..., COMPONENT_RETURN],
        name: str | None = None,
        args: tuple[Any, ...] | None = None,
        kwargs: dict[str, Any] | None = None,
    ):
        self._constructor = function
        self._file = inspect.getfile(self._constructor)
        self._sig = inspect.signature(self._constructor)
        self._scene_in_params = "scene" in self._sig.parameters
        self._constructor_name = self._constructor.__name__
        self._set_name = name
        self._args = args or ()
        self._kwargs = kwargs or {}

        self._is_compound = None

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
        if self._is_compound is None:
            raise RuntimeError(
                "The component type is not set yet and can only be "
                "determined after it has been run."
            )
        return self._is_compound

    def _set_type(self, constructed: COMPONENT_RETURN) -> None:
        """Sets the type of the component based on the constructed object."""
        if isinstance(constructed, Comp):
            self._is_compound = False
        elif isinstance(constructed, Compound):
            self._is_compound = True
        else:
            raise TypeError(
                f"Expected Comp or Compound, got {type(constructed)}."
            )

    def _run_constructor(
        self, *, ctx: Context | None = None, scene: S | None = None
    ) -> COMPONENT_RETURN:
        """Calls the component function with the provided context and scene."""
        if scene is None and self._scene_in_params:
            raise ValueError(
                "Scene must be provided to the component constructor, "
                "scene is required by the component."
            )
        fn, args, kwargs = self._constructor, self._args, self._kwargs.copy()
        if self._scene_in_params:
            kwargs["scene"] = scene
        if ctx:
            constructed = ctx.run(fn, *args, **kwargs)
        else:
            constructed = fn(*args, **kwargs)
        self._set_type(constructed)
        return constructed

    def run(self, proj_ctx: ProjectContext[S]) -> None:
        """Run the component in the project context, for the current scene."""
        ctx = proj_ctx.push_key_for_context(self.stable_key)
        scene = proj_ctx.current_scene_for(self.name)
        constructed = self._run_constructor(ctx=ctx, scene=scene)
        # is_compound is set in _run_constructor
        if self.is_compound:
            self._build_compound(proj_ctx, constructed)  # type: ignore[call-arg]
        else:
            self._build_component(constructed)  # type: ignore[call-arg]
        proj_ctx.pop_key()

    def _build_component(self, constructed: Comp) -> None:
        constructed.build(self.name)

    def _build_compound(self, p: ProjectContext, constructed: Compound) -> None:
        constructed.pre_build(self.name)
        for comp in constructed.components:
            comp.run(p)
        constructed.post_build(self.name)

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
    function: Callable[..., COMPONENT_RETURN],
) -> Callable[..., FusrrComponent]:
    """Construct a component."""

    @wraps(function)
    def wrapper(*args, name: str | None = None, **kwargs) -> FusrrComponent:
        return FusrrComponent(function, name, args, kwargs)

    return wrapper
