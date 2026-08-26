# AGENTS.md

## Projektziel

Dieses Repository erzeugt druckbare deutsche A4-PDFs mit Schachrätseln aus der
offiziellen **Lichess Puzzle Database**.

Der Generator heißt:

```bash
lichess-puzzle-pdf
```

Python-Paket:

```text
lichess_puzzle_pdf
```

## Zentrale Invarianten

1. Lichess ist die einzige Puzzlequelle.
2. Keine selbst erzeugten Positionen.
3. Kein Fallback auf interne Generatoren.
4. Keine zweite externe Puzzlequelle.
5. Das Lichess-`FEN` niemals direkt rendern.
6. Immer zuerst den ersten Zug aus `Moves` anwenden.
7. Alle verbleibenden Lösungszüge müssen legal sein.
8. `mateIn1` muss genau einen legalen Mattzug besitzen.
9. Dieser Mattzug muss dem ersten Lichess-Lösungszug entsprechen.
10. Theme-Namen nicht erfinden.
11. Neue Themes immer gegen die tatsächliche Lichess-Datenbank oder offizielle
    Lichess-Quellen prüfen.
12. Renderer zeichnet Brett und Figuren direkt.
13. Keine Unicode-Figur-Überdeckungslogik einführen.
14. Figuren dürfen keine benachbarten Felder übermalen.
15. Brettlinien müssen vollständig sichtbar bleiben.

## Technischer Überblick

- Python >= 3.11
- `python-chess` für schachliche Interpretation
- `zstandard` und `csv` für Streaming der `.csv.zst`
- `reportlab` und `svglib` für PDF/SVG-Rendering
- `pytest` für Tests

Wichtige Dateien:

```text
src/lichess_puzzle_pdf/
├── __main__.py
├── cli.py
├── config.py
├── lichess.py
├── notation.py
├── puzzle.py
├── render.py
└── selection.py

tests/
└── test_lichess.py
```

## Architektur

### `config.py`

Enthält zentrale Theme- und Schwierigkeitseinstellungen.

Theme-Strings müssen echte Lichess-Theme-Namen sein, z. B.:

```text
mateIn1
mateIn2
fork
skewer
pin
discoveredAttack
underPromotion
enPassant
```

### `lichess.py`

Verantwortlich für:

- `.csv.zst` Streaming
- CSV Parsing
- zentrale Rekonstruktion über `reconstruct_puzzle`
- Lichess Theme Handling
- grundlegende Legalitätsprüfung
- zusätzliche Mattprüfung für `mateIn1`, `mateIn2`, `mateIn3`

Die Lichess-Rekonstruktion darf nicht dupliziert werden.

### `selection.py`

Verantwortlich für:

- Typfilter
- sekundäre Theme-Filter
- Ausschlussfilter
- Rating, Popularity, NbPlays
- Difficulty
- Reservoir Sampling
- Seed-Reproduzierbarkeit
- Mengenverteilung

### `notation.py`

Verantwortlich für deutsche SAN-Ausgabe:

```text
K = König
D = Dame
T = Turm
L = Läufer
S = Springer
```

Bauernzüge bleiben ohne Buchstaben.

### `render.py`

Enthält ausschließlich Darstellung und PDF-Erzeugung.

Besonders wichtig für Änderungen am Brett:

1. Felder werden zuerst einzeln gefüllt.
2. Das Raster wird als eigene Vektorebene gezeichnet.
3. SVG-Figuren werden ohne Hintergrundrechteck direkt in das Zielfeld gesetzt.
4. Figuren müssen innerhalb ihres Feldes bleiben und optisch sauber zentriert
   sein.
5. Koordinaten müssen zur Brettorientierung passen.
6. Schwarz am Zug wird gespiegelt dargestellt.

## CLI

Beispiele:

```bash
lichess-puzzle-pdf download-db
```

```bash
lichess-puzzle-pdf --type mateIn2 --count 30 --output mate-in-2.pdf
```

```bash
lichess-puzzle-pdf \
  --puzzles mateIn1=10 mateIn2=10 fork=10 \
  --layout grouped \
  --output training.pdf
```

Kein automatischer Download beim PDF-Erzeugen.

## Tests

Vor Abschluss einer Änderung immer ausführen:

```bash
python -m pytest
```

Bei Rendering-Änderungen zusätzlich nach Möglichkeit ein Beispiel-PDF erzeugen.
Wenn keine lokale Lichess-Datenbank vorhanden ist, dies im Abschlussbericht
klar sagen.

## Definition of Done

Eine Änderung ist fertig, wenn:

- die gewünschte Funktion umgesetzt ist
- Lichess die einzige Puzzlequelle bleibt
- bestehende Tests erfolgreich sind
- neue relevante Fälle getestet sind
- README/AGENTS aktualisiert wurden, falls Bedienung oder Architektur sich
  geändert haben
- bei Rendering-Änderungen das PDF visuell plausibel ist
