from __future__ import annotations

import csv
from pathlib import Path

import chess
import zstandard

from lichess_puzzle_pdf.config import Difficulty, PuzzleType
from lichess_puzzle_pdf.lichess import (
    LichessPuzzleRow,
    count_mate_in_one_moves,
    difficulty_for_rating,
    parse_row,
    primary_type_for,
    puzzle_from_row,
    reconstruct_puzzle,
)
from lichess_puzzle_pdf.notation import san_to_german, solution_to_german
from lichess_puzzle_pdf.render import create_pdf, difficulty_stars, rating_metadata
from lichess_puzzle_pdf.selection import PuzzleFilter, SelectionRequest, mixed, select_puzzles


HEADER = [
    "PuzzleId",
    "FEN",
    "Moves",
    "Rating",
    "RatingDeviation",
    "Popularity",
    "NbPlays",
    "Themes",
    "GameUrl",
    "OpeningTags",
]

MATE_IN_1_ROW = {
    "PuzzleId": "mate1",
    "FEN": "rnbqkbnr/pppp1ppp/8/4p3/8/5P2/PPPPP1PP/RNBQKBNR w KQkq - 0 2",
    "Moves": "g2g4 d8h4",
    "Rating": "740",
    "RatingDeviation": "80",
    "Popularity": "95",
    "NbPlays": "500",
    "Themes": "mate mateIn1 opening oneMove",
    "GameUrl": "https://lichess.org/test#3",
    "OpeningTags": "King_Pawn_Game",
}

MATE_IN_2_ROW = {
    "PuzzleId": "mate2",
    "FEN": "q3k1nr/1pp1nQpp/3p4/1P2p3/4P3/B1PP1b2/B5PP/5K2 b k - 0 17",
    "Moves": "e8d7 a2e6 d7d8 f7f8",
    "Rating": "998",
    "RatingDeviation": "80",
    "Popularity": "83",
    "NbPlays": "72",
    "Themes": "mate mateIn2 middlegame short",
    "GameUrl": "https://lichess.org/yyznGmXs/black#34",
    "OpeningTags": "Italian_Game Italian_Game_Classical_Variation",
}

FORK_ROW = {
    "PuzzleId": "fork1",
    "FEN": "r3r1k1/p4ppp/2p2n2/1p6/3P1qb1/2NQR3/PPB2PP1/R1B3K1 w - - 5 18",
    "Moves": "e3g3 e8e1 g1h2 e1c1 a1c1 f4h6 h2g1 h6c1",
    "Rating": "1380",
    "RatingDeviation": "105",
    "Popularity": "87",
    "NbPlays": "325",
    "Themes": "advantage attraction fork middlegame sacrifice veryLong",
    "GameUrl": "https://lichess.org/gyFeQsOE#35",
    "OpeningTags": "French_Defense French_Defense_Exchange_Variation",
}

PIN_ROW = {
    "PuzzleId": "pin1",
    "FEN": "r3r1k1/p4ppp/2p2n2/1p6/3P1qb1/2NQR3/PPB2PP1/R1B3K1 w - - 5 18",
    "Moves": "e3g3 e8e1 g1h2 e1c1 a1c1 f4h6 h2g1 h6c1",
    "Rating": "990",
    "RatingDeviation": "105",
    "Popularity": "87",
    "NbPlays": "325",
    "Themes": "advantage pin middlegame veryLong",
    "GameUrl": "",
    "OpeningTags": "",
}


def write_db(path: Path, rows: list[dict[str, str]]) -> Path:
    csv_path = path.with_suffix(".csv")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=HEADER)
        writer.writeheader()
        writer.writerows(rows)
    path.write_bytes(zstandard.ZstdCompressor().compress(csv_path.read_bytes()))
    return path


def row(overrides: dict[str, str] | None = None) -> LichessPuzzleRow:
    data = dict(MATE_IN_1_ROW)
    data.update(overrides or {})
    return parse_row(data)


def test_parse_row_handles_themes_openings_and_empty_optional_fields():
    parsed = parse_row({**PIN_ROW, "GameUrl": "", "OpeningTags": ""})
    assert parsed.themes == frozenset({"advantage", "pin", "middlegame", "veryLong"})
    assert parsed.game_url is None
    assert parsed.opening_tags == ()


def test_reconstruct_applies_first_move_and_keeps_remaining_solution():
    reconstructed = reconstruct_puzzle(MATE_IN_1_ROW["FEN"], MATE_IN_1_ROW["Moves"].split())
    board = chess.Board(MATE_IN_1_ROW["FEN"])
    board.push(chess.Move.from_uci("g2g4"))
    assert reconstructed.starting_fen == board.fen()
    assert reconstructed.solution_moves == (chess.Move.from_uci("d8h4"),)
    assert reconstructed.solution_san == ("Qh4#",)


def test_primary_type_uses_priority_and_unknown_theme_is_ignored():
    assert primary_type_for(frozenset({"mateIn2", "sacrifice", "endgame"})) == PuzzleType.MATE_IN_2
    assert primary_type_for(frozenset({"unknownTheme"})) is None


def test_filter_type_theme_and_exclude_theme():
    puzzle = puzzle_from_row(parse_row(FORK_ROW))
    assert puzzle is not None
    assert PuzzleFilter(types=frozenset({PuzzleType.FORK}), required_themes=frozenset({"middlegame"})).matches(puzzle)
    assert not PuzzleFilter(types=frozenset({PuzzleType.PIN})).matches(puzzle)
    assert not PuzzleFilter(types=frozenset({PuzzleType.FORK}), excluded_themes=frozenset({"sacrifice"})).matches(puzzle)


def test_filter_rejects_irrelevant_row_before_reconstruction():
    parsed = parse_row(FORK_ROW)
    assert not PuzzleFilter(types=frozenset({PuzzleType.MATE_IN_1})).matches_row(parsed)
    assert PuzzleFilter(types=frozenset({PuzzleType.FORK}), rating_min=1200).matches_row(parsed)


def test_difficulty_ranges():
    assert difficulty_for_rating(599) is None
    assert difficulty_for_rating(740) == Difficulty.EASY
    assert difficulty_for_rating(899) == Difficulty.EASY
    assert difficulty_for_rating(900) == Difficulty.MEDIUM
    assert difficulty_for_rating(998) == Difficulty.MEDIUM
    assert difficulty_for_rating(1199) == Difficulty.MEDIUM
    assert difficulty_for_rating(1200) == Difficulty.CHALLENGING
    assert difficulty_for_rating(1380) == Difficulty.CHALLENGING
    assert difficulty_for_rating(1599) == Difficulty.CHALLENGING
    assert difficulty_for_rating(1600) == Difficulty.HARD
    assert difficulty_for_rating(1999) == Difficulty.HARD
    assert difficulty_for_rating(2000) == Difficulty.VERY_HARD
    assert difficulty_for_rating(2166) == Difficulty.VERY_HARD
    assert difficulty_for_rating(10_000) == Difficulty.VERY_HARD


def test_difficulty_stars():
    assert difficulty_stars(Difficulty.EASY) == "★"
    assert difficulty_stars(Difficulty.MEDIUM) == "★★"
    assert difficulty_stars(Difficulty.CHALLENGING) == "★★★"
    assert difficulty_stars(Difficulty.HARD) == "★★★★"
    assert difficulty_stars(Difficulty.VERY_HARD) == "★★★★★"
    assert difficulty_stars(None) == ""


def test_rating_metadata_includes_optional_move_count():
    mate = puzzle_from_row(parse_row(MATE_IN_1_ROW))
    fork = puzzle_from_row(parse_row(FORK_ROW))
    assert mate is not None
    assert fork is not None
    assert rating_metadata(mate) == "(740, 1 Zug)"
    assert rating_metadata(fork) == "(1380, 7 Züge)"
    assert rating_metadata(fork, show_move_count=False) == "(1380)"


def test_mate_in_1_requires_exactly_one_matching_mate():
    accepted = puzzle_from_row(parse_row(MATE_IN_1_ROW))
    assert accepted is not None
    assert len(count_mate_in_one_moves(chess.Board(accepted.starting_fen))) == 1


def test_mate_in_1_rejects_non_mating_solution():
    rejected = puzzle_from_row(row({"Moves": "g2g4 a7a6"}))
    assert rejected is None


def test_mate_in_2_sequence_is_legal_and_ends_in_mate():
    puzzle = puzzle_from_row(parse_row(MATE_IN_2_ROW))
    assert puzzle is not None
    board = chess.Board(puzzle.starting_fen)
    for move in puzzle.solution_moves:
        assert move in board.legal_moves
        board.push(move)
    assert board.is_checkmate()


def test_tactic_themes_are_accepted_from_lichess_theme():
    assert puzzle_from_row(parse_row(FORK_ROW)).primary_type == PuzzleType.FORK
    assert puzzle_from_row(parse_row(PIN_ROW)).primary_type == PuzzleType.PIN


def test_sampling_is_reproducible_and_distribution_is_exact(tmp_path: Path):
    rows = []
    for i in range(8):
        rows.append({
            **MATE_IN_1_ROW,
            "PuzzleId": f"m{i}",
            "FEN": MATE_IN_1_ROW["FEN"].replace("0 2", f"{i} {2 + i}"),
            "Rating": str(700 + i),
        })
    rows.extend([
        {**FORK_ROW, "PuzzleId": "f1"},
        {**PIN_ROW, "PuzzleId": "p1", "FEN": PIN_ROW["FEN"].replace("5 18", "6 18")},
    ])
    db = write_db(tmp_path / "puzzles.csv.zst", rows)
    requests = [
        SelectionRequest("mateIn1", 2, PuzzleFilter(types=frozenset({PuzzleType.MATE_IN_1}))),
        SelectionRequest("fork", 1, PuzzleFilter(types=frozenset({PuzzleType.FORK}))),
        SelectionRequest("pin", 1, PuzzleFilter(types=frozenset({PuzzleType.PIN}))),
    ]
    first = select_puzzles(db, requests, seed=42)
    second = select_puzzles(db, requests, seed=42)
    assert [p.puzzle_id for p in first] == [p.puzzle_id for p in second]
    assert len(first) == 4
    assert {p.primary_type for p in first} == {PuzzleType.MATE_IN_1, PuzzleType.FORK, PuzzleType.PIN}


def test_sampling_can_stop_after_candidate_limit(tmp_path: Path):
    db = write_db(tmp_path / "puzzles.csv.zst", [
        {
            **MATE_IN_1_ROW,
            "PuzzleId": f"m{i}",
            "FEN": MATE_IN_1_ROW["FEN"].replace("0 2", f"{i} {2 + i}"),
            "Rating": str(700 + i),
        }
        for i in range(10)
    ])
    request = [SelectionRequest("mateIn1", 2, PuzzleFilter(types=frozenset({PuzzleType.MATE_IN_1})))]
    selected = select_puzzles(db, request, seed=42, candidate_limit=3)
    assert len(selected) == 2
    assert all(int(p.puzzle_id.removeprefix("m")) < 3 for p in selected)


def test_sampling_candidate_limit_zero_is_invalid_internal_api(tmp_path: Path):
    db = write_db(tmp_path / "puzzles.csv.zst", [MATE_IN_1_ROW])
    request = [SelectionRequest("mateIn1", 1, PuzzleFilter(types=frozenset({PuzzleType.MATE_IN_1})))]
    try:
        select_puzzles(db, request, seed=42, candidate_limit=0)
    except ValueError as exc:
        assert "candidate_limit" in str(exc)
    else:
        raise AssertionError("candidate_limit=0 should be normalized by CLI, not accepted internally")


def test_different_seeds_normally_pick_different_puzzles(tmp_path: Path):
    db = write_db(tmp_path / "puzzles.csv.zst", [
        {
            **MATE_IN_1_ROW,
            "PuzzleId": f"m{i}",
            "FEN": MATE_IN_1_ROW["FEN"].replace("0 2", f"{i} {2 + i}"),
            "Rating": str(700 + i),
        }
        for i in range(20)
    ])
    request = [SelectionRequest("mateIn1", 5, PuzzleFilter(types=frozenset({PuzzleType.MATE_IN_1})))]
    assert [p.puzzle_id for p in select_puzzles(db, request, seed=1)] != [
        p.puzzle_id for p in select_puzzles(db, request, seed=2)
    ]


def test_german_notation():
    assert san_to_german("Nf6+") == "Sf6+"
    assert solution_to_german(("Nf6+", "Kf8", "Qh6#")) == "Sf6+ Kf8 Dh6#"


def test_pdf_smoke_for_mate_in_1_mate_in_2_fork_and_mixed(tmp_path: Path):
    puzzles = [
        puzzle_from_row(parse_row(MATE_IN_1_ROW)),
        puzzle_from_row(parse_row(MATE_IN_2_ROW)),
        puzzle_from_row(parse_row(FORK_ROW)),
        puzzle_from_row(parse_row(PIN_ROW)),
    ]
    assert all(puzzles)
    out = tmp_path / "mixed.pdf"
    create_pdf([p for p in puzzles if p is not None], out)
    assert out.exists()
    assert out.stat().st_size > 10_000


def test_mixed_layout_is_seeded():
    puzzles = [puzzle_from_row(parse_row({**MATE_IN_1_ROW, "PuzzleId": f"m{i}"})) for i in range(6)]
    valid = [p for p in puzzles if p is not None]
    assert [p.puzzle_id for p in mixed(valid, 7)] == [p.puzzle_id for p in mixed(valid, 7)]
