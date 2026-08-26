from __future__ import annotations

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
