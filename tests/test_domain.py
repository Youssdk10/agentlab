from agentlab.db import get_connection, reset
from agentlab.domain import get_order, list_orders

def make_db():
    conn = get_connection(":memory:")
    reset(conn)
    return conn

def test_get_order_returns_order_with_items():
    conn = make_db()
    result = get_order(conn, 101)
    assert "order" in result
    assert result["order"]["status"] == "placed"
    assert result["order"]["customer_id"] == 1
    assert len(result["order"]["items"]) == 2


def test_get_order_missing_returns_error():
    conn = make_db()
    result = get_order(conn, 999)
    assert result["error"] == "order_not_found"

def test_list_orders_newest_first():
    conn = make_db()
    result = list_orders(conn, 1)
    ids = [o["id"] for o in result["orders"]]
    assert ids == [105, 101, 102, 103, 108, 104]

def test_list_orders_only_that_customer():
    conn = make_db()
    result = list_orders(conn, 2)
    ids = [o["id"] for o in result["orders"]]
    assert ids == [107, 106]


def test_list_orders_unknown_customer_returns_empty_list():
    conn = make_db()
    result = list_orders(conn, 99)
    assert result["orders"] == []