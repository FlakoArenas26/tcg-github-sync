
# TCG GitHub Sync

Descarga cartas de **apitcg** (18 TCGs), **pokeapi** (Pokémon) y
**deckofcardsapi** (baraja estándar), las normaliza a un esquema único y
las guarda como JSON en **este mismo repo de GitHub**. El juego lee los
archivos crudos desde `raw.githubusercontent.com` — cero peticiones a las
APIs de origen, cero cuota quemada.

## Flujo

```
[ tu PC / GitHub Actions ]  --sync-->  apitcg / pokeapi / deckofcardsapi
                                        |
                                   guarda JSON normalizado
                                        |
                                   push a este repo
                                        |
[ tu juego ] <--lee raw.githubusercontent.com--┘
```

## Esquema unificado

Toda carta, de cualquier fuente, tiene la misma forma:

```json
{
  "source": "apitcg | pokeapi | deckofcards",
  "deck": "id del mazo/set (ej. one-piece-pillars-of-strength, pokemon, poker-standard)",
  "id": "id unico dentro de la fuente",
  "name": "...",
  "image": {"small": "...", "medium": "...", "large": "..."},
  "attributes": {}
}
```

Las imágenes son siempre URLs a los CDN originales (TCGPlayer, GitHub de
PokeAPI, deckofcardsapi.com) — nunca se versionan binarios, para mantener
el repo liviano.

## Estructura de datos

```
data/
  manifest.json                   # índice de todos los mazos disponibles
  apitcg/{tcg}/_sets.json         # sets/expansiones de ese TCG
  apitcg/{tcg}/{set-slug}.json    # cartas de ese set
  pokeapi/pokemon.json            # todos los pokemon (campos curados)
  deckofcards/standard-52.json    # 52 cartas + 2 jokers
```

`manifest.json` es el punto de entrada: lista cada mazo con su `source`,
`deck`, `name`, `count` y `path`, para que el juego sepa qué mazos existen
sin tener que descargar todo.

## Uso

```bash
cp .env.example .env   # editalo con tus datos
pip install -r requirements.txt
python sync.py
```

Esto descarga todo (apitcg puede tardar por el volumen: ~296k cartas) y
hace push automático.

## Leer los datos desde el juego

```python
import httpx

BASE = "https://raw.githubusercontent.com/FlakoArenas26/tcg-github-sync/main/data"

def get_manifest():
    return httpx.get(f"{BASE}/manifest.json", timeout=30).json()

def get_deck(path: str):
    return httpx.get(f"{BASE}/{path}", timeout=30).json()
```

GitHub sirve estos archivos por CDN — es gratis y rapidísimo. **El juego
no debe espejar el catálogo completo en su base de datos**: solo debe
guardar lo relacional propio de cada partida/usuario (referenciando
`source` + `deck` + `id`), y pedir el JSON del mazo puntual cuando lo
necesita.

## Sync automático

El workflow `.github/workflows/sync.yml` corre el sync automáticamente
una vez al día usando GitHub Actions. Necesitás agregar el secret
`APITCG_API_KEY` en Settings → Secrets → Actions (el `GITHUB_TOKEN` ya lo
provee GitHub Actions automáticamente).
