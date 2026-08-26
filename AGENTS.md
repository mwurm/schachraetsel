# AGENTS.md

## Projektziel

Dieses Repository erzeugt druckbare deutsche A4-PDFs mit kindgerechten
**„Matt in 1“**-Schachrätseln.

Der Generator soll bewusst klein und nachvollziehbar bleiben. Die Rätsel
bestehen aktuell aus **König + Dame oder Turm gegen König**. Für jede erzeugte
Stellung muss es **genau einen legalen Mattzug** geben.

Wichtige Qualitätsziele:

- reproduzierbare Rätsel über einen festen Seed
- eindeutiger Mattzug pro Aufgabe
- sauberes A4-Drucklayout
- tonersparende Bretter
- vektorbasierte Schachfiguren
- keine grafischen Artefakte an Feldgrenzen
- einfache Installation und Nutzung als CLI

## Technischer Überblick

- Python >= 3.11
- `reportlab` für PDF-Erzeugung
- `svglib` für SVG-Schachfiguren
- `pytest` für Tests
- `src`-Layout mit Paket `matt_in_1_pdf`

Wichtige Dateien:

```text
src/matt_in_1_pdf/
├── __main__.py
├── cli.py              # CLI und Parameterprüfung
├── chess.py            # Schachlogik und Rätselgenerierung
├── render.py           # PDF-, Brett- und SVG-Rendering
└── assets/cburnett/    # SVG-Figuren

tests/
├── test_chess.py
└── test_render.py
```

## Architektur und Verantwortlichkeiten

### `chess.py`

Enthält die komplette fachliche Logik für die aktuell unterstützten
Stellungstypen.

Dazu gehören insbesondere:

- Repräsentation von Feldern und Positionen
- Angriffserkennung
- legale Züge
- Mattprüfung
- Ermittlung aller Matt-in-1-Züge
- zufällige, reproduzierbare Generierung von Rätseln

Die zentrale Invariante lautet:

> Jede ausgegebene Aufgabe besitzt genau einen Mattzug.

Änderungen an der Schachlogik müssen deshalb immer durch Tests abgesichert
werden.

### `render.py`

Enthält ausschließlich Darstellung und PDF-Erzeugung.

Besonders wichtig für Änderungen am Brett:

1. Felder werden zuerst einzeln gefüllt.
2. Das Raster wird als eigene Vektorebene gezeichnet.
3. SVG-Figuren werden ohne Hintergrundrechteck direkt in das Zielfeld gesetzt.
4. Figuren müssen innerhalb ihres Feldes bleiben und optisch sauber zentriert
   sein.

Frühere Ansätze, bei denen Unicode-Figuren nachträglich überdeckt und durch
SVGs ersetzt wurden, führten zu beschädigten Rasterlinien und überstehenden
weißen bzw. grauen Flächen. Diesen Ansatz **nicht wieder einführen**.

Aktuelle Standardwerte:

- `gray = 0.92`
- `piece_scale = 0.86`
- `piece_lift = 0.5`

`piece_lift` ist in PDF-Punkten angegeben und verschiebt die Figur optisch nach
oben.

### `cli.py`

CLI-Einstiegspunkt. Der installierte Befehl lautet:

```bash
matt-in-1-pdf
```

Wichtige Optionen:

```text
-o / --output
-n / --count
--seed
--gray
--piece-scale
--piece-lift
```

CLI-Optionen sollen möglichst rückwärtskompatibel bleiben.

## Entwicklung

Virtuelle Umgebung anlegen und Projekt installieren:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install pytest
```

Unter Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
pip install pytest
```

## Tests

Vor Abschluss einer Änderung immer ausführen:

```bash
python -m pytest
```

Die bestehenden Tests prüfen unter anderem:

- 30 Aufgaben können erzeugt werden
- jede Stellung besitzt genau einen Mattzug
- Weiß und Schwarz wechseln sich ab
- PDF-Erzeugung funktioniert grundsätzlich

Bei Änderungen an Schachlogik oder Generator zusätzliche Tests ergänzen.

Bei Änderungen am Rendering zusätzlich ein Beispiel-PDF erzeugen:

```bash
matt-in-1-pdf --seed 20260826 -o /tmp/matt_in_1_preview.pdf
```

Rendering-Änderungen nach Möglichkeit auch visuell prüfen. Besonders auf
folgende Fehler achten:

- Figur liegt zu hoch oder zu tief
- Figur berührt oder überschreibt Rasterlinien
- Hintergrund einer Figur überdeckt Nachbarfelder
- Grauwerte wechseln an Figurenfeldern
- Koordinaten passen nicht zur Brettorientierung
- schwarzer Spieler wird nicht korrekt gespiegelt
- Text oder Lösungszeilen laufen aus dem Seitenbereich

## Coding-Konventionen

- bestehende Python-Struktur und Typannotationen beibehalten
- kleine, klar benannte Funktionen bevorzugen
- keine unnötigen Abhängigkeiten hinzufügen
- Fachlogik nicht in `render.py` duplizieren
- Rendering-Code nicht in `chess.py` verschieben
- Zufall ausschließlich über kontrollierte Seeds verwenden, wenn
  Reproduzierbarkeit relevant ist
- bestehende öffentliche Funktionen nur mit gutem Grund inkompatibel ändern

## Regeln für Schachänderungen

Der aktuelle Generator implementiert bewusst nur einen kleinen Teil des
Schachspiels. Nicht stillschweigend davon ausgehen, dass er bereits vollständige
FIDE-Zuglogik besitzt.

Wenn neue Figuren oder Stellungstypen ergänzt werden, müssen mindestens diese
Punkte korrekt behandelt werden:

- legale Zugbewegung
- Blockaden bei Langschrittfiguren
- Könige dürfen nicht benachbart stehen
- eigener König darf nicht im Schach stehen
- gegnerischer König darf keine angegriffenen Fluchtfelder haben
- gegnerischer König darf eine ungedeckte angreifende Figur gegebenenfalls
  schlagen
- Matt muss echtes Matt sein, nicht nur Schach
- für Rätsel weiterhin genau ein Matt-in-1-Zug

Für eine spätere deutliche Erweiterung auf vollständiges Schach darf
`python-chess` erwogen werden. Eine solche Migration sollte aber bewusst und
mit Tests erfolgen und nicht nebenbei eingeführt werden.

## PDF- und Layout-Regeln

Das Standardformat bleibt A4.

Das aktuelle Layout verwendet:

- 6 Aufgaben pro Seite
- 2 Spalten × 3 Reihen
- anschließend eine Lösungsseite
- deutsche Bezeichnungen (`D` für Dame, `T` für Turm)

Bei Layoutänderungen darauf achten, dass die Standardausgabe mit 30 Aufgaben
weiterhin sinnvoll paginiert wird.

Das Brett soll tonersparend bleiben. Dunkle Felder sind deshalb standardmäßig
nur hellgrau statt schwarz.

## SVG-Schachfiguren und Lizenzen

Die mitgelieferten Cburnett-SVGs sind Drittmaterial. Lizenz- und
Attributionshinweise stehen in:

```text
THIRD_PARTY_NOTICES.md
```

Diese Hinweise bei Änderungen an Assets oder Distribution nicht entfernen.

Der Python-Code des Projekts steht unter der Lizenz in `LICENSE`.

## Erwartetes Vorgehen für Codex

Bei einer Aufgabe in diesem Repository:

1. relevante Dateien lesen, bevor Code geändert wird
2. Ursache des Problems identifizieren statt nur Symptome zu übermalen
3. Änderung möglichst klein und lokal halten
4. passende Tests ergänzen oder anpassen
5. `python -m pytest` ausführen
6. bei Rendering-Änderungen zusätzlich ein Beispiel-PDF erzeugen
7. geänderte Dateien und Testergebnis knapp zusammenfassen

Keine generierten PDFs, virtuellen Umgebungen oder Build-Artefakte committen,
sofern sie nicht ausdrücklich als Beispielartefakt im Repository vorgesehen
sind.

## Definition of Done

Eine Änderung ist fertig, wenn:

- die gewünschte Funktion umgesetzt ist
- bestehende Tests weiterhin erfolgreich sind
- neue relevante Fälle getestet sind
- bei Rendering-Änderungen das PDF visuell plausibel ist
- keine Feldhintergründe oder Rasterlinien durch Figuren beschädigt werden
- README/AGENTS aktualisiert wurden, falls Bedienung oder Architektur sich
  geändert haben
