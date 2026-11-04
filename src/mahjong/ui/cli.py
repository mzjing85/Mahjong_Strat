from __future__ import annotations

from typing import List, Tuple

from ..core.game import Game
from ..core.tiles import Tile
from ..players.base import Player
from .render import render_discard_history


def display_player_hand(player: Player) -> None:
    print(f"{player.player_name} hand:")
    if not player.hand.tiles:
        print("  (empty)")
        return

    for index, tile in enumerate(player.hand.tiles):
        print(f"  [{index}] {tile.unicode_symbol}")


def handle_player_turn(game: Game, player: Player, discard_history: List[Tuple[str, Tile]]) -> None:
    print("\n" + "=" * 50)
    print(render_discard_history(discard_history))
    print(f"{player.player_name} to act (Seat {player.seat_number})")
    print(f"Current game state: {game}")
    print(f"Wall tiles remaining: {len(game.wall)}")
    display_player_hand(player)

    while True:
        command = input("Enter command ('hand', 'discard <index>', or 'quit'): ").strip()

        if command.lower() in {"hand", "show hand"}:
            display_player_hand(player)
            continue

        if command.lower() in {"quit", "exit"}:
            raise SystemExit(0)

        if command.lower().startswith("discard "):
            try:
                tile_index = int(command.split()[1])
            except (IndexError, ValueError):
                print("Invalid discard format. Use: discard <index>")
                continue

            try:
                discarded_tile = player.discard_tile_by_index(tile_index)
            except ValueError as exc:
                print(f"Error: {exc}")
                continue

            print(f"{player.player_name} discarded {discarded_tile.unicode_symbol}")
            discard_history.append((player.player_name, discarded_tile))
            print(render_discard_history(discard_history))
            return

        print("Unknown command.")


def run_cli_game() -> None:
    game = Game()
    game.deal_initial_hands()
    print("Welcome to Mahjong CLI")
    print("Four players are seated and the wall has been shuffled.")
    print("Each player will take turns choosing a tile to discard.")
    discard_history: List[Tuple[str, Tile]] = []

    for _ in range(4):
        current_player = game.current_player()
        handle_player_turn(game, current_player, discard_history)
        game.next_turn()

    print("\nInitial turn cycle complete.")
    print("Step 1 is complete: 4 players, turn order, and CLI input are working.")
