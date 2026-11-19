def get_order(connection, order_id):
    row = connection.execute(
        "SELECT id, customer_id, status, placed_at, total, ship_address, refund_amount "
        "FROM orders WHERE id = ?",
        (order_id,),
    ).fetchone()

    if row is None:
        return {"error": "order_not_found", "message": f"Order {order_id} does not exist."}

    items = connection.execute(
        "SELECT sku, qty, price FROM order_items WHERE order_id = ? ORDER BY sku",
        (order_id,),
    ).fetchall()

    return {
        "order": {
            "id": row[0],
            "customer_id": row[1],
            "status": row[2],
            "placed_at": row[3],
            "total": row[4],
            "ship_address": row[5],
            "refund_amount": row[6],
            "items": [{"sku": s, "qty": q, "price": p} for s, q, p in items],
        }
    }

def list_orders(connection, customer_id):
    rows = connection.execute(
        "SELECT id, status, placed_at, total FROM orders "
        "WHERE customer_id = ? ORDER BY placed_at DESC, id DESC",
        (customer_id,),
    ).fetchall()

    return {
        "orders": [
            {"id": r[0], "status": r[1], "placed_at": r[2], "total": r[3]}
            for r in rows
        ]
    }

def add_note(connection, order_id, text, today):
    exists = connection.execute(
        "SELECT 1 FROM orders WHERE id = ?", (order_id,)
    ).fetchone()
    if exists is None:
        return {"error": "order_not_found", "message": f"Order {order_id} does not exist."}

    cursor = connection.execute(
        "INSERT INTO notes (order_id, text, created_at) VALUES (?, ?, ?)",
        (order_id, text, today),
    )
    connection.commit()
    return {"note": {"id": cursor.lastrowid, "order_id": order_id, "text": text}}

def update_address(connection, order_id, new_address):
    row = connection.execute(
        "SELECT status FROM orders WHERE id = ?", (order_id,)
    ).fetchone()
    if row is None:
        return {"error": "order_not_found", "message": f"Order {order_id} does not exist."}

    address = new_address.strip()
    if not address or len(address) > 200:
        return {"error": "invalid_address", "message": "Address must be 1 to 200 characters."}

    if row[0] != "placed":
        return {
            "error": "address_change_not_allowed",
            "message": f"Address can only be changed while the order is placed (status is {row[0]}).",
        }

    connection.execute(
        "UPDATE orders SET ship_address = ? WHERE id = ?", (address, order_id)
    )
    connection.commit()
    return get_order(connection, order_id)