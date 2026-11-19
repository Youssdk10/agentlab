from agentlab.db import get_connection, reset
from agentlab.domain import get_order


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