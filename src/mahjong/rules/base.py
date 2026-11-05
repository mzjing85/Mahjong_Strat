from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from typing import List, Sequence, Tuple

from ..core.tiles import Suit, Tile
from ..players.base import Player


@dataclass(frozen=True)
class RulesConfig:
    fourTilePengGrantsExtraDraw: bool = True
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

    def is_complete_hand(
        self,
        player: Player,
        additional_tile: Tile | None = None,
    ) -> bool:
        concealed_tiles = list(player.hand.tiles)
        if additional_tile is not None:
            concealed_tiles.append(additional_tile)

        exposed_tile_count = sum(
            self.meld_tile_count(meld) for meld in player.melds
        )
        if len(concealed_tiles) + exposed_tile_count != 14:
            return False

        tile_counts = Counter(
            (tile.suit.value, tile.rank) for tile in concealed_tiles
        )
        return self._can_form_complete_hand(tuple(sorted(tile_counts.items())))

    def can_win_on_discard(self, player: Player, discarded_tile: Tile) -> bool:
        return self.is_complete_hand(player, additional_tile=discarded_tile)

    @staticmethod
    @lru_cache(maxsize=None)
    def _can_form_complete_hand(
        counted_tiles: tuple[tuple[tuple[str, int], int], ...],
    ) -> bool:
        counts = dict(counted_tiles)
        for pair_tile, pair_count in counts.items():
            if pair_count < 2:
                continue
            remaining = counts.copy()
            remaining[pair_tile] -= 2
            if remaining[pair_tile] == 0:
                del remaining[pair_tile]
            if BaseRules._can_form_melds(tuple(sorted(remaining.items()))):
                return True
        return not counts

    @staticmethod
    @lru_cache(maxsize=None)
    def _can_form_melds(
        counted_tiles: tuple[tuple[tuple[str, int], int], ...],
    ) -> bool:
        counts = dict(counted_tiles)
        if not counts:
            return True

        first_tile = min(counts)
        suit, rank = first_tile
        if counts[first_tile] >= 3:
            remaining = counts.copy()
            remaining[first_tile] -= 3
            if remaining[first_tile] == 0:
                del remaining[first_tile]
            if BaseRules._can_form_melds(tuple(sorted(remaining.items()))):
                return True

        sequence_tiles = ((suit, rank), (suit, rank + 1), (suit, rank + 2))
        if suit in {"bamboo", "character", "dot"} and rank <= 7 and all(
            counts.get(tile, 0) > 0 for tile in sequence_tiles
        ):
            remaining = counts.copy()
            for tile in sequence_tiles:
                remaining[tile] -= 1
                if remaining[tile] == 0:
                    del remaining[tile]
            if BaseRules._can_form_melds(tuple(sorted(remaining.items()))):
                return True

        return False