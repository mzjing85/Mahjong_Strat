from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from functools import lru_cache
from typing import List, Optional

from ..players.base import Player
from ..rules.base import BaseRules
from .wall import Wall


@dataclass
class Game:
    players: List[Player] = field(default_factory=list)
    wall: Wall = field(default_factory=Wall)
    current_player_index: int = 0
    dealer_index: int = 0
    winner: Optional[Player] = None
    round_number: int = 1
    rules: BaseRules = field(default_factory=BaseRules)

    def __post_init__(self) -> None:
        if not self.players:
            self.players = [
                Player(player_name=f"Player {index + 1}", seat_number=index + 1)
                for index in range(4)
            ]
        self.wall.shuffle()

    def deal_initial_hands(self, tiles_per_player: int = 13) -> None:
        for _ in range(tiles_per_player):
            for player in self.players:
                player.draw_tile(self.wall.draw())

        for player in self.players:
            player.sort_hand()

    def next_turn(self) -> None:
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def current_player(self) -> Player:
        return self.players[self.current_player_index]

    def set_current_player(self, seat_number: int) -> None:
        for index, player in enumerate(self.players):
            if player.seat_number == seat_number:
                self.current_player_index = index
                return
        raise ValueError(f"Seat number {seat_number} does not exist in the game")

    def check_complete_hand(self, player: Player) -> bool:
        exposed_tile_count = sum(
            self.rules.meld_tile_count(meld) for meld in player.melds
        )
        if len(player.hand) + exposed_tile_count != 14:
            return False

        tile_counts = Counter(
            (tile.suit.value, tile.rank) for tile in player.hand
        )
        return self._can_form_complete_hand(tuple(sorted(tile_counts.items())))

    @staticmethod
    @lru_cache(maxsize=None)
    def _can_form_complete_hand(
        counted_tiles: tuple[tuple[tuple[str, int], int], ...],
    ) -> bool:
        counts = dict(counted_tiles)
        if not counts:
            return True

        for pair_tile, pair_count in counts.items():
            if pair_count >= 2:
                remaining = counts.copy()
                remaining[pair_tile] -= 2
                if remaining[pair_tile] == 0:
                    del remaining[pair_tile]
                if Game._can_form_melds(tuple(sorted(remaining.items()))):
                    return True

        return False

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
            if Game._can_form_melds(tuple(sorted(remaining.items()))):
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
            if Game._can_form_melds(tuple(sorted(remaining.items()))):
                return True

        return False

    def declare_winner(self, player: Player) -> None:
        self.winner = player

    def start_turn(self) -> Optional[Player]:
        if self.winner is not None:
            return self.winner

        player = self.current_player()
        player.draw_tile(self.wall.draw())
        player.sort_hand()

        if self.check_complete_hand(player):
            self.declare_winner(player)
            return player

        return None

    def run_turn(self) -> Optional[Player]:
        winner = self.start_turn()
        if winner is None:
            self.next_turn()
        return winner

    def __str__(self) -> str:
        return (
            f"Game(round={self.round_number}, dealer={self.dealer_index + 1}, "
            f"current_turn={self.current_player_index + 1}, winner={self.winner.player_name if self.winner else 'None'})"
        )
