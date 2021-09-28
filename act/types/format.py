import re
from typing import Text

from act.types.types import object_validates


class ValidationError(Exception):
    pass


def format_tool(tool: Text) -> Text:
    """Format tool name:
    * remove text in paranthesis
    * replace multiple whitespace with single space
    * lowercase
    * check that tool validates
    """

    name = re.sub(r"\s+", " ", re.sub(r"\(.*\)", "", tool)).lower().strip()

    if not object_validates("tool", name):
        raise ValidationError(f"Tool does not validate: {tool}")

    return name


def format_threat_actor(threat_actor: Text) -> Text:
    """Format Threat Actor:
    * lowercase
    * check that threat actor validates
    """

    name = re.sub(r"\(.*\)", "", threat_actor).lower().strip()

    if not object_validates("threatActor", name):
        raise ValidationError(f"ThreatActor does not validate: {threat_actor}")

    return name
