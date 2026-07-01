from __future__ import annotations
import urllib.parse
from typing import Optional, Dict, Any

import requests
import streamlit as st

SCRYFALL_NAMED = "https://api.scryfall.com/cards/named?exact="
SCRYFALL_SEARCH = "https://scryfall.com/search?as=grid&order=name&q=!"


def scryfall_search_url(card_name: str) -> str:
    return SCRYFALL_SEARCH + urllib.parse.quote(card_name)


@st.cache_data(show_spinner=False, ttl=60 * 60 * 24)
def fetch_card_image(card_name: str) -> Optional[str]:
    """Return a Scryfall normal image URI, or None if unavailable.

    This needs internet access where the Streamlit app is running. If the app is
    offline, the UI will still work and display text/logs plus a Scryfall link.
    """
    try:
        url = SCRYFALL_NAMED + urllib.parse.quote(card_name)
        r = requests.get(url, timeout=8)
        if r.status_code != 200:
            return None
        data: Dict[str, Any] = r.json()
        if "image_uris" in data:
            return data["image_uris"].get("normal") or data["image_uris"].get("large")
        faces = data.get("card_faces") or []
        for face in faces:
            if "image_uris" in face:
                return face["image_uris"].get("normal") or face["image_uris"].get("large")
    except Exception:
        return None
    return None
