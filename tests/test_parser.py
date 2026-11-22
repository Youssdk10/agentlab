import pytest

from parser import parse_tool_call


def test_valid_tool_call():
    response = {
        "name": "get_age",
        "arguments": {"name": "Youss"}
    }

    name, args = parse_tool_call(response)

    assert name == "get_age"
    assert args == {"name": "Youss"}


def test_missing_arguments():
    response = {"name": "get_age"}

    with pytest.raises(ValueError, match="Missing tool arguments"):
        parse_tool_call(response)


def test_missing_name():
    response = {"arguments": {"name": "Youss"}}

    with pytest.raises(ValueError, match="Missing tool name"):
        parse_tool_call(response)
