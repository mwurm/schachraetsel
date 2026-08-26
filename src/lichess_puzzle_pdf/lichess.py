from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, TextIO

import chess
import zstandard

from .config import Difficulty, DIFFICULTY_RANGES, PRIMARY_TYPE_PRIORITY, PuzzleType
from .puzzle import Puzzle, ReconstructedPuzzle


PUZZLE_DB_URL = "https://database.lichess.org/lichess_db_puzzle.csv.zst"
DEFAULT_CACHE_DIR = Path.home() / ".cache" / "lichess-puzzle-pdf"
DEFAULT_DB_PATH = DEFAULT_CACHE_DIR / "lichess_db_puzzle.csv.zst"


@dataclass(frozen=True)
class LichessPuzzleRow:
    puzzle_id: str
    fen: str
    moves: tuple[str, ...]
    rating: int
    rating_deviation: int
    popularity: int
    nb_plays: int
    themes: frozenset[str]
    game_url: str | None
    opening_tags: tuple[str, ...]


def split_words(value: str | None) -> tuple[str, ...]:
    if not value:
        return ()
    return tuple(part for part in value.split() if part)


def parse_row(row: dict[str, str]) -> LichessPuzzleRow:
    return LichessPuzzleRow(
        puzzle_id=row["PuzzleId"],
        fen=row["FEN"],
        moves=split_words(row["Moves"]),
        rating=int(row["Rating"]),
        rating_deviation=int(row["RatingDeviation"]),
        popularity=int(row["Popularity"]),
        nb_plays=int(row["NbPlays"]),
        themes=frozenset(split_words(row.get("Themes"))),
        game_url=row.get("GameUrl") or None,
        opening_tags=split_words(row.get("OpeningTags")),
    )


def _iter_text_from_zst(path: Path) -> TextIO:
    compressed = path.open("rb")
    reader = zstandard.ZstdDecompressor().stream_reader(compressed)
    return TextIOWrapperWithClose(reader, compressed)


class TextIOWrapperWithClose:
    def __init__(self, reader, compressed) -> None:
        import io

        self._reader = reader
        self._compressed = compressed
        self._text = io.TextIOWrapper(reader, encoding="utf-8", newline="")

    def __enter__(self):
        return self._text

    def __exit__(self, exc_type, exc, tb) -> None:
        self._text.close()
        self._reader.close()
        self._compressed.close()


def stream_rows(path: Path) -> Iterator[LichessPuzzleRow]:
    with _iter_text_from_zst(path) as text:
        for row in csv.DictReader(text):
            yield parse_row(row)


def reconstruct_puzzle(fen: str, moves: list[str] | tuple[str, ...]) -> ReconstructedPuzzle:
    if not moves:
        raise ValueError("Lichess-Puzzle enthält keine Moves")
    board = chess.Board(fen)
    first = chess.Move.from_uci(moves[0])
    if first not in board.legal_moves:
        raise ValueError(f"Erster Lichess-Zug ist illegal: {moves[0]}")
    board.push(first)
    start = board.copy(stack=False)
    solution_moves: list[chess.Move] = []
    solution_san: list[str] = []
    for move_text in moves[1:]:
        move = chess.Move.from_uci(move_text)
        if move not in board.legal_moves:
            raise ValueError(f"Lösungszug ist illegal: {move_text}")
        solution_san.append(board.san(move))
        board.push(move)
        solution_moves.append(move)
    return ReconstructedPuzzle(
        board=start,
        starting_fen=start.fen(),
        solution_moves=tuple(solution_moves),
        solution_san=tuple(solution_san),
    )


def primary_type_for(themes: frozenset[str]) -> PuzzleType | None:
    for puzzle_type in PRIMARY_TYPE_PRIORITY:
        if puzzle_type.value in themes:
            return puzzle_type
    return None


def difficulty_for_rating(rating: int) -> Difficulty | None:
    for difficulty, rating_range in DIFFICULTY_RANGES.items():
        if rating_range.contains(rating):
            return difficulty
    return None


def count_mate_in_one_moves(board: chess.Board) -> list[chess.Move]:
    mates: list[chess.Move] = []
    for move in board.legal_moves:
        test = board.copy(stack=False)
        test.push(move)
        if test.is_checkmate():
            mates.append(move)
    return mates


def validate_reconstructed(row: LichessPuzzleRow, reconstructed: ReconstructedPuzzle) -> bool:
    if not reconstructed.solution_moves:
        return False
    playback = chess.Board(reconstructed.starting_fen)
    for move in reconstructed.solution_moves:
        if move not in playback.legal_moves:
            return False
        playback.push(move)
    if "mateIn1" in row.themes:
        mates = count_mate_in_one_moves(reconstructed.board)
        return len(mates) == 1 and mates[0] == reconstructed.solution_moves[0]
    if "mateIn2" in row.themes or "mateIn3" in row.themes:
        return playback.is_checkmate()
    return playback.is_valid()


def puzzle_from_row(row: LichessPuzzleRow) -> Puzzle | None:
    primary_type = primary_type_for(row.themes)
    if primary_type is None:
        return None
    try:
        reconstructed = reconstruct_puzzle(row.fen, row.moves)
    except (ValueError, chess.InvalidMoveError):
        return None
    if not reconstructed.board.is_valid():
        return None
    if not validate_reconstructed(row, reconstructed):
        return None
    return Puzzle(
        puzzle_id=row.puzzle_id,
        starting_fen=reconstructed.starting_fen,
        solution_moves=reconstructed.solution_moves,
        solution_san=reconstructed.solution_san,
        rating=row.rating,
        rating_deviation=row.rating_deviation,
        popularity=row.popularity,
        nb_plays=row.nb_plays,
        primary_type=primary_type,
        themes=row.themes,
        difficulty=difficulty_for_rating(row.rating),
        game_url=row.game_url,
        opening_tags=row.opening_tags,
    )
