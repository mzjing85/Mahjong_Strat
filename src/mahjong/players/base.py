from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from ..core.hands import Hand
from ..core.tiles import Tile


@dataclass
class Player:
    player_name: str
    seat_number: int
    hand: Hand = field(default_factory=Hand)
    discarded_tiles: List[Tile] = field(default_factory=list)
    melds: List[List[Tile]] = field(default_factory=list)

    def draw_tile(self, tile: Tile) -> None:
        self.hand.add_tile(tile)

    def discard_tile_by_index(self, tile_index: int) -> Tile:
        if tile_index < 0 or tile_index >= len(self.hand.tiles):
            raise ValueError(f"Invalid tile index: {tile_index}")

        tile = self.hand.tiles.pop(tile_index)
        self.discarded_tiles.append(tile)
        return tile

    def discard_tile(self, tile: Tile) -> Tile:
        if tile not in self.hand.tiles:
            raise ValueError(f"Tile {tile.code} is not in {self.player_name}'s hand")

        self.hand.tiles.remove(tile)
        self.discarded_tiles.append(tile)
        return tile

    def sort_hand(self) -> None:
        self.hand.sort()

    def has_tile(self, tile: Tile) -> bool:
        return any(existing_tile == tile for existing_tile in self.hand.tiles)

    def __str__(self) -> str:
        return f"{self.player_name} (Seat {self.seat_number})"
