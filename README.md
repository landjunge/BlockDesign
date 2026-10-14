# Block Design

Sprach-Layout-Editor: Du sprichst, die KI baut.

Kein klassischer Editor mit Werkzeugleiste — ein Gespräch, das direkt in sichtbare Ergebnisse mündet.

## Kernprinzip

- Alles ist ein **Rechteck** mit Attributen: Nummer, Farbe, Typ, Breite, Höhe, Position, Rundung, Umrandungsfarbe
- **Vorgabe-Prinzip**: erstes Element ist die Referenz, Shift-Markierung überträgt Größe, Schrift und Farbe auf die anderen
- **Typen** sind Etiketten, keine festen Kategorien — jedes Rechteck kann jeden Typ annehmen
- **Verzögerte Sichtbarkeit**: erst Rechtecke, am Ende das echte Layout mit CSS

## Oberfläche

- Arbeitsbereich: 1280 × 768, weiß
- Alles aus Linienrechtecken, farbige Module nur zur Orientierung
- Zwei Tasten: eine fixiert Höhe, eine Breite
- Grid mit leichter Magnetisierung
- Palette: 16 Grundfarben als gemeinsame Quelle

## Farbe

Block Design: **#42a5f5** (Blau, Memory-Farbe aus der gemeinsamen Palette)

## Status

Brainstorm abgeschlossen, Prototyp in Arbeit.

## Maßgebliche Konzeptquellen

Bearbeitungsquelle in ThreadDesk: `/Users/landjunge/.threaddesk/Zukunftsvisionen/Ideen/Block Designer/`.

- `BD Ziel Idee.md`: Vision und Ziel.
- `BD Brainstorm Destillat.md`: Bedienkonzept und erhaltene Entscheidungen.
- `BD Pre-Plan.md`: konkreter Bauplan BD-01 bis BD-08 und Abnahmekriterien.

Die Dateien unter [docs/concept](docs/concept) sind eine versionierte Sicherung dieser Quellen, kein separat zu pflegender Konzeptstand. Änderungen zuerst in ThreadDesk vornehmen und anschließend diese Sicherung samt SHA-256-Prüfsummen in `docs/concept/source.json` aktualisieren. Vor Implementierung alle drei Quellen lesen; die kurze README ersetzt sie nicht. Der alte Einzelpfad `BlockDesigner.md` ist veraltet.

Notion-Verweise: [Plan — Design Editor](https://app.notion.com/p/3eec08fa272a81389bf7f0f9ad7987f3) und [Brainstorm — Design Editor](https://app.notion.com/p/3eec08fa272a813680cfd78c72ce457a).

Repository-Zuordnung: Das vorhandene Repository heißt `landjunge/blockdesign`. Der Pre-Plan nennt als gewünschten Zielnamen `blockdesigner`; dieser Name wurde bei der Sicherung nicht angelegt und kein Repository umbenannt. Vor Bauarbeiten diese Abweichung berücksichtigen.
