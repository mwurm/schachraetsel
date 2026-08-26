from __future__ import annotations

from copy import deepcopy
from importlib.resources import files
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg

from .chess import Puzzle, Square, square_name

MM = 72 / 25.4


PIECE_ASSET = {
    ("white", "K"): "wK.svg",
    ("white", "Q"): "wQ.svg",
    ("white", "R"): "wR.svg",
    ("black", "K"): "bK.svg",
    ("black", "Q"): "bQ.svg",
    ("black", "R"): "bR.svg",
}


class PieceSet:
    def __init__(self) -> None:
        root = files("matt_in_1_pdf").joinpath("assets/cburnett")
        self._drawings = {
            key: svg2rlg(str(root.joinpath(name))) for key, name in PIECE_ASSET.items()
        }

    def draw(self, c: canvas.Canvas, color: str, kind: str, x: float, y: float,
             field: float, scale: float, lift: float) -> None:
        drawing = deepcopy(self._drawings[(color, kind)])
        target = field * scale
        factor = min(target / drawing.width, target / drawing.height)
        drawing.scale(factor, factor)
        w = drawing.width * factor
        h = drawing.height * factor
        renderPDF.draw(drawing, c, x + (field - w) / 2, y + (field - h) / 2 + lift)


def _board_square_xy(square: Square, x: float, y: float, field: float, flipped: bool) -> tuple[float, float]:
    f, r = square
    col = 7 - f if flipped else f
    row = r if flipped else 7 - r
    # PDF y grows upwards; board row 0 is the visual top.
    return x + col * field, y + (7 - row) * field


def _draw_board(c: canvas.Canvas, puzzle: Puzzle, x: float, y: float, board_size: float,
                gray: float, piece_scale: float, piece_lift: float, pieces: PieceSet) -> None:
    field = board_size / 8
    flipped = puzzle.position.attacker == "black"

    # Fill squares first. Each fill is exactly clipped to its own field; nothing from a piece
    # has a background rectangle, so neighboring fields can never be overwritten.
    c.setLineWidth(0)
    for vis_row in range(8):
        for vis_col in range(8):
            is_dark = (vis_row + vis_col) % 2 == 0
            shade = gray if is_dark else 1.0
            c.setFillGray(shade)
            sx = x + vis_col * field
            sy = y + (7 - vis_row) * field
            c.rect(sx, sy, field, field, stroke=0, fill=1)

    # Grid as a separate vector layer.
    c.setStrokeGray(0)
    c.setLineWidth(0.55)
    for i in range(9):
        c.line(x + i * field, y, x + i * field, y + board_size)
        c.line(x, y + i * field, x + board_size, y + i * field)

    pos = puzzle.position
    enemy = "black" if pos.attacker == "white" else "white"
    for color, kind, square in [
        (pos.attacker, "K", pos.king),
        (pos.attacker, pos.piece_type, pos.piece),
        (enemy, "K", pos.enemy_king),
    ]:
        sx, sy = _board_square_xy(square, x, y, field, flipped)
        pieces.draw(c, color, kind, sx, sy, field, piece_scale, piece_lift)

    # Coordinates.
    c.setFillGray(0.35)
    c.setFont("Helvetica", 5.5)
    file_labels = "hgfedcba" if flipped else "abcdefgh"
    rank_labels = "12345678" if flipped else "87654321"
    for i, label in enumerate(file_labels):
        c.drawCentredString(x + (i + 0.5) * field, y - 4.2, label)
    for i, label in enumerate(rank_labels):
        c.drawRightString(x - 3.0, y + board_size - (i + 0.64) * field, label)


def create_pdf(puzzles: list[Puzzle], output: str | Path, *, gray: float = 0.92,
               piece_scale: float = 0.86, piece_lift: float = 0.5) -> Path:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(output), pagesize=A4)
    width, height = A4
    pieces = PieceSet()

    per_page = 6
    board = 54 * MM
    x_positions = [22 * MM, 120 * MM]
    y_positions = [194 * MM, 111 * MM, 28 * MM]

    for page_start in range(0, len(puzzles), per_page):
        page_items = puzzles[page_start:page_start + per_page]
        if page_start == 0:
            c.setFont("Helvetica-Bold", 22)
            c.drawString(25 * MM, 281 * MM, "Matt in 1")
            c.setFont("Helvetica", 11)
            c.drawString(25 * MM, 272.5 * MM, "Schachrätsel für Kinder - finde den einzigen Mattzug!")

        for local, puzzle in enumerate(page_items):
            col = local % 2
            row = local // 2
            x = x_positions[col]
            y = y_positions[row]
            task_no = page_start + local + 1
            heading_y = y + board + 10.5 * MM
            c.setFillGray(0)
            c.setFont("Helvetica-Bold", 12)
            c.drawString(x - 10 * MM, heading_y, f"Aufgabe {task_no}")
            c.setFont("Helvetica", 10)
            side = "Weiß" if puzzle.position.attacker == "white" else "Schwarz"
            c.drawString(x - 10 * MM, heading_y - 6.2 * MM, f"{side} am Zug - Matt in 1")
            _draw_board(c, puzzle, x, y, board, gray, piece_scale, piece_lift, pieces)
            c.setFillGray(0.35)
            c.setFont("Helvetica", 9)
            c.drawString(x - 10 * MM, y - 8.0 * MM, "Mattzug:")
            c.line(x + 10 * MM, y - 8.7 * MM, x + 54 * MM, y - 8.7 * MM)

        c.setFillGray(0.4)
        c.setFont("Helvetica", 7)
        c.drawCentredString(width / 2, 8 * MM, f"Seite {page_start // per_page + 1}")
        c.showPage()

    # Solutions.
    c.setFillGray(0)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(25 * MM, 281 * MM, "Lösungen")
    c.setFont("Helvetica", 10)
    c.drawString(25 * MM, 272 * MM, "Der eindeutige Mattzug zu jeder Aufgabe:")
    cols = 3
    rows = 10
    for i, puzzle in enumerate(puzzles):
        col = i // rows
        row = i % rows
        x = (25 + col * 58) * MM
        y = (255 - row * 20) * MM
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x, y, f"{i + 1}.")
        c.setFont("Helvetica", 10)
        c.drawString(x + 9 * MM, y, puzzle.solution_de)
    c.setFont("Helvetica", 5.5)
    c.setFillGray(0.35)
    c.drawString(15 * MM, 8 * MM, "Schachfiguren: Cburnett-Stil von Colin M.L. Burnett, CC BY-SA 3.0; siehe THIRD_PARTY_NOTICES.md")
    c.save()
    return output
