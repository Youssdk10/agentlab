AgentLab default spec: an order desk
Tables: customers(id, name, email, address), orders(id, customer_id, status, placed_at, total), order_items(order_id, sku, qty, price), notes(id, order_id, text, created_at). Order status: placed, shipped, delivered, cancelled, refunded.

Policy rules (write these in plain English in DESIGN.md):

An order can be cancelled only if its status is placed.
A refund is allowed only for delivered orders placed within 30 days and only once per order.
Address changes are allowed only on placed orders.
Refund amount cannot exceed the order total.
Notes may be added to any order and never change its status.
The agent must not act on an order that belongs to a different customer than the one verified in the conversation.
Tools: get_order(order_id), list_orders(customer_id), cancel_order(order_id), refund_order(order_id, amount), update_address(order_id, new_address), add_note(order_id, text).

Scenario categories (aim for about 6-8 each): simple lookup; valid write (cancel a placed order); policy refusal (refund an order older than 30 days, so the database must stay unchanged); multi-step (find the customer's latest order, then cancel it); wrong-customer attempt; error recovery (first tool call fails once).

Failure types to inject: timeout, HTTP 500, malformed JSON in the response, duplicated response. Always seeded.

Metrics: success per run (database matches expected rows), pass^k as the fraction of scenarios where all k runs succeeded, average steps, tool calls, loop count, tokens, estimated cost.