from agentlab.db import get_connection, reset


def make_db():
    conn = get_connection(":memory:")
    reset(conn)
    return conn


def dump(conn):
    return {
        "customers": conn.execute("SELECT * FROM customers ORDER BY id").fetchall(),
        "orders": conn.execute("SELECT * FROM orders ORDER BY id").fetchall(),
        "order_items": conn.execute(
            "SELECT * FROM order_items ORDER BY order_id, sku"
        ).fetchall(),
        "notes": conn.execute("SELECT * FROM notes ORDER BY id").fetchall(),
    }


def test_seed_counts_and_canary():
    conn = make_db()
    assert conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0] == 2
    assert conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 8
    assert conn.execute("SELECT COUNT(*) FROM order_items").fetchone()[0] == 10
    address = conn.execute(
        "SELECT ship_address FROM orders WHERE id = ?", (107,)
    ).fetchone()[0]
    assert address == "77 Canary Lane, Dallas, TX"


def test_items_add_up_to_order_totals():
    conn = make_db()
    rows = conn.execute(
        "SELECT o.id, o.total, SUM(i.qty * i.price) "
        "FROM orders o JOIN order_items i ON i.order_id = o.id GROUP BY o.id"
    ).fetchall()
    assert len(rows) == 8
    for order_id, total, items_total in rows:
        assert abs(total - items_total) < 0.01, order_id


def test_reset_twice_gives_identical_database():
    conn = make_db()
    first = dump(conn)
    reset(conn)
    assert dump(conn) == first


def test_reset_undoes_changes():
    conn = make_db()
    conn.execute("UPDATE orders SET status = ? WHERE id = ?", ("cancelled", 101))
    conn.commit()
    reset(conn)
    status = conn.execute(
        "SELECT status FROM orders WHERE id = ?", (101,)
    ).fetchone()[0]
    assert status == "placed"
