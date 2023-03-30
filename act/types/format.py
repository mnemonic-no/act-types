import re
import string
from typing import Text


def default_lowercase_format(value: Text) -> Text:
    """Default lowercase format
    * remove text in paranthesis
    * replace multiple whitespace with single space
    * lowercase
    """

    return re.sub(r"\s+", " ", re.sub(r"\(.*\)", "", str(value))).lower().strip()


def hash_format(value: Text) -> Text:
    value = value.strip()

    if (value.upper() == value) and all(c in string.hexdigits for c in value):
        # All characters in the hash is uppercase hexdigists so it is safe to lowercase
        # the value We can not always lowercase, since we support hashes with mixed
        # case, e.g. ssdeep
        return value.lower()

    return value


OBJECT_FORMATTERS = {
    "tool": default_lowercase_format,
    "threatActor": default_lowercase_format,
    "vulnerability": default_lowercase_format,
    "hash": hash_format,
    "content": hash_format,
}


def object_format(object_type: Text, object_value: Text) -> Text:
    if object_type in OBJECT_FORMATTERS:
        return OBJECT_FORMATTERS[object_type](object_value)

    # No formatter specified
    return object_value
