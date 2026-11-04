from __future__ import annotations

from typing import List, Tuple

from ..core.tiles import Tile


def render_discard_history(discard_history: List[Tuple[str, Tile]]) -> str:
    lines = ["All discards:"]
    if not discard_history:
        lines.append("  (none)")
    else:
        for discard_number, (player_name, tile) in enumerate(discard_history, start=1):
            lines.append(f"  {discard_number}. {player_name}: {tile.unicode_symbol}")
    return "\n".join(lines)
