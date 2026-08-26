# Matt-in-1 PDF Generator

Ein kleiner Python-Generator für **deutsche, druckbare A4-Schachrätsel** für
Kinder. Er erzeugt standardmäßig 30 eindeutige „Matt in 1“-Stellungen und ein
Lösungsblatt.

## Eigenschaften

- 30 Aufgaben, standardmäßig 6 pro A4-Seite
- Weiß und Schwarz wechseln sich ab
- nur wenige Figuren pro Stellung (König + Dame/Turm gegen König)
- jede Stellung besitzt **genau einen** Mattzug
- tonersparendes Brett mit hellgrauen Feldern
- vektorbasierte Cburnett-Schachfiguren statt Unicode-Glyphen
- Figuren werden feldzentriert gezeichnet; kein Hintergrundrechteck kann in
  Nachbarfelder hineinragen
- separate Vektor-Rasterebene für saubere Brettlinien
- reproduzierbare Generierung über `--seed`
- keine externe Schachbibliothek nötig

## Installation

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
pip install -e .
```

## PDF erzeugen

```bash
matt-in-1-pdf
```

Erzeugt `matt_in_1.pdf`.

Eigener Dateiname:

```bash
matt-in-1-pdf -o meine_raetsel.pdf
```

## Layout anpassen

Die Parameter entsprechen der aktuellen druckoptimierten Version:

```bash
matt-in-1-pdf \
  --gray 0.92 \
  --piece-scale 0.86 \
  --piece-lift 0.5
```

- `--gray`: Grauwert der dunklen Felder; `1.0` ist weiß, `0.0` schwarz.
- `--piece-scale`: Größe der SVG-Figur relativ zur Feldgröße.
- `--piece-lift`: optische Verschiebung nach oben in PDF-Punkten.
- `--seed`: erzeugt bei gleichem Wert wieder dieselben Aufgaben.
- `--count`: Anzahl der Aufgaben.

Beispiel mit 50 Aufgaben:

```bash
matt-in-1-pdf --count 50 --seed 12345 -o matt_50.pdf
```

## Tests

```bash
pip install pytest
pytest
```

Die Tests prüfen unter anderem, dass jede generierte Stellung genau einen
Mattzug besitzt.

## Projektstruktur

```text
src/matt_in_1_pdf/
├── assets/cburnett/   # SVG-Figuren
├── chess.py           # Erzeugung + kleine K/Q/R-vs-K-Schachlogik
├── render.py          # A4-/Brett-/SVG-Rendering
└── cli.py             # Kommandozeile
```

## GitHub

Nach dem Entpacken zum Beispiel:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin git@github.com:DEIN-USER/matt-in-1-pdf-generator.git
git push -u origin main
```

## Lizenzen

Der Python-Code steht unter MIT. Die mitgelieferten Cburnett-Figuren sind
separates Drittmaterial; Details stehen in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
