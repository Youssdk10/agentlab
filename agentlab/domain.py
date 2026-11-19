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