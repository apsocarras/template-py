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
    >>> random.seed(1238)
    >>> for word in interject_with_foo("Hello", "world", ""):
    ...     print(word)
    FOO!...Hello
    wor-FOO!...ld
    ...foo?

    ```
    """
    for word in words:
        if len(word) == 0:
            yield "...foo?"
        else:
            idx = randint(0, len(word) - 1)
            yield word[:idx] + f"{'-' if idx != 0 else ''}FOO!..." + word[idx:]


if __name__ == "__main__":
    import doctest

    _ = doctest.testmod()

    # Run tests defined in your docstrings.
