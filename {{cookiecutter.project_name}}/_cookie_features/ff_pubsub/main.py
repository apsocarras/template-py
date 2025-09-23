import functions_framework as ff
from cloudevents.http import CloudEvent

from .utils import check_duplicate


@ff.cloud_event
def run(cloud_event: CloudEvent) -> None:
    if check_duplicate(cloud_event.get_attributes()):
        return
