from pathlib import Path

from matt_in_1_pdf.chess import generate_puzzles
from matt_in_1_pdf.render import _task_heading, create_pdf


def test_task_heading_uses_compact_white_turn_label():
    assert _task_heading(7, "white") == "Nr. 7 ♔ - Matt in 1"


def test_task_heading_uses_compact_black_turn_label():
    assert _task_heading(8, "black") == "Nr. 8 ♚ - Matt in 1"


def test_pdf_smoke(tmp_path: Path):
    out = tmp_path / "test.pdf"
    create_pdf(generate_puzzles(6, 123), out)
    assert out.exists()
    assert out.stat().st_size > 10_000
