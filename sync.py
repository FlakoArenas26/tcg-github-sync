
"""Entry point: corre esto localmente o desde GitHub Actions.

    python sync.py

Descarga apitcg (todas las TCGs), pokeapi (todos los pokemon) y
deckofcardsapi (baraja estandar), normaliza todo al esquema unificado,
guarda JSON fraccionado en data/ y hace push al repo de GitHub.
"""

import os
from dotenv import load_dotenv
from tcg_sync import APITCGClient, PokeAPIClient, DeckOfCardsClient, Exporter, Publisher
from tcg_sync.normalize import normalize_apitcg_card, normalize_pokemon, normalize_deckofcards_card

load_dotenv()


def sync_apitcg(exporter: Exporter):
    client = APITCGClient(
        api_key=os.environ["APITCG_API_KEY"],
        requests_per_minute=int(os.getenv("REQUESTS_PER_MINUTE", "30")),
    )
    tcgs = client.list_tcgs()
    tcg_ids = [t["_id"] for t in tcgs]
    print(f"TCGs encontrados: {tcg_ids}")

    for tcg in tcg_ids:
        sets = client.list_sets(tcg)
        exporter.save_apitcg_sets_index(tcg, sets)
        print(f"⬇️  {tcg}: {len(sets)} sets")
        for s in sets:
            set_id = s["_id"]
            raw_cards = client.list_cards_for_set(tcg, set_id)
            if not raw_cards:
                continue
            cards = [normalize_apitcg_card(c, tcg, set_id) for c in raw_cards]
            path = exporter.save_apitcg_set(tcg, set_id, s.get("name", set_id), cards)
            print(f"   {set_id}: {len(cards)} cartas -> {path}")


def sync_pokeapi(exporter: Exporter):
    client = PokeAPIClient()
    entries = client.list_pokemon()
    print(f"⬇️  pokeapi: {len(entries)} pokemon")
    pokemon = []
    for i, e in enumerate(entries, 1):
        raw = client.get_pokemon(e["url"])
        pokemon.append(normalize_pokemon(raw))
        if i % 100 == 0:
            print(f"   {i}/{len(entries)} pokemon procesados")
    path = exporter.save_pokemon(pokemon)
    print(f"   {len(pokemon)} pokemon -> {path}")


def sync_deckofcards(exporter: Exporter):
    client = DeckOfCardsClient()
    raw_cards = client.get_standard_deck()
    cards = [normalize_deckofcards_card(c) for c in raw_cards]
    path = exporter.save_deckofcards(cards)
    print(f"⬇️  deckofcards: {len(cards)} cartas -> {path}")


def main():
    exporter = Exporter("data")

    sync_deckofcards(exporter)
    sync_pokeapi(exporter)
    sync_apitcg(exporter)

    manifest_path = exporter.save_manifest()
    print(f"📇 manifest -> {manifest_path}")

    publisher = Publisher(
        repo_dir=os.getcwd(),
        github_repo=os.environ["GITHUB_REPO"],
        github_token=os.getenv("GITHUB_TOKEN") or None,
    )
    publisher.publish()
    print("🎉 Sync completo.")


if __name__ == "__main__":
    main()
