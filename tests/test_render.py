from pathlib import Path

from matt_in_1_pdf.chess import generate_puzzles
from matt_in_1_pdf.render import create_pdf


def test_pdf_smoke(tmp_path: Path):
    out = tmp_path / "test.pdf"
    create_pdf(generate_puzzles(6, 123), out)
    assert out.exists()
    assert out.stat().st_size > 10_000
