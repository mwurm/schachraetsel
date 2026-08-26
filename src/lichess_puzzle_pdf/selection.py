from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import random
from pathlib import Path
from typing import Iterable

from .config import Difficulty, PuzzleType
from .lichess import LichessPuzzleRow, difficulty_for_rating, primary_type_for, puzzle_from_row, stream_rows
from .puzzle import Puzzle


@dataclass(frozen=True)
class PuzzleFilter:
    types: frozenset[PuzzleType]
    required_themes: frozenset[str] = frozenset()
    excluded_themes: frozenset[str] = frozenset()
    rating_min: int | None = None
    rating_max: int | None = None
    min_popularity: int | None = None
    min_plays: int | None = None
    difficulty: Difficulty | None = None

    def matches_row(self, row: LichessPuzzleRow) -> bool:
        primary_type = primary_type_for(row.themes)
        if self.types and primary_type not in self.types:
            return False
        if self.required_themes and not self.required_themes.issubset(row.themes):
            return False
        if self.excluded_themes and self.excluded_themes.intersection(row.themes):
            return False
        if self.rating_min is not None and row.rating < self.rating_min:
            return False
        if self.rating_max is not None and row.rating > self.rating_max:
            return False
        if self.min_popularity is not None and row.popularity < self.min_popularity:
            return False
        if self.min_plays is not None and row.nb_plays < self.min_plays:
            return False
        if self.difficulty is not None and difficulty_for_rating(row.rating) != self.difficulty:
            return False
        return True

    def matches(self, puzzle: Puzzle) -> bool:
        if self.types and puzzle.primary_type not in self.types:
            return False
        if self.required_themes and not self.required_themes.issubset(puzzle.themes):
            return False
        if self.excluded_themes and self.excluded_themes.intersection(puzzle.themes):
            return False
        if self.rating_min is not None and puzzle.rating < self.rating_min:
            return False
        if self.rating_max is not None and puzzle.rating > self.rating_max:
            return False
        if self.min_popularity is not None and puzzle.popularity < self.min_popularity:
            return False
        if self.min_plays is not None and puzzle.nb_plays < self.min_plays:
            return False
        if self.difficulty is not None and puzzle.difficulty != self.difficulty:
            return False
        return True


@dataclass(frozen=True)
class SelectionRequest:
    name: str
    count: int
    filter: PuzzleFilter


def reservoir_sample(candidates: Iterable[Puzzle], count: int, rng: random.Random,
                     seen_ids: set[str], seen_fens: set[str]) -> list[Puzzle]:
    reservoir: list[Puzzle] = []
    matched = 0
    for puzzle in candidates:
        if puzzle.puzzle_id in seen_ids or puzzle.starting_fen in seen_fens:
            continue
        matched += 1
        if len(reservoir) < count:
            reservoir.append(puzzle)
        else:
            index = rng.randrange(matched)
            if index < count:
                reservoir[index] = puzzle
    if len(reservoir) < count:
        raise ValueError(f"Nicht genug passende Rätsel gefunden: {len(reservoir)}/{count}")
    for puzzle in reservoir:
        seen_ids.add(puzzle.puzzle_id)
        seen_fens.add(puzzle.starting_fen)
    return reservoir


def select_puzzles(db_path: Path, requests: list[SelectionRequest], seed: int,
                   candidate_limit: int | None = 500) -> list[Puzzle]:
    if not db_path.exists():
        raise FileNotFoundError(f"Lichess-Datenbank nicht gefunden: {db_path}")
    if candidate_limit is not None and candidate_limit <= 0:
        raise ValueError("candidate_limit muss > 0 sein oder None für vollständigen Scan")
    rng = random.Random(seed)
    reservoirs: dict[str, list[Puzzle]] = {request.name: [] for request in requests}
    matched_counts: dict[str, int] = defaultdict(int)
    seen_in_reservoir: dict[str, set[str]] = {request.name: set() for request in requests}
    all_seen_ids: set[str] = set()
    all_seen_fens: set[str] = set()

    def enough_candidates_seen() -> bool:
        if candidate_limit is None:
            return False
        return all(
            len(reservoirs[request.name]) >= request.count
            and matched_counts[request.name] >= max(request.count, candidate_limit)
            for request in requests
        )

    for row in stream_rows(db_path):
        matching_requests = [
            request for request in requests
            if request.filter.matches_row(row)
        ]
        if not matching_requests:
            continue
        puzzle = puzzle_from_row(row)
        if puzzle is None:
            continue
        for request in matching_requests:
            if not request.filter.matches(puzzle):
                continue
            if puzzle.puzzle_id in all_seen_ids or puzzle.starting_fen in all_seen_fens:
                continue
            if puzzle.puzzle_id in seen_in_reservoir[request.name]:
                continue
            matched_counts[request.name] += 1
            reservoir = reservoirs[request.name]
            if len(reservoir) < request.count:
                reservoir.append(puzzle)
                seen_in_reservoir[request.name].add(puzzle.puzzle_id)
            else:
                index = rng.randrange(matched_counts[request.name])
                if index < request.count:
                    seen_in_reservoir[request.name].discard(reservoir[index].puzzle_id)
                    reservoir[index] = puzzle
                    seen_in_reservoir[request.name].add(puzzle.puzzle_id)
        if enough_candidates_seen():
            break

    selected: list[Puzzle] = []
    for request in requests:
        reservoir = reservoirs[request.name]
        if len(reservoir) < request.count:
            raise ValueError(
                f"Nicht genug passende Rätsel für {request.name}: {len(reservoir)}/{request.count}"
            )
        for puzzle in reservoir:
            if puzzle.puzzle_id in all_seen_ids or puzzle.starting_fen in all_seen_fens:
                raise ValueError(f"Duplikat in Auswahl: {puzzle.puzzle_id}")
            all_seen_ids.add(puzzle.puzzle_id)
            all_seen_fens.add(puzzle.starting_fen)
            selected.append(puzzle)
    return selected


def mixed(puzzles: list[Puzzle], seed: int) -> list[Puzzle]:
    shuffled = list(puzzles)
    random.Random(seed).shuffle(shuffled)
    return shuffled
