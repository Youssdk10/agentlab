from agentlab.db import get_connection, reset
from agentlab.domain import get_order, list_orders, add_note, update_address, cancel_order

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

def test_add_note_creates_note_and_keeps_status():
    conn = make_db()
    result = add_note(conn, 101, "ring the bell", "2026-11-01")
    assert result["note"]["order_id"] == 101
    count = conn.execute("SELECT COUNT(*) FROM notes WHERE order_id = ?", (101,)).fetchone()[0]
    assert count == 1
    assert get_order(conn, 101)["order"]["status"] == "placed"


def test_add_note_allowed_on_cancelled_order():
    conn = make_db()
    result = add_note(conn, 108, "customer called", "2026-11-01")
    assert "note" in result


def test_add_note_missing_order():
    conn = make_db()
    result = add_note(conn, 999, "hello", "2026-11-01")
    assert result["error"] == "order_not_found"
    assert conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0] == 0


def test_update_address_on_placed_order():
    conn = make_db()
    result = update_address(conn, 101, "12 Oak Street, Austin, TX")
    assert result["order"]["ship_address"] == "12 Oak Street, Austin, TX"
    stored = conn.execute("SELECT ship_address FROM orders WHERE id = ?", (101,)).fetchone()[0]
    assert stored == "12 Oak Street, Austin, TX"


def test_update_address_refused_when_shipped():
    conn = make_db()
    result = update_address(conn, 102, "12 Oak Street, Austin, TX")
    assert result["error"] == "address_change_not_allowed"
    stored = conn.execute("SELECT ship_address FROM orders WHERE id = ?", (102,)).fetchone()[0]
    assert stored == "1 Main Street, Austin, TX"


def test_update_address_refused_when_cancelled():
    conn = make_db()
    result = update_address(conn, 108, "12 Oak Street, Austin, TX")
    assert result["error"] == "address_change_not_allowed"


def test_update_address_missing_order():
    conn = make_db()
    assert update_address(conn, 999, "12 Oak Street, Austin, TX")["error"] == "order_not_found"


def test_update_address_rejects_empty_and_too_long():
    conn = make_db()
    assert update_address(conn, 101, "   ")["error"] == "invalid_address"
    assert update_address(conn, 101, "x" * 201)["error"] == "invalid_address"
    stored = conn.execute("SELECT ship_address FROM orders WHERE id = ?", (101,)).fetchone()[0]
    assert stored == "1 Main Street, Austin, TX"

def test_cancel_placed_order():
    conn = make_db()
    result = cancel_order(conn, 101)
    assert result["order"]["status"] == "cancelled"
    stored = conn.execute("SELECT status FROM orders WHERE id = ?", (101,)).fetchone()[0]
    assert stored == "cancelled"


def test_cancel_refused_when_shipped():
    conn = make_db()
    result = cancel_order(conn, 102)
    assert result["error"] == "not_cancellable"
    stored = conn.execute("SELECT status FROM orders WHERE id = ?", (102,)).fetchone()[0]
    assert stored == "shipped"


def test_cancel_refused_when_delivered():
    conn = make_db()
    result = cancel_order(conn, 103)
    assert result["error"] == "not_cancellable"
    stored = conn.execute("SELECT status FROM orders WHERE id = ?", (103,)).fetchone()[0]
    assert stored == "delivered"


def test_cancel_already_cancelled():
    conn = make_db()
    result = cancel_order(conn, 108)
    assert result["error"] == "already_cancelled"


def test_cancel_missing_order():
    conn = make_db()
    assert cancel_order(conn, 999)["error"] == "order_not_found"