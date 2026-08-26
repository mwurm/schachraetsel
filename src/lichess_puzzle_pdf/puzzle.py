from __future__ import annotations

from dataclasses import dataclass

import chess

from .config import Difficulty, PuzzleType


@dataclass(frozen=True)
class ReconstructedPuzzle:
    board: chess.Board
    starting_fen: str
    solution_moves: tuple[chess.Move, ...]
    solution_san: tuple[str, ...]


@dataclass(frozen=True)
class Puzzle:
    puzzle_id: str
    starting_fen: str
    solution_moves: tuple[chess.Move, ...]
    solution_san: tuple[str, ...]
    rating: int
    rating_deviation: int
    popularity: int
    nb_plays: int
    primary_type: PuzzleType
    themes: frozenset[str]
    difficulty: Difficulty | None
    game_url: str | None
    opening_tags: tuple[str, ...]

    @property
    def side_to_move_de(self) -> str:
        return "Weiß" if chess.Board(self.starting_fen).turn == chess.WHITE else "Schwarz"
