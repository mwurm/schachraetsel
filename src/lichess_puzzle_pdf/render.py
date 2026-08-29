from __future__ import annotations

from copy import deepcopy
import io
from pathlib import Path

import chess
import chess.svg
from reportlab.graphics import renderPDF
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from svglib.svglib import svg2rlg

from .config import Difficulty, PUZZLE_TYPES
from .notation import solution_to_figurine_moves
from .puzzle import Puzzle

MM = 72 / 25.4
TEXT_FONT = "ComicSans"
TEXT_FONT_BOLD = "ComicSans-Bold"
SYMBOL_FONT = "ChessSymbol"
PAGE_MARGIN = 10 * MM
BOARD_MARGIN_LEFT = 13 * MM
BOARD_SIZE = 73 * MM
TASK_HEADING_TOP = 263 * MM
TASK_HEADING_BOARD_GAP = 5 * MM
TASK_ROW_GAP = 8 * MM
COORD_FONT_SIZE = 8.25
SOLUTION_FONT_SIZE = 12
SOLUTION_ROWS_PER_GROUP = 3
SOLUTION_COLUMNS = 2
SOLUTION_GROUPS_PER_PAGE = 3
SOLUTION_ROW_GAP = 18 * MM
SOLUTION_GROUP_GAP = 11 * MM
SOLUTION_ICON_SIZE = 15.75
SOLUTION_MOVE_GAP = 4.5
SOLUTION_ICON_TEXT_GAP = 1.5
SOLUTION_WRAP_GAP = 14.0


def _register_font(name: str, paths: list[Path], fallback: str) -> str:
    for path in paths:
        if path.exists():
            if name not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont(name, str(path)))
            return name
    return fallback


def _register_text_fonts() -> tuple[str, str]:
    regular = _register_font(
        TEXT_FONT,
        [Path("/mnt/c/Windows/Fonts/comic.ttf"), Path("C:/Windows/Fonts/comic.ttf")],
        "Helvetica",
    )
    bold = _register_font(
        TEXT_FONT_BOLD,
        [Path("/mnt/c/Windows/Fonts/comicbd.ttf"), Path("C:/Windows/Fonts/comicbd.ttf")],
        "Helvetica-Bold",
    )
    return regular, bold


def _register_symbol_font() -> str:
    return _register_font(
        SYMBOL_FONT,
        [
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            Path("/usr/local/share/fonts/dejavu/DejaVuSans.ttf"),
            Path("/mnt/c/Windows/Fonts/seguisym.ttf"),
            Path("C:/Windows/Fonts/seguisym.ttf"),
        ],
        "Helvetica",
    )


class PieceSet:
    def __init__(self) -> None:
        self._drawings = {
            piece: svg2rlg(io.BytesIO(chess.svg.piece(piece).encode("utf-8")))
            for piece_type in chess.PIECE_TYPES
            for color in [chess.WHITE, chess.BLACK]
            for piece in [chess.Piece(piece_type, color)]
        }

    def draw(self, c: canvas.Canvas, piece: chess.Piece, x: float, y: float,
             field: float, scale: float, lift: float) -> None:
        drawing = deepcopy(self._drawings[piece])
        target = field * scale
        factor = min(target / drawing.width, target / drawing.height)
        drawing.scale(factor, factor)
        w = drawing.width * factor
        h = drawing.height * factor
        renderPDF.draw(drawing, c, x + (field - w) / 2, y + (field - h) / 2 + lift)


def _turn_piece(turn: bool) -> chess.Piece:
    return chess.Piece(chess.KING, chess.WHITE if turn == chess.WHITE else chess.BLACK)


def difficulty_stars(difficulty: Difficulty | None) -> str:
    return {
        Difficulty.EASY: "★",
        Difficulty.MEDIUM: "★★",
        Difficulty.CHALLENGING: "★★★",
        Difficulty.HARD: "★★★★",
        Difficulty.VERY_HARD: "★★★★★",
    }.get(difficulty, "")


def rating_metadata(puzzle: Puzzle, *, show_move_count: bool = True) -> str:
    if not show_move_count:
        return f"({puzzle.rating})"
    moves = len(puzzle.solution_moves)
    move_label = "Zug" if moves == 1 else "Züge"
    return f"({puzzle.rating}, {moves} {move_label})"


def task_instruction(puzzle: Puzzle) -> str:
    return PUZZLE_TYPES[puzzle.primary_type].instruction


def _draw_task_heading(c: canvas.Canvas, x: float, y: float, puzzle: Puzzle, task_no: int,
                       text_font: str, symbol_font: str, show_move_count: bool,
                       pieces: PieceSet) -> None:
    board = chess.Board(puzzle.starting_fen)
    stars = difficulty_stars(puzzle.difficulty)
    meta_label = rating_metadata(puzzle, show_move_count=show_move_count)
    prefix = f"Nr. {task_no} "
    middle = f" - {task_instruction(puzzle)}"
    size = 10
    c.setFont(text_font, size)
    c.drawString(x, y, prefix)
    symbol_x = x + c.stringWidth(prefix, text_font, size)
    pieces.draw(c, _turn_piece(board.turn), symbol_x, y - 1.7, size, 0.92, 0.0)
    suffix_x = symbol_x + size + 1.5
    c.setFont(text_font, size)
    c.drawString(suffix_x, y, middle)
    meta_x = suffix_x + c.stringWidth(middle + " ", text_font, size)
    if stars:
        c.setFont(symbol_font, size)
        c.drawString(meta_x, y, stars)
        meta_x += c.stringWidth(stars + " ", symbol_font, size)
    c.setFont(text_font, size)
    c.drawString(meta_x, y, meta_label)


def _board_square_xy(square: chess.Square, x: float, y: float, field: float, flipped: bool) -> tuple[float, float]:
    file = chess.square_file(square)
    rank = chess.square_rank(square)
    col = 7 - file if flipped else file
    row = rank if flipped else 7 - rank
    return x + col * field, y + (7 - row) * field


def _draw_board(c: canvas.Canvas, board: chess.Board, x: float, y: float, board_size: float,
                gray: float, piece_scale: float, piece_lift: float, pieces: PieceSet,
                text_font: str) -> None:
    field = board_size / 8
    flipped = board.turn == chess.BLACK
    c.setLineWidth(0)
    for vis_row in range(8):
        for vis_col in range(8):
            c.setFillGray(gray if (vis_row + vis_col) % 2 == 0 else 1.0)
            c.rect(x + vis_col * field, y + (7 - vis_row) * field, field, field, stroke=0, fill=1)

    c.setStrokeGray(0)
    c.setLineWidth(0.55)
    for i in range(9):
        c.line(x + i * field, y, x + i * field, y + board_size)
        c.line(x, y + i * field, x + board_size, y + i * field)

    for square, piece in board.piece_map().items():
        sx, sy = _board_square_xy(square, x, y, field, flipped)
        pieces.draw(c, piece, sx, sy, field, piece_scale, piece_lift)

    c.setFillGray(0.35)
    c.setFont(text_font, COORD_FONT_SIZE)
    file_labels = "hgfedcba" if flipped else "abcdefgh"
    rank_labels = "12345678" if flipped else "87654321"
    for i, label in enumerate(file_labels):
        c.drawCentredString(x + (i + 0.5) * field, y - 8.0, label)
        c.drawCentredString(x + (i + 0.5) * field, y + board_size + 2.0, label)
    for i, label in enumerate(rank_labels):
        c.drawRightString(x - 3.0, y + board_size - (i + 0.64) * field, label)
        c.drawString(x + board_size + 3.0, y + board_size - (i + 0.64) * field, label)


def default_title(puzzles: list[Puzzle]) -> str:
    if not puzzles:
        return "Schachtaktik"
    types = {puzzle.primary_type for puzzle in puzzles}
    if len(types) == 1:
        return PUZZLE_TYPES[next(iter(types))].german_name
    return "Schachtaktik"


def _draw_solution_line(c: canvas.Canvas, puzzle: Puzzle, x: float, y: float,
                        max_width: float, text_font: str, pieces: PieceSet) -> None:
    cursor_x = x
    cursor_y = y
    for move in solution_to_figurine_moves(puzzle.starting_fen, puzzle.solution_moves):
        text_width = c.stringWidth(move.text, text_font, SOLUTION_FONT_SIZE)
        move_width = SOLUTION_ICON_SIZE + SOLUTION_ICON_TEXT_GAP + text_width
        if cursor_x > x and cursor_x + move_width > x + max_width:
            cursor_x = x
            cursor_y -= SOLUTION_WRAP_GAP
        pieces.draw(
            c,
            move.piece,
            cursor_x,
            cursor_y - 2.0,
            SOLUTION_ICON_SIZE,
            0.92,
            0.0,
        )
        c.setFont(text_font, SOLUTION_FONT_SIZE)
        c.drawString(cursor_x + SOLUTION_ICON_SIZE + SOLUTION_ICON_TEXT_GAP, cursor_y, move.text)
        cursor_x += move_width + SOLUTION_MOVE_GAP


def _draw_solution_pages(c: canvas.Canvas, puzzles: list[Puzzle], text_font: str,
                         text_font_bold: str, pieces: PieceSet) -> None:
    width, _ = A4
    per_solution_page = SOLUTION_ROWS_PER_GROUP * SOLUTION_COLUMNS * SOLUTION_GROUPS_PER_PAGE
    column_x = [PAGE_MARGIN, width / 2 + 4 * MM]
    number_gap = 10 * MM
    solution_width = width / 2 - PAGE_MARGIN - number_gap - 6 * MM
    first_row_y = 255 * MM

    for page_start in range(0, len(puzzles), per_solution_page):
        page_items = puzzles[page_start:page_start + per_solution_page]
        c.setFillGray(0)
        c.setFont(text_font_bold, 22)
        c.drawString(PAGE_MARGIN, 281 * MM, "Lösungen")
        c.setFont(text_font, 10)
        c.drawString(PAGE_MARGIN, 272 * MM, "Die Lichess-Hauptvariante zu jeder Aufgabe:")

        for local, puzzle in enumerate(page_items):
            row_in_page = local // SOLUTION_COLUMNS
            col = local % SOLUTION_COLUMNS
            group = row_in_page // SOLUTION_ROWS_PER_GROUP
            row = row_in_page % SOLUTION_ROWS_PER_GROUP
            x = column_x[col]
            y = first_row_y - group * (
                SOLUTION_ROWS_PER_GROUP * SOLUTION_ROW_GAP + SOLUTION_GROUP_GAP
            ) - row * SOLUTION_ROW_GAP
            task_no = page_start + local + 1

            c.setFont(text_font_bold, SOLUTION_FONT_SIZE)
            c.drawString(x, y, f"{task_no}.")
            _draw_solution_line(
                c,
                puzzle,
                x + number_gap,
                y,
                solution_width,
                text_font,
                pieces,
            )

        groups_on_page = (len(page_items) + SOLUTION_ROWS_PER_GROUP * SOLUTION_COLUMNS - 1) // (
            SOLUTION_ROWS_PER_GROUP * SOLUTION_COLUMNS
        )
        c.setStrokeGray(0.7)
        c.setLineWidth(0.45)
        for group in range(groups_on_page - 1):
            y = first_row_y - (group + 1) * SOLUTION_ROWS_PER_GROUP * SOLUTION_ROW_GAP
            y -= group * SOLUTION_GROUP_GAP
            y += (SOLUTION_ROW_GAP - SOLUTION_GROUP_GAP) / 2
            c.line(PAGE_MARGIN, y, width - PAGE_MARGIN, y)

        c.setFont(text_font, 5.5)
        c.setFillGray(0.35)
        c.drawString(PAGE_MARGIN, PAGE_MARGIN, "Puzzlequelle: Lichess Puzzle Database (CC0), database.lichess.org")
        c.showPage()


def create_pdf(puzzles: list[Puzzle], output: str | Path, *, title: str | None = None,
               gray: float = 0.92, piece_scale: float = 0.86,
               piece_lift: float = 0.5, show_move_count: bool = True) -> Path:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(output), pagesize=A4)
    width, _ = A4
    pieces = PieceSet()
    text_font, text_font_bold = _register_text_fonts()
    symbol_font = _register_symbol_font()

    per_page = 6
    board_size = BOARD_SIZE
    x_positions = [BOARD_MARGIN_LEFT, width - PAGE_MARGIN - board_size - 3 * MM]
    heading_y_positions = [
        TASK_HEADING_TOP - row * (board_size + TASK_HEADING_BOARD_GAP + TASK_ROW_GAP)
        for row in range(3)
    ]
    y_positions = [heading_y - TASK_HEADING_BOARD_GAP - board_size for heading_y in heading_y_positions]
    page_title = title or default_title(puzzles)

    for page_start in range(0, len(puzzles), per_page):
        page_items = puzzles[page_start:page_start + per_page]
        if page_start == 0:
            c.setFont(text_font_bold, 22)
            c.drawString(PAGE_MARGIN, 281 * MM, page_title)
            c.setFont(text_font, 11)
            c.drawString(PAGE_MARGIN, 272.5 * MM, "Finde den besten Zug!")

        for local, puzzle in enumerate(page_items):
            col = local % 2
            row = local // 2
            x = x_positions[col]
            y = y_positions[row]
            task_no = page_start + local + 1
            heading_x = PAGE_MARGIN if col == 0 else x - 3 * MM
            c.setFillGray(0)
            _draw_task_heading(
                c,
                heading_x,
                heading_y_positions[row],
                puzzle,
                task_no,
                text_font,
                symbol_font,
                show_move_count,
                pieces,
            )
            _draw_board(
                c,
                chess.Board(puzzle.starting_fen),
                x,
                y,
                board_size,
                gray,
                piece_scale,
                piece_lift,
                pieces,
                text_font,
            )

        c.setFillGray(0.4)
        c.setFont(text_font, 7)
        c.drawCentredString(width / 2, PAGE_MARGIN, f"Seite {page_start // per_page + 1}")
        c.showPage()

    _draw_solution_pages(c, puzzles, text_font, text_font_bold, pieces)
    c.save()
    return output
