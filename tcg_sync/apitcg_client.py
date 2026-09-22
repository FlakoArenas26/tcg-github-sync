
import time
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential


class APITCGClient:
    """Cliente para api.apitcg.com. Endpoint real de cartas: /api/products
    (no /api/{tcg}/cards, que no existe)."""

    BASE_URL = "https://api.apitcg.com"

    def __init__(self, api_key: str, requests_per_minute: int = 30):
        self.min_interval = 60.0 / requests_per_minute
        self._last_call = 0.0
        self._client = httpx.Client(
            headers={"x-api-key": api_key}, timeout=60.0
        )

    def _throttle(self):
        elapsed = time.time() - self._last_call
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self._last_call = time.time()

    @retry(stop=stop_after_attempt(5),
           wait=wait_exponential(multiplier=2, min=2, max=60))
    def get(self, path: str, params: dict | None = None):
        self._throttle()
        resp = self._client.get(f"{self.BASE_URL}{path}", params=params)
        if resp.status_code == 429:
            raise httpx.HTTPStatusError("429", request=resp.request, response=resp)
        resp.raise_for_status()
        return resp.json()

    def list_tcgs(self) -> list[dict]:
        return self.get("/api/tcgs")["data"]

    def list_sets(self, tcg: str) -> list[dict]:
        sets, page = [], 1
        while True:
            data = self.get(f"/api/{tcg}/sets", params={"page": page, "limit": 100})
            batch = data.get("data", [])
            if not batch:
                break
            sets.extend(batch)
            if len(batch) < 100:
                break
            page += 1
        return sets

    def list_cards_for_set(self, tcg: str, set_id: str) -> list[dict]:
        cards, page = [], 1
        while True:
            data = self.get("/api/products", params={
                "type": "card", "tcg": tcg, "set": set_id,
                "limit": 100, "page": page,
            })
            batch = data.get("data", [])
            if not batch:
                break
            cards.extend(batch)
            if len(batch) < 100:
                break
            page += 1
        return cards
