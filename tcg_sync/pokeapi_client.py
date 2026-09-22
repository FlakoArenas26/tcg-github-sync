
import time
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential


class PokeAPIClient:
    """Cliente para pokeapi.co. Sin API key, pero se throttlea por respeto
    al servicio gratuito."""

    BASE_URL = "https://pokeapi.co/api/v2"

    def __init__(self, requests_per_second: float = 8.0):
        self.min_interval = 1.0 / requests_per_second
        self._last_call = 0.0
        self._client = httpx.Client(timeout=30.0)

    def _throttle(self):
        elapsed = time.time() - self._last_call
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self._last_call = time.time()

    @retry(stop=stop_after_attempt(5),
           wait=wait_exponential(multiplier=2, min=2, max=60))
    def get(self, url: str):
        self._throttle()
        resp = self._client.get(url)
        if resp.status_code == 429:
            raise httpx.HTTPStatusError("429", request=resp.request, response=resp)
        resp.raise_for_status()
        return resp.json()

    def list_pokemon(self) -> list[dict]:
        """Devuelve [{name, url}, ...] para todos los pokemon (paginado)."""
        entries, url = [], f"{self.BASE_URL}/pokemon?limit=200&offset=0"
        while url:
            data = self.get(url)
            entries.extend(data["results"])
            url = data.get("next")
        return entries

    def get_pokemon(self, url: str) -> dict:
        return self.get(url)
