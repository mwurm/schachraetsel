from __future__ import annotations

from dataclasses import dataclass
import random

FILES = "abcdefgh"
RANKS = "12345678"
Square = tuple[int, int]  # file 0..7, rank 0..7


def square_name(sq: Square) -> str:
    return f"{FILES[sq[0]]}{RANKS[sq[1]]}"


def inside(sq: Square) -> bool:
    return 0 <= sq[0] < 8 and 0 <= sq[1] < 8


def kings_adjacent(a: Square, b: Square) -> bool:
    return max(abs(a[0] - b[0]), abs(a[1] - b[1])) <= 1


@dataclass(frozen=True)
class Position:
    attacker: str  # "white" or "black"
    king: Square
    piece: Square
    piece_type: str  # "Q" or "R"
    enemy_king: Square

    @property
    def defender(self) -> str:
        return "black" if self.attacker == "white" else "white"


@dataclass(frozen=True)
class Puzzle:
    position: Position
    mate_from: Square
    mate_to: Square

    @property
    def solution_de(self) -> str:
        letter = "D" if self.position.piece_type == "Q" else "T"
        return f"{letter}{square_name(self.mate_to)}#"


def _ray_attacks(src: Square, dst: Square, piece_type: str, blockers: set[Square]) -> bool:
    dx = dst[0] - src[0]
    dy = dst[1] - src[1]
    if dx == 0 and dy == 0:
        return False
    if piece_type == "R":
        if not (dx == 0 or dy == 0):
            return False
    else:  # queen
        if not (dx == 0 or dy == 0 or abs(dx) == abs(dy)):
            return False
    sx = 0 if dx == 0 else (1 if dx > 0 else -1)
    sy = 0 if dy == 0 else (1 if dy > 0 else -1)
    cur = (src[0] + sx, src[1] + sy)
    while cur != dst:
        if cur in blockers:
            return False
        cur = (cur[0] + sx, cur[1] + sy)
    return True


def attacked_by_attacker(pos: Position, sq: Square, piece_square: Square | None = None) -> bool:
    ps = pos.piece if piece_square is None else piece_square
    if kings_adjacent(pos.king, sq):
        return True
    blockers = {pos.king, pos.enemy_king}
    blockers.discard(sq)
    blockers.discard(ps)
    return _ray_attacks(ps, sq, pos.piece_type, blockers)


def defender_in_check(pos: Position, piece_square: Square | None = None) -> bool:
    return attacked_by_attacker(pos, pos.enemy_king, piece_square)


def slider_moves(pos: Position) -> list[Square]:
    directions = [(1,0),(-1,0),(0,1),(0,-1)]
    if pos.piece_type == "Q":
        directions += [(1,1),(1,-1),(-1,1),(-1,-1)]
    occupied = {pos.king, pos.enemy_king}
    out: list[Square] = []
    for dx, dy in directions:
        cur = (pos.piece[0] + dx, pos.piece[1] + dy)
        while inside(cur):
            if cur in occupied:
                break
            out.append(cur)
            cur = (cur[0] + dx, cur[1] + dy)
    return out


def defender_legal_moves(pos: Position, piece_square: Square) -> list[Square]:
    out: list[Square] = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            dst = (pos.enemy_king[0] + dx, pos.enemy_king[1] + dy)
            if not inside(dst) or dst == pos.king:
                continue
            # Capturing the major piece is allowed if the square is not protected by the king.
            if kings_adjacent(pos.king, dst):
                continue
            if dst == piece_square:
                out.append(dst)
                continue
            test = Position(pos.attacker, pos.king, piece_square, pos.piece_type, dst)
            if not attacked_by_attacker(test, dst, piece_square):
                out.append(dst)
    return out


def is_mate_after_slider_move(pos: Position, dst: Square) -> bool:
    moved = Position(pos.attacker, pos.king, dst, pos.piece_type, pos.enemy_king)
    if not defender_in_check(moved, dst):
        return False
    return not defender_legal_moves(moved, dst)


def unique_mate_moves(pos: Position) -> list[Square]:
    return [dst for dst in slider_moves(pos) if is_mate_after_slider_move(pos, dst)]


def legal_start(pos: Position) -> bool:
    if len({pos.king, pos.piece, pos.enemy_king}) != 3:
        return False
    if kings_adjacent(pos.king, pos.enemy_king):
        return False
    # The puzzle starts from a quiet legal position, not with the defending king already in check.
    if defender_in_check(pos):
        return False
    return True


def generate_puzzles(count: int = 30, seed: int = 20260826) -> list[Puzzle]:
    rng = random.Random(seed)
    puzzles: list[Puzzle] = []
    seen: set[Position] = set()
    attempts = 0
    while len(puzzles) < count:
        attempts += 1
        if attempts > 2_000_000:
            raise RuntimeError("Konnte nicht genug eindeutige Matt-in-1-Stellungen erzeugen.")
        attacker = "white" if len(puzzles) % 2 == 0 else "black"
        piece_type = "Q" if (len(puzzles) // 2) % 2 == 0 else "R"
        squares = rng.sample([(f, r) for f in range(8) for r in range(8)], 3)
        pos = Position(attacker, squares[0], squares[1], piece_type, squares[2])
        if pos in seen or not legal_start(pos):
            continue
        mates = unique_mate_moves(pos)
        if len(mates) != 1:
            continue
        # Keep the diagrams easy to read: avoid ultra-long puzzle moves across the entire board.
        dst = mates[0]
        if max(abs(dst[0] - pos.piece[0]), abs(dst[1] - pos.piece[1])) > 6:
            continue
        seen.add(pos)
        puzzles.append(Puzzle(pos, pos.piece, dst))
    return puzzles
