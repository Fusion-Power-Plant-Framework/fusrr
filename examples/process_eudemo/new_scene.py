from fusrr import (
    Comp,
    Compound,
    ProjectContext,
    component,
)
from fusrr.hooks import (
    Designer,
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


class ExampleInnerCompDesigner(Designer):
    def run(self) -> None:
        print("$$$ Running ExampleInnerCompDesigner")


@component
def InnerComp(some_prop):
    """A component for building an inner component."""
    p = useProvider(a)
    useDesigner(ExampleInnerCompDesigner())

    def builder() -> None:
        print(
            f"InnerComp: some_prop={some_prop}, provided_value={p.some_value}"
        )

    return Comp(builder=builder)


class ExampleCompDesigner(Designer):
    def __init__(self, bval: int = 0):
        self.bval = bval

    def run(self) -> None:
        print("$$$ Running ExampleCompDesigner")
        self.val = 5


@component
def ExampleCoComp():
    """An example compound component."""
    print("Running ExampleCoComp...")

    useSetProvider(a, 42)

    des = useDesigner(ExampleCompDesigner(bval=10))

    return Compound([InnerComp(some_prop=i) for i in range(des.val)])


# Example usage
p = ProjectContext()
c = ExampleCoComp()
print("START ")
c.run(p)

print("Next scene:")
c.run(p)
