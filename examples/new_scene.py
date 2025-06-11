from fusrr import Comp, ProjectContext, SceneState, component
from fusrr.new_base.hooks.base import Designer
from fusrr.new_base.hooks.hooks import (
    provider,
    useDesigner,
    useProvider,
    useSetProvider,
)


class TestClassToBeProvided(Designer):
    def __init__(self, value: int):
        self.some_value = value

    def run(self) -> None:
        print(f"Running TestClassToBeProvided with value: {self.some_value}")


a = provider(TestClassToBeProvided)


class InnerCompBuilder(Comp):
    def __init__(self, some_prop: int, another_prop: int):
        self.some_prop = some_prop
        self.another_prop = another_prop

    def build(self) -> None:
        print(f"Building InnerComp... {self.some_prop=}, {self.another_prop=}")


@component
def InnerComp(some_prop, *, scene: SceneState):
    print("Running InnerComp... in scene:", scene.name)

    d = useProvider(a)

    return InnerCompBuilder(some_prop, d.some_value)


class ExampleCompDesigner(Designer):
    def __init__(self, bval: int = 0):
        self.bval = bval

    def run(self) -> None:
        print(f"$$$ Running ExampleCompDesigner")
        self.val = 5


@component
def ExampleCoComp():
    print("Running ExampleCoComp...")

    useSetProvider(a, TestClassToBeProvided(42))

    des = useDesigner(ExampleCompDesigner(bval=10))

    return [InnerComp(some_prop=i) for i in range(des.val)]


# Example usage
p = ProjectContext()
c = ExampleCoComp()
print("START ")
c.run(p)
print("###############")
print("START AGAIN")
print("###############")
c.run(p)
