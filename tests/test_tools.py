from fastapi.testclient import TestClient

from agentlab.client import OrderDeskClient
from agentlab.service import create_app
from agentlab.tools import ARG_MODELS, TOOL_SCHEMAS, ToolBox


def make_toolbox(tmp_path):
    http = TestClient(create_app(str(tmp_path / "test.db"), today="2026-11-01"))
    client = OrderDeskClient(http)
    client.reset()
    return ToolBox(client)


def status_of(toolbox, order_id):
    return toolbox.call("get_order", {"order_id": order_id})["order"]["status"]


def test_schemas_match_models():
    names = [schema["function"]["name"] for schema in TOOL_SCHEMAS]
    assert sorted(names) == sorted(ARG_MODELS)
    for schema in TOOL_SCHEMAS:
        function = schema["function"]
        fields = set(ARG_MODELS[function["name"]].model_fields)
        assert set(function["parameters"]["properties"]) == fields
        assert set(function["parameters"]["required"]) == fields


def test_every_tool_exists_on_client():
    for name in ARG_MODELS:
        assert callable(getattr(OrderDeskClient, name))


def test_call_get_order(tmp_path):
    toolbox = make_toolbox(tmp_path)
    assert status_of(toolbox, 101) == "placed"


def test_json_string_arguments_are_accepted(tmp_path):
    toolbox = make_toolbox(tmp_path)
    result = toolbox.call("get_order", '{"order_id": 101}')
    assert result["order"]["id"] == 101


def test_number_sent_as_text_is_converted(tmp_path):
    toolbox = make_toolbox(tmp_path)
    assert toolbox.call("get_order", {"order_id": "101"})["order"]["id"] == 101


def test_missing_argument(tmp_path):
    toolbox = make_toolbox(tmp_path)
    result = toolbox.call("cancel_order", {})
    assert result["error"] == "invalid_arguments"
    assert "order_id" in result["message"]


def test_wrong_type(tmp_path):
    toolbox = make_toolbox(tmp_path)
    result = toolbox.call("get_order", {"order_id": "abc"})
    assert result["error"] == "invalid_arguments"
    assert "get_order" in result["message"]


def test_extra_argument_is_rejected(tmp_path):
    toolbox = make_toolbox(tmp_path)
    result = toolbox.call("get_order", {"order_id": 101, "customer_id": 1})
    assert result["error"] == "invalid_arguments"


def test_unknown_tool(tmp_path):
    toolbox = make_toolbox(tmp_path)
    result = toolbox.call("delete_everything", {})
    assert result["error"] == "unknown_tool"
    assert "get_order" in result["message"]


def test_arguments_that_are_not_json(tmp_path):
    toolbox = make_toolbox(tmp_path)
    assert toolbox.call("get_order", "not json")["error"] == "invalid_arguments"


def test_arguments_that_are_not_an_object(tmp_path):
    toolbox = make_toolbox(tmp_path)
    assert toolbox.call("get_order", [101])["error"] == "invalid_arguments"


def test_bad_arguments_do_not_change_the_database(tmp_path):
    toolbox = make_toolbox(tmp_path)
    result = toolbox.call("refund_order", {"order_id": 103, "amount": "lots"})
    assert result["error"] == "invalid_arguments"
    assert status_of(toolbox, 103) == "delivered"


def test_domain_errors_pass_through(tmp_path):
    toolbox = make_toolbox(tmp_path)
    assert toolbox.call("cancel_order", {"order_id": 102})["error"] == "not_cancellable"


def test_refund_through_toolbox(tmp_path):
    toolbox = make_toolbox(tmp_path)
    result = toolbox.call("refund_order", {"order_id": 103, "amount": 80.0})
    assert result["order"]["status"] == "refunded"