import httpx


class OrderDeskClient:
    def __init__(self, http):
        # http is anything with a .request(method, path, json=...) method:
        # a TestClient in tests, or httpx.Client(base_url=..., timeout=5.0) for the real server.
        self.http = http

    def _request(self, method, path, json=None):
        try:
            response = self.http.request(method, path, json=json)
        except httpx.TimeoutException:
            return {"error": "timeout", "message": "The order desk did not answer in time."}
        except httpx.HTTPError as exc:
            return {"error": "connection_error", "message": f"Could not reach the order desk: {exc}"}

        if response.status_code >= 500:
            return {
                "error": "server_error",
                "message": f"The order desk failed (HTTP {response.status_code}).",
            }

        try:
            body = response.json()
        except ValueError:
            return {"error": "invalid_response", "message": "The order desk returned something that is not JSON."}

        if not isinstance(body, dict):
            return {"error": "invalid_response", "message": "The order desk returned an unexpected response."}
        if "error" not in body and "detail" in body:
            return {"error": "invalid_request", "message": "The request was rejected as malformed."}
        return body

    def get_order(self, order_id):
        return self._request("GET", f"/orders/{order_id}")

    def list_orders(self, customer_id):
        return self._request("GET", f"/customers/{customer_id}/orders")

    def cancel_order(self, order_id):
        return self._request("POST", f"/orders/{order_id}/cancel")

    def refund_order(self, order_id, amount):
        return self._request("POST", f"/orders/{order_id}/refund", json={"amount": amount})

    def update_address(self, order_id, new_address):
        return self._request("PUT", f"/orders/{order_id}/address", json={"new_address": new_address})

    def add_note(self, order_id, text):
        return self._request("POST", f"/orders/{order_id}/notes", json={"text": text})

    def reset(self):
        return self._request("POST", "/reset")
    