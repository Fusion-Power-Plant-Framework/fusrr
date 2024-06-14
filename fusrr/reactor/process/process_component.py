from fusrr.base.entity.collection import FusrrSceneCollection
from fusrr.base.entity.object import (
    FusrrSceneObject,
    FusrrSceneObjectWithContext,
)
from fusrr.base.types import CFT
from fusrr.reactor.process.process_adaptor import ProcessParams


class ProcessComponentCollection(FusrrSceneCollection):
    def __init__(
        self,
        collection_name: str,
        reactor_params: ProcessParams,
    ):
        self.params = reactor_params
        super().__init__(collection_name)


class ProcessComponent(FusrrSceneObject):
    def __init__(self, component_name: str, reactor_params: ProcessParams):
        self.params = reactor_params
        super().__init__(component_name)


class ProcessComponentWithContext(FusrrSceneObjectWithContext[CFT]):
    def __init__(
        self, component_name: str, ctx: CFT, reactor_params: ProcessParams
    ):
        self.params = reactor_params
        super().__init__(component_name, ctx)
