import requests

from utils.logger import get_logger


class BookerClient:
    """Thin wrapper around the Restful-Booker API.

    All HTTP calls go through `_request`, so logging, timeouts and headers
    are handled in one place and tests stay short and readable.
    """

    TIMEOUT = 15

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
        self.log = get_logger("BookerClient")

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}{path}"
        response = self.session.request(method, url, timeout=self.TIMEOUT, **kwargs)
        self.log.info("%s %s -> %s (%.0f ms)", method, url, response.status_code,
                      response.elapsed.total_seconds() * 1000)
        return response

    # ---- Auth ----
    def create_token(self, username: str, password: str) -> requests.Response:
        return self._request("POST", "/auth", json={"username": username, "password": password})

    # ---- Booking CRUD ----
    def get_booking_ids(self, **filters) -> requests.Response:
        return self._request("GET", "/booking", params=filters)

    def get_booking(self, booking_id: int) -> requests.Response:
        return self._request("GET", f"/booking/{booking_id}")

    def create_booking(self, payload: dict) -> requests.Response:
        return self._request("POST", "/booking", json=payload)

    def update_booking(self, booking_id: int, payload: dict, token: str = None) -> requests.Response:
        return self._request("PUT", f"/booking/{booking_id}", json=payload,
                             headers=self._auth_header(token))

    def partial_update_booking(self, booking_id: int, payload: dict, token: str = None) -> requests.Response:
        return self._request("PATCH", f"/booking/{booking_id}", json=payload,
                             headers=self._auth_header(token))

    def delete_booking(self, booking_id: int, token: str = None) -> requests.Response:
        return self._request("DELETE", f"/booking/{booking_id}",
                             headers=self._auth_header(token))

    def health_check(self) -> requests.Response:
        return self._request("GET", "/ping")

    @staticmethod
    def _auth_header(token: str):
        return {"Cookie": f"token={token}"} if token else {}
