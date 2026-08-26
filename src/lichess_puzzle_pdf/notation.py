from __future__ import annotations

import chess

SAN_PIECES_DE = str.maketrans({
    "K": "K",
    "Q": "D",
    "R": "T",
    "B": "L",
    "N": "S",
})

SAN_PIECES_UNICODE = str.maketrans({
    "K": "♔",
    "Q": "♕",
    "R": "♖",
    "B": "♗",
    "N": "♘",
})

PIECE_SYMBOLS_UNICODE = {
    chess.Piece(chess.PAWN, chess.WHITE): "♙",
    chess.Piece(chess.KNIGHT, chess.WHITE): "♘",
    chess.Piece(chess.BISHOP, chess.WHITE): "♗",
    chess.Piece(chess.ROOK, chess.WHITE): "♖",
    chess.Piece(chess.QUEEN, chess.WHITE): "♕",
    chess.Piece(chess.KING, chess.WHITE): "♔",
    chess.Piece(chess.PAWN, chess.BLACK): "♟",
    chess.Piece(chess.KNIGHT, chess.BLACK): "♞",
    chess.Piece(chess.BISHOP, chess.BLACK): "♝",
    chess.Piece(chess.ROOK, chess.BLACK): "♜",
    chess.Piece(chess.QUEEN, chess.BLACK): "♛",
    chess.Piece(chess.KING, chess.BLACK): "♚",
}


def san_to_german(san: str) -> str:
    return san.translate(SAN_PIECES_DE)


def solution_to_german(san_moves: tuple[str, ...]) -> str:
    return " ".join(san_to_german(move) for move in san_moves)


def san_to_unicode(san: str) -> str:
    return san.translate(SAN_PIECES_UNICODE)


def solution_to_unicode(san_moves: tuple[str, ...]) -> str:
    return " ".join(san_to_unicode(move) for move in san_moves)


def move_to_unicode(board: chess.Board, move: chess.Move) -> str:
    piece = board.piece_at(move.from_square)
    if piece is None:
        raise ValueError(f"Keine Figur auf dem Ausgangsfeld: {move}")
    san = board.san(move)
    symbol = PIECE_SYMBOLS_UNICODE[piece]
    if piece.piece_type == chess.PAWN:
        return f"{symbol}{san}"
    if san and san[0] in "KQRBN":
        san = san[1:]
    return f"{symbol}{san}"


def solution_to_unicode_with_sides(starting_fen: str, solution_moves: tuple[chess.Move, ...]) -> str:
    board = chess.Board(starting_fen)
    rendered: list[str] = []
    for move in solution_moves:
        rendered.append(move_to_unicode(board, move))
        board.push(move)
    return " ".join(rendered)
