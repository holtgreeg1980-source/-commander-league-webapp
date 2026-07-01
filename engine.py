from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional
import random, time, json

ZONES = ["library", "hand", "battlefield", "graveyard", "exile", "command_zone"]
BASIC_LANDS = {"Plains", "Island", "Swamp", "Mountain", "Forest", "Wastes"}


def parse_decklist(text: str) -> List[str]:
    cards: List[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(" ", 1)
        if len(parts) != 2 or not parts[0].isdigit():
            continue
        count, name = int(parts[0]), parts[1].strip()
        cards.extend([name] * count)
    return cards


def deck_summary(text: str, commander: str) -> Dict[str, Any]:
    cards = parse_decklist(text)
    counts = {c: cards.count(c) for c in sorted(set(cards))}
    return {
        "total_cards": len(cards),
        "commander_count": cards.count(commander),
        "main_deck_cards_after_commander_removed": len(cards) - min(cards.count(commander), 1),
        "commander_present": commander in cards,
        "unique_cards": len(set(cards)),
        "duplicates": {c: n for c, n in counts.items() if n > 1 and c not in BASIC_LANDS},
    }

@dataclass
class PlayerState:
    name: str
    commander: str
    life: int = 40
    eliminated: bool = False
    finish_place: Optional[int] = None
    commander_tax: int = 0
    commander_damage: Dict[str, int] = field(default_factory=dict)
    library: List[str] = field(default_factory=list)
    hand: List[str] = field(default_factory=list)
    battlefield: List[str] = field(default_factory=list)
    graveyard: List[str] = field(default_factory=list)
    exile: List[str] = field(default_factory=list)
    command_zone: List[str] = field(default_factory=list)
    tokens: List[str] = field(default_factory=list)
    counters: Dict[str, str] = field(default_factory=dict)
    notes: str = ""

@dataclass
class GameState:
    game_id: str
    turn: int = 1
    active_player: int = 0
    players: List[PlayerState] = field(default_factory=list)
    stack: List[str] = field(default_factory=list)
    log: List[str] = field(default_factory=list)
    played_cards: List[Dict[str, Any]] = field(default_factory=list)
    seed: int = 0
    rules_notes: str = "Commander League v2"
    season_stats: Dict[str, Any] = field(default_factory=dict)

    def add_log(self, text: str, card: Optional[str] = None, player_idx: Optional[int] = None) -> None:
        stamp = f"T{self.turn} P{self.active_player+1}"
        self.log.insert(0, f"{stamp}: {text}")
        if card:
            idx = self.active_player if player_idx is None else player_idx
            name = self.players[idx].name if 0 <= idx < len(self.players) else "Unknown"
            self.played_cards.insert(0, {"turn": self.turn, "player": name, "card": card, "text": text})
            self.played_cards = self.played_cards[:80]

    def player(self, idx: Optional[int] = None) -> PlayerState:
        return self.players[self.active_player if idx is None else idx]


def new_game(decklists: Dict[str, str], commanders: Dict[str, str], seed: Optional[int] = None, game_id: str = "Season-1-Game-1") -> GameState:
    if seed is None or seed == 0:
        seed = int(time.time())
    rng = random.Random(seed)
    game = GameState(game_id=f"{game_id}-{seed}", seed=seed)
    items = list(decklists.items())
    # Preserve league order; user can randomize seating in app if desired.
    for deck_name, text in items:
        cards = parse_decklist(text)
        commander = commanders[deck_name]
        if commander in cards:
            cards.remove(commander)
        rng.shuffle(cards)
        p = PlayerState(name=deck_name, commander=commander, library=cards, command_zone=[commander])
        for _ in range(7):
            if p.library:
                p.hand.append(p.library.pop(0))
        game.players.append(p)
    game.add_log(f"New game started. Seed {seed}. Opening hands drawn.")
    return game


def draw(game: GameState, player_idx: int, n: int = 1) -> List[str]:
    p = game.players[player_idx]
    drawn: List[str] = []
    for _ in range(n):
        if not p.library:
            game.add_log(f"{p.name} tried to draw from an empty library.")
            break
        card = p.library.pop(0)
        p.hand.append(card)
        drawn.append(card)
    game.add_log(f"{p.name} drew {', '.join(drawn) if drawn else 'nothing'}.")
    return drawn


def move_card(game: GameState, player_idx: int, card: str, src: str, dst: str) -> bool:
    p = game.players[player_idx]
    if src not in ZONES or dst not in ZONES:
        raise ValueError("Invalid zone")
    source = getattr(p, src)
    dest = getattr(p, dst)
    if card not in source:
        game.add_log(f"ERROR: {card} not found in {p.name}'s {src}.")
        return False
    source.remove(card)
    dest.append(card)
    game.add_log(f"{p.name}: {card} moved {src} → {dst}.", card=card, player_idx=player_idx)
    return True


def cast_from_hand(game: GameState, player_idx: int, card: str, destination: str = "battlefield") -> bool:
    return move_card(game, player_idx, card, "hand", destination)


def commander_to_battlefield(game: GameState, player_idx: int) -> bool:
    p = game.players[player_idx]
    ok = move_card(game, player_idx, p.commander, "command_zone", "battlefield")
    if ok:
        game.add_log(f"{p.name} cast commander {p.commander}. Current tax: {p.commander_tax}.", card=p.commander, player_idx=player_idx)
    return ok


def commander_to_command_zone(game: GameState, player_idx: int, src: str = "battlefield") -> bool:
    p = game.players[player_idx]
    if move_card(game, player_idx, p.commander, src, "command_zone"):
        p.commander_tax += 2
        game.add_log(f"{p.commander} returned to command zone. New tax {p.commander_tax}.", card=p.commander, player_idx=player_idx)
        return True
    return False


def life_change(game: GameState, player_idx: int, amount: int) -> None:
    p = game.players[player_idx]
    p.life += amount
    game.add_log(f"{p.name} life changed by {amount} to {p.life}.")


def add_commander_damage(game: GameState, target_idx: int, source_commander: str, amount: int) -> None:
    p = game.players[target_idx]
    p.commander_damage[source_commander] = p.commander_damage.get(source_commander, 0) + amount
    p.life -= amount
    game.add_log(f"{p.name} took {amount} commander damage from {source_commander}. Total from that commander: {p.commander_damage[source_commander]}. Life {p.life}.", card=source_commander)


def add_token(game: GameState, player_idx: int, token_name: str) -> None:
    p = game.players[player_idx]
    p.tokens.append(token_name)
    game.add_log(f"{p.name} created token: {token_name}.")


def eliminate_player(game: GameState, player_idx: int) -> None:
    p = game.players[player_idx]
    remaining = [x for x in game.players if not x.eliminated]
    p.eliminated = True
    p.finish_place = len(remaining)
    game.add_log(f"{p.name} eliminated. Finish place: {p.finish_place}.")


def advance_turn(game: GameState) -> None:
    if not game.players:
        return
    for _ in range(len(game.players)):
        game.active_player = (game.active_player + 1) % len(game.players)
        if game.active_player == 0:
            game.turn += 1
        if not game.players[game.active_player].eliminated:
            break
    game.add_log(f"Turn advanced. Active player: {game.player().name}.")


def shuffle_library(game: GameState, player_idx: int) -> None:
    rng = random.Random(game.seed + game.turn + player_idx + len(game.log))
    rng.shuffle(game.players[player_idx].library)
    game.add_log(f"{game.players[player_idx].name} shuffled their library.")


def to_json(game: GameState) -> str:
    return json.dumps(asdict(game), indent=2)


def from_json(text: str) -> GameState:
    data = json.loads(text)
    players = [PlayerState(**p) for p in data.pop("players")]
    return GameState(players=players, **data)


def validate(game: GameState) -> List[str]:
    issues: List[str] = []
    for p in game.players:
        zones_count = sum(len(getattr(p, z)) for z in ZONES)
        if p.commander not in [card for z in ZONES for card in getattr(p, z)]:
            issues.append(f"{p.name}: commander not found in any zone.")
        if zones_count != 100:
            issues.append(f"{p.name}: tracked card count is {zones_count}, expected 100 including commander in command zone. Tokens are separate: {len(p.tokens)}")
        if len(p.library) + len(p.hand) + len(p.battlefield) + len(p.graveyard) + len(p.exile) != 99:
            issues.append(f"{p.name}: non-commander zones total should be 99 cards after commander is separated.")
    return issues
