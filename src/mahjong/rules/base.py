from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Tuple

from ..core.tiles import Suit, Tile
from ..players.base import Player


@dataclass(frozen=True)
class RulesConfig:
    fourTilePengGrantsExtraDraw: bool = False
    fourTilePengCountsAsSingleSet: bool = True
    closestPengWins: bool = True


class BaseRules:
    def __init__(self, config: RulesConfig | None = None) -> None:
        self.config = config or RulesConfig()

    def chi_options(self, player: Player, discarded_tile: Tile) -> List[Tuple[Tile, Tile, Tile]]:
        if discarded_tile.suit not in {Suit.BAMBOO, Suit.CHARACTER, Suit.DOT}:
            return []

        options: List[Tuple[Tile, Tile, Tile]] = []
        for start_rank in range(max(1, discarded_tile.rank - 2), min(7, discarded_tile.rank) + 1):
            sequence = tuple(
                Tile(discarded_tile.suit, start_rank + offset)
                for offset in range(3)
            )
            if discarded_tile not in sequence:
                continue
            required_tiles = list(sequence)
            required_tiles.remove(discarded_tile)
            if all(player.has_tile(tile) for tile in required_tiles):
                options.append(sequence)
        return options

    def can_peng(self, player: Player, discarded_tile: Tile) -> bool:
        return sum(tile == discarded_tile for tile in player.hand) >= 2

    def can_four_tile_peng(self, player: Player, discarded_tile: Tile) -> bool:
        return sum(tile == discarded_tile for tile in player.hand) >= 3

    def claim_chi(
        self,
        player: Player,
        discarded_tile: Tile,
        sequence: Sequence[Tile],
    ) -> List[Tile]:
        if tuple(sequence) not in self.chi_options(player, discarded_tile):
            raise ValueError("The selected tiles do not form a valid chi")
        exposed_tiles = list(sequence)
        for tile in exposed_tiles:
            if tile != discarded_tile:
                player.hand.remove_tile(tile)
        player.melds.append(exposed_tiles)
        return exposed_tiles

    def claim_peng(
        self,
        player: Player,
        discarded_tile: Tile,
        four_tile: bool = False,
    ) -> List[Tile]:
        required_count = 3 if four_tile else 2
        if sum(tile == discarded_tile for tile in player.hand) < required_count:
            raise ValueError("The player does not have enough matching tiles")
        for _ in range(required_count):
            player.hand.remove_tile(discarded_tile)
        exposed_tiles = [discarded_tile] * (required_count + 1)
        player.melds.append(exposed_tiles)
        return exposed_tiles

    def meld_tile_count(self, meld: Sequence[Tile]) -> int:
        if len(meld) == 4 and self.config.fourTilePengCountsAsSingleSet:
            return 3
        return len(meld)