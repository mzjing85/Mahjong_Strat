from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Suit(str, Enum):
    BAMBOO = "bamboo"
    CHARACTER = "character"
    DOT = "dot"
    WIND = "wind"
    DRAGON = "dragon"


@dataclass(frozen=True, order=True)
class Tile:
    suit: Suit
    rank: int
    name: Optional[str] = None

    def __post_init__(self) -> None:
        if self.suit == Suit.WIND:
            if self.rank not in range(1, 5):
                raise ValueError(f"Invalid rank for {self.suit.value}: {self.rank}")
        elif self.suit == Suit.DRAGON:
            if self.rank not in range(1, 4):
                raise ValueError(f"Invalid rank for {self.suit.value}: {self.rank}")
        elif self.rank not in range(1, 10):
            raise ValueError(f"Invalid rank for {self.suit.value}: {self.rank}")

        if self.name is None:
            object.__setattr__(self, "name", self._default_name())

    def _default_name(self) -> str:
        if self.suit == Suit.WIND:
            wind_names = {1: "East", 2: "South", 3: "West", 4: "North"}
            return f"Wind {wind_names.get(self.rank, self.rank)}"
        if self.suit == Suit.DRAGON:
            dragon_names = {1: "Zhong", 2: "Fa", 3: "Blank"}
            return dragon_names[self.rank]
        return f"{self.suit.value.title()} {self.rank}"

    def __str__(self) -> str:
        return self.unicode_symbol

    @property
    def unicode_symbol(self) -> str:
        code_point_by_suit = {
            Suit.WIND: (0x1F000, 4),
            Suit.DRAGON: (0x1F004, 3),
            Suit.CHARACTER: (0x1F010, 9),
            Suit.BAMBOO: (0x1F020, 9),
            Suit.DOT: (0x1F030, 9),
        }
        code_point_start, tile_count = code_point_by_suit[self.suit]
        if self.rank > tile_count:
            raise ValueError(f"Invalid rank for {self.suit.value}: {self.rank}")
        return chr(code_point_start + self.rank - 1)

    @property
    def code(self) -> str:
        prefix = {
            Suit.BAMBOO: "B",
            Suit.CHARACTER: "C",
            Suit.DOT: "D",
            Suit.WIND: "W",
            Suit.DRAGON: "R",
        }[self.suit]
        return f"{prefix}{self.rank}"
