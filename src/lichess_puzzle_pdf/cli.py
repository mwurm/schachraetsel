from __future__ import annotations

import argparse
from pathlib import Path
import urllib.request

from .config import Difficulty, PuzzleType, parse_puzzle_type
from .lichess import DEFAULT_DB_PATH, PUZZLE_DB_URL
from .render import create_pdf
from .selection import PuzzleFilter, SelectionRequest, mixed, select_puzzles


def _split_values(values: list[str] | list[list[str]] | None) -> list[str]:
    out: list[str] = []
    for value in values or []:
        if isinstance(value, list):
            out.extend(_split_values(value))
            continue
        out.extend(part.strip() for part in value.split(",") if part.strip())
    return out


def parse_types(values: list[str] | None) -> frozenset[PuzzleType]:
    parsed = []
    for value in _split_values(values):
        parsed.append(parse_puzzle_type(value))
    return frozenset(parsed)


def parse_puzzle_counts(values: list[str] | None) -> dict[PuzzleType, int]:
    counts: dict[PuzzleType, int] = {}
    for value in _split_values(values):
        if "=" not in value:
            raise ValueError("--puzzles erwartet Werte wie mateIn1=10")
        type_text, count_text = value.split("=", 1)
        puzzle_type = parse_puzzle_type(type_text)
        count = int(count_text)
        if count <= 0:
            raise ValueError("--puzzles-Anzahlen müssen > 0 sein")
        counts[puzzle_type] = counts.get(puzzle_type, 0) + count
    return counts


def build_requests(args: argparse.Namespace) -> list[SelectionRequest]:
    required_themes = frozenset(_split_values(args.theme))
    excluded_themes = frozenset(_split_values(args.exclude_theme))
    common = dict(
        required_themes=required_themes,
        excluded_themes=excluded_themes,
        rating_min=args.rating_min,
        rating_max=args.rating_max,
        min_popularity=args.min_popularity,
        min_plays=args.min_plays,
    )
    puzzle_counts = parse_puzzle_counts(args.puzzles)
    if puzzle_counts:
        return [
            SelectionRequest(
                name=puzzle_type.value,
                count=count,
                filter=PuzzleFilter(types=frozenset({puzzle_type}), **common),
            )
            for puzzle_type, count in puzzle_counts.items()
        ]

    types = parse_types(args.type) or frozenset({PuzzleType.MATE_IN_1})
    difficulty_counts = {
        Difficulty.EASY: args.easy,
        Difficulty.MEDIUM: args.medium,
        Difficulty.CHALLENGING: args.challenging,
        Difficulty.HARD: args.hard,
        Difficulty.VERY_HARD: args.very_hard,
    }
    if any(count is not None for count in difficulty_counts.values()):
        return [
            SelectionRequest(
                name=f"{difficulty.value}",
                count=count,
                filter=PuzzleFilter(types=types, difficulty=difficulty, **common),
            )
            for difficulty, count in difficulty_counts.items()
            if count
        ]
    return [
        SelectionRequest(
            name="default",
            count=args.count,
            filter=PuzzleFilter(types=types, **common),
        )
    ]


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Erzeuge deutsche A4-PDFs aus der Lichess Puzzle Database.")
    sub = p.add_subparsers(dest="command")
    download = sub.add_parser("download-db", help="Lichess Puzzle Database nach ~/.cache laden")
    download.add_argument("--output", type=Path, default=DEFAULT_DB_PATH)
    download.add_argument("--url", default=PUZZLE_DB_URL)

    p.add_argument("-o", "--output", type=Path, default=Path("lichess_puzzles.pdf"))
    p.add_argument("--db", type=Path, default=DEFAULT_DB_PATH, help="Pfad zur lichess_db_puzzle.csv.zst")
    p.add_argument("-n", "--count", type=int, default=30)
    p.add_argument("--type", action="append", help="Primärer Lichess-Typ, mehrfach oder kommasepariert")
    p.add_argument("--puzzles", action="append", nargs="+", help="Verteilung, z.B. mateIn1=10 fork=10")
    p.add_argument("--easy", type=int)
    p.add_argument("--medium", type=int)
    p.add_argument("--challenging", type=int)
    p.add_argument("--hard", type=int)
    p.add_argument("--very-hard", dest="very_hard", type=int)
    p.add_argument("--layout", choices=["grouped", "mixed"], default="grouped")
    p.add_argument("--title")
    p.add_argument("--seed", type=int, default=20260826, help="Seed für reproduzierbare Auswahl")
    p.add_argument(
        "--candidate-limit",
        type=int,
        default=500,
        help="Validierte Kandidaten pro Auswahlgruppe; 0 scannt die komplette Datenbank",
    )
    p.add_argument("--rating-min", type=int)
    p.add_argument("--rating-max", type=int)
    p.add_argument("--min-popularity", type=int)
    p.add_argument("--min-plays", type=int)
    p.add_argument("--theme", action="append", help="Zusätzlich erforderliches sekundäres Theme")
    p.add_argument("--exclude-theme", action="append", help="Auszuschließendes Theme")
    p.add_argument("--gray", type=float, default=0.92)
    p.add_argument("--piece-scale", type=float, default=0.86)
    p.add_argument("--piece-lift", type=float, default=0.5)
    return p


def download_db(output: Path, url: str) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as response, output.open("wb") as target:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            target.write(chunk)
    return output


def main() -> None:
    args = parser().parse_args()
    if args.command == "download-db":
        print(download_db(args.output, args.url))
        return
    if args.count <= 0:
        raise SystemExit("--count muss > 0 sein")
    if not 0.0 <= args.gray <= 1.0:
        raise SystemExit("--gray muss zwischen 0 und 1 liegen")
    try:
        requests = build_requests(args)
        candidate_limit = None if args.candidate_limit == 0 else args.candidate_limit
        puzzles = select_puzzles(args.db, requests, args.seed, candidate_limit)
    except (ValueError, FileNotFoundError) as exc:
        raise SystemExit(str(exc)) from exc
    if args.layout == "mixed":
        puzzles = mixed(puzzles, args.seed)
    path = create_pdf(
        puzzles,
        args.output,
        title=args.title,
        gray=args.gray,
        piece_scale=args.piece_scale,
        piece_lift=args.piece_lift,
    )
    print(path)


if __name__ == "__main__":
    main()
