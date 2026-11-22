import httpx
from fastapi.testclient import TestClient

from agentlab.client import OrderDeskClient
from agentlab.service import create_app


def make_client(tmp_path):
    http = TestClient(create_app(str(tmp_path / "test.db"), today="2026-11-01"))
    client = OrderDeskClient(http)
    client.reset()
    return client


class FakeResponse:
    def __init__(self, status_code=200, text="{}"):
        self.status_code = status_code
        self.text = text

    def json(self):
        import json
        return json.loads(self.text)


class FakeHttp:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error

    def request(self, method, path, json=None):
        if self.error is not None:
            raise self.error
        return self.response


def test_get_order_through_client(tmp_path):
    client = make_client(tmp_path)
    assert client.get_order(101)["order"]["status"] == "placed"


def test_missing_order_returns_error_dict(tmp_path):
    client = make_client(tmp_path)
    assert client.get_order(999)["error"] == "order_not_found"


def test_list_orders_through_client(tmp_path):
    client = make_client(tmp_path)
    ids = [o["id"] for o in client.list_orders(2)["orders"]]
    assert ids == [107, 106]


def test_cancel_twice_through_client(tmp_path):
    client = make_client(tmp_path)
    assert client.cancel_order(101)["order"]["status"] == "cancelled"
    assert client.cancel_order(101)["error"] == "already_cancelled"


def test_refund_through_client(tmp_path):
    client = make_client(tmp_path)
    result = client.refund_order(103, 80.0)
    assert result["order"]["status"] == "refunded"
    assert result["order"]["refund_amount"] == 80.0


def test_update_address_through_client(tmp_path):
    client = make_client(tmp_path)
    result = client.update_address(101, "12 Oak Street, Austin, TX")
    assert result["order"]["ship_address"] == "12 Oak Street, Austin, TX"


def test_add_note_through_client(tmp_path):
    client = make_client(tmp_path)
    assert client.add_note(101, "ring the bell")["note"]["order_id"] == 101


def test_invalid_request_becomes_error(tmp_path):
    client = make_client(tmp_path)
    assert client.refund_order(103, "abc")["error"] == "invalid_request"


def test_timeout_becomes_error():
    client = OrderDeskClient(FakeHttp(error=httpx.ReadTimeout("slow")))
    assert client.get_order(101)["error"] == "timeout"


def test_connection_error_becomes_error():
    client = OrderDeskClient(FakeHttp(error=httpx.ConnectError("refused")))
    assert client.get_order(101)["error"] == "connection_error"


def test_server_error_becomes_error():
    client = OrderDeskClient(FakeHttp(response=FakeResponse(500, "Internal Server Error")))
    assert client.get_order(101)["error"] == "server_error"


def test_non_json_response_becomes_error():
    client = OrderDeskClient(FakeHttp(response=FakeResponse(200, "{not json")))
    assert client.get_order(101)["error"] == "invalid_response"