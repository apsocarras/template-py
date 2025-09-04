from typing_extensions import override


class MyClass:
    """
    Lorem ipsum
    """

    def __init__(self, foo: str) -> None:
        self.foo: str = foo

    @override
    def __str__(self) -> str:
        return self.foo
