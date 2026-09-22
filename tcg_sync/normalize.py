
"""Normaliza cada fuente al esquema unificado que consume el juego:

    {
        "source": "apitcg" | "pokeapi" | "deckofcards",
        "deck": "<id del mazo/set>",
        "id": "<id unico dentro de la fuente>",
        "name": "...",
        "image": {"small": "...", "medium": "...", "large": "..."},
        "attributes": {...}
    }
"""


def normalize_apitcg_card(raw: dict, tcg: str, set_id: str) -> dict:
    images = raw.get("images") or [{}]
    img = images[0] if images else {}
    attributes = dict(raw.get("attributes") or {})
    attributes["code"] = raw.get("code")
    return {
        "source": "apitcg",
        "deck": set_id,
        "id": raw.get("_id"),
        "name": raw.get("name"),
        "image": {
            "small": img.get("small"),
            "medium": img.get("medium"),
            "large": img.get("large"),
        },
        "attributes": attributes,
    }


def normalize_pokemon(raw: dict) -> dict:
    sprites = raw.get("sprites") or {}
    other = sprites.get("other") or {}
    artwork = other.get("official-artwork") or {}
    home = other.get("home") or {}
    stats = {
        s["stat"]["name"]: s["base_stat"]
        for s in raw.get("stats", [])
    }
    return {
        "source": "pokeapi",
        "deck": "pokemon",
        "id": raw.get("id"),
        "name": raw.get("name"),
        "image": {
            "small": sprites.get("front_default"),
            "medium": artwork.get("front_default"),
            "large": home.get("front_default") or artwork.get("front_default"),
        },
        "attributes": {
            "types": [t["type"]["name"] for t in raw.get("types", [])],
            "abilities": [a["ability"]["name"] for a in raw.get("abilities", [])],
            "stats": stats,
            "height": raw.get("height"),
            "weight": raw.get("weight"),
            "shiny_image": artwork.get("front_shiny"),
        },
    }


def normalize_deckofcards_card(raw: dict) -> dict:
    images = raw.get("images") or {}
    return {
        "source": "deckofcards",
        "deck": "poker-standard",
        "id": raw.get("code"),
        "name": f"{raw.get('value')} of {raw.get('suit')}" if raw.get("suit") else raw.get("value"),
        "image": {
            "small": raw.get("image"),
            "medium": images.get("png"),
            "large": images.get("svg"),
        },
        "attributes": {
            "value": raw.get("value"),
            "suit": raw.get("suit"),
        },
    }
