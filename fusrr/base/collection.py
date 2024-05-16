import abc

from fusrr.base.entity import FusrrSceneEntity
from fusrr.base.pipeline import FusrrBuildPipeline
from fusrr.blender.scene_tools import (
    check_collection_in_scene,
    create_collection,
    get_collections,
    link_collections,
    select_objects,
)


class FusrrSceneCollection(FusrrSceneEntity, abc.ABC):
    """A FusrrSceneCollection defines a Blender collection
    of FusrrSceneObject's.
    """

    def __init__(self, collection_name: str):
        """Initializes a FusrrSceneCollection."""
        super().__init__(collection_name)

        pipeline = FusrrBuildPipeline()
        self._setup(pipeline)
        self._pipeline = pipeline

    @abc.abstractmethod
    def _setup(self, pipeline: FusrrBuildPipeline) -> None:
        """Setup this collection, adding objects to the pipeline."""
        raise NotImplementedError

    def execute(self):
        """Execute all objects in this collection's pipeline,
        and create and add them to a Blender collection afterwards.

        Note:
            This collection will be created after all sub-collection are
            created, resulting a in a depth-first creation order.
        """
        self._pipeline.execute()

        # select all created objects, create a collection and add them to it
        created_objs = select_objects(self._pipeline.object_names())

        if check_collection_in_scene(self.name):
            raise ValueError(
                f"Collection with name {self.name} already exists in the scene."
            )
        this_c = create_collection(self.name, created_objs)

        # get all sub-collections and link them to this collection
        sub_cs = get_collections(self._pipeline.collection_names())
        for c in sub_cs:
            link_collections(this_c, c)

    def execute_no_create_collection(self):
        """Execute all objects in this collection's pipeline only.

        Note:
            This will not create a collection or add the objects to it.
        """
        self._pipeline.execute()
