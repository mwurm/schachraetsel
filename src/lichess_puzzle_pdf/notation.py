from __future__ import annotations

from dataclasses import dataclass

import chess

SAN_PIECES_DE = str.maketrans({
    "K": "K",
    "Q": "D",
    "R": "T",
    "B": "L",
    "N": "S",
})

def san_to_german(san: str) -> str:
    return san.translate(SAN_PIECES_DE)


def solution_to_german(san_moves: tuple[str, ...]) -> str:
    return " ".join(san_to_german(move) for move in san_moves)


@dataclass(frozen=True)
class FigurineMove:
    piece: chess.Piece
    text: str


def move_to_figurine_move(board: chess.Board, move: chess.Move) -> FigurineMove:
    piece = board.piece_at(move.from_square)
    if piece is None:
        raise ValueError(f"Keine Figur auf dem Ausgangsfeld: {move}")
    san = board.san(move)
    if piece.piece_type != chess.PAWN and san and san[0] in "KQRBN":
        san = san[1:]
    return FigurineMove(piece=piece, text=san)


def solution_to_figurine_moves(starting_fen: str, solution_moves: tuple[chess.Move, ...]) -> tuple[FigurineMove, ...]:
    board = chess.Board(starting_fen)
    rendered: list[FigurineMove] = []
    for move in solution_moves:
        rendered.append(move_to_figurine_move(board, move))
        board.push(move)
    return tuple(rendered)
