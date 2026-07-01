from __future__ import annotations
import json
from pathlib import Path

import pandas as pd
import streamlit as st

from engine import (
    new_game, draw, move_card, cast_from_hand, commander_to_battlefield,
    commander_to_command_zone, advance_turn, to_json, from_json, validate, ZONES,
    deck_summary, parse_decklist, life_change, add_commander_damage, add_token,
    eliminate_player, shuffle_library,
)
from league_store import load_decks, save_decks
from card_images import fetch_card_image, scryfall_search_url

st.set_page_config(page_title="Commander League Simulator v2", layout="wide")
st.title("Commander League Simulator v2")
st.caption("Text + card images, exact zones, league rules, and expandable deck roster.")

if "decklists" not in st.session_state or "commanders" not in st.session_state:
    st.session_state.decklists, st.session_state.commanders = load_decks()
if "game" not in st.session_state:
    st.session_state.game = None
if "show_images" not in st.session_state:
    st.session_state.show_images = True


def card_preview(card_name: str, width: int = 220):
    image = fetch_card_image(card_name)
    if image:
        st.image(image, width=width)
    else:
        st.caption("Image unavailable. Internet may be off or Scryfall did not return an image.")
        st.link_button("Open on Scryfall", scryfall_search_url(card_name))


def zone_select_cards(cards):
    return cards if cards else ["— empty —"]

with st.sidebar:
    st.header("League Controls")
    st.session_state.show_images = st.toggle("Show card pictures", value=st.session_state.show_images)
    seed = st.number_input("Random seed", min_value=0, value=0, step=1, help="Use 0 for a fresh random seed.")
    game_label = st.text_input("Game label", "Season-1-Game-1")

    st.subheader("Choose Pod Decks")
    deck_names = list(st.session_state.decklists.keys())
    default_count = min(4, len(deck_names))
    chosen_decks = st.multiselect("Decks in this game", deck_names, default=deck_names[:default_count])

    if st.button("Start New Game", use_container_width=True):
        if len(chosen_decks) < 2:
            st.error("Choose at least 2 decks.")
        else:
            decks = {name: st.session_state.decklists[name] for name in chosen_decks}
            commanders = {name: st.session_state.commanders[name] for name in chosen_decks}
            st.session_state.game = new_game(decks, commanders, None if seed == 0 else int(seed), game_label)
            st.rerun()

    uploaded = st.file_uploader("Load saved game JSON", type=["json"])
    if uploaded is not None:
        st.session_state.game = from_json(uploaded.read().decode("utf-8"))
        st.success("Saved game loaded.")

main_tabs = st.tabs(["Game", "Deck Manager", "League Rules"])

with main_tabs[1]:
    st.header("Deck Manager")
    st.write("Add more Commander decks to the league. Paste a decklist in `1 Card Name` format and include 99 main-deck cards plus 1 commander line. The app removes the commander before shuffling.")

    with st.expander("Add or replace a deck", expanded=True):
        deck_name = st.text_input("Deck name", placeholder="Example: Veloci-ramp-tor")
        commander = st.text_input("Commander name exactly as listed", placeholder="Example: Pantlaza, Sun-Favored")
        deck_text = st.text_area("99+1 Commander decklist", height=260, placeholder="1 Sol Ring\n1 Arcane Signet\n36 Forest\n1 Commander Name")
        if deck_text and commander:
            summary = deck_summary(deck_text, commander)
            st.json(summary)
        if st.button("Save deck to league roster"):
            if not deck_name.strip() or not commander.strip() or not deck_text.strip():
                st.error("Deck name, commander, and decklist are required.")
            else:
                summary = deck_summary(deck_text, commander)
                if summary["total_cards"] != 100:
                    st.warning(f"This list has {summary['total_cards']} total cards, not 100. It should be 99 main-deck cards plus 1 commander.")
                if not summary["commander_present"]:
                    st.warning("Commander was not found in the decklist. It will save, but game start will not be able to move it from deck to command zone.")
                st.session_state.decklists[deck_name.strip()] = deck_text
                st.session_state.commanders[deck_name.strip()] = commander.strip()
                save_decks(st.session_state.decklists, st.session_state.commanders)
                st.success(f"Saved {deck_name.strip()}.")

    st.subheader("Current League Roster")
    rows = []
    for name, text in st.session_state.decklists.items():
        commander = st.session_state.commanders.get(name, "")
        s = deck_summary(text, commander)
        rows.append({"Deck": name, "Commander": commander, "Total": s["total_cards"], "Main after commander removed": s.get("main_deck_cards_after_commander_removed", ""), "Commander present": s["commander_present"], "Duplicate nonbasics": len(s["duplicates"])})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

with main_tabs[2]:
    st.header("Commander League Rules")
    rules_path = Path(__file__).with_name("LEAGUE_RULES.md")
    st.markdown(rules_path.read_text() if rules_path.exists() else "Rules file missing.")

with main_tabs[0]:
    if st.session_state.game is None:
        st.info("Start a new game from the sidebar. The app will shuffle each selected deck and draw real opening hands.")
        st.subheader("Loaded League Decks")
        st.write(list(st.session_state.decklists.keys()))
        st.stop()

    game = st.session_state.game
    active = game.active_player

    cols = st.columns([2, 1, 1, 1])
    cols[0].metric("Game", game.game_id)
    cols[1].metric("Turn", game.turn)
    cols[2].metric("Active Seat", active + 1)
    cols[3].metric("Active Player", game.player().name)

    issues = validate(game)
    if issues:
        st.error("Validation issues: " + " | ".join(issues))
    else:
        st.success("Game state validates: each player has 100 real cards tracked across zones.")

    st.divider()

    score_rows = []
    for i, p in enumerate(game.players):
        score_rows.append({
            "Seat": i + 1,
            "Deck": p.name,
            "Commander": p.commander,
            "Life": p.life,
            "Eliminated": p.eliminated,
            "Library": len(p.library),
            "Hand": len(p.hand),
            "Battlefield": len(p.battlefield),
            "Graveyard": len(p.graveyard),
            "Exile": len(p.exile),
            "Commander Tax": p.commander_tax,
            "Tokens": len(p.tokens),
        })
    st.dataframe(pd.DataFrame(score_rows), use_container_width=True, hide_index=True)

    st.subheader("Take an Action")
    a1, a2, a3, a4 = st.columns(4)
    with a1:
        chosen_player = st.selectbox("Player", range(len(game.players)), format_func=lambda i: f"Seat {i+1}: {game.players[i].name}")
    with a2:
        action = st.selectbox("Action", [
            "Draw", "Cast from hand to battlefield", "Cast instant/sorcery to graveyard", "Move card",
            "Cast commander", "Commander to command zone", "Life change", "Commander damage",
            "Add token", "Eliminate player", "Shuffle library", "Advance turn"
        ])
    with a3:
        amount = st.number_input("Amount", value=1, step=1)
    with a4:
        st.write(" ")
        st.write(" ")
        do_action = st.button("Apply Action", use_container_width=True)

    p = game.players[chosen_player]
    card = None
    src = dst = None
    source_commander = None
    token_name = None

    if action in {"Cast from hand to battlefield", "Cast instant/sorcery to graveyard"}:
        card = st.selectbox("Card in hand", p.hand) if p.hand else None
        if card and st.session_state.show_images:
            card_preview(card, width=180)
    elif action == "Move card":
        c1, c2, c3 = st.columns(3)
        with c1:
            src = st.selectbox("From zone", ZONES)
        with c2:
            dst = st.selectbox("To zone", ZONES, index=2)
        source_cards = getattr(p, src)
        with c3:
            card = st.selectbox("Card", source_cards) if source_cards else None
        if card and st.session_state.show_images:
            card_preview(card, width=180)
    elif action == "Commander to command zone":
        src = st.selectbox("Commander currently in", ["battlefield", "graveyard", "exile", "hand"])
    elif action == "Commander damage":
        source_commander = st.selectbox("Source commander", [x.commander for x in game.players])
        st.caption("This also subtracts life.")
    elif action == "Life change":
        st.caption("Use negative number for damage/life loss, positive for gain.")
    elif action == "Add token":
        token_name = st.text_input("Token name", "1/1 Eldrazi Spawn")

    if do_action:
        if action == "Draw":
            draw(game, chosen_player, int(amount))
        elif action == "Cast from hand to battlefield" and card:
            cast_from_hand(game, chosen_player, card, "battlefield")
        elif action == "Cast instant/sorcery to graveyard" and card:
            cast_from_hand(game, chosen_player, card, "graveyard")
        elif action == "Move card" and card and src and dst:
            move_card(game, chosen_player, card, src, dst)
        elif action == "Cast commander":
            commander_to_battlefield(game, chosen_player)
        elif action == "Commander to command zone" and src:
            commander_to_command_zone(game, chosen_player, src)
        elif action == "Life change":
            life_change(game, chosen_player, int(amount))
        elif action == "Commander damage" and source_commander:
            add_commander_damage(game, chosen_player, source_commander, int(amount))
        elif action == "Add token" and token_name:
            add_token(game, chosen_player, token_name)
        elif action == "Eliminate player":
            eliminate_player(game, chosen_player)
        elif action == "Shuffle library":
            shuffle_library(game, chosen_player)
        elif action == "Advance turn":
            advance_turn(game)
        st.rerun()

    st.divider()

    c_log, c_preview = st.columns([2, 1])
    with c_log:
        st.subheader("Recent Played Cards")
        if not game.played_cards:
            st.write("No cards played yet.")
        else:
            for item in game.played_cards[:12]:
                st.markdown(f"**Turn {item['turn']} — {item['player']}**: {item['card']}")
                st.caption(item["text"])
    with c_preview:
        st.subheader("Card Pictures")
        if st.session_state.show_images and game.played_cards:
            selected_play = st.selectbox("Preview played card", range(min(12, len(game.played_cards))), format_func=lambda i: game.played_cards[i]["card"])
            card_preview(game.played_cards[selected_play]["card"])
        elif not st.session_state.show_images:
            st.info("Card pictures are turned off in the sidebar.")

    st.divider()
    st.subheader("Player Zones")
    tabs = st.tabs([f"Seat {i+1}: {p.name}" for i, p in enumerate(game.players)])
    for i, tab in enumerate(tabs):
        p = game.players[i]
        with tab:
            z1, z2, z3 = st.columns(3)
            with z1:
                st.markdown("**Hand**")
                st.write(p.hand)
                st.markdown("**Battlefield**")
                st.write(p.battlefield)
                st.markdown("**Tokens**")
                st.write(p.tokens)
            with z2:
                st.markdown("**Command Zone**")
                st.write(p.command_zone)
                st.markdown("**Graveyard**")
                st.write(p.graveyard)
                st.markdown("**Exile**")
                st.write(p.exile)
            with z3:
                st.markdown("**Library**")
                st.write(f"{len(p.library)} cards")
                show_top = st.checkbox(f"Reveal top 10 for {p.name}", key=f"top{i}")
                if show_top:
                    st.write(p.library[:10])
                st.markdown("**Commander Damage Taken**")
                st.write(p.commander_damage)
                p.notes = st.text_area("Notes", p.notes, key=f"notes{i}")
                if st.session_state.show_images:
                    all_visible = p.hand + p.battlefield + p.graveyard + p.exile + p.command_zone
                    if all_visible:
                        preview_name = st.selectbox("Preview any visible card", all_visible, key=f"preview{i}")
                        card_preview(preview_name, width=180)

    st.divider()
    st.subheader("Game Log")
    st.text_area("Log", "\n".join(game.log[:200]), height=300)

    st.download_button("Download Saved Game JSON", to_json(game), file_name=f"{game.game_id}.json", mime="application/json")
