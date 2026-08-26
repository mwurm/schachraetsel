from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PuzzleType(str, Enum):
    MATE_IN_1 = "mateIn1"
    MATE_IN_2 = "mateIn2"
    MATE_IN_3 = "mateIn3"
    FORK = "fork"
    SKEWER = "skewer"
    PIN = "pin"
    DISCOVERED_ATTACK = "discoveredAttack"
    DOUBLE_CHECK = "doubleCheck"
    SACRIFICE = "sacrifice"
    DEFLECTION = "deflection"
    ATTRACTION = "attraction"
    CLEARANCE = "clearance"
    INTERFERENCE = "interference"
    BACK_RANK_MATE = "backRankMate"
    SMOTHERED_MATE = "smotheredMate"
    PROMOTION = "promotion"
    UNDER_PROMOTION = "underPromotion"
    EN_PASSANT = "enPassant"
    ENDGAME = "endgame"
    OPENING = "opening"
    MIDDLEGAME = "middlegame"


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass(frozen=True)
class RatingRange:
    minimum: int
    maximum: int

    def contains(self, rating: int) -> bool:
        return self.minimum <= rating <= self.maximum


@dataclass(frozen=True)
class PuzzleTypeConfig:
    lichess_theme: str
    german_name: str
    instruction: str
    priority: int


DIFFICULTY_RANGES: dict[Difficulty, RatingRange] = {
    Difficulty.EASY: RatingRange(600, 899),
    Difficulty.MEDIUM: RatingRange(900, 1199),
    Difficulty.HARD: RatingRange(1200, 1499),
}


PUZZLE_TYPES: dict[PuzzleType, PuzzleTypeConfig] = {
    PuzzleType.MATE_IN_1: PuzzleTypeConfig("mateIn1", "Matt in 1", "Matt in 1", 10),
    PuzzleType.MATE_IN_2: PuzzleTypeConfig("mateIn2", "Matt in 2", "Matt in 2", 11),
    PuzzleType.MATE_IN_3: PuzzleTypeConfig("mateIn3", "Matt in 3", "Matt in 3", 12),
    PuzzleType.SMOTHERED_MATE: PuzzleTypeConfig("smotheredMate", "Ersticktes Matt", "Finde das erstickte Matt", 20),
    PuzzleType.BACK_RANK_MATE: PuzzleTypeConfig("backRankMate", "Grundreihenmatt", "Finde das Grundreihenmatt", 21),
    PuzzleType.FORK: PuzzleTypeConfig("fork", "Gabel", "Finde die Gabel", 30),
    PuzzleType.SKEWER: PuzzleTypeConfig("skewer", "Spieß", "Finde den Spieß", 31),
    PuzzleType.PIN: PuzzleTypeConfig("pin", "Fesselung", "Finde die Fesselung", 32),
    PuzzleType.DISCOVERED_ATTACK: PuzzleTypeConfig("discoveredAttack", "Abzugsangriff", "Finde den Abzugsangriff", 33),
    PuzzleType.DOUBLE_CHECK: PuzzleTypeConfig("doubleCheck", "Doppelschach", "Finde das Doppelschach", 34),
    PuzzleType.SACRIFICE: PuzzleTypeConfig("sacrifice", "Opfer", "Finde das Opfer", 40),
    PuzzleType.DEFLECTION: PuzzleTypeConfig("deflection", "Ablenkung", "Finde die Ablenkung", 41),
    PuzzleType.ATTRACTION: PuzzleTypeConfig("attraction", "Hinlenkung", "Finde die Hinlenkung", 42),
    PuzzleType.CLEARANCE: PuzzleTypeConfig("clearance", "Linienräumung", "Finde die Linienräumung", 43),
    PuzzleType.INTERFERENCE: PuzzleTypeConfig("interference", "Unterbrechung", "Finde die Unterbrechung", 44),
    PuzzleType.PROMOTION: PuzzleTypeConfig("promotion", "Umwandlung", "Finde die Umwandlung", 50),
    PuzzleType.UNDER_PROMOTION: PuzzleTypeConfig("underPromotion", "Unterverwandlung", "Finde die Unterverwandlung", 51),
    PuzzleType.EN_PASSANT: PuzzleTypeConfig("enPassant", "En passant", "Finde en passant", 52),
    PuzzleType.ENDGAME: PuzzleTypeConfig("endgame", "Endspiel", "Finde den besten Endspielzug", 60),
    PuzzleType.MIDDLEGAME: PuzzleTypeConfig("middlegame", "Mittelspiel", "Finde den besten Mittelspielzug", 61),
    PuzzleType.OPENING: PuzzleTypeConfig("opening", "Eröffnung", "Finde den besten Eröffnungszug", 62),
}


SUPPORTED_LICHESS_THEMES = frozenset(config.lichess_theme for config in PUZZLE_TYPES.values())
PRIMARY_TYPE_PRIORITY = tuple(
    puzzle_type
    for puzzle_type, _ in sorted(PUZZLE_TYPES.items(), key=lambda item: item[1].priority)
)
PUZZLE_TYPE_LABELS_DE = {
    config.lichess_theme: config.german_name for config in PUZZLE_TYPES.values()
}
PUZZLE_TYPE_INSTRUCTIONS_DE = {
    config.lichess_theme: config.instruction for config in PUZZLE_TYPES.values()
}


def parse_puzzle_type(value: str) -> PuzzleType:
    try:
        return PuzzleType(value)
    except ValueError as exc:
        allowed = ", ".join(sorted(SUPPORTED_LICHESS_THEMES))
        raise ValueError(f"Unbekannter Rätseltyp {value!r}. Unterstützt: {allowed}") from exc
