from fastapi.testclient import TestClient

from agentlab.service import create_app


def make_client(tmp_path):
    app = create_app(str(tmp_path / "test.db"), today="2026-11-01")
    client = TestClient(app)
    client.post("/reset")
    return client


def test_get_order_over_http(tmp_path):
    client = make_client(tmp_path)
    response = client.get("/orders/101")
    assert response.status_code == 200
    assert response.json()["order"]["status"] == "placed"


def test_get_missing_order_is_404(tmp_path):
    client = make_client(tmp_path)
    response = client.get("/orders/999")
    assert response.status_code == 404
    assert response.json()["error"] == "order_not_found"


def test_list_orders_over_http(tmp_path):
    client = make_client(tmp_path)
    response = client.get("/customers/2/orders")
    assert response.status_code == 200
    assert [o["id"] for o in response.json()["orders"]] == [107, 106]

def test_cancel_over_http(tmp_path):
    client = make_client(tmp_path)
    response = client.post("/orders/101/cancel")
    assert response.status_code == 200
    assert response.json()["order"]["status"] == "cancelled"


def test_cancel_shipped_is_409(tmp_path):
    client = make_client(tmp_path)
    response = client.post("/orders/102/cancel")
    assert response.status_code == 409
    assert response.json()["error"] == "not_cancellable"


def test_refund_over_http(tmp_path):
    client = make_client(tmp_path)
    response = client.post("/orders/103/refund", json={"amount": 80.0})
    assert response.status_code == 200
    assert response.json()["order"]["status"] == "refunded"


def test_refund_too_old_is_409(tmp_path):
    client = make_client(tmp_path)
    response = client.post("/orders/104/refund", json={"amount": 50.0})
    assert response.status_code == 409
    assert response.json()["error"] == "refund_not_allowed"


def test_refund_bad_amount_is_422(tmp_path):
    client = make_client(tmp_path)
    response = client.post("/orders/103/refund", json={"amount": 500.0})
    assert response.status_code == 422
    assert response.json()["error"] == "invalid_amount"


def test_refund_missing_body_field_is_422(tmp_path):
    client = make_client(tmp_path)
    response = client.post("/orders/103/refund", json={})
    assert response.status_code == 422
    assert "detail" in response.json()


def test_update_address_over_http(tmp_path):
    client = make_client(tmp_path)
    response = client.put("/orders/101/address", json={"new_address": "12 Oak Street, Austin, TX"})
    assert response.status_code == 200
    assert response.json()["order"]["ship_address"] == "12 Oak Street, Austin, TX"


def test_update_address_shipped_is_409(tmp_path):
    client = make_client(tmp_path)
    response = client.put("/orders/102/address", json={"new_address": "12 Oak Street, Austin, TX"})
    assert response.status_code == 409
    assert response.json()["error"] == "address_change_not_allowed"


def test_add_note_over_http(tmp_path):
    client = make_client(tmp_path)
    response = client.post("/orders/101/notes", json={"text": "ring the bell"})
    assert response.status_code == 201
    assert response.json()["note"]["order_id"] == 101


def test_add_note_missing_order_is_404(tmp_path):
    client = make_client(tmp_path)
    response = client.post("/orders/999/notes", json={"text": "hello"})
    assert response.status_code == 404


def test_reset_restores_seed_data(tmp_path):
    client = make_client(tmp_path)
    client.post("/orders/101/cancel")
    client.post("/reset")
    assert client.get("/orders/101").json()["order"]["status"] == "placed"