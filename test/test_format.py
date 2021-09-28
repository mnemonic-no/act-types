from act.types.format import format_threat_actor, format_tool


def test_tool_format():
    assert format_tool("Mimikatz") == "mimikatz"
    assert format_tool("Super (awesome) tool") == "super tool"


def test_threatactor_format():
    assert format_threat_actor("APT28") == "apt28"
    assert format_threat_actor("APT28 ") == "apt28"
    assert format_threat_actor("supER+@ta") == "super+@ta"
