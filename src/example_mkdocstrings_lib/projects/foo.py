from collections.abc import Generator
from random import randint


def interject_with_foo(*words: str) -> Generator[str, str, None]:
    """
    Changed to escape with `pycon`.

    * ~~Pygments syntax highlighting isn't working (yet)~~
    * It now works by adding - pymdownx.superfences to the mkdocs.yaml
    * Add pymdownx.tilde for tilde strikethrough

    ```pycon
    >>> import random
    >>> random.seed(80085)
    >>> for word in interject_with_foo("Hello", "world", ""):
    ... print(word)
    Hell-FOO!...o
    w-FOO!...orld
    ...foo?

    ```
    """
    for word in words:
        if len(word) == 0:
            yield "...foo?"
        else:
            idx = randint(0, len(word) - 1)
            yield word[:idx] + "-FOO!..." + word[idx:]
