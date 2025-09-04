from collections.abc import Generator
from random import randint


def interject_with_foo(*words: str) -> Generator[str, str, None]:
    """
    Example function to illustrate what happens when you don't escape doctests with `pycon`
    >>> import random
    >>> random.seed(80085)
    >>> for word in interject_with_foo("Hello", "world", ""):
    ... print(word)
    Hell-FOO!...o
    w-FOO!...orld
    ...foo?
    """
    for word in words:
        if len(word) == 0:
            yield "...foo?"
        else:
            idx = randint(0, len(word) - 1)
            yield word[:idx] + "-FOO!..." + word[idx:]
