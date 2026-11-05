from __future__ import annotations

from dataclasses import dataclass, field
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
    initial_discard_pending: bool = False

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

        self.current_player_index = self.dealer_index
        self.players[self.dealer_index].draw_tile(self.wall.draw())

        for player in self.players:
            player.sort_hand()
        self.initial_discard_pending = True

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
        return self.rules.is_complete_hand(player)

    def declare_winner(self, player: Player) -> None:
        self.winner = player

    def start_turn(self) -> Optional[Player]:
        if self.winner is not None:
            return self.winner

        player = self.current_player()
        if self.initial_discard_pending:
            self.initial_discard_pending = False
        else:
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
