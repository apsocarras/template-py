"""TODO: Any pubsub function should implement idempotency check OR filter duplicate events upstream."""
# ruff: noqa: F401

from __future__ import annotations

from collections.abc import Mapping

from type_cellar import (
    SequenceNotStr as Sequence,  # pyright: ignore[reportUnusedImport]
)


def check_duplicate(attributes: Mapping[str, str]) -> bool:
    """TODO: implement idempotency check OR filter duplicate events upstream.

    Suggested implementation is to make a hash of the salient attributes and perhaps the body.
    """
    raise NotImplementedError
