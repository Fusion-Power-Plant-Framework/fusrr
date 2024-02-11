from fusrr.base.object import FusrrSceneObject
from fusrr.reactor.process.process_adaptor import ProcessParams


class ProcessComponent(FusrrSceneObject):
    def __init__(self, component_name: str, reactor_params: ProcessParams):
        self.params = reactor_params
        super().__init__(component_name, None)
