from __future__ import annotations

import argparse
from pathlib import Path

from .chess import generate_puzzles
from .render import create_pdf


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Erzeuge ein deutsches A4-PDF mit Matt-in-1-Aufgaben.")
    p.add_argument("-o", "--output", type=Path, default=Path("matt_in_1.pdf"))
    p.add_argument("-n", "--count", type=int, default=30)
    p.add_argument("--seed", type=int, default=20260826, help="Seed für reproduzierbare Aufgaben")
    p.add_argument("--gray", type=float, default=0.92, help="Grauwert der dunklen Felder (0=schwarz, 1=weiß)")
    p.add_argument("--piece-scale", type=float, default=0.86, help="Figurengröße relativ zum Feld")
    p.add_argument("--piece-lift", type=float, default=0.5, help="Optische Verschiebung der Figuren nach oben in PDF-Punkten")
    return p


def main() -> None:
    args = parser().parse_args()
    if args.count <= 0:
        raise SystemExit("--count muss > 0 sein")
    if not 0.0 <= args.gray <= 1.0:
        raise SystemExit("--gray muss zwischen 0 und 1 liegen")
    puzzles = generate_puzzles(args.count, args.seed)
    path = create_pdf(
        puzzles,
        args.output,
        gray=args.gray,
        piece_scale=args.piece_scale,
        piece_lift=args.piece_lift,
    )
    print(path)


if __name__ == "__main__":
    main()
