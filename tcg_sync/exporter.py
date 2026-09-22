
import json
import os
import re


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "set"


class Exporter:
    """Guarda los datos normalizados como JSON fraccionado en data/."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self._manifest: list[dict] = []

    def save_apitcg_set(self, tcg: str, set_id: str, set_name: str, cards: list[dict]) -> str:
        set_dir = f"{self.data_dir}/apitcg/{tcg}"
        os.makedirs(set_dir, exist_ok=True)
        slug = _slugify(set_id)
        path = f"{set_dir}/{slug}.json"
        self._write(path, cards)
        self._manifest.append({
            "source": "apitcg",
            "tcg": tcg,
            "deck": set_id,
            "name": set_name,
            "count": len(cards),
            "path": path,
        })
        return path

    def save_apitcg_sets_index(self, tcg: str, sets: list[dict]) -> str:
        set_dir = f"{self.data_dir}/apitcg/{tcg}"
        os.makedirs(set_dir, exist_ok=True)
        path = f"{set_dir}/_sets.json"
        self._write(path, sets)
        return path

    def save_pokemon(self, pokemon: list[dict]) -> str:
        pdir = f"{self.data_dir}/pokeapi"
        os.makedirs(pdir, exist_ok=True)
        path = f"{pdir}/pokemon.json"
        self._write(path, pokemon)
        self._manifest.append({
            "source": "pokeapi",
            "tcg": None,
            "deck": "pokemon",
            "name": "Pokémon",
            "count": len(pokemon),
            "path": path,
        })
        return path

    def save_deckofcards(self, cards: list[dict]) -> str:
        ddir = f"{self.data_dir}/deckofcards"
        os.makedirs(ddir, exist_ok=True)
        path = f"{ddir}/standard-52.json"
        self._write(path, cards)
        self._manifest.append({
            "source": "deckofcards",
            "tcg": None,
            "deck": "poker-standard",
            "name": "Baraja estandar (52 + jokers)",
            "count": len(cards),
            "path": path,
        })
        return path

    def save_manifest(self) -> str:
        path = f"{self.data_dir}/manifest.json"
        self._write(path, {"decks": self._manifest})
        return path

    @staticmethod
    def _write(path: str, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
