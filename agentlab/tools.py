import json

from pydantic import BaseModel, ConfigDict, ValidationError


class StrictArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")  # unknown arguments are rejected


class GetOrderArgs(StrictArgs):
    order_id: int


class ListOrdersArgs(StrictArgs):
    customer_id: int


class CancelOrderArgs(StrictArgs):
    order_id: int


class RefundOrderArgs(StrictArgs):
    order_id: int
    amount: float


class UpdateAddressArgs(StrictArgs):
    order_id: int
    new_address: str


class AddNoteArgs(StrictArgs):
    order_id: int
    text: str


# Tool name -> argument model. The tool name is also the name of the client method.
ARG_MODELS = {
    "get_order": GetOrderArgs,
    "list_orders": ListOrdersArgs,
    "cancel_order": CancelOrderArgs,
    "refund_order": RefundOrderArgs,
    "update_address": UpdateAddressArgs,
    "add_note": AddNoteArgs,
}


def _tool(name, description, properties):
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": list(properties),
            },
        },
    }


ORDER_ID = {"type": "integer", "description": "The order's ID, for example 101"}

TOOL_SCHEMAS = [
    _tool(
        "get_order",
        "Look up one order by its ID. Returns its status, date, total, shipping address, refund amount and items.",
        {"order_id": ORDER_ID},
    ),
    _tool(
        "list_orders",
        "List all orders of one customer, newest first.",
        {"customer_id": {"type": "integer", "description": "The customer's ID, for example 1"}},
    ),
    _tool(
        "cancel_order",
        "Cancel one order.",
        {"order_id": ORDER_ID},
    ),
    _tool(
        "refund_order",
        "Refund an order. Give the amount in dollars.",
        {
            "order_id": ORDER_ID,
            "amount": {"type": "number", "description": "Refund amount in dollars, for example 25.50"},
        },
    ),
    _tool(
        "update_address",
        "Change the shipping address of one order.",
        {
            "order_id": ORDER_ID,
            "new_address": {"type": "string", "description": "The full new shipping address"},
        },
    ),
    _tool(
        "add_note",
        "Add a text note to one order.",
        {
            "order_id": ORDER_ID,
            "text": {"type": "string", "description": "The note text"},
        },
    ),
]


def _bad_arguments(message):
    return {"error": "invalid_arguments", "message": message}


class ToolBox:
    def __init__(self, client):
        self.client = client

    @property
    def schemas(self):
        return TOOL_SCHEMAS

    def call(self, name, arguments):
        model = ARG_MODELS.get(name)
        if model is None:
            return {
                "error": "unknown_tool",
                "message": f"There is no tool named '{name}'. Available tools: {', '.join(ARG_MODELS)}.",
            }

        if arguments is None:
            arguments = {}
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except ValueError:
                return _bad_arguments(f"Arguments for {name} must be a JSON object, but the text was not valid JSON.")
        if not isinstance(arguments, dict):
            return _bad_arguments(f"Arguments for {name} must be a JSON object with named values.")

        try:
            args = model.model_validate(arguments)
        except ValidationError as exc:
            problems = []
            for err in exc.errors():
                field = ".".join(str(part) for part in err["loc"]) or "arguments"
                problems.append(f"{field}: {err['msg']}")
            expected = ", ".join(model.model_fields)
            return _bad_arguments(
                f"Bad arguments for {name}. " + "; ".join(problems) + f". Expected exactly: {expected}."
            )

        function = getattr(self.client, name)
        return function(**args.model_dump())