# Modul- und Startvertrag · BlockDesigner 0.2.0

Der maßgebliche Plan bleibt `BD Pre-Plan.md` im vorhandenen Konzeptordner. Dies dokumentiert die implementierten Schnittstellen. Die Architektur von 0.1 bleibt im Git-Verlauf erhalten.

`./start.command` startet ES-Module ohne Framework/Buildschritt über einen Loopback-Host auf 127.0.0.1:5190. Python 3.12 und der vorhandene ThreadDesk-Checkout `/Users/landjunge/threaddesk-worktrees/ordinal-lock/src` (`3b6f3fa`) sind Laufzeitvoraussetzungen. `--setup` aktualisiert die eigene Modulbindung. `module.json` behält die stabile Modul-ID `block-designer`; eigene Rechte: Whiteboard lesen/anhängen, eigener Projektspeicher über `projects:write`, lokaler Ollama-Connector. Keine fremden Datenbankrechte, kein zweiter Orchestrator. Whiteboard-Thread und historische technische IDs bleiben erhalten.

| Modul | Zuständigkeit / Erweiterungspunkt |
|---|---|
| `core/model.js`, `geometry.js`, `actions.js` | Boxformat/Aktionsformat 1, gemeinsame Validatoren, reine Geometrie, atomarer Reducer. Mehrfachbewegung vereinigt Familien nach IDs und begrenzt einen gemeinsamen Versatz. |
| `core/store.js` | Ein maßgeblicher Zustand: `getState`, `subscribe`, `dispatch`. `begin/end` fassen Gesten zusammen; Undo/Redo erhöhen die Revision monoton. `candidate/prepare` validiert ohne Anwendung und berechnet denselben Undo-Schritt wie die Übernahme; `lock/commitCandidate` ermöglichen dauerhafte KI-Übernahme ohne Zwischenmutation. |
| `input/shortcuts.js`, `controller.js` | Eine Shortcut-Definition für Matching und Hilfe. Fokus-/Modalitätswächter, virtuelle Greifposition, D/F und A. Neue Kürzel hier ergänzen, Hilfe und Ablaufprüfung mitführen. |
| `shell/header.js`, `help.js`, `sidebars.js` | Kompakter Header, Dialogfokus, unabhängige Sidebars/Breiten. Versionierte lokale Layoutpräferenzen getrennt von Projektdaten. |
| `workspace/render.js`, `layers-grid.js`, `monitor.js` | Ein Zustand für Struktur/Gestaltung, geprüfte KI-Vorschau nur als Renderdaten. Zoom ist Darstellung. Rastergrenzen deaktivieren unmögliche Schritte. Monitor in Fensterkoordinaten, bei Resize erreichbar begrenzt. |
| `panels/selection.js`, `proposal.js`, `myspace.js` | Vorhandene Attribute/T/Eltern/Palette erhalten. Vorschläge/Behalten verwenden dieselbe dauerhafte Übernahmeschnittstelle wie KI-Aktionen. |
| `panels/ai-space.js`, `bridge/whiteboard.js` | Projektgespräch, Status, Rückfragen, Vorschau/Übernehmen/Verwerfen. Paket bindet aktuelle Auswahl/Revision und dauerhaften Snapshot; ältere Ziele bleiben Kontext. |
| `bridge/projects.js` | `init/open/create/rename`, `snapshot/flush`, `apply`, `history/inspect/restore`; alleinige Browser-Speicherschnittstelle. Schreibwarteschlange und sichtbarer Fehlerzustand. |
| `scripts/project_store.py` | Privater lokaler Projekt-/Snapshotstore, CAS-Verweise, fsync/replace, Prozess-/Threadserialisierung, Head-Konflikte und Recovery. Wiederverwendet `ContentAddressedArtifacts`; Modulkontext-Record speichert nur die eigene Anbindung. |
| `scripts/host.py`, `ai_adapter.py`, `server.py` | Vorhandener Modulhost, überprüfte Whiteboardzustellung/-Rückgabe, lokales Modell und unabhängige JSON-Validierung. HTTP schützt Host/Origin und liefert nur Produktassets aus. |
| `app.js` | Einmaliges Öffnen/Montieren dieser Module; keine zweite Dokumentlogik. |

Fachliche Module sind Elternboxen, keine Softwaremodule. Kinder gehören zur gleichen Ebene, Zyklen sind gesperrt. Elternbewegung nimmt jedes Kind einmal mit; Skalierung verändert Kinder nicht. T erhält Position/Identität/Zuordnung. Orientierungs- und Gestaltungsfarbe bleiben getrennt. Gemeinsame Palette/Systemschriften und unveränderte `networkpunkt.css` (`b0b6815`, SHA256 `98371bd9edc96fb940a0e0de34933740fed1062b510aa516498fcb53e112591e`) bleiben die Designbasis; kompakte Anordnung erhält 40 px Bedienhöhe und gemeinsame Tokens.

## Dauerhafte Daten und Wiederanlauf

Standard ausschließlich lokal: `~/Library/Application Support/BlockDesigner/`. `.runtime/` enthält weiterhin ignorierte Hostbindung und Aufgabenjournal; keine Projektinhalte werden in Git gespeichert. `BD_PROJECT_ROOT` / `BD_TASK_ROOT` wählen ausdrücklich isolierte Testablagen, keine Vorgaben aus Auftrag oder Modelltext. `BD_THREADDESK_SOURCE` und `BD_WHITEBOARD_ROOT` wählen nur explizite Hostbindungen.

HTTP: GET `/api/projects`; GET `/api/projects/{id}`; POST dorthin mit `body`, `meta`, erwartetem `base`-Head; GET `/history` und `/snapshots/{id}`. Bodyformat 1 enthält Zustand (Boxformat 1), Auswahl, MySpace, Gespräch und Undo/Redo. Unbekannte künftige Formate werden sichtbar abgelehnt; spätere Änderungen benötigen explizite Migrationen und Kompatibilitätsprüfungen. Frühere Format-1-Stände mit eingebetteten Boxen/Undo-Frames bleiben lesbar.

`projects/{uuid}/commits/{sequence}-{snapshot_uuid}.json` ist ein unveränderlicher Commit mit Format, Projekt-/Snapshotkennung, Revision, Auswahl, Zeitpunkt, Parent, Art, Auftrags-/Gesprächs-/Wiederherstellungsbezug und Inhaltsverweisen. Seine kanonische Darstellung hat eine SHA256-Prüfsumme. Dokumentmetadaten, Boxen, MySpace, Gespräch, UI-Einstellungen sowie Undo-Frames werden über `artifacts/{sha256}` wiederverwendet. Frames referenzieren Box-/MySpace-Inhalte ebenfalls, statt sie mehrfach einzubetten. Einfache JSON-Dateien, keine neue Datenbank/Pluginarchitektur.

Schreibfolge: Daten prüfen → Inhalte stagen/fsync → vorhandenen Artefaktpublisher nutzen → Verzeichnissynchronisierung → Commit in temporärer Datei schreiben/fsync → atomar ersetzen → Verzeichnissynchronisierung. Commitpublikation ist der Abschluss; HEAD ist ein reparierbarer Hinweis. Ein gemeinsamer lokaler Filelock serialisiert auch mehrere Hostprozesse, erwarteter Head verhindert blindes Überschreiben durch konkurrierende Tabs. Unfertige temporäre Dateien werden ignoriert. Beschädigte Commits/Inhalte bleiben erhalten; Öffnen sucht den letzten lesbaren Stand und meldet die Beschädigung. Kein automatisches Bereinigen alter Stände oder unreferenzierter Inhalte.

Vor **jedem** Chatversand: dauerhafter `preRequest`-Snapshot mit Task, Auftrag, Revision, Auswahl und vorherigem Taskbezug; erst danach Whiteboardversand. Server prüft den vollständigen semantischen Snapshot und die Vorgeschichte gegen diesen lokalen Stand. Fragen, Vorschauen, Verwerfen und Fehler bekommen zugeordnete Stände. Anwendung rechnet die komplette Antwort auf einem Kandidaten durch, sperrt kurz semantische Eingaben, sichert den Ergebnisstand dauerhaft und übernimmt erst dann. Speicherfehler lassen Boxen unverändert und bieten „Erneut sichern“. Normale Bedienänderungen werden nach 500 ms Ruhe automatisch gesichert; Header zeigt den ungesicherten Zeitraum. Bei ungesicherten Änderungen warnt normales Verlassen des Tabs; bei abruptem Browser-/Stromausfall können noch ungesicherte Eingaben fehlen.

Historie: Ansehen ist read-only. Restore sichert zuerst den aktuellen Zustand, lädt ausschließlich Daten, erhöht die aktuelle Revision und schreibt einen neuen Commit mit `restore_of`; keine alten KI-Aufträge/Aktionen werden abgespielt. Neuere Snapshots bleiben erhalten. Undo/Redo stellen Inhaltsframes wieder her, ebenfalls mit monotoner Revision. Ein KI-Batch und eine zusammenhängende Geste sind jeweils ein Schritt. Erneute Zustellung derselben Antwort wirkt auch nach Undo nicht erneut.

Die Historie liegt auf demselben Datenträger und ist **kein externes Backup**. Kein automatischer Upload, kein stilles Löschen, keine Zusage eines Stromausfalltests an echter Hardware.

## Gespräch und KI-Vertrag

Bestehendes POST `/api/tasks`: Task-ID, Auftrag, aktuelle geordnete Box-IDs, Revision und vollständiger semantischer Snapshot (Maße, Ursprung 0/0, X rechts/Y unten, Pixelmaßstab 1, Ebene, Raster, Zoom/Sprache). Optionale Gesprächserweiterung Version 1: Projekt-/Vorher-Snapshot-ID, Bezugstask, Auswahlwechsel und höchstens zwei relevante vorherige Aufträge samt Ergebnis/Aktionen/Rückfrage. Das vollständige Gespräch bleibt dauerhaft im Projekt. Der vorhandene Transport erhält echte vergangene user/assistant-Beiträge getrennt vom letzten Auftrag. Explizite Antworten auf eine frühere Rückfrage nehmen diese als Bezug; aktuelle Ziele gelten immer. Alte Pakete ohne Gespräch bleiben für den bestehenden Vertrag lesbar.

Whiteboard-task → read-back → claimed → vorhandener `services.ollama_local.complete` → deklarative Antwort → Prüfung auf temporärem Dokument → Whiteboard-result/read-back → Browserprüfung → Vorschau oder dauerhafte Anwendung. Höchstens ein Modellauftrag pro Host. Modell in `ai-config.json` nur produktbezogen; keine globalen Hausmeisteränderungen, Agentenstarts oder externen Schlüssel. Für Gesprächskontext 8192 Token, 800 Antworttoken; konservative Kontext-/Whiteboardobergrenzen vor dem Aufruf, keine stille Kürzung. Im selben Whiteboard-Job ordnet zuerst ein kurzer begrenzter lokaler Modellaufruf die Absicht edit/proposal/question und den nötigen Gesprächsbezug ein. Eigenständige Aufträge verwenden die aktuellen Dokumentdaten, Folgeaufträge zusätzlich den relevanten Verlauf. Nicht übernommene Vorschläge werden dabei ausdrücklich von ausgeführten Aktionen unterschieden. Danach erzeugt derselbe vorhandene Transport die dazu passende exklusive Antwort: Vorschläge ohne Aktionen, Änderungen ohne Vorschläge oder eine Rückfrage ohne Änderungen. Beide Aufrufe sind begrenzt und in Modell-/Tokenmetadaten belegt. Dies sind zwei sequenzielle Schritte innerhalb des vorhandenen Produktadapters, kein zusätzlicher Dispatcher/Agent. Ein flaches JSON-Schema begrenzt die Serialisierung; unabhängige Validatoren bleiben maßgeblich.

Antwort: `summary`, `actions`, `proposals`, optional `question`. Rückfrage verlangt leere Aktions-/Vorschlagslisten. Fehlt die Auswahl, fragt BlockDesigner nach dem gewünschten Bezug, bevor an die KI zugestellt wird. Diese Produktrückfrage hat ausdrücklich keinen fingierten Modellbeleg. Eine präzisierende Antwort kann einen dokumentweiten Auftrag oder neue Gestaltungsvorschläge freigeben. Erlaubt sind patch auf exakt beauftragte IDs (bekannte Werte/Schriften), proportionale scale oder geprüftes grid. Vorschläge haben validierte Styleattribute ohne Position. Kein Modellcode. IDs/Nummern/Orientierungsfarben/Ebenen/Zuordnungen bleiben geschützt; Module/Kinder werden auch bei KI-Patches geprüft.

Direkt anwenden nur **eine** Patchaktion auf **eine kinderlose** ausgewählte Box: ausschließlich Beschriftung bis 80 Zeichen oder ausschließlich Breite/Höhe mit höchstens 10 Prozent Änderung. Andere geprüfte Änderungen bekommen sichtbare Geometrie-/Gestaltungsvorschau und Aktionsdifferenz; Übernehmen prüft Revision, Auswahl, Ebene und Werte erneut. Verwerfen speichert die Entscheidung ohne Boxänderung. Auswahl-/Dokumentwechsel macht die Antwort sichtbar veraltet. Antwort-Idempotenz bleibt nach Neuladen und Undo erhalten. Statusabruf nach Unterbrechung startet keine Inferenz erneut. Wiederhergestellte historische Tasks sind archiviert.

Grundlage der lokalen JSON-Schnittstelle: [Ollama Structured Outputs](https://docs.ollama.com/capabilities/structured-outputs). Sie ersetzt keine unabhängige Validierung.

Technische Prüfung beweist keine fehlerfreie Sprachabsicht. Leere, falsche oder widersprüchliche Modellantworten zählen nicht als erfolgreiche Änderung. Konkrete Modellwahl und tatsächliche Prüfungsergebnisse stehen im Abnahmebericht.

## Gezielte Prüfwege

`npm test`: Modell/Geometrie/atomare Aktionen/Familien/Undo. `tests/adapter_test.py`: Ziele, Ebenen, Werte, Kontext, Rückfragen und Antwortschema. `tests/host_contract_test.py`: eigene Manifestmigration ohne Umgehen deaktivierter Module. `tests/project_store_test.py`: deduplizierte Daten, Unterbrechung/Beschädigung, Konflikt, Format und Schreibfehler. `npm run browser`: vorhandene echte Modulregression. `npm run browser:upgrade`: eigene isolierte Chrome-/Hostablage, neue UI-/Historie-/Gesprächs-/Fehlerabläufe; Teilmenge über Fall-IDs möglich. `npm run browser:zoom`: echte Chrome-Einstellungen für 125/150/200 Prozent, keine CSS-Zoomsimulation. Neue Belege/Screenshots bleiben ignoriert unter `.runtime/`, öffentliche Berichte enthalten nur Prüfaussagen. Nach Moduländerung betroffene Fälle plus kurze durchgängige Regression ausführen.


## Konsolidierter Einstieg · 18.10.2026

Die vorhandene Produktbasis1357416 bleibt erhalten; der alte main-Prototyp ist
kein alternativer Startweg. `start.command` wählt einen vorhandenen Interpreter
(`BD_PYTHON` oder Python im PATH) und ruft `scripts/launch.py` auf. Dessen
`--check` ist eine lesende Voraussetzungen-/Bindungsprüfung; Import und fehlende
Konfiguration werden vor Setup/Serverstart verständlich eingeordnet. Vorhandene
Bindung/Whiteboardroot und deaktivierte Modulentscheidung werden respektiert.
Erst normaler Start beziehungsweise explizites `--setup` nutzt den vorhandenen
Host-Setupweg; es entsteht keine neue Registrierungs-/Berechtigungsarchitektur.

NP-Basis unverändert: Gitblob673f4e265c8c46618ba86d9e98f8da09fd0bf107,
identisch mit aktueller lokaler TG/FP-Kopie. Bestehende Undo/Redo-Buttons nutzen
gebogene Symbole mit lokalisierten zugänglichen Namen, keine neue Aktionslogik.
Editorfenster, Dokumentkoordinaten und Zielseiten-Referenzviewport bleiben getrennt.
[Design-source v1](contracts/design-source-v1.md) ist der vorbereitete Vertrag für
BD-C02–04, noch kein Import-/MCP-/Bridge-Adapter. Keine Änderung an Box-/Projekt-
Format1, Revision, UndoFrames oder historischen Daten.

## Referenzimport / BD-C02–03 · 18.10.2026

`core/design.js` prüft den additiven optionalen Dokumentteil `design`, berechnet
die proportionale Referenz→Dokument-Abbildung und beschreibt `move/replace/new`
im bestehenden Source-Vertrag. `panels/source.js` nutzt die bestehenden MySpace-
und Auswahlpanels; dauerhafte Übernahme ausschließlich durch `projects.apply`.
Reduceraktionen `designImport/designBind` prüfen Revision, aktuelle Quelle und
Ebene. Die vorhandene Übernahmequeue prüft zusätzlich die erwartete Projekt-ID,
damit ein später Upload nach Projektwechsel nicht bei gleicher Revision in ein
fremdes Dokument gelangt. Ein Import verändert keine Boxidentität/Geometrie; ein Import-/Bindungsschritt
ist ein vorhandener Undo-Schritt. Alte Inline-Frames ohne design stellen keine
Referenz wieder her. `workspace/render.js` zeigt dasselbe inerte PNG in Dokument
und Historie unter allen drei Boxebenen. Die bisherige Dokumentgröße bleibt erhalten.

`scripts/design_source.py` prüft begrenzte PNG-/HTML-Bytes und einen statischen
ID-Katalog, ohne eine Quelle auszuführen oder eine URL zu öffnen. `ProjectStore`
publiziert Originalbytes im vorhandenen CAS; Dokument/Frames referenzieren Hashes,
ohne PNG/HTML in jedem Undo-Frame zu wiederholen. Quelle/Vorschau/ID-Katalog werden
bei dauerhafter Übernahme und erneutem Lesen geprüft. Nur PNG ist über den lokalen
Server abrufbar. Keine neuen Rechte oder Modellaufrufe.

Schema, Grenzen und spätere Ausgabebindung: [design-source-v1](contracts/design-source-v1.md).
Die bisherige Whiteboard-Snapshotform bleibt erhalten: aktuelle Boxdaten und
Revision, kein HTML und kein zweiter KI-/Bridge-Auftragsweg. Neue Entwurfsmetadaten
erhöhen dieselbe Revision und machen alte Boxantworten weiterhin veraltet.
BD-C04 muss den exakt gespeicherten Stand mit dem zentralen Issued-/Run-Vertrag
prüfen; der lokale Descriptor und sein `ready`-Flag sind keine Berechtigung.

## Codeübergabe / BD-C04 · 18.10.2026

Reviewkorrektur19.10.: `blockdesigner.operator-profile.v1` pinnt vor dem ersten
Versand kanonisches CWD samt beobachteter Verzeichnisidentität, feste Quell-/PNG-
Dateinamen sowie konfigurierte Peer-/Principal-/Konfig-/State-Referenzen. Keine
Tokens oder Credentialinhalte; diese Clientbeobachtung ist keine Remoteattestierung.
Jede Folgeaktion und jeder ausgehende Clientcall prüft den bestehenden Pin; vor
Dateiübernahme nochmals nach RPC. Drift verweigert bereits die erste Rückvorschau
und Entscheidung. Die Aktion nutzt eine Kopie des ursprünglichen Pins, keine
zwischenzeitlich umkonfigurierte Dateizuordnung. Der Browser sieht nur den Hash
und einen lokalisierten Sperrstatus, keine internen Pfade/Backenddaten.

Die Startsperre liest alle persistierten eigenen Zuordnungen, unabhängig von der
heutigen Profilliste. Ursprünglicher kanonischer Pfad oder beobachtetes dev/inode
eines ungeklärten Starts sperren dasselbe Quellprojekt auch nach Profilentfernung,
Umordnung oder Verzeichnisumbenennung. Fehlende historische Pins werden nicht
geraten und blockieren konservativ; keine automatische Migration/Löschung.
Maximal4096 Einträge/16MiB und zwischen Dateiprüfungen ein2s-Scanbudget, sonst
failclosed. Das ist keine OS-weite Sperre oder harte Echtzeitgarantie für langsame
Dateisysteme. [Gezielte Gegenfälle](acceptance/PROFILE-PIN-20261019.md).

`scripts/design_workflow.py` erzeugt serverseitig aus einem tatsächlichen aktuellen
Projekt/Snapshot einen unveränderlichen Descriptor im vorhandenen CAS. Der optionale
`FixedBridgeClient` verwendet vorhandene KiraBridge-MCP-Werkzeuge; seine lokale
Konfiguration/Identität und die feste Projekt→CWD-/Dateinamen-Zuordnung kommen nur
aus einem vertrauenswürdigen Betreiber-Embedding. Der normale Server startet ohne
dieses Profil und verweigert Codeausführung. Es wird keine Konfiguration migriert,
kein Geheimnis im Browser angelegt und keine vorhandene Runtime verändert.

Die vorhandenen ThreadDesk-Verwaltungsoperationen create/set_note/add_file tragen
den tatsächlichen Descriptor-SHA256 und immutable Descriptor-/HTML-/PNG-Dateien.
Keine neue `context.design`-Mutation ist nötig. `handoff.issue` belegt den festen
Issued-Stand mit tatsächlichen source_refs-Hashes; erst ein gesonderter Start
verwendet den bestehenden M2-Code-Agenten. Frage/Antwort/Status/Inbox/Entscheidung
verwenden dessen vorhandene Task-/Sitzungs-/Return-Verträge.

`projects/{id}/design-workflows/{uuid}.json` ist eine additive, private, begrenzte
Zuordnung (`blockdesigner.workflow-binding.v1`), **keine Queue**. Sie speichert
Anfragehash und stabile Bridge-Task-ID vor dem Senden. Ein unklarer Versand liest
danach ausschließlich task_get; kein Startup-Worker und keine automatische
Wiederholung. Vorhersehbare IDs werden aus Projekt/Workflow/Schritt abgeleitet,
originale ThreadDesk-task_id einschließlich Doppelpunkt bleibt unverändert.
Projekt-/Snapshot-Revision, SHA256, Issued-/Run-/Return-ID und Principal werden
getrennt geprüft. Derselbe feste Projektpfad darf keinen zweiten Start erhalten,
solange ein vorheriger eigener Lauf ungeklärt ist. Keine OS-Sandbox behauptet.

Der bestehende Projekt-/CAS-Lock und eine nicht wartende Aktionssperre serialisieren
Schritte. Ein read-only Clientaufruf hat8s, ein Schritt insgesamt30s; lokale
Abschlussabfragen sind begrenzt. Maximal64 Zuordnungen je Projekt,128 gespeicherte
Operationsbezüge je Zuordnung,2MiB je Datensatz; keine automatische Bereinigung.
PNG-/HTML-Grenzen des vorhandenen Importers gelten. Ausgaben lesen ausschließlich
vereinbarte Dateinamen im festen CWD, nie beliebige Modellpfade. HTML bleibt inert.

`src/bridge/design-workflow.js` steuert nur die kompakte bestehende MySpace-Ansicht
und feste Host-APIs. GET `/api/design/workflows/{project}/{id}` liest die Zuordnung.
POST `/api/design/workflows` bereitet einen konkreten gespeicherten Snapshot vor
oder stößt genau eine erlaubte Schrittoperation an. Host-/Origin-/JSON-/CSP-
Grenzen bleiben erhalten. Kein Polling führt implizit eine Ausführung aus;
Neuladen stellt nur gespeicherte Ansicht wieder her. Fremde/veraltete Ergebnisdaten
oder eine abweichende doppelte Entscheidung werden abgewiesen. Code/PNG bleiben
unverified; Annahme ändert weder aktuellen Entwurf noch dessen Originalreferenz.

Quell-/PNG-Lesen ist technisch lokal belegt, keine allgemeine Modellfunktion oder
installierte Runtimeabnahme. [Prüfumfang und Betreiberweg DE/EN](acceptance/HANDOFF-20261018.md).
