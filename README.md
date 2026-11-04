# Mahjong Strat

A terminal-based Mahjong game built in Python. The current version provides a
simple four-player local CLI with Unicode tile displays and chronological
discard tracking.

## Current features

- Four local players with turn order
- Shuffled 136-tile wall
- Characters, bamboo, dots, winds, and three dragons:
  - Zhong (red)
  - Fa (green)
  - Blank (white)
- No flower tiles
- Initial 13-tile hands
- Indexed discard commands
- Ongoing discard history
- UTF-8 output configuration for Windows terminals

## Requirements

- Python 3.12 or newer
- A terminal with a font that supports Mahjong Unicode glyphs

## Run the CLI

From the repository root, set the `src` directory on Python's import path:

```powershell
$env:PYTHONPATH = "$PWD\src"
python -m mahjong
```

In the game, use:

- `hand` or `show hand` to display the current hand
- `discard <index>` to discard a tile by its displayed index
- `quit` or `exit` to leave the game

## Project structure

```text
src/mahjong/
├── core/       Game state, tiles, hands, and wall
├── players/   Human and AI player abstractions
├── rules/     Rule and scoring modules
└── ui/        CLI input and terminal rendering
```

See [`build.md`](./build.md) for the implementation plan and future milestones.

## Planned ML backend

The next major extension is a backend game-state interface for automated and
machine-learning players. It will expose serializable state, stable
human-readable tile names, legal actions, ordered game events, and separate
public and private observations without requiring an ML player to parse terminal
output.
