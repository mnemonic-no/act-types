from act.types.format import object_format


def test_tool_format() -> None:
    assert object_format("tool", "Mimikatz") == "mimikatz"
    assert object_format("tool", "Super (awesome) tool") == "super tool"


def test_threatactor_format() -> None:
    assert object_format("threatActor", "APT28") == "apt28"
    assert object_format("threatActor", "APT28 ") == "apt28"
    assert object_format("threatActor", "supER+@ta") == "super+@ta"


def test_vulnerability_format() -> None:
    assert object_format("vulnerability", "CVE-2017-0199") == "cve-2017-0199"


def test_hash_format() -> None:
    sha256 = "87428fc522803d31065e7bce3cf03fe475096631e5e07bbd7a0fde60c4cf25c7"
    sha256_upper = sha256.upper()
    ssdeep = "24:Ol9rFBzwjx5ZKvBF+bi8RuM4Pp6rG5Yg+q8wIXhMC:qrFBzKx5s8sM4grq8wIXht"
    ssdeep_upper = "24:87428FC522803D31065E7BCE3CF03FE475096631E5E07BBD7A0FDE60C4CF25C7"
    assert object_format("content", sha256) == sha256
    assert object_format("content", sha256_upper) == sha256
    assert object_format("hash", sha256) == sha256
    assert object_format("hash", sha256_upper) == sha256

    # ssdeep mixed case and contains non hex digests and should never be lowercased
    assert object_format("hash", ssdeep) == ssdeep
    assert object_format("hash", ssdeep_upper) == ssdeep_upper
