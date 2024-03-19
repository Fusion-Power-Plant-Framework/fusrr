from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from fusrr.base.object import FusrrSceneObject
    from fusrr.base.scene import FusrrScene


class FusrrPipeline(abc.ABC):
    """A FusrrPipeline defines a set of operations to be executed
    on a FusrrScene.
    """

    @abc.abstractmethod
    def execute(self, scene: FusrrScene):  # noqa: D102
        pass


class FusrrBuildPipeline(FusrrPipeline):
    """A FusrrBuildPipeline defines a container and a deterministic build order
    for constructing `FusrrSceneObject`s.
    """

    def __init__(self, collection_name: str | None = None):
        """Construct a new build pipeline.

        Args:
            collection_name: The name of the collection to create and add
                objects to. If None, no collection will be created.
        """
        self.collection_name = collection_name
        # had to do all this typing and tuple stuff due to circular imports
        self._pipeline: list[
            tuple[
                Literal["obj"],
                FusrrSceneObject,
            ]
            | tuple[
                Literal["pipe"],
                FusrrBuildPipeline,
            ]
        ] = []

    def add_object(self, obj: FusrrSceneObject):
        """Add an object to this pipeline."""
        self._pipeline.append(("obj", obj))

    def add_pipe(self, pipe: FusrrBuildPipeline):
        """Add a nested pipeline to this pipeline."""
        self._pipeline.append(("pipe", pipe))

    def execute(self, scene: FusrrScene):
        """Execute this pipeline.

        This will execute every object and nested pipeline in this pipeline
        (in order), modifying the scene as it goes.

        If a collection name was provided, this will also create a collection
        and add all objects (and sub-collections) to it.

        Args:
            scene: The scene to execute this pipeline on.
        """
        if not self._pipeline:
            return

        object_names = set()
        for pipe_type, pipe_item in self._pipeline:
            pipe_item.execute(scene)
            if pipe_type == "obj":
                obj: FusrrSceneObject = pipe_item  # type: ignore[assignment]
                object_names.add(obj.name)

        if self.collection_name:
            created_objs = scene.select_objects(object_names)
            scene.create_collection(self.collection_name, created_objs)
            scene.deselect_all()


class FusrrViewPipeline(FusrrPipeline):
    ...
