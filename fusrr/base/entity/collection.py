from __future__ import annotations

import abc

from fusrr.base.entity.entity import FusrrWorldEntity
from fusrr.base.pipeline import FusrrBuildPipeline
from fusrr.blender.scene_tools import (
    check_collection_in_scene,
    create_collection,
    get_collections,
    get_objects,
    link_collections,
    link_objects_to_collection,
    select_objects,
)


class FusrrWorldCollection(FusrrWorldEntity, abc.ABC):
    """A FusrrSceneCollection defines a Blender collection
    of FusrrSceneObject's.
    """

    def __init__(self, collection_name: str):
        """Initializes a FusrrSceneCollection."""
        super().__init__(collection_name)
        self._pipeline = FusrrBuildPipeline()

    @abc.abstractmethod
    def setup(self, pipeline: FusrrBuildPipeline) -> None:
        """Setup this collection.

        All sub-entities should be added to the pipeline here.
        All calculations should happen here.
        """
        raise NotImplementedError

    def prepare(self) -> None:
        """Prepare this collection for execution."""
        self.setup(self._pipeline)
        self._pipeline.prepare()

    def execute(self):
        """Execute all objects in this collection's pipeline,
        and create and add them to a Blender collection afterwards.

        Note:
            This collection will be created after all sub-collection are
            created, resulting a in a depth-first creation order.
        """
        self._pipeline.execute()

        # select all created objects, create a collection and add them to it
        created_objs = get_objects(self._pipeline.object_names())

        if check_collection_in_scene(self.name):
            raise ValueError(
                f"Collection with name {self.name} already exists in the scene."
            )
        this_c = create_collection(self.name)
        link_objects_to_collection(this_c, created_objs)

        # get all sub-collections and link them to this collection
        sub_cs = get_collections(self._pipeline.collection_names())
        for c in sub_cs:
            link_collections(this_c, c)

    def execute_no_create_collection(self):
        """Execute all objects in this collection's pipeline.

        Note:
            This will not create a collection or add the objects to it.
        """
        self._pipeline.execute()
