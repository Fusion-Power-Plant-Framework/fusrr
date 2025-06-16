from fusrr import (
    Comp,
    Designer,
    ProjectContext,
    SceneState,
    co_component,
    component,
)
from fusrr.hooks import (
    provider,
    useDesigner,
    useProvider,
    useSetCallProvider,
)


class TestClassToBeProvided(Designer):
    def __init__(self, value: int):
        self.some_value = value

    def run(self) -> None:
        print(f"Running TestClassToBeProvided with value: {self.some_value}")


a = provider(lambda n: TestClassToBeProvided(n))


class ExampleInnerCompDesigner(Designer):
    def run(self) -> None:
        print(f"$$$ Running ExampleInnerCompDesigner")


class InnerCompBuilder(Comp):
    def __init__(self, some_prop: int, another_prop: int):
        self.some_prop = some_prop
        self.another_prop = another_prop

    def build(self) -> None:
        print(f"Building InnerComp... {self.some_prop=}, {self.another_prop=}")


@component
def InnerComp(some_prop, *, scene: SceneState):
    print("Running InnerComp... in scene:", scene.name)

    p = useProvider(a)
    d = useDesigner(ExampleInnerCompDesigner())

    return InnerCompBuilder(some_prop, p.some_value)


class ExampleCompDesigner(Designer):
    def __init__(self, bval: int = 0):
        self.bval = bval

    def run(self) -> None:
        print(f"$$$ Running ExampleCompDesigner")
        self.val = 5


@co_component
def ExampleCoComp():
    print("Running ExampleCoComp...")

    useSetCallProvider(a, 42)

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
