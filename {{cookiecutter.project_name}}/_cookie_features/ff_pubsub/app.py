"""FIXME: Add description"""
# ruff: noqa: F401

from __future__ import annotations

import functions_framework as ff
from cloudevents.http import CloudEvent
from type_cellar import (
    SequenceNotStr as Sequence,  # pyright: ignore[reportUnusedImport]
)

from .utils import check_duplicate  # type: ignore[import-not-found]


@ff.cloud_event
def run(cloud_event: CloudEvent) -> None:
    """FIXME: Add description.

    Main entry point of the pubsub function.
    """
    if check_duplicate(cloud_event.get_attributes()):
        return
