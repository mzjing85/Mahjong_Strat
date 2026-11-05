from __future__ import annotations

from typing import List, Optional, Tuple

from ..core.game import Game
from ..core.tiles import Tile
from ..players.base import Player
from ..rules.base import BaseRules
from .render import render_discard_history, render_player_discards


TILE_COLUMN_WIDTH = 5


def format_tile(tile: Tile) -> str:
    return f"{tile.unicode_symbol} {tile.code} ({tile.name})"


def display_help() -> None:
    print(
        "\nCommands:\n"
        "  hand                 Show your concealed hand\n"
        "  discard <index>      Discard a tile by index\n"
        "  exposed              Show exposed melds\n"
        "  table                Show table status and discards\n"
        "  history              Show chronological discard history\n"
        "  help                 Show these commands\n"
        "  quit                 Leave the game\n"
    )


def display_player_hand(player: Player) -> None:
    print(f"{player.player_name} hand:")
    if not player.hand.tiles:
        print("(empty)")
        return

    indices = " ".join(
        f"[{index}]".center(TILE_COLUMN_WIDTH)
        for index in range(len(player.hand.tiles))
    )
    tiles = " ".join(
        tile.unicode_symbol.center(TILE_COLUMN_WIDTH)
        for tile in player.hand.tiles
    )
    print(indices)
    print(tiles)


def display_exposed_melds(player: Player) -> None:
    print("Exposed melds:")
    if not player.exposed_melds:
        print("  (none)")
        return
    for meld in player.exposed_melds:
        print("  " + " ".join(tile.unicode_symbol for tile in meld))


def display_all_exposed_melds(game: Game) -> None:
    print("Exposed melds:")
    any_exposed_melds = False
    for player in game.players:
        if not player.exposed_melds:
            continue
        any_exposed_melds = True
        meld_text = " | ".join(
            " ".join(f"{tile.unicode_symbol} {tile.code}" for tile in meld)
            for meld in player.exposed_melds
        )
        print(f"  {player.player_name:<10} {meld_text}")
    if not any_exposed_melds:
        print("  (none)")


def handle_player_turn(game: Game, player: Player, discard_history: List[Tuple[str, Tile]]) -> Tile:
    print("\n" + "=" * 80)
    print("TABLE")
    print(f"  Round: {game.round_number:<5} Wall remaining: {len(game.wall):<4} "
          f"Current player: {player.player_name} (Seat {player.seat_number})")
    print(render_player_discards(game.players))
    display_all_exposed_melds(game)
    print(f"\nPLAYER: {player.player_name}")
    display_exposed_melds(player)
    display_player_hand(player)

    while True:
        command = input("\nCommand (help for options): ").strip()

        if command.lower() in {"hand", "show hand"}:
            display_player_hand(player)
            continue

        if command.lower() in {"help", "?"}:
            display_help()
            continue

        if command.lower() == "exposed":
            display_exposed_melds(player)
            continue

        if command.lower() == "table":
            print(render_player_discards(game.players))
            display_all_exposed_melds(game)
            continue

        if command.lower() == "history":
            print(render_discard_history(discard_history))
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

            print(f"{player.player_name} discarded {format_tile(discarded_tile)}")
            discard_history.append((player.player_name, discarded_tile))
            print(render_player_discards(game.players))
            return discarded_tile

        print("Unknown command.")


def player_order_after(game: Game, player: Player) -> List[Player]:
    player_index = game.players.index(player)
    return [
        game.players[(player_index + offset) % len(game.players)]
        for offset in range(1, len(game.players))
    ]


def player_can_win_on_discard(game: Game, player: Player, discarded_tile: Tile) -> bool:
    return game.rules.can_win_on_discard(player, discarded_tile)


def prompt_for_claim(
    player: Player,
    claim_type: str,
    options: Optional[List[Tuple[Tile, Tile, Tile]]] = None,
) -> bool:
    print(f"\n{player.player_name} can claim {claim_type}.")
    if options:
        for index, option in enumerate(options, start=1):
            print(f"  {index}. " + "  ".join(format_tile(tile) for tile in option))
        answer = input("Choose an option number, or press Enter to pass: ").strip()
        return bool(answer)
    answer = input("Claim it? [y/N]: ").strip().lower()
    return answer in {"y", "yes"}


def resolve_discard_claim(
    game: Game,
    discarder: Player,
    discarded_tile: Tile,
) -> Optional[Player]:
    ordered_players = player_order_after(game, discarder)
    rules: BaseRules = game.rules

    def remove_claimed_discard() -> None:
        if discarded_tile in discarder.discarded_tiles:
            discarder.discarded_tiles.remove(discarded_tile)

    for player in ordered_players:
        if player_can_win_on_discard(game, player, discarded_tile):
            if prompt_for_claim(player, "win"):
                remove_claimed_discard()
                player.draw_tile(discarded_tile)
                game.declare_winner(player)
                return player

    peng_candidates = [
        player for player in ordered_players
        if rules.can_peng(player, discarded_tile)
    ]
    if not rules.config.closestPengWins:
        peng_candidates = [
            player for player in game.players
            if player is not discarder and player in peng_candidates
        ]

    for player in peng_candidates:
        can_four_tile_peng = rules.can_four_tile_peng(player, discarded_tile)
        claim_type = "peng or four-tile peng" if can_four_tile_peng else "peng"
        if not prompt_for_claim(player, claim_type):
            continue
        four_tile = can_four_tile_peng and input(
            "Use four-tile peng? [y/N] "
        ).strip().lower() == "y"
        rules.claim_peng(player, discarded_tile, four_tile=four_tile)
        remove_claimed_discard()
        if four_tile and rules.config.fourTilePengGrantsExtraDraw:
            player.draw_tile(game.wall.draw())
            player.sort_hand()
            print(f"{player.player_name} received an extra draw.")
            if game.check_complete_hand(player):
                game.declare_winner(player)
                return player
        print(f"{player.player_name} exposed {claim_type}.")
        return player

    next_player = ordered_players[0]
    chi_options = rules.chi_options(next_player, discarded_tile)
    if chi_options:
        print(f"\n{next_player.player_name} can claim chi:")
        for index, option in enumerate(chi_options, start=1):
            print(f"  {index}. " + "  ".join(format_tile(tile) for tile in option))
        choice = input("Choose an option number, or press Enter to pass: ").strip()
        if choice:
            try:
                selected_option = chi_options[int(choice) - 1]
                rules.claim_chi(next_player, discarded_tile, selected_option)
                remove_claimed_discard()
                print(f"{next_player.player_name} exposed chi.")
                return next_player
            except (IndexError, ValueError):
                print("Invalid chi option; the discard was not claimed.")

    return None


def run_cli_game() -> None:
    game = Game()
    game.deal_initial_hands()
    print("Welcome to Mahjong CLI")
    print("Four players are seated and the wall has been shuffled.")
    print("Each player will draw and then choose a tile to discard.")
    discard_history: List[Tuple[str, Tile]] = []

    while game.winner is None:
        current_player = game.current_player()
        try:
            winner = game.start_turn()
        except ValueError as exc:
            print(f"\nRound ended: {exc}")
            break

        if winner is not None:
            print(f"\n{winner.player_name} wins!")
            break

        discarded_tile = handle_player_turn(game, current_player, discard_history)
        claimant = resolve_discard_claim(game, current_player, discarded_tile)
        if claimant is not None:
            if game.winner is not None:
                print(f"\n{claimant.player_name} wins!")
                break
            current_player = claimant
            handle_player_turn(game, current_player, discard_history)
            game.set_current_player(current_player.seat_number)
        game.next_turn()

    if game.winner is None and not game.wall:
        print("No tiles remain in the wall. The round is a draw.")
