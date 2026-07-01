# Commander League Simulator v2

A Streamlit app for tracking your Commander deck-building league with exact game zones, card images, rules, and support for adding more decks.

## What's included

- Four starting league decks:
  - Eldrazi Incursion / Ulalek
  - Pantlaza
  - Aesi
  - Disa
- Add or replace decks from the Deck Manager.
- Start games with any 2+ decks from the roster.
- Shuffle with a seed and draw real opening hands.
- Track every real card across:
  - Library
  - Hand
  - Battlefield
  - Graveyard
  - Exile
  - Command zone
- Track life, commander tax, commander damage, tokens, eliminated players, and notes.
- Save/load games as JSON.
- Show card pictures for cards as they are played using Scryfall.

## Important note about card pictures

Card images are loaded from Scryfall while the app is running. If your computer/server has no internet connection, the simulator still works, but images may not appear. Text logs and all game tracking still work.


## Deploy as a web app for iPhone

See `DEPLOY_TO_IPHONE.md`. The quick version is: upload this folder to GitHub, deploy it on Streamlit Community Cloud, then open the Streamlit link on your iPhone.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Use on iPhone

Best options:

1. Deploy this folder to Streamlit Community Cloud and open the app link on your iPhone.
2. Run it on a home computer and open the local Streamlit network URL from your iPhone.

## Adding decks

Open the **Deck Manager** tab, then paste a decklist like this:

```text
1 Sol Ring
1 Arcane Signet
36 Forest
1 Commander Name
```

Enter the deck name and commander name exactly. The app will save the deck into `league_decks.json`.

## What this app is

This is a structured Commander game-state tracker and league ledger. It prevents cards from accidentally appearing twice and gives you a clean record of every zone.

## What this app is not yet

It is not a full Magic rules engine. It does not automatically resolve every card's rules text. You still choose the actions, and the app records them accurately.
