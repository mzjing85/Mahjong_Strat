from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List

from .tiles import Suit, Tile


@dataclass
class Wall:
    tiles: List[Tile] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.tiles:
            self.tiles = self._build_standard_wall()

    def _build_standard_wall(self) -> List[Tile]:
        all_tiles: List[Tile] = []

        for suit in (Suit.BAMBOO, Suit.CHARACTER, Suit.DOT):
            for rank in range(1, 10):
                for _ in range(4):
                    all_tiles.append(Tile(suit=suit, rank=rank))

        for suit, rank_count in ((Suit.WIND, 4), (Suit.DRAGON, 3)):
            for rank in range(1, rank_count + 1):
                for _ in range(4):
                    all_tiles.append(Tile(suit=suit, rank=rank))

        return all_tiles

    def shuffle(self) -> None:
        random.shuffle(self.tiles)

    def draw(self) -> Tile:
        if not self.tiles:
            raise ValueError("Cannot draw from an empty wall")
        return self.tiles.pop()

    def remaining_tiles(self) -> int:
        return len(self.tiles)

    def __len__(self) -> int:
        return len(self.tiles)

    def __iter__(self):
        return iter(self.tiles)
