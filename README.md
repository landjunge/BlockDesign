# BlockDesigner · 0.2.0

Vorhandener modularer Browsereditor, erweitert um eine kompakte Oberfläche, lokale Projekte/Historie und Gespräche mit echter lokaler KI. MySpace links, Workspace mittig, KI-Space rechts; die drei Bearbeitungsebenen sind davon unabhängig.

```sh
cd /Users/landjunge/blockdesigner
./start.command
```

Browser: http://127.0.0.1:5190 . Terminal offen lassen; Ctrl+C beendet den Server. Bei belegtem Port `./start.command --port 5193`. Kein Buildschritt, keine CDN-Abhängigkeit. Vorhandener Python-3.12-Interpreter und ThreadDesk-Modulhost werden nach Vorabprüfung verwendet. `./start.command --setup` legt die eigene Modul-/Whiteboard-Bindung bei Bedarf an; bestehende Bindungen und deaktivierte Module bleiben erhalten. Repository: bestehendes `landjunge/blockdesign`, Branch `feat/compact-project-history`; kein Repository umbenannt oder gelöscht.

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

## Aktueller Einstieg und Quellstand / Current entry and source

Produktbasis ist der modulare Stand `135741679fc8c92fe15804d94aa47bed3a4c0636`
(0.2.0), nicht der historische defekte Ein-Datei-Prototyp `0bf8209` auf dem alten
main. Die Konsolidierung führt diese vorhandenen Module mit gezielten
Einstiegskorrekturen Richtung main; kein neuer Editor. Historische Belege vom
14.10. bleiben datiert. Die neuen begrenzten Prüfungen stehen unter
[CONSOLIDATION-20261018](docs/acceptance/CONSOLIDATION-20261018.md).

Für den vorhandenen Checkout im Projektordner:

```sh
./start.command --check  # rein lesende Vorabprüfung; Exit2 bei fehlender Voraussetzung/Bindung
./start.command         # vorhandenen lokalen Host starten
./start.command --port 5193  # alternativer freier Loopback-Port
```

`--help` und `--check` richten nichts ein, starten keine KI und verändern keine
Projektdaten. Der normale erste Start verwendet weiterhin den bestehenden eigenen
Modul-/Whiteboard-Setupweg. Bereits deaktivierte Module werden dabei und durch
`--setup` **nicht reaktiviert**. Vorhandene Bindungen werden nicht überschrieben;
bei anderem ausgewähltem Whiteboard zuerst Herkunft/Root prüfen. Eine verweigerte
Modulfreigabe ist keine Aufforderung, alle Rechte pauschal zu erweitern.

Fehlt eine Voraussetzung, vorhandenen Python3.12-Interpreter und kompatiblen
ThreadDesk-`src`-Ordner explizit wählen, dann erneut prüfen:

```sh
BD_PYTHON=/absolute/path/to/python3.12 \
BD_THREADDESK_SOURCE=/absolute/path/to/threaddesk/src ./start.command --check
```

Die Platzhalter sind durch tatsächlich vorhandene lokale Pfade zu ersetzen.
Kein automatisches Herunterladen, Paketmanager, sudo oder Kontozwang. Standard
ist `python3.12` bzw. `python3` im PATH; unterstützt geprüft wurde Python3.12 auf
diesem Mac. ThreadDesk muss seine ModuleManifest/Registry/Runtime-API enthalten.
Das ältere feste Nutzerpfad-Fallback für Python entfällt. Weitere Plattformen
werden durch die POSIX-Startdatei allein nicht als abgenommen behauptet.

| Operatorwert | Zweck / Meaning |
|---|---|
| `BD_PYTHON` | Vorhandener Interpreter; keine Installation |
| `BD_THREADDESK_SOURCE` | Kompatibles vorhandenes `src`; Standard `~/threaddesk-worktrees/ordinal-lock/src` |
| `BD_WHITEBOARD_ROOT` | Expliziter vorhandener/lokaler Hostworkspace; Standard `~/.threaddesk` |
| `BD_PROJECT_ROOT`, `BD_TASK_ROOT` | Eigene lokale Ablagen; isolierte Werte für Tests verwenden |

Der Prüfbericht meldet Voraussetzungen/Bindung, nicht jede mögliche KI- oder
Speicherfunktion. Das aktuelle lokale Modell darf offline sein; Boxen und lokale
Projekte bleiben bedienbar, die Oberfläche benennt die fehlende KI-Verbindung.
Keine neue Inferenz wurde für diesen Einstiegstest gestartet.

### English quick start and limits

From the current modular source checkout, run `./start.command --check`, then
`./start.command`. Keep that terminal open; Ctrl+C stops **that** local server.
`--port 5193` selects another free loopback port. No build, CDN or new framework.
Set `BD_PYTHON` and `BD_THREADDESK_SOURCE` to existing local paths if the read-only
preflight explains a missing prerequisite. `--check` exits2 until a valid binding
exists; ordinary first startup uses the existing own module setup. A previously
disabled module stays disabled, including explicit `--setup`; existing data and
bindings are not reset. No dependencies, accounts or elevated privileges are
installed automatically. Python3.12/macOS/actual Chrome were checked; no other
platform acceptance is implied.

Three spaces are navigation/work areas; three layers are editable document layers.
The editor document remains1000×640 document pixels; zoom affects presentation
only. A1440×900 reference editor window /1180×760 intended minimum is **not** a
webpage export viewport or a responsive-layout promise. Curved undo/redo buttons
retain the existing actions with German/English accessible names and keyboard
shortcuts. Help uses the same shortcut registry; Escape restores focus.

Projects, MySpace, conversation and monotone Undo/Redo/snapshots use existing local
format1 storage. History is on the same disk, not an external backup. An uncertain
AI task is read before any retry. Existing Whiteboard/Ollama and conservative
preview/apply rules remain; no KiraBridge/MCP, HTML import, DOM mapping or website
export is claimed. The [prepared source/reference boundary](docs/contracts/design-source-v1.md)
extends a future ThreadDesk `context.design`; it is not an implemented importer.
Technical evidence is separate from user acceptance and a distributed release.
