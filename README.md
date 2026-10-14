# Block Designer · 0.1.0

Modulares Browser-Prototyp-Modul: Boxen mit wenigen Tasten steuern, Handlungen an die echte lokale KI beschreiben. MySpace links, Workspace mittig, KI-Space rechts. Die drei Bearbeitungsebenen liegen im Dokument.

```sh
cd /Users/landjunge/blockdesigner
./start.command
```

Öffnen: http://127.0.0.1:5190 . Das Terminal bleibt für den Server offen; Ctrl+C beendet ihn. Bei belegtem Port: `./start.command --port 5191`. Es gibt keinen Buildschritt und keine CDN-Abhängigkeit. Auf diesem Mac werden Python 3.12 und der vorhandene ThreadDesk-Modulhost verwendet. `./start.command --setup` stellt die lokale Modul-/Whiteboard-Bindung wieder her. Details: [Host- und Modulvertrag](docs/architecture.md).

| Taste / Handlung | Wirkung |
| --- | --- |
| B | 50 × 50 px mittig auf aktiver Ebene, weitere mit 5 px Versatz |
| 1 / 2 / 3 | Bearbeitbare Ebene wählen, andere sperren |
| Space | Nächsten Mittelpunkt greifen; erneut drücken setzt ab |
| Maus | Gegriffene Box relativ bewegen; virtueller Greifer zeigt die Mitte |
| D halten | Nur Höhe über vertikale Mausbewegung ändern |
| F halten | Nur Breite über horizontale Mausbewegung ändern |
| D + F | Keine Größenänderung |
| + / − | Proportional Faktor 1,1 / Kehrwert; mindestens 4 px |
| Klick / Shift-Klick | Auswählen / Auswahl ergänzen oder entfernen; erste Box ist Primary |
| T | Passende Größe, Gestaltung, Schrift und Beschriftung von Primary übernehmen |
| A halten | Vorläufiger Attributtest: Grundfarbe anklicken, Rad stellt Helligkeit fein ein; Loslassen übernimmt |
| Escape | Attributvorschau abbrechen, Greifer lösen oder Hilfedialog schließen |
| Monitor-Kopf ziehen / Pfeiltasten | Werte-Monitor verschieben |

Boxen zunächst absetzen, dann rechts den Auftrag beschreiben. Zulässige Modellaktionen ändern vorhandene ausgewählte Boxen oder das Raster. Gestaltungsvorschläge lassen sich ansehen, anwenden und in MySpace behalten. Die KI benutzt den bestehenden lokalen Whiteboard-/Ollama-Weg; der Browser führt ausschließlich validierte Datenaktionen aus. Veraltete Antworten bleiben sichtbar zurückgestellt. Bei Verbindungsabbruch erst „Status abrufen“, damit kein unklarer Auftrag blind wiederholt wird.

Das Dokument hat fest initialisierte 1000 × 640 Pixel. Zoom ändert nur die Darstellung. Raster zunächst 20 px mit 2 px Fangbereich; „Feiner ÷ 2“ halbiert beides. Orientierungsfarbe und Gestaltungsfarbe sind getrennt. Module bewegen ihre Kinder, skalieren sie im Prototyp jedoch nicht automatisch.

MySpace und das Dokument gelten für den laufenden Tab. Mikrofon, Datei-/Webseitenimport, Export/Speichern, Symbolbibliothek und MCP sind spätere Ausbaustufen. Die Browserumsetzung verwendet einen virtuellen Greifer; sie versetzt den Systemmauszeiger nicht.

```sh
npm test
/usr/local/bin/python3.12 tests/adapter_test.py
npm run browser
```

Die Browserabnahme benutzt den vorhandenen Google Chrome und die vorhandene Playwright-Installation von ThreadDesk. Die echten KI-Prüfungen benötigen laufendes Ollama und das in `ai-config.json` gewählte bereits installierte Modell. Negative Rückgabe-/Transportfixtures sind im Prüfskript ausdrücklich gekennzeichnet; sie zählen nicht als echter KI-Erfolg. [Abnahme und Grenzen](docs/acceptance/REPORT.md).

Maßgebliche Konzepte werden ausschließlich in `/Users/landjunge/.threaddesk/Zukunftsvisionen/Ideen/Block Designer/` gepflegt: `BD Ziel Idee.md`, `BD Brainstorm Destillat.md`, `BD Pre-Plan.md`. [docs/concept](docs/concept) ist deren automatische Sicherung, keine zweite Bearbeitungsquelle.

Dieser Workspace verwendet das bestehende Remote `landjunge/blockdesign`. `landjunge/blockdesigner` existierte beim Anschluss nicht; `landjunge/block-design` wurde erhalten. Der gewünschte lokale Workspace heißt weiterhin `blockdesigner`. Der frühere defekte Ein-Datei-Prototyp ist im Git-Verlauf erhalten.
