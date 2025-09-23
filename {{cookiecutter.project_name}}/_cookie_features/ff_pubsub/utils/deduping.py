from collections.abc import Mapping


def check_duplicate(attributes: Mapping[str, str], *args, **kwargs) -> bool:
    """
    TODO: Any pubsub function should implement idempotency check OR filter duplicate events usptream.
    """
    raise NotImplementedError
