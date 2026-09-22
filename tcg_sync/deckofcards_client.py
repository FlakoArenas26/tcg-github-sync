
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential


class DeckOfCardsClient:
    """Cliente para deckofcardsapi.com. Solo usamos el catalogo estatico de
    52 cartas + 2 jokers (no manejamos sesiones de partida aca, eso es
    logica del juego)."""

    BASE_URL = "https://deckofcardsapi.com/api/deck"

    def __init__(self):
        self._client = httpx.Client(timeout=30.0)

    @retry(stop=stop_after_attempt(5),
           wait=wait_exponential(multiplier=2, min=2, max=30))
    def _get(self, url: str):
        resp = self._client.get(url)
        resp.raise_for_status()
        return resp.json()

    def get_standard_deck(self) -> list[dict]:
        new_deck = self._get(f"{self.BASE_URL}/new/shuffle/?jokers_enabled=true&deck_count=1")
        deck_id = new_deck["deck_id"]
        drawn = self._get(f"{self.BASE_URL}/{deck_id}/draw/?count=54")
        return drawn["cards"]
