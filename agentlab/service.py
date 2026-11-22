from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from agentlab import domain
from agentlab.db import get_connection, reset

ERROR_STATUS = {
    "order_not_found": 404,
    "already_cancelled": 409,
    "already_refunded": 409,
    "not_cancellable": 409,
    "refund_not_allowed": 409,
    "address_change_not_allowed": 409,
    "invalid_amount": 422,
    "invalid_address": 422,
}


class RefundBody(BaseModel):
    amount: float


class AddressBody(BaseModel):
    new_address: str


class NoteBody(BaseModel):
    text: str


def create_app(db_path, today="2026-11-01"):
    app = FastAPI(title="AgentLab order desk")

    def run(function, *args):
        connection = get_connection(db_path)
        try:
            result = function(connection, *args)
        finally:
            connection.close()
        if "error" in result:
            status = ERROR_STATUS.get(result["error"], 400)
            return JSONResponse(status_code=status, content=result)
        return result

    @app.get("/orders/{order_id}")
    def get_order(order_id: int):
        return run(domain.get_order, order_id)

    @app.get("/customers/{customer_id}/orders")
    def list_orders(customer_id: int):
        return run(domain.list_orders, customer_id)

    @app.post("/reset")
    def reset_database():
        connection = get_connection(db_path)
        try:
            reset(connection)
        finally:
            connection.close()
        return {"status": "reset"}


    @app.post("/orders/{order_id}/cancel")
    def cancel_order(order_id: int):
        return run(domain.cancel_order, order_id)

    @app.post("/orders/{order_id}/refund")
    def refund_order(order_id: int, body: RefundBody):
        return run(domain.refund_order, order_id, body.amount, today)

    @app.put("/orders/{order_id}/address")
    def update_address(order_id: int, body: AddressBody):
        return run(domain.update_address, order_id, body.new_address)

    @app.post("/orders/{order_id}/notes", status_code=201)
    def add_note(order_id: int, body: NoteBody):
        return run(domain.add_note, order_id, body.text, today)
    
    return app


app = create_app("agentlab.db")

