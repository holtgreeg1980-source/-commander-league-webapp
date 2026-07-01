# Commander League Simulator Web App v2 — 99+1 Commander Format

This Streamlit web app runs a Commander league with exact zone tracking.

## Correct deck format
Each deck is stored as a 100-card list by quantity:
- 99 cards become the shuffled library.
- 1 listed commander is removed and put in the command zone.

At game start, each player draws a random 7-card opening hand from the 99-card library.

## Included Season 1 decks
- Eldrazi Incursion — commander: Ulalek, Fused Atrocity
- Pantlaza — commander: Pantlaza, Sun-Favored
- Aesi — commander: Aesi, Tyrant of Gyre Strait
- Disa — commander: Disa the Restless

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy for iPhone
Upload this folder to GitHub, then deploy `app.py` on Streamlit Community Cloud. Open the Streamlit link on iPhone Safari and use Share → Add to Home Screen.
