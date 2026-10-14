# BlockDesigner · 0.2.0

Vorhandener modularer Browsereditor, erweitert um eine kompakte Oberfläche, lokale Projekte/Historie und Gespräche mit echter lokaler KI. MySpace links, Workspace mittig, KI-Space rechts; die drei Bearbeitungsebenen sind davon unabhängig.

```sh
cd /Users/landjunge/blockdesigner
./start.command
```

Browser: http://127.0.0.1:5190 . Terminal offen lassen; Ctrl+C beendet den Server. Bei belegtem Port `./start.command --port 5193`. Kein Buildschritt, keine CDN-Abhängigkeit. Vorhandener Python-3.12-Interpreter und ThreadDesk-Modulhost werden verwendet. `./start.command --setup` aktualisiert die eigene Modul-/Whiteboard-Bindung. Repository: bestehendes `landjunge/blockdesign`, Branch `feat/compact-project-history`; kein Repository umbenannt oder gelöscht.

H öffnet die vollständige Hilfe aus derselben Shortcut-Definition wie die Eingabesteuerung. Escape schließt und gibt den Fokus zurück. Während Texteingaben bleiben Editorkürzel gesperrt.

| Taste / Handlung | Wirkung |
|---|---|
| B | 50 × 50 px mittig, weitere Boxen +5 px |
| 1 / 2 / 3 | Bearbeitbare Ebene wählen |
| Space | Mehrfachauswahl gemeinsam greifen/absetzen; sonst nächster Mittelpunkt |
| D / F halten | Mit Maus ausschließlich Höhe / Breite ändern; D+F ändert keine Größe |
| + / − | Proportional × 1,1 / ÷ 1,1; mindestens 4 px |
| Klick / Shift-Klick / Enter | Auswahl / geordnet ergänzen oder entfernen / fokussierte Box auswählen |
| T | Passende Eigenschaften einschließlich Text von Primary übernehmen |
| A halten | Farbe wählen, Rad: Helligkeit; Loslassen übernimmt, Escape bricht ab |
| ⌘/Ctrl+Z · ⌘/Ctrl+Shift+Z / ⌘/Ctrl+Y | Rückgängig / Wiederholen |
| H / Escape | Hilfe öffnen / schließen oder Attributgeste abbrechen |
| Monitor-Kopf ziehen / Pfeile | Monitor über der gesamten App verschieben |

Die Kopfleiste bündelt Ebene, Ansicht, Raster, Zoom, DE/EN, Hilfe und Sidebar-Schalter. Beide Sidebars lassen sich unabhängig ausblenden und am Rand verbreitern; der Workspace erhält die freie Fläche. Ihre Breiten/Sichtbarkeit und die Monitorposition werden lokal im Browser gemerkt. Dokumentwerte bleiben bei Zoom unverändert. Raster startet mit 20/2 Dokumentpixeln; feiner/gröber halbiert/verdoppelt Abstand und Fangbereich. Grenzen der Schalter sind sichtbar. Dokument 1000 × 640 px; Eltern bewegen Kinder einmal mit, keine automatische Kindskalierung. Der Browser benutzt einen virtuellen Greifer.

Dokument, MySpace, Gespräch und Undo/Redo liegen dauerhaft unter `~/Library/Application Support/BlockDesigner/`. Automatische Sicherung nach kurzer Ruhephase; der Header zeigt ausstehende oder fehlgeschlagene Sicherung. Vor jedem Chatversand entsteht ein dauerhafter Vorher-Snapshot. Eine KI-Änderung wird erst nach erfolgreicher Sicherung ihres geprüften Ergebnisstands sichtbar übernommen. Größere Änderungen erhalten Vorschau, Übernehmen und Verwerfen. Direkte kleine Änderung: genau eine kinderlose Zielbox, eine kurze Beschriftung oder eine einzelne Breiten-/Höhenänderung bis 10 Prozent. Sämtliche Aktionen einer Antwort bilden einen Undo-Schritt.

MySpace → Historie zeigt frühere Stände. Ansehen verändert nichts; Wiederherstellen sichert zuerst den aktuellen Stand und erzeugt einen neuen mit Bezug zum gewählten Snapshot. Neuere Stände bleiben erhalten. Alte Aufträge werden dabei nicht erneut gestartet. Projekte lassen sich links auswählen, benennen und neu anlegen. Nach Serverneustart wird das zuletzt gewählte Projekt wieder geöffnet.

KI-Aufträge verwenden den bestehenden Whiteboard-/Ollama-Weg und das bereits installierte lokale Modell aus `ai-config.json`. Folgeaufträge enthalten relevante vorherige Aufträge/Ergebnisse und die aktuelle Auswahl; ein Auswahlwechsel wird sichtbar benannt. Rückfragen können beantwortet werden. Ohne Auswahl fragt zunächst BlockDesigner nach dem gewünschten Bezug; das ist klar von echten Modellantworten getrennt. Bei Verbindungsabbruch zunächst „Status abrufen“; kein automatischer Modellneustart. Ungültige/duplizierte/veraltete Rückgaben und fremde Ziele werden nicht angewendet. Kein Modellcode wird ausgeführt.

Die lokale Historie schützt **nicht vor Ausfall desselben Datenträgers**. Projektdaten werden nicht nach GitHub oder an externe Dienste übertragen. Externe Backups, Mikrofon, Import/Export, Symbolbibliothek und MCP sind nicht Bestandteil dieses Umbaus. Sprachverständnis bleibt fehlbar; Vorschau und Rückfragen erleichtern die Kontrolle. Technische Abnahme ersetzt die Nutzerbewertung nicht.

```sh
npm test
/usr/local/bin/python3.12 tests/adapter_test.py
/usr/local/bin/python3.12 tests/project_store_test.py
/usr/local/bin/python3.12 tests/host_contract_test.py
# Vollständige neue Chrome-Prüfung mit eigenem lokalen Testserver/Datenspeicher:
npm run browser:upgrade
# Vorhandene Regression: isolierter Testhost, dann in anderem Terminal:
BD_PROJECT_ROOT="$PWD/.runtime/acceptance-projects" ./start.command --port 5191
npm run browser
BD_TEST_URL=http://127.0.0.1:5191 npm run browser:zoom
```

Chrome und Playwright stammen aus der vorhandenen ThreadDesk-Installation. Echte KI-Tests benötigen laufendes Ollama. Negative Rückgabe-/Transportfixtures sind ausdrücklich markiert; Speicherfehler werden zusätzlich durch tatsächlich verweigerte Dateischreibrechte geprüft. Neue Browserbelege bleiben unter `.runtime/` lokal und Git-ignoriert. [Modul-/Speichervertrag](docs/architecture.md), [Abnahme](docs/acceptance/REPORT.md).

Maßgebliche Konzepte ausschließlich im bestehenden Ordner `/Users/landjunge/.threaddesk/Zukunftsvisionen/Ideen/Block Designer/`. `docs/concept` wird automatisch daraus gesichert und nicht unabhängig gepflegt.
