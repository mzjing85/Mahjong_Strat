from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .tiles import Tile


@dataclass
class Hand:
    tiles: List[Tile] = field(default_factory=list)

    def add_tile(self, tile: Tile) -> None:
        self.tiles.append(tile)

    def remove_tile(self, tile: Tile) -> None:
        if tile not in self.tiles:
            raise ValueError(f"Tile {tile.code} not found in hand")
        self.tiles.remove(tile)

    def sort(self) -> None:
        self.tiles = sorted(self.tiles, key=lambda tile: (tile.suit.value, tile.rank))

    def __iter__(self):
        return iter(self.tiles)

    def __len__(self) -> int:
        return len(self.tiles)

    def __str__(self) -> str:
        return " ".join(tile.unicode_symbol for tile in self.tiles)
