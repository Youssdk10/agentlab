def parse_tool_call(response: dict) -> tuple[str, dict]:
    if "name" not in response:
        raise ValueError("Missing tool name")
    if "arguments" not in response:
        raise ValueError("Missing tool arguments")

    return response["name"], response["arguments"]