from fusrr.base.object import FusrrSceneObject
from fusrr.base.scene import FusrrScene


class Plasma(FusrrSceneObject):
    def __init__(self, name: str):
        # all the things here
        super().__init__(name, None)

    def _build(self) -> None:
        # do calcs here
        # set some state here
        ...

    def _self_construct(self, scene: FusrrScene) -> None: ...

    # def _self_construct(self, scene: FusrrScene) -> None:


class FusrrReactor(FusrrSceneObject):
    def __init__(self, name: str):
        # all the things here
        super().__init__(name, None)

    def _build(self):
        self.add_object(Plasma("plasma"))
