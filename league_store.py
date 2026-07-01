from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Tuple
from decks import DECKLISTS as DEFAULT_DECKS, COMMANDERS as DEFAULT_COMMANDERS

STORE = Path(__file__).with_name("league_decks.json")


def load_decks() -> Tuple[Dict[str, str], Dict[str, str]]:
    decks = dict(DEFAULT_DECKS)
    commanders = dict(DEFAULT_COMMANDERS)
    if STORE.exists():
        try:
            data = json.loads(STORE.read_text())
            decks.update(data.get("decklists", {}))
            commanders.update(data.get("commanders", {}))
        except Exception:
            pass
    return decks, commanders


def save_decks(decklists: Dict[str, str], commanders: Dict[str, str]) -> None:
    custom_decks = {k: v for k, v in decklists.items() if k not in DEFAULT_DECKS or DEFAULT_DECKS.get(k) != v}
    custom_commanders = {k: v for k, v in commanders.items() if k not in DEFAULT_COMMANDERS or DEFAULT_COMMANDERS.get(k) != v}
    STORE.write_text(json.dumps({"decklists": custom_decks, "commanders": custom_commanders}, indent=2))
