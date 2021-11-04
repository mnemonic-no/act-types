import re
from typing import Text

from act.types.types import object_validates


class ValidationError(Exception):
    pass


def default_lowercase_format(value: Text) -> Text:
    """Default lowercase format
    * remove text in paranthesis
    * replace multiple whitespace with single space
    * lowercase
    """

    return re.sub(r"\s+", " ", re.sub(r"\(.*\)", "", value)).lower().strip()


def validate(object_type: Text, object_value: Text):
    """Validate object type/value"""
    if not object_validates(object_type, object_value):
        raise ValidationError(f"{object_type} does not validate: {object_value}")

    return object_value


def format_tool(tool: Text) -> Text:
    """Format and validate tool name"""

    return validate("tool", default_lowercase_format(tool))


def format_threat_actor(threat_actor: Text) -> Text:
    """Format and validate Threat Actor name"""

    return validate("threatActor", default_lowercase_format(threat_actor))
