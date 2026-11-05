from __future__ import annotations

from typing import List, Tuple

from ..core.tiles import Tile


def render_discard_history(discard_history: List[Tuple[str, Tile]]) -> str:
    lines = ["Discard history:"]
    if not discard_history:
        lines.append("  (none)")
    else:
        for discard_number, (player_name, tile) in enumerate(discard_history, start=1):
            lines.append(
                f"  {discard_number:>2}. {player_name:<10} "
                f"{tile.unicode_symbol} {tile.code:<3} {tile.name}"
            )
    return "\n".join(lines)


def render_player_discards(players: List[object]) -> str:
    lines = ["Discards by player:"]
    has_discards = False
    for player in players:
        if player.discarded_tiles:
            has_discards = True
            tiles = "  ".join(
                f"{tile.unicode_symbol} {tile.code}" for tile in player.discarded_tiles
            )
            lines.append(f"  {player.player_name:<10} {tiles}")
    if not has_discards:
        lines.append("  (none)")
    return "\n".join(lines)
