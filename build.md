# Mahjong CLI Build Plan

This document outlines a practical, incremental plan for building a full command-line Mahjong project with 4 players, all interacting through terminal input.

The goal for the first iteration is a working, playable CLI game where:
- 4 players are seated and controlled in the terminal
- each player can enter commands into the console
- turns progress in order
- the game tracks hands, discards, wall, melds, and win conditions
- the system is structured cleanly enough to extend later with AI, scoring, and rule variants

## AI design principles for every change

These principles apply to every implementation step, code review, and refactor.

- YAGNI: Don't build it until you need it.
- DRY: Extract patterns after the second duplication, not before.
- Fail Fast: Explicit errors beat silent failures.
- Simple First: Write the obvious solution, optimize only if needed.
- Delete Aggressively: Less code = fewer bugs.
- Semantic Naming: Always name variables, parameters, and API surfaces with verbose, self-documenting names that optimize for comprehension by both humans and LLMs, not brevity. Examples:
  - Prefer `waitUntilObjectIsSaved = true` over `wait = true`
  - Prefer `playerSeatNumber` over `seat`
  - Prefer `discardedTileIndices` over `discarded`
- Naming the app in identifiers: spell it out as `Batterby` / `batterby` in code — variables, constants, config values, and storage keys. The short `btb` / `BTB_` form is only for identifiers that are also read outside this codebase and benefit from being terse: DOM ids and classes in the browser extension, Blender object prefixes, and generated filenames.

Follow these principles strictly during implementation. If a feature is not required for the current milestone, do not add it. If a pattern repeats twice, extract it. If something can fail unexpectedly, raise a clear error immediately. Prefer obvious logic over clever abstractions.

## 1. Project structure and architecture

The project already has a sensible folder structure:

- `src/mahjong/__main__.py`  
  Application entry point.

- `src/mahjong/core/`  
  Core game engine and model classes.

- `src/mahjong/players/`  
  Player definitions and turn logic.

- `src/mahjong/rules/`  
  Rule variations and scoring logic.

- `src/mahjong/ui/`  
  Command-line rendering, prompts, and terminal display helpers.

This is the right high-level separation. For a CLI-first project, the most important thing is to keep business logic separate from UI code.

### Architecture principle

Keep these responsibilities distinct:
- `core/` = game state and rules engine
- `players/` = behavior and input strategies
- `ui/` = console presentation and input/output
- `rules/` = special rules and score validation

The UI should not directly manipulate the game state too much. Instead, it should read state and send player commands into the game engine.

## 2. Recommended build sequence

Build in this order:

### Step 1: Create the game model

Start with the foundational data structures:
- `Tile`
- `Suit` or tile type definitions
- `Player`
- `Hand`
- `Meld`
- `Wall`
- `DiscardPile`
- `GameState`

This is the root of the entire project.

#### Why this comes first
A terminal UI is easy to fake, but the actual game logic is hard. If the model is wrong, the UI will just reflect broken state.

#### Deliverable for this step
A simple model where:
- a tile has identity and type
- a player has a hand
- a wall can be created and shuffled
- a discard pile exists
- a game state holds current turn, dealer, and player list

### Step 2: Implement the turn loop

Build a `Game` object that controls the flow of the match.

Core methods to define:
- `start_game()`
- `deal_initial_hands()`
- `draw_tile(player)`
- `discard_tile(player, tile)`
- `next_turn()`
- `check_win(player)`
- `handle_turn(player)`

This gives you a working game cycle.

#### Basic flow
1. Create 4 players.
2. Shuffle wall and deal tiles.
3. Determine dealer and starting player.
4. In turn order:
   - current player draws a tile
   - current player chooses discard or action
   - discard is recorded
   - next player becomes active
5. Continue until win or termination condition is met.

This is the most important milestone for the first build.

### Step 3: Define player abstraction

Create a common `Player` interface that all players implement.

At minimum:
- `name`
- `seat`
- `hand`
- `discarded_tiles`
- `melds`
- `draw_tile(tile)`
- `discard_tile(tile)`
- `choose_discard()`
- `choose_action(options)`

For the first iteration, you can have:
- `HumanPlayer` for CLI input
- `AIPlayer` placeholder or stub for future rules

This makes it easy to support four local human players later without rewriting the engine.

### Step 4: Build the CLI input layer

Create the command-line interface in `src/mahjong/ui/cli.py`.

Responsibilities:
- print each player’s hand in a readable way
- show whose turn it is
- show the discard pile or most recent discard
- read input from terminal
- validate commands and map them to game actions

#### User interaction model
The CLI should allow each player to respond like this:
- show hand
- discard tile by index or tile identifier
- optionally draw/keep/declare actions if supported

Example commands:
- `hand`
- `discard 3`
- `meld`
- `pass`
- `help`

This is where the “everyone enters inputs into the command line” experience is implemented.

### Step 5: Add hand evaluation and win checking

Once the turn loop and player model work, add logic to detect if a player has completed a valid hand.

At this stage, you may not need full scoring yet. You just need a placeholder validation layer.

Functions could include:
- `is_complete_hand(player)`
- `evaluate_hand(player)`
- `is_valid_meld_set(melds)`

This can be simple but structured so it can evolve into full riichi or Hong Kong rules.

### Step 6: Add rule modules

Once the core match works, implement specific rule frameworks:
- `rules/base.py`
- `rules/riichi.py`
- `rules/hongkong.py`

These modules should define:
- valid win conditions
- scoring rules
- tile counting / special cases
- exceptions and edge cases

This is where you define whether the game is standard riichi, Hong Kong style, or a custom simplified version.

### Step 7: Add rendering and output formatting

After the engine is stable, polish the terminal experience.

Files:
- `src/mahjong/ui/render.py`
- `src/mahjong/ui/theme.py`

These can manage:
- board coloring or symbol formatting
- grouped tile display
- turn banners
- status messages
- clear terminal views

Keep them separate from game logic.

### Step 8: Add scoring and end-of-round logic

After all the game flow works, add:
- hand valuation
- winner declaration
- score tracking
- round summary
- next round logic

This is not needed in the first bare-bones playable prototype, but it is essential for a complete game.

### Step 9: Add testing and validation

Before calling it complete, test:
- dealing works correctly
- players receive proper tiles
- turn order advances
- discards are tracked
- invalid commands are rejected
- win detection catches complete hands
- game ends properly

### Step 10: Build a backend game-state interface

Create a backend-facing version of the game engine that exposes what is
happening without relying on terminal formatting or Unicode glyphs. This
interface will support future machine-learning players and automated
simulations.

The backend should provide:
- a complete, serializable snapshot of the current game state
- each tile represented by stable human-readable names, such as `1 bamboo`,
  `East wind`, `Zhong`, `Fa`, and `Blank`
- each player's hand, melds, discards, seat, and turn status
- the remaining wall count and, where appropriate, the visible wall state
- an ordered event or action history for draws, discards, melds, wins, and turns
- validated actions that can be issued by either a human player or an ML agent
- a clear separation between hidden information, such as another player's hand,
  and public information, such as discards

Keep this backend independent from the CLI renderer. The CLI should consume the
same game-state and action APIs that an ML player will use, so display changes
do not alter the rules or the data available to agents.

## 3. First workable milestone

The very first milestone should not try to be complete mahjong. It should be the following:

- 4 players are created
- a shuffled wall exists
- each player receives 13 tiles
- turn order works
- current player can discard a tile by entering a terminal command
- discard is recorded and next player receives the turn
- a basic winner check exists

This is the minimum useful “working” command-line version.

## 4. Recommended implementation order by file

This is the suggested order of work.

### Phase 1: Core data model
- `src/mahjong/core/tiles.py`
- `src/mahjong/core/hands.py`
- `src/mahjong/core/melds.py`
- `src/mahjong/core/wall.py`
- `src/mahjong/core/game.py`

### Phase 2: Players
- `src/mahjong/players/base.py`
- `src/mahjong/players/human.py`
- `src/mahjong/players/ai.py`

### Phase 3: CLI UI
- `src/mahjong/ui/cli.py`
- `src/mahjong/ui/render.py`
- `src/mahjong/ui/theme.py`

### Phase 4: Rules and scoring
- `src/mahjong/rules/base.py`
- `src/mahjong/rules/riichi.py`
- `src/mahjong/rules/hongkong.py`
- `src/mahjong/rules/score/`

## 5. Key design decisions early on

These are the most important choices to lock down before building too much.

### 5.1 Should the game be rule-accurate or simplified?
For the first iteration, use a simplified but structured version.

Recommended approach:
- valid tile system
- turn flow
- discard logic
- winner detection placeholder
- no advanced scoring until later

This prevents you from getting stuck on rule edge cases too early.

### 5.2 How will players input commands?
For a CLI-first game, use text commands and index-based tile selection.

Examples:
- `discard 2`
- `show hand`
- `meld 1 2 3`
- `pass`

Keep commands simple and parse-driven.

### 5.3 How do you represent tiles?
Use a compact tile model with:
- suit
- rank
- identifier or code

Example:
- `B1`, `B9`
- `D2`, `D4`
- `C5`
- `WIND_EAST`
- `DRAGON_RED`

This makes the system readable in both logic and CLI output.

## 6. Suggested minimal starter object model

A simple but effective version:

- `Tile`  
  A single mahjong tile with suit and rank.

- `Wall`  
  Randomized deck of tiles.

- `Player`  
  A participant with a hand and seat position.

- `Hand`  
  A collection of tiles and helper methods for sorting and grouping.

- `Meld`  
  A completed set like a triplet, sequence, or quartet.

- `Game`  
  Maintains state: wall, players, turn order, winner, active player.

This is enough to implement a first working turn-based CLI game.

## 7. Suggested implementation milestone checklist

### Milestone 1: Skeleton app runs
- `__main__.py` starts the app
- no crash on startup
- shows a title and prompts

### Milestone 2: 4 players + wall
- create 4 player objects
- create and shuffle wall
- deal initial tiles
- display state for each player

### Milestone 3: Turn loop works
- player 1 draws
- player 1 discards
- turn advances to player 2
- repeat for all players

### Milestone 4: Human input works
- current player enters commands in terminal
- inputs are parsed and validated
- invalid input is rejected without crashing

### Milestone 5: Win detection exists
- complete hand can be detected
- winner is declared
- game ends cleanly

### Milestone 6: Rule modules added
- riichi or Hong Kong logic integrated
- scoring system begins to function

### Milestone 7: UI polish
- clean terminal formatting
- better state output
- clearer prompts and turn summaries

### Milestone 8: ML-ready backend
- define stable human-readable names for every tile
- add serializable game-state snapshots
- record ordered game events and legal actions
- separate public observations from private player information
- allow an automated player to advance the game without terminal input
- add deterministic seeding or replay support for training and debugging

## 8. Common mistakes to avoid

- Building the UI before the engine: this leads to fake gameplay and messy logic.
- Making the rules too complex too early: you will sink time into edge cases before the game loop works.
- Having the CLI directly mutate internal game state without validation: business logic should be centralized.
- Trying to implement a full scoring engine before a playable turn loop exists.

## 9. Recommended first coding move

The first code to write should be in this order:

1. `src/mahjong/core/tiles.py`
2. `src/mahjong/core/wall.py`
3. `src/mahjong/core/hands.py`
4. `src/mahjong/players/base.py`
5. `src/mahjong/core/game.py`
6. `src/mahjong/ui/cli.py`
7. `src/mahjong/__main__.py`

This creates the exact structure needed for a working CLI app without overbuilding the rest first.

## 10. Final recommendation

For this first project version, aim for a clean, simple, fully terminal-driven mahjong engine with:
- 4 players
- local input from CLI
- a consistent turn loop
- tile and discard state tracking
- basic win detection

Do not chase perfect rules or polished visuals in the first build. The real objective is a stable engine and a functional command-line loop.

Once that is complete, the project can be expanded naturally into a more advanced rules-based and scoring-driven mahjong system.

## 11. Suggested next action

The next step is to implement the foundational classes in this exact order:
- `Tile`
- `Wall`
- `Player`
- `Game`
- terminal turn loop

After that, you can plug in the CLI display and validation logic.

## 12. Current simplified rules overview

The current version is a simplified four-player Mahjong round. It is intended
to establish the game flow before adding a complete ruleset or scoring system.

### Setup

- Four players are seated at the table.
- The wall contains 136 tiles: three numbered suits, four winds, and three
  dragons, with four copies of each tile.
- Each player receives 13 tiles.
- The dealer is the first player to draw.

### Normal turn

1. The active player draws one tile from the wall.
2. The player may declare a win if the hand is complete.
3. If the player does not win, they discard one tile.
4. The discard is added to that player's discard pile.
5. Play passes to the next player in seat order.

The round ends when a player wins, the wall is exhausted, or a player exits
the CLI. A drawn hand occurs when the wall is exhausted without a winner.

### Chi (吃)

Chi is a meld made from three consecutive numbered tiles of the same suit,
such as 3-4-5 bamboo. A player may claim the most recent discard for chi only
when:

- the discard completes a consecutive three-tile sequence;
- the player is the next player in turn order; and
- the tiles are all from a numbered suit, not winds or dragons.

The player reveals the sequence, places it in their melds, then discards one
tile. The CLI prompts the next player when a valid chi is available and displays the
claimed sequence as an exposed meld.

### Peng (碰)

Peng is a meld made from three identical tiles. A player may claim the most
recent discard for peng when they hold two matching copies. The player reveals
the triplet, places it in their melds, then discards one tile. Unlike chi, peng
can be claimed by any player, subject to resolving competing claims according
to the rules implementation.

The CLI prompts eligible players for peng before offering chi. Exposed peng
and four-tile peng sets are shown above the player's concealed hand.

### Winning and scoring

The current engine checks for a basic four-meld-and-a-pair structure using the
concealed tiles and any recorded three-tile melds. It does not calculate
points, apply yaku or fan, or select a specific Riichi or Hong Kong scoring
system. Those rules belong in the later rule-module and scoring phases.
