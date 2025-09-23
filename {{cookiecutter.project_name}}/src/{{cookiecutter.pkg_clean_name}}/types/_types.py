from __future__ import annotations

from beartype.typing import (
    Any,
    Iterator,
    Protocol,
    Sequence,
    TypeVar,
    runtime_checkable,
)
from typing_extensions import SupportsIndex, overload

_T_co = TypeVar("_T_co", covariant=True)


@runtime_checkable
class SequenceNotStr(Protocol[_T_co]):
    """
    # Python

    You are so stupid but loveable all the same. https://github.com/python/typing/issues/256#issuecomment-1442633430
    """

    @overload
    def __getitem__(self, index: SupportsIndex, /) -> _T_co: ...
    @overload
    def __getitem__(self, index: slice, /) -> Sequence[_T_co]: ...
    def __contains__(self, value: object, /) -> bool: ...
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[_T_co]: ...
    def index(self, value: Any, start: int = 0, stop: int = ..., /) -> int: ...
    def count(self, value: Any, /) -> int: ...
    def __reversed__(self) -> Iterator[_T_co]: ...


NonStrSequence = SequenceNotStr[str]
