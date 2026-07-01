# Commander League Rules

## League Format

- Default pod size: 4 players.
- Starting life: 40.
- Commander rules apply, including commander tax and commander damage.
- Decks must be exactly 100 cards including commander unless you intentionally mark a deck as casual/test.
- Singleton rule applies except basic lands and cards that explicitly allow extra copies.
- Seating order should be randomized for each game.
- Each game uses a random seed so it can be replayed if needed.

## Game Tracking Rules

Every game should track:

- Library order after shuffle.
- Opening hands.
- Mulligans.
- Battlefield.
- Graveyard.
- Exile.
- Command zone.
- Commander tax.
- Life totals.
- Commander damage.
- Tokens and counters.
- A complete game log.

A card may only move between zones through a logged action. If a card is cast, destroyed, exiled, bounced, or searched for, it must move to the correct zone.

## Mulligans

Use the London mulligan:

1. Draw 7.
2. For each mulligan, shuffle hand into library and draw 7 again.
3. Put one card on the bottom of the library for each mulligan taken.

The app currently tracks hands and libraries; mulligan decisions can be done manually with zone movement until automated mulligans are added.

## Scoring

Recommended Season 1 scoring:

- Winner: 5 points.
- 2nd place: 3 points.
- 3rd place: 1 point.
- 4th place: 0 points.
- Commander kill bonus: +1 point.
- First blood bonus: +1 point for the first player to deal combat damage to another player.
- No infinite-combo bonus stacking unless the league agrees before the game.

## Season Records

Track these stats across games:

- Wins.
- Pod appearances.
- Average finish.
- Total points.
- Commander casts.
- Commander kills.
- First bloods.
- Average turn of victory.
- Most valuable card for each game.
- Notes about misplays or rules corrections.

## Adding New Decks

A deck list should use this format:

```text
1 Sol Ring
1 Arcane Signet
36 Forest
1 Commander Name
```

When adding a deck, enter:

- Deck name.
- Commander name exactly as it appears in the list.
- Full 100-card decklist.

The simulator will parse the list, move the commander to the command zone at game start, and validate that exactly 100 cards are tracked.
