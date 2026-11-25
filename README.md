# Lichess Puzzle PDF

Erzeugt deutsche, druckbare A4-Schachrätsel-PDFs aus der offiziellen
**Lichess Puzzle Database**.

Die einzige Puzzlequelle ist der offizielle `.csv.zst`-Export von
[`database.lichess.org`](https://database.lichess.org/). Das Programm erzeugt
keine eigenen Stellungen und lädt beim PDF-Erzeugen keine Daten automatisch
herunter.

## Eigenschaften

- Streaming-Verarbeitung der Lichess Puzzle Database mit `zstandard` und `csv`
- Reservoir Sampling über die gesamte Datenbank für faire, reproduzierbare Auswahl
- mehrere Rätseltypen über echte Lichess-`Themes`
- variable Lösungslängen mit SVG-Figuren-Notation inklusive Bauern
- Rating-Schwierigkeit `easy`, `medium`, `challenging`, `hard`, `veryHard`
- mehrere Typen in einem PDF, gruppiert oder gemischt
- vektorbasierte Brett- und Figuren-Ausgabe
- tonersparende Bretter mit hellgrauen Feldern

## Installation

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .
```

## Datenbank

```bash
lichess-puzzle-pdf download-db
```

Standardpfad:

```text
~/.cache/lichess-puzzle-pdf/lichess_db_puzzle.csv.zst
```

Ein eigener Pfad kann beim Erzeugen mit `--db` angegeben werden.

Standardmäßig sampelt das Programm pro Auswahlgruppe zufällig aus bis zu 500
passenden, validierten Kandidaten. Das hält Befehle wie
`--type mateIn1 --count 30` praktisch benutzbar. Der schnelle CSV-Filter läuft
vor der schachlichen Rekonstruktion, sodass nur potenziell passende Zeilen mit
`python-chess` validiert werden. Der verwendete Seed wird nach der PDF-Erzeugung
ausgegeben und kann mit `--seed` erneut verwendet werden.

Für einen vollständigen Reservoir-Scan über die gesamte Datenbank:

```bash
lichess-puzzle-pdf --type mateIn1 --count 30 --candidate-limit 0
```

Reproduzierbare Auswahl:

```bash
lichess-puzzle-pdf --type fork --count 30 --seed 42 --output forks.pdf
```

## PDF Erzeugen

```bash
lichess-puzzle-pdf --type mateIn1 --count 30 --output mate-in-1.pdf
```

Ohne `--output` wird ein zufälliger Dateiname mit der Rätselanzahl am Ende
erzeugt, z. B. `lichess-puzzles-a1b2c3d4-30.pdf`.

Mehrere Typen:

```bash
lichess-puzzle-pdf \
  --type mateIn1 \
  --type fork \
  --type pin \
  --count 30 \
  --output training.pdf
```

Konkrete Verteilung:

```bash
lichess-puzzle-pdf \
  --puzzles mateIn1=10 mateIn2=10 fork=10 \
  --layout grouped \
  --output training.pdf
```

Mattmuster gezielt auswählen:

```bash
lichess-puzzle-pdf \
  --puzzles anastasiaMate=10 arabianMate=10 backRankMate=10 \
  --rating-min 600 --rating-max 899 \
  --layout grouped \
  --output mattmuster.pdf
```

`--type` und `--puzzles` berücksichtigen alle Themes eines Rätsels. Ein Rätsel
mit `mateIn2` und `anastasiaMate` ist daher auch über `anastasiaMate` auswählbar.
Die Aufgabenüberschrift verwendet den angeforderten Typ. Mehrere `--type`-Werte
sind ODER-verknüpft; `--theme` verlangt zusätzliche Themes.

Bei `--puzzles` gelten die dort angegebenen Stückzahlen; Schwierigkeitsanzahlen
wie `--easy` werden in dieser Kombination nicht berücksichtigt. Für eine
Rating-Einschränkung zusätzlich `--rating-min` und `--rating-max` verwenden.

Nach Schwierigkeit:

```bash
lichess-puzzle-pdf \
  --type fork \
  --easy 10 \
  --medium 10 \
  --challenging 10 \
  --hard 10 \
  --very-hard 10 \
  --output forks.pdf
```

Die Zuganzahl in der Aufgabenüberschrift ist standardmäßig aktiv und kann
abgeschaltet werden:

```bash
lichess-puzzle-pdf --type fork --count 30 --no-move-count --output forks.pdf
```

Sekundäre Themes filtern:

```bash
lichess-puzzle-pdf \
  --type fork \
  --theme endgame \
  --exclude-theme opening \
  --count 20
```

## Unterstützte Themes

Die Theme-Namen entsprechen den sichtbaren Lichess-Puzzle-Themes aus dem
offiziellen Lichess-Code und der Lichess Puzzle Database. Alle 19 Mattmuster
der [Lichess-Themenseite](https://lichess.org/training/themes) werden unterstützt.

| Lichess Theme | Deutsch |
| --- | --- |
| mateIn1 | Matt in 1 |
| mateIn2 | Matt in 2 |
| mateIn3 | Matt in 3 |
| anastasiaMate | Anastasia-Matt |
| arabianMate | Arabisches Matt |
| smotheredMate | Ersticktes Matt |
| backRankMate | Grundreihenmatt |
| balestraMate | Balestra-Matt |
| blindSwineMate | Blind-Swine-Matt |
| bodenMate | Boden-Matt |
| cornerMate | Eckmatt |
| doubleBishopMate | Doppelläufermatt |
| dovetailMate | Dovetail-Matt |
| epauletteMate | Epaulettenmatt |
| hookMate | Hakenmatt |
| killBoxMate | Kill-Box-Matt |
| pillsburysMate | Pillsbury-Matt |
| morphysMate | Morphy-Matt |
| operaMate | Opernmatt |
| swallowstailMate | Schwalbenschwanzmatt |
| triangleMate | Dreiecksmatt |
| vukovicMate | Vuković-Matt |
| fork | Gabel |
| skewer | Spieß |
| pin | Fesselung |
| discoveredAttack | Abzugsangriff |
| doubleCheck | Doppelschach |
| sacrifice | Opfer |
| deflection | Ablenkung |
| attraction | Hinlenkung |
| clearance | Linienräumung |
| interference | Unterbrechung |
| promotion | Umwandlung |
| underPromotion | Unterverwandlung |
| enPassant | En passant |
| endgame | Endspiel |
| middlegame | Mittelspiel |
| opening | Eröffnung |

## Schwierigkeit

Die Schwierigkeit wird nur aus dem Lichess-Rating abgeleitet:

```text
★        easy:        600-899
★★       medium:      900-1199
★★★      challenging: 1200-1599
★★★★     hard:        1600-1999
★★★★★    veryHard:    2000+
```

Typ und Schwierigkeit sind unabhängig: Ein `fork` kann leicht, mittel oder
sehr schwer sein. Im PDF steht das Lichess-Rating in Klammern hinter den
Sternen, standardmäßig gefolgt von der Anzahl der nötigen Lösungszüge.

Die Lösungsseiten zeigen zwei Lösungen pro Zeile. Nach jeweils drei Zeilen
trennt eine Linie die nächste Sechsergruppe passend zu einer Aufgabenseite.
Am Anfang jeder Lösung steht die Aufgabennummer (`1.`, `2.`, …) als blauer, unterstrichener
Link zum zugehörigen Lichess-Puzzle. Die URL wird nicht als Text angezeigt.

## Lichess-Rekonstruktion

Das `FEN` aus der CSV ist nicht direkt die Diagrammstellung. Für jedes Puzzle
wird zentral rekonstruiert:

1. `FEN` laden.
2. Den ersten UCI-Zug aus `Moves` ausführen.
3. Diese Stellung wird im PDF gezeigt.
4. Die restlichen Züge sind die Lösung.

Für `mateIn1` wird zusätzlich geprüft, dass genau ein legaler Mattzug existiert
und dass er dem ersten Lichess-Lösungszug entspricht. Für `mateIn2` und
`mateIn3` wird die komplette Lichess-Hauptvariante legal abgespielt und die
Endstellung als Matt validiert. Für andere Themes gilt das Lichess-Theme als
Ground Truth; die Zugfolge muss legal sein.

## Projektstruktur

```text
src/lichess_puzzle_pdf/
├── cli.py          # CLI und download-db
├── config.py       # Theme-, Typ- und Difficulty-Konfiguration
├── lichess.py      # CSV-Streaming, Parsing, Rekonstruktion, Validierung
├── notation.py     # deutsche SAN-Ausgabe
├── puzzle.py       # Domainmodelle
├── render.py       # PDF-, Brett- und SVG-Rendering
└── selection.py    # Filter, Reservoir Sampling, Verteilung
```

## Tests

```bash
python -m pytest
```

## Lizenzen

Der Python-Code steht unter MIT. Die Lichess Puzzle Database ist CC0. Hinweise
zu mitgelieferten Drittmaterialien stehen in
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
