import abc
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from fusrr.base.object import FusrrSceneObject
    from fusrr.base.scene import FusrrScene


class FusrrPipeline(abc.ABC):
    @abc.abstractmethod
    def execute(self):
        pass


class FusrrBuildPipeline(FusrrPipeline):
    def __init__(self, collection_name: str | None = None):
        self.collection_name = collection_name
        # had to do all this typing and tuple stuff due to circular imports
        self._pipeline: list[
            tuple[
                Literal["obj"],
                "FusrrSceneObject",
            ]
            | tuple[
                Literal["pipe"],
                "FusrrBuildPipeline",
            ]
        ] = []

    def clear(self):
        self._pipeline.clear()

    def add_object(self, obj: "FusrrSceneObject"):
        self._pipeline.append(("obj", obj))

    def add_pipe(self, pipe: "FusrrBuildPipeline"):
        self._pipeline.append(("pipe", pipe))

    def execute(self, scene: "FusrrScene"):
        if not self._pipeline:
            return

        object_names = set()
        for pipe_type, pipe_item in self._pipeline:
            pipe_item.execute(scene)
            if pipe_type == "obj":
                obj: "FusrrSceneObject" = pipe_item  # type: ignore[assignment]
                object_names.add(obj.name)

        if self.collection_name: ...
        # select and add objects to collection using object_names


class FusrrViewPipeline(FusrrPipeline):
    def execute(self):
        raise NotImplementedError
