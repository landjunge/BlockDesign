# BlockDesigner · 0.2.0

Vorhandener modularer Browsereditor, erweitert um eine kompakte Oberfläche, lokale Projekte/Historie und Gespräche mit echter lokaler KI. MySpace links, Workspace mittig, KI-Space rechts; die drei Bearbeitungsebenen sind davon unabhängig.

```sh
cd /Users/landjunge/blockdesigner
./start.command
```

Browser: http://127.0.0.1:5190 . Terminal offen lassen; Ctrl+C beendet den Server. Bei belegtem Port `./start.command --port 5193`. Kein Buildschritt, keine CDN-Abhängigkeit. Vorhandener Python-3.12-Interpreter und ThreadDesk-Modulhost werden nach Vorabprüfung verwendet. `./start.command --setup` legt die eigene Modul-/Whiteboard-Bindung bei Bedarf an; bestehende Bindungen und deaktivierte Module bleiben erhalten. Repository: bestehendes `landjunge/blockdesign`, konsolidierter `main`; die historische Produktbasis `feat/compact-project-history` bleibt erhalten. Kein Repository umbenannt oder gelöscht.

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

Die lokale Historie schützt **nicht vor Ausfall desselben Datenträgers**. Der normale Editor speichert lokal und lädt keine Projektdaten nach GitHub. Der optionale Codeauftrag unten übergibt nur ausdrücklich beauftragten Kontext an einen fest eingerichteten Backend-Zugang; dessen Agenten-/Providergrenzen gelten zusätzlich. Externe Backups, Mikrofon, Webseitenexport und Symbolbibliothek bleiben offen. Sprachverständnis bleibt fehlbar; Vorschau und Rückfragen erleichtern die Kontrolle. Technische Abnahme ersetzt die Nutzerbewertung nicht.

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

Der vorhandene Benutzercheckout wurde am 19.10.2026 auf den integrierten Mainstand
gebracht. Sein rein lesender Startcheck bestätigt die erhaltene eigene Bindung;
[Beleg, Bedienung und Grenzen](docs/acceptance/USER-START-20261019.md).

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
preview/apply rules remain. The reference import below stores an inert PNG and
optionally indexes static HTML IDs. It does not run an HTML page or prove its runtime
DOM/functionality. The optional coding workflow below is separate; no website export is claimed.
The [source/reference boundary](docs/contracts/design-source-v1.md) describes this
local design; the coding adapter attaches its immutable descriptor through existing ThreadDesk files/notes.
Technical evidence is separate from user acceptance and a distributed release.

## Codeauftrag und Rückvorschau / Coding task and returned preview

MySpace → **Codeauftrag · Übergabe und Rückvorschau**: den Änderungswunsch eingeben
und **Stand vorbereiten**. Das liest den tatsächlich gespeicherten Projekt-/Snapshot-
und Elementstand; es startet keinen Agenten. Ein eingerichteter fester Backend-
Fachclient kann danach **An ThreadDesk übergeben · kein Start** ausführen. Erst
**Diesen Codeauftrag starten** verwendet den vorhandenen KiraBridge-M2-Lauf.
Rückfragen, Status und Entscheidung bleiben getrennte ausdrückliche Schritte.
Nach Unterbrechung vorhandenen Lauf abfragen; keine neue Kennung als Wiederholung.

Der optionale [Betreiber-Profilladeweg](docs/WORKFLOW-PROFILE.md) ist jetzt im
bestehenden Start integriert: `./start.command --check --workflow-profile /absolute/private/workflow.json`
prüft lokal und rein lesend; derselbe Aufruf ohne `--check` startet den vorhandenen
Host mit festem Client/Projektprofil. Kein Agent startet dadurch. `BD_WORKFLOW_PROFILE`
ist die alternative lokale Auswahl; Datei/Bridge-Konfiguration bleiben privat,
Browserdaten können weder URLs noch Rechte festlegen. Profil, Bridge-Konfiguration
und referenzierte Zugangsdaten/TLS-Dateien müssen außerhalb des gesamten Editorprojekts
liegen; auch `0600` macht sie nicht zu öffentlichen Assets. Ohne explizites Profil bleibt
das bisherige Verhalten erhalten. Fehlendes kompatibles SDK blockiert verständlich,
keine Installation. [DE/EN-Vorlage, Grenzen und Rückweg](docs/WORKFLOW-PROFILE.md).

The existing startup now accepts an optional private operator profile through
`--workflow-profile` or `BD_WORKFLOW_PROFILE`. Run `--check` first: local prerequisites
only, no network, database, model or server launch. Without `--check`, the existing
host receives that fixed client/profile; explicit issue/start are still separate.
No browser URLs/tokens or permission expansion. Configuration/credential/TLS paths
must stay outside the entire editor project; private `0600` files are not public assets.
Without a profile, the default
remains unavailable. See the [DE/EN configuration example](docs/WORKFLOW-PROFILE.md).

Der Standardstart richtet diesen Zugang **nicht** ein: Ohne Backend-Projektprofil
und optionales KiraBridge-SDK meldet das Panel die fehlende Voraussetzung und hält
Übergabe/Start gesperrt. Browsertexte können keine Rechte, Peeradressen, Quellpfade,
Sitzungen oder Belege festlegen. Es gibt keinen zweiten Agentenstarter/Taskdienst.
Die vorhandene lokale Whiteboard-/Ollama-Boxbearbeitung bleibt eigenständig.

Gelieferte PNG und Codebezug erscheinen **ungeprüft**, neben dem Zielentwurf.
Aktueller Projekt-/Snapshot-/Quellstand und tatsächliche Issued-/Run-/Returnbelege
müssen passen. Ein späterer oder fremder Reply ändert den Entwurf nicht.
Übernehmen/Nacharbeit/Verwerfen dokumentiert eine begründete Entscheidung über
diese Lieferung; es wendet keine neue Referenz oder Codeänderung automatisch an
und startet keine Nacharbeit. Quellcommit, Bild-/HTML-Beziehung und Funktion bleiben
ohne gesonderten Nachweis unbekannt. Ein Betreiberentscheid ist kein Funktionstest.

Vor dem ersten Versand wird das kanonische Betreiberprofil privat gepinnt:
Quell-CWD/Verzeichnisidentität, feste Dateinamen und beobachtbare lokale Backend-/
Principalreferenzen. Jede Folgeaktion einschließlich erster Rückvorschau/Entscheidung
verweigert geänderte Profile. Alte ungeklärte Starts sperren weiterhin ihr ursprünglich
gespeichertes Quellprojekt, auch nach Entfernen/Umordnen der aktuellen Profile.
Fehlende historische Bindungen werden nicht aus heutiger Konfiguration geraten.

In **MySpace → Coding task**, prepare the exact saved version first, issue it
through ThreadDesk separately, then explicitly start the existing Bridge workflow.
Default startup has no configured backend identity/project profile and cannot
dispatch coding work. The browser never receives tokens or controls a peer/path.
Refresh reads the existing owned run; answering resumes its exact recorded session.
Returned code/PNG is unverified and cannot replace a newer design. A reasoned
decision is separate from delivery, functional verification and overall acceptance;
rework does not start a new agent. Existing local box editing is unchanged.
The original canonical operator/source profile is persisted before dispatch and
checked on every follow-up, including the first returned preview. Drift fails closed.
Unknown prior starts retain their original source barrier even after configured
profiles are removed or remapped. No credential or raw profile path is exposed to
the browser; configured peer references are not remote attestation.

The source adapter was tested using real isolated MCP/ThreadDesk and an explicitly
synthetic own CLI fixture, not a real model or installed-user runtime. A harmless
HTML demo was actually edited and independently rendered to the exact delivered
PNG hash. [Contract, operator prerequisites and DE/EN acceptance](docs/acceptance/HANDOFF-20261018.md).

## Referenz und Originalbezug / Reference and original element

MySpace → **Referenz importieren**: PNG-Vorschau auswählen, optional die zugehörige
UTF-8-HTML-Datei für genaue Original-IDs. Referenzviewport in CSS-Pixeln ausdrücklich
angeben und dann importieren; PNG-Pixel allein belegen diesen nicht (HiDPI).
Der vorhandene Speicher
sichert zuerst, danach erscheint der Hintergrund unter allen drei bearbeitbaren
Ebenen. Originaldateien werden weder geändert noch ausgeführt. Kein Agent startet.
PNG und HTML erhalten getrennte SHA256; Quellcommit bleibt sichtbar unbekannt.
Der Zusammenhang zwischen selbst gewähltem PNG und HTML ist von dir zu prüfen.
Das Bild wird proportional ab0/0 ins Dokument eingepasst; Referenzviewport und
Dokumentzoom bleiben getrennt und gespeichert. Kein Verzerren oder Mobilstapeln.

Box auswählen → **Auswahl** → **Änderung am Original**: Verschieben/Ersetzen/Neu.
Eine genaue statische HTML-ID wählen und **Bezug sichern**. Gleich aussehende
Buttons mit verschiedenen IDs bleiben verschieden; doppelte/fehlende IDs ergeben
eine sichtbare Rückfrage. Nach neuer Quelle werden bisherige Bezüge veraltet,
bis sie ausdrücklich neu zugeordnet sind. „Neu“ behauptet kein Originalelement.
Dies ist ein Entwurf, noch keine Änderung oder Funktionsprüfung des Originalcodes.

MySpace → **Import reference**: select a PNG and optionally its UTF-8 HTML source,
and declare its reference viewport in CSS pixels, then import. PNG pixel dimensions
alone do not prove that viewport (HiDPI). The existing project store saves before displaying the inert background.
Choose a box → **Selection** → **Original change** → Move/Replace/Add new and an
exact static source ID → **Save reference**. Missing/duplicate IDs require an explicit
answer; a changed source leaves old mappings visibly stale. Original files never run
or change. Separate image/source hashes and an unknown source commit remain honest;
matching image and HTML is the user's responsibility. This is a design, not a coding
task, runtime DOM proof or functional acceptance.

Limits: PNG RGB/RGBA8 without interlace/animation, up to1MiB and4Megapixels;
HTML up to256KiB; at most256 indexed ID occurrences/references. Scripts/resources
are not loaded; template/noscript IDs remain unresolved. Functionality, dynamically
created elements and automatic HTML rendering are outside this local import.
Old documents remain readable; Undo/Redo/History preserve reference and mapping.
[Checks and limits / Prüfung](docs/acceptance/IMPORT-20261018.md).

### Legacy execution barrier / Historische Ausführungssperre

Ungeklärte historische Task-/Run-/Return-/Antwortbelege behalten ihre lokale
Startsperre auch ohne alten Startindex; fehlende Quellbelege werden nicht geraten.
Reines Prepare/Issue behauptet weiterhin keine Ausführung. Unknown historical
execution evidence retains its original local overlap barrier; prepare/issue alone
still makes no execution claim. [Narrow follow-up evidence DE/EN](docs/acceptance/LEGACY-BARRIER-20261019.md).
