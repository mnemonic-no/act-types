from act.types.types import object_validates


def test_tool_validator():
    assert object_validates("tool", "Mimikatz") == False
    assert object_validates("tool", "mimikatz") == True
    assert object_validates("tool", "many 0days: ie") == False


def test_threatactor_validator():
    assert object_validates("threatActor", "APT28") == False
    assert object_validates("threatActor", "apt28") == True
    assert object_validates("threatActor", "some-ta") == True
