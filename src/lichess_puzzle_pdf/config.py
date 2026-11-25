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
    MATE_ANASTASIA = "anastasiaMate"
    MATE_ARABIAN = "arabianMate"
    BACK_RANK_MATE = "backRankMate"
    SMOTHERED_MATE = "smotheredMate"
    BALESTRA_MATE = "balestraMate"
    BLIND_SWINE_MATE = "blindSwineMate"
    BODEN_MATE = "bodenMate"
    CORNER_MATE = "cornerMate"
    DOUBLE_BISHOP_MATE = "doubleBishopMate"
    DOVETAIL_MATE = "dovetailMate"
    EPAULETTE_MATE = "epauletteMate"
    HOOK_MATE = "hookMate"
    KILL_BOX_MATE = "killBoxMate"
    PILLSBURYS_MATE = "pillsburysMate"
    MORPHYS_MATE = "morphysMate"
    OPERA_MATE = "operaMate"
    SWALLOWS_TAIL_MATE = "swallowstailMate"
    TRIANGLE_MATE = "triangleMate"
    VUKOVIC_MATE = "vukovicMate"
    PROMOTION = "promotion"
    UNDER_PROMOTION = "underPromotion"
    EN_PASSANT = "enPassant"
    ENDGAME = "endgame"
    OPENING = "opening"
    MIDDLEGAME = "middlegame"


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    CHALLENGING = "challenging"
    HARD = "hard"
    VERY_HARD = "veryHard"


@dataclass(frozen=True)
class RatingRange:
    minimum: int
    maximum: int | None

    def contains(self, rating: int) -> bool:
        if self.maximum is None:
            return rating >= self.minimum
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
    Difficulty.CHALLENGING: RatingRange(1200, 1599),
    Difficulty.HARD: RatingRange(1600, 1999),
    Difficulty.VERY_HARD: RatingRange(2000, None),
}


PUZZLE_TYPES: dict[PuzzleType, PuzzleTypeConfig] = {
    PuzzleType.MATE_IN_1: PuzzleTypeConfig("mateIn1", "Matt in 1", "Matt in 1", 10),
    PuzzleType.MATE_IN_2: PuzzleTypeConfig("mateIn2", "Matt in 2", "Matt in 2", 11),
    PuzzleType.MATE_IN_3: PuzzleTypeConfig("mateIn3", "Matt in 3", "Matt in 3", 12),
    PuzzleType.MATE_ANASTASIA: PuzzleTypeConfig("anastasiaMate", "Anastasia-Matt", "Finde das Anastasia-Matt", 18),
    PuzzleType.MATE_ARABIAN: PuzzleTypeConfig("arabianMate", "Arabisches Matt", "Finde das arabische Matt", 19),
    PuzzleType.SMOTHERED_MATE: PuzzleTypeConfig("smotheredMate", "Ersticktes Matt", "Finde das erstickte Matt", 20),
    PuzzleType.BACK_RANK_MATE: PuzzleTypeConfig("backRankMate", "Grundreihenmatt", "Finde das Grundreihenmatt", 21),
    PuzzleType.BALESTRA_MATE: PuzzleTypeConfig("balestraMate", "Balestra-Matt", "Finde das Balestra-Matt", 22),
    PuzzleType.BLIND_SWINE_MATE: PuzzleTypeConfig("blindSwineMate", "Blind-Swine-Matt", "Finde das Blind-Swine-Matt", 23),
    PuzzleType.BODEN_MATE: PuzzleTypeConfig("bodenMate", "Boden-Matt", "Finde das Boden-Matt", 24),
    PuzzleType.CORNER_MATE: PuzzleTypeConfig("cornerMate", "Eckmatt", "Finde das Eckmatt", 25),
    PuzzleType.DOUBLE_BISHOP_MATE: PuzzleTypeConfig("doubleBishopMate", "Doppelläufermatt", "Finde das Doppelläufermatt", 26),
    PuzzleType.DOVETAIL_MATE: PuzzleTypeConfig("dovetailMate", "Dovetail-Matt", "Finde das Dovetail-Matt", 27),
    PuzzleType.EPAULETTE_MATE: PuzzleTypeConfig("epauletteMate", "Epaulettenmatt", "Finde das Epaulettenmatt", 28),
    PuzzleType.HOOK_MATE: PuzzleTypeConfig("hookMate", "Hakenmatt", "Finde das Hakenmatt", 29),
    PuzzleType.KILL_BOX_MATE: PuzzleTypeConfig("killBoxMate", "Kill-Box-Matt", "Finde das Kill-Box-Matt", 30),
    PuzzleType.PILLSBURYS_MATE: PuzzleTypeConfig("pillsburysMate", "Pillsbury-Matt", "Finde das Pillsbury-Matt", 31),
    PuzzleType.MORPHYS_MATE: PuzzleTypeConfig("morphysMate", "Morphy-Matt", "Finde das Morphy-Matt", 32),
    PuzzleType.OPERA_MATE: PuzzleTypeConfig("operaMate", "Opernmatt", "Finde das Opernmatt", 33),
    PuzzleType.SWALLOWS_TAIL_MATE: PuzzleTypeConfig("swallowstailMate", "Schwalbenschwanzmatt", "Finde das Schwalbenschwanzmatt", 34),
    PuzzleType.TRIANGLE_MATE: PuzzleTypeConfig("triangleMate", "Dreiecksmatt", "Finde das Dreiecksmatt", 35),
    PuzzleType.VUKOVIC_MATE: PuzzleTypeConfig("vukovicMate", "Vuković-Matt", "Finde das Vuković-Matt", 36),
    PuzzleType.FORK: PuzzleTypeConfig("fork", "Gabel", "Finde die Gabel", 40),
    PuzzleType.SKEWER: PuzzleTypeConfig("skewer", "Spieß", "Finde den Spieß", 41),
    PuzzleType.PIN: PuzzleTypeConfig("pin", "Fesselung", "Finde die Fesselung", 42),
    PuzzleType.DISCOVERED_ATTACK: PuzzleTypeConfig("discoveredAttack", "Abzugsangriff", "Finde den Abzugsangriff", 43),
    PuzzleType.DOUBLE_CHECK: PuzzleTypeConfig("doubleCheck", "Doppelschach", "Finde das Doppelschach", 44),
    PuzzleType.SACRIFICE: PuzzleTypeConfig("sacrifice", "Opfer", "Finde das Opfer", 50),
    PuzzleType.DEFLECTION: PuzzleTypeConfig("deflection", "Ablenkung", "Finde die Ablenkung", 51),
    PuzzleType.ATTRACTION: PuzzleTypeConfig("attraction", "Hinlenkung", "Finde die Hinlenkung", 52),
    PuzzleType.CLEARANCE: PuzzleTypeConfig("clearance", "Linienräumung", "Finde die Linienräumung", 53),
    PuzzleType.INTERFERENCE: PuzzleTypeConfig("interference", "Unterbrechung", "Finde die Unterbrechung", 54),
    PuzzleType.PROMOTION: PuzzleTypeConfig("promotion", "Umwandlung", "Finde die Umwandlung", 60),
    PuzzleType.UNDER_PROMOTION: PuzzleTypeConfig("underPromotion", "Unterverwandlung", "Finde die Unterverwandlung", 61),
    PuzzleType.EN_PASSANT: PuzzleTypeConfig("enPassant", "En passant", "Finde en passant", 62),
    PuzzleType.ENDGAME: PuzzleTypeConfig("endgame", "Endspiel", "Finde den besten Endspielzug", 70),
    PuzzleType.MIDDLEGAME: PuzzleTypeConfig("middlegame", "Mittelspiel", "Finde den besten Mittelspielzug", 71),
    PuzzleType.OPENING: PuzzleTypeConfig("opening", "Eröffnung", "Finde den besten Eröffnungszug", 72),
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
