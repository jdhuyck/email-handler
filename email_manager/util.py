import dataclasses
import os

sentinel = object()


def env(key, convert=str, **kwargs):
    """
    Args:
        key: in the format of either KEY or KEY:DEFAULT
        convert: a function that accepts a string and returns a different type
        kwargs: any remaining kwargs for 'dataclasses.field'

    Returns:
        dataclasses.field
    """
    key, partition, default = key.partition(":")

    # handle 'KEY:' for default of empty string as partition returns empty string when partition is missing.
    if partition == "":
        default = sentinel

    def default_factory(key=key, default=default, convert=convert):
        value = os.environ.get(key)
        if value is None:
            if default != sentinel:
                value = default
            else:
                raise KeyError(key)

        return convert(value)

    return dataclasses.field(default_factory=default_factory, **kwargs)
