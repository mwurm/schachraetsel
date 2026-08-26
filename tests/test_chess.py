from matt_in_1_pdf.chess import generate_puzzles, unique_mate_moves


def test_default_set_has_30_unique_mates():
    puzzles = generate_puzzles(30, 20260826)
    assert len(puzzles) == 30
    for puzzle in puzzles:
        assert unique_mate_moves(puzzle.position) == [puzzle.mate_to]


def test_colors_alternate():
    puzzles = generate_puzzles(10, 42)
    assert [p.position.attacker for p in puzzles] == [
        "white", "black", "white", "black", "white",
        "black", "white", "black", "white", "black",
    ]
