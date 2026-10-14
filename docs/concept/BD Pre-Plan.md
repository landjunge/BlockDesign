# BD Pre-Plan

## Ziel, Quellen und Ablage
Startbares Browser-Prototyp-Modul mit Boxbedienung, zwei Ansichten, Attributmodul und echter KI-Anbindung über den bestehenden Whiteboard-Weg.
Quellen im selben Ordner: BD Brainstorm Destillat.md; BD Ziel Idee.md.
Projektworkspace: /Users/landjunge/blockdesigner. GitHub-Ziel laut Nutzer: blockdesigner ohne Bindestrich; tatsächliches Remote vor Schreiben prüfen. Keine anderen Repositories löschen.
Regeln: /Users/landjunge/threaddesk-worktrees/closed-chat-import/docs/usability/GOLDENRULES.MD (§§15–19 einschließlich späterer Desktop-Präzisierung); /Users/landjunge/.threaddesk/Workflow/Workflow-Planerstellung-fuer-andere-KIs.md. Regelstand vor Umsetzung abgleichen.
Speichern/Export, Webseitenimport, Symbolbibliothek, MCP und Mikrofon sind spätere Ausbaustufen. Die vollständige Vision bleibt in den Quellen erhalten.

## Gemeinsamer Bauvertrag
Vorhandene Module, Schnittstellen und Tests nutzen. Keine zusätzlichen ThreadDesk-Kernrechte, kein zweiter Orchestrator und keine direkten Zugriffe auf fremde Datenbanken.
Eine maßgebliche Objektstruktur: ID, fortlaufende Nummer, Orientierungsfarbe, Ebene, Typ, X/Y, Breite/Höhe, Rundung, Gestaltungsfarbe, Schrift, Beschriftung, Modulzuordnung; geordnete Auswahl, Zustandsrevision, Raster und Dokumentmaße.
Ursprung oben links (0,0), X nach rechts, Y nach unten; unten rechts (Dokumentbreite,Dokumenthöhe). Zoom verändert Dokumentkoordinaten nicht. Für den ersten Test werden Dokumentmaße ausdrücklich initialisiert; kein stiller Größenwechsel bei Fensteränderung.

## Modulare Architektur — verbindliche Nutzerpräzisierung
Das gesamte Tool wird wie die anderen Werkzeuge modulbasiert aufgebaut. Vor Umsetzung vorhandene Modulverträge und wiederverwendbare Bausteine prüfen und nutzen; kein monolithischer Ein-Datei-Ausbau und kein konkurrierendes Modulframework.
Klare Zuständigkeiten für gemeinsames Box-/Dokumentmodell, Tastatur-/Maussteuerung, Workspace-Darstellung, Ebenen/Raster, Auswahl/Attribute/Module, MySpace, KI-Space und den bestehenden Whiteboard-KI-Adapter. Die konkrete Dateiaufteilung folgt vorhandenen Verträgen und tatsächlichem Bedarf, nicht einer Pflicht zu einem Framework oder einer Datei je Begriff.
Ein maßgeblicher Zustand mit versionierten, validierten Aktionen; Struktur- und Gestaltungsansicht sowie KI-Anschluss greifen über kleine definierte Schnittstellen darauf zu. Keine mehrfach gepflegten Boxzustände, keine direkten Datenbankzugriffe anderer Produkte. Fachliche Box-Module mit Kindern bleiben von Softwaremodulen begrifflich getrennt.
Abnahme zusätzlich: Modulgrenzen und Start-/Integrationsvertrag dokumentiert, zentrale Bedienabläufe über die echten Modulgrenzen getestet. Modulare Architektur ist Bestandteil der gesamten Umsetzung BD-01 bis BD-08, keine spätere Nachrüstung.

## BD-01 — Anschluss und Start
Vorhandenen Zielhost/Modulvertrag und Whiteboard-Anschluss lesen. Tatsächliches GitHub-Remote prüfen. Browserlaufzeit, Startbefehl und Modulgrenzen dokumentieren; vorhandenen einfachen Projektweg verwenden.
Abschluss: Leeres Modul startet sichtbar; Repository-Zuordnung und ausführende Session sind belegt.

## BD-02 — Zustand, Ebenen und Erstellen
Drei Ebenen mit 1/2/3; nur aktive Ebene bearbeitbar. B erzeugt 50 × 50 Pixel mittig. Weitere dort erzeugte Boxen jeweils +5 Pixel rechts/unten; Raster darf diesen Erstellungsversatz nicht aufheben.
Jede Box bekommt eigene ID, nächste Nummer und helle Orientierungsfarbe. Rahmen ohne Füllung, Nummer klein oben links, sichtbarer Mittelpunktmarker von einem Pixel.
Mittelpunkt stets (X+Breite/2,Y+Höhe/2), auch nach Skalieren. Typwechsel erhalten Identität. Shift ergänzt Auswahl; erste Auswahl ist Primary-Box.
Abschluss: Erstellen, Nummerierung, Versatz, Mittelpunkt und Ebenensperren funktionieren. Bei erschöpftem Erstellungsraum sichtbaren Hinweis statt ungreifbarer überlagerter Box erzeugen.

## BD-03 — Greifen und Größenänderung
Space greift die bearbeitbare Box mit dem nächstgelegenen Mittelpunkt; bei Gleichstand deterministisch nach Nummer. Greifer in die Mitte setzen, Mausbewegung führt die Box; nächstes Space setzt sie ab. Ein Systemzeigersprung ist nur bei tatsächlicher Laufzeitunterstützung behauptbar; im Browser virtuellen Greifer und relative Mausbewegung als technische Umsetzung sichtbar dokumentieren.
F halten: horizontale Mausbewegung verändert ausschließlich Breite; D halten: vertikale Bewegung ausschließlich Höhe. Diagonale Bewegung wirkt nur auf gewählte Achse. D+F: keine Größenänderung. Bei Größenänderung linke obere Ecke fest; rechts/unten wachsen oder schrumpfen. Bewegung ist dann ausgesetzt.
Plus Faktor 1,1; Minus Kehrwert; relative Größenbefehle ebenso. Mindestmaß 4 Pixel je Achse; kleine Objekte bleiben durch ausreichend große Greifbereiche erreichbar.
Harter Stopp am Dokumentrand, einschließlich Modulkindern. Proportionale Skalierung insgesamt begrenzen, Seitenverhältnis erhalten. Exakte Werte intern, verständlich gerundete Anzeige.
Abschluss: Achsensperren, Anker, Greifen, Stufen und Grenzen tatsächlich bedienbar.

## BD-04 — Raster und Monitor
Rasterabstand 20 Pixel, Fangbereich 2 Pixel. Beim Bewegen linke/obere Kante einrasten; bei D/F die jeweils bewegte Kante. Raster darf weder gesperrte Achse noch harte Grenzen verletzen.
„Feiner um Faktor zwei“: Abstand 10, Fangbereich 1 Pixel. Rasterweite per KI-Auftrag veränderbar, positive Werte prüfen.
Frei platzierbarer Monitor: Nummer, X/Y, Breite/Höhe, Rahmenfarbe; letzte Auswahl bleibt angezeigt.
Abschluss: Einrasten, Verfeinern und Monitor stimmen mit tatsächlichen Objektwerten überein.

## BD-05 — Attribute, Übernehmen und Module
Typzuweisung und Kinderzuordnung funktionierend. Zyklen verhindern; Modulbewegung nimmt Kinder mit unverändertem Versatz mit. Beim Prototyp verschieben Module Kinder, skalieren sie jedoch nicht automatisch.
T übernimmt Größe, Rundung, Gestaltungsfarbe, Schrift und Beschriftung von Primary-Box. ID, Nummer, Orientierungsfarbe, Ebene, Position und Zuordnung bleiben erhalten. Nur passende Attribute übertragen, keine erfundenen funktionalen Bindungen.
Palette: 16 Grundfarben; vorhandene Quelle nutzen. Rahmenidentität und Designfarbe getrennt.
Abstandsvorgabe durch zwei Buttons und automatische Kinderverteilung bleiben spätere Verfeinerung im Destillat.
Abschluss: Übernehmen und Gruppieren funktionieren ohne Verlust von Identität oder Zuordnung.

## BD-06 — Zwei Ansichten und Attributtest
Boxansicht und sichtbare Gestaltungsansicht verwenden denselben Zustand. Attributmodul hängt an gemeinsame Eingabesteuerung.
Test: Taste halten → Attribut/Grundfarbe wählen → Scrollrad fein einstellen → Vorschau sofort sichtbar → Loslassen übernimmt. Scrollrad im Attributmodus verändert Werte statt die Fläche zu scrollen.
Konkrete Taste, Attributwechsel und Übergang Grundfarbe/Feinwert sind bewusst Testvarianten, keine endgültigen Nutzerentscheidungen. Ausführende KI liefert eine dokumentierte, konfliktfreie vorläufige Belegung und kennzeichnet diese; Farbe zuerst, Feineinstellung zunächst Helligkeit. Abbruch stellt Ausgangswert wieder her.
Abschluss: Ablauf direkt ausprobierbar; Vorbelegung und spätere Änderbarkeit verständlich.

## BD-07 — Whiteboard und echte KI
Vorhandenen Workflow anschließen, MCP später. Texteingabe reicht zunächst. Auftrag enthält task_id, Box-IDs, aktuelle Revision, Maße, Ursprung/Achsen, Pixelmaßstab, gegebenenfalls Zoom, Ebene, Raster und relevante Attribute.
Bewegung aktualisiert Zustand exakt; endgültige Position beim Absetzen zuverlässig bereitstellen. Keine Schätzung aus Bildern.
KI-Rückgabe an Auftrag und Ausgangsrevision binden; erlaubte Ziele/Attribute/Werte und Ebenensperren prüfen. Duplikate wirken nicht zweimal; veraltete Antworten werden sichtbar zurückgestellt. Kein beliebiger Code aus Modelltext.
Abschluss: Echter Auftrag → tatsächliche KI-Übernahme → Rückgabe → sichtbare zulässige Änderung; zusätzlich Gestaltungsvorschlag auswählen/anwenden. Fehler-, Duplikat- und Veraltungsfälle geprüft. Kein simuliertes KI-Ergebnis.

## BD-08 — Integration und Abnahme
Gesamtablauf: Start → Ebenen → Erstellen → Greifen → Bewegung → D/F → Skalieren → Raster → Mehrfachauswahl/T → Typ/Modul → beide Ansichten → Attributtest → echter Whiteboard-KI-Auftrag.
Prüfen: DE/EN, Tastatur, lange Texte, Leer-/Fehlerzustände, Zoom, kleinerer Fensterausschnitt, ungültige KI-Antwort und Verbindungsabbruch. Kürzel nicht in Texteingaben/Dialogen auslösen.
Synthetische Daten, vorhandene passende Tests; Ergebnis mit Commit/Version und Belegen als bestanden/fehlgeschlagen/nicht geprüft. Liefern: Code, Startweg, Tastenübersicht, Abnahmebericht und Grenzen.
Abschluss: Direkt startbarer und getesteter Prototyp. Technischer Abschluss ist keine vorweggenommene Nutzerakzeptanz oder Erfüllung der gesamten Vision.

## Verbindliches Design
Gemeinsamen networkpunkt.css-Kern einer festgehaltenen Version lokal nutzen, keine CDN/Webfonts. Systemschrift 12/14/16/24; Bedienhöhe 40; Abstände 4/8/12/16/24/32. Eckige Komponenten, sichtbarer Fokus, Fehler/Status als Text, eine ruhige Hauptaktion.
MySpace links, Workspace Mitte, KI-Space rechts. Dunkelgraue Arbeitsfläche #1a1c20, Grundfläche #121316; helle Farblinien, zurückhaltendes helles Raster. Bearbeiteter Designinhalt darf eigene Farben/Rundungen haben.
Desktop 1440 × 900, vorgesehen mindestens 1180 × 760 CSS-Pixel; kein automatisches Mobilstapeln. Scrollbarkeit ohne sichtbare Balken erhalten. Dialogfokus hinein/zurück, Escape schließt.

## Verbindlicher Vergabe- und Rückmeldeablauf
Jedes BD-Paket bei Vergabe in kleine prüfbare Teilaufgaben mit eigener step_id zerlegen. Eintrag enthält task_id, step_id, Verantwortlichen, Ziel, Eingaben, Dateizuständigkeit, Abhängigkeiten, Abschlusskriterium und Gewicht.
1. Agent holt eine freigegebene Teilaufgabe und meldet sofort „Arbeit abgeholt“ mit task_id/step_id, Session, Zeit und nächster Handlung im Whiteboard.
2. Nach erfülltem Kriterium sofort „Erfüllt“ mit denselben IDs, Zeitpunkt, Ergebnis und Beleg/Commit. Kein Erfolg allein durch Behauptung.
3. Danach selbstständig nächste freigegebene Aufgabe holen und deren Übernahme erneut melden. Nicht auf Nutzerantwort warten. Blocker sofort melden und unabhängige freigegebene Arbeit fortsetzen.
4. Während längerer Arbeit spätestens nach 60 Sekunden auftragsbezogenen Zwischenstand melden. Tatsächlichen Feedback-Timer gemäß vorhandenem Workflow starten beziehungsweise Hook nachweisen; nach Frist ohne Rückmeldung nachhaken. Eine aufgeschriebene Regel ist kein laufender Timer.
5. Koordination erhält jede Übernahme-, Fortschritts-, Erfüllt- und Blockermeldung. Zustellung und erste echte Arbeit vor Laufbestätigung prüfen.
Abhängigkeiten: 01 → 02; danach 03/04/05 auf abgestimmten Schnittstellen, 06 nach 05, 07 nach 01/02; 08 nach allen. Parallel nur mit klar getrennten Dateien beziehungsweise isolierten Arbeitsständen.
Acht gleich gewichtete Pakete; Teilgewichte summieren sich je Paket zu dessen Gewicht. 100 Prozent erst nach BD-08. Günstigste geeignete zugelassene KI und vorhandene deterministische Wege nutzen.

## Übergabestatus
Am 14.10.2026 direkt durch den Nutzer an die aktive Codex-Session `01a13ae2-819a-7442-8789-a7e7c4f1cc94` zugestellt. Übernahme und erste echte Arbeit im Whiteboard-Thread `2e1032dcf420` bestätigt. Kein rekursiver Sessionstart. Gesamtauftrag `bd-build-20261014`, Paketaufträge `bd-01` bis `bd-08`; Fortschritt ausschließlich nach belegten Abschlusskriterien.

## Konkretisierte Architektur und Baufolge · 14.10.2026
Diese Ergänzung präzisiert die oben erhaltenen Verträge. Bestehende Historie und Bedienentscheidungen bleiben verbindlich.

### Geprüfter Anschluss und Repository
`/Users/landjunge/blockdesigner` war leer und kein Git-Repository. `landjunge/blockdesigner` existierte nicht. `landjunge/blockdesign` enthält den alten defekten Ein-Datei-Prototyp und die automatisch gesicherten Konzepte; `landjunge/block-design` verweist ebenfalls auf diese Sicherung. Deshalb wird **blockdesign** im gewünschten lokalen Workspace verwendet, Branch `feat/modular-block-designer`. Kein Repository wird umbenannt oder gelöscht. Die kurze alte README ist historisch und wird an die Umsetzung angepasst.
ThreadDesk-Modulvertrag: `ModuleManifest`, `ModuleRegistry`, `ModuleRuntime`, `ModuleContext`; Whiteboard nur `read_whiteboard`/`append_whiteboard`. Gepinnter vorhandener Checkout `/Users/landjunge/threaddesk-worktrees/ordinal-lock/src`, Commit `3b6f3fa`, mit serialisiertem append-only Store; kein Eingriff in dessen ungesicherte Arbeit. Modul `block-designer`: Whiteboard lesen/anhängen, lokaler Ollama-Connector, Browseransicht, keine weiteren Kernrechte. Bestehendes lokales `llama3.2:3b` über `services.ollama_local`; keine bezahlten Aufrufe oder Agentenstarts. Das Produktprofil bleibt lokal auf `llama3.2:3b` begrenzt: Die kleinere 1b-Variante scheiterte an Vorschlägen, 7b brachte keine Verbesserung. Diese aufgabenbezogene Auswahl verändert keine globalen Hausmeister-Einstellungen. Der feste Systemvertrag und die relevanten Zielattribute/Kindergeometrie gehen an das Modell; das vollständige Dokument bleibt im Whiteboardauftrag. Kontext-/Metadatenobergrenzen werden vor dem Modellaufruf geprüft, keine stille Kürzung. Die Hausmeister-Zusammenfassungslogik passt fachlich nicht auf Boxaktionen; der Produktadapter nutzt dessen vorhandenen lokalen Transport und Modulgrenze mit einem begrenzten Boxantwortvertrag.
Gemeinsamer Designkern: unveränderte lokale `networkpunkt.css` von ThreadDesk `b0b6815`, SHA-256 `98371bd9edc96fb940a0e0de34933740fed1062b510aa516498fcb53e112591e`.

### Zuständigkeiten und Schnittstellen
| Bereich / Dateien | Verantwortung und erlaubte Abhängigkeiten |
| --- | --- |
| `src/core/model.js`, `geometry.js`, `actions.js`, `store.js` | Ein Dokument mit Boxen, Auswahl und Revision; reine Geometrie; validierte atomare Aktionen v1. Alle anderen Module lesen über `getState`, verändern nur über `dispatch`; kein DOM im Kern. |
| `src/core/palette.js` | Eine gemeinsame 16-Farben-Quelle für Attribute, Vorschläge und Rendern; Orientierungsfarben unabhängig davon. Kein bereits definiertes vollständiges 16-Farben-Artefakt in den geprüften Quellen gefunden; vorläufige nummerierte Grundpalette explizit dokumentieren. |
| `src/input/controller.js` | Tastatur/Maus, Fokuswächter, relative Dokumentbewegung, Greifer, A-Vorschau; nutzt Kernaktionen und Workspace-Koordinaten. |
| `src/workspace/render.js`, `layers-grid.js`, `monitor.js` | Beide Ansichten aus demselben Zustand; Zoom nur Darstellung; Raster, aktive Ebene und frei platzierbarer Monitor. |
| `src/panels/selection.js` | Typ, Beschriftung, Primary/T, Kinderzuordnung; keine eigene Boxkopie. |
| `src/panels/myspace.js` | Behaltene Vorschläge im laufenden Dokument, direkt einsetzbar; Persistenz/Dateiimport bleiben spätere Stufen. |
| `src/panels/ai-space.js`, `src/bridge/whiteboard.js` | Texteingabe, Aufgabenstatus, Vorschlagsauswahl; Bindung task_id/Revision/Box-IDs und zweite Validierung vor Anwendung. |
| `scripts/host.py`, `ai_adapter.py`, `server.py` | Feste lokale Hostbindung; Task über bestehendes Whiteboard zustellen, auslesen, tatsächlich übernehmen; vorhandenen lokalen Modelltransport benutzen; JSON prüfen und Whiteboard-Rückgabe liefern. Kein Modellcode, keine fremden DB-Zugriffe, kein allgemeiner Dispatcher. |
| `src/app.js`, `index.html`, `styles/` | Einmalige Montage und Designadapter, keinerlei zweite Zustandslogik; statischer ES-Modulweg ohne Framework/Buildschritt. |

Datenfluss: Mensch → Eingabesteuerung/Panel → `dispatch({version:1,type,...})` → Validator/atomarer Reducer → ein neuer Zustand/Revision → abonnierte Ansichten. KI: abgesetzter Zustand → Auftrag mit Dokumentkontext → Whiteboard-task → read-back/claimed → lokales Modell → geprüfte deklarative Aktionen/Vorschläge → Whiteboard-result → Browserprüfung gegen aktuelle Revision → `dispatch`. Veraltetes bleibt sichtbar zurückgestellt; ein neuer Auftrag ist eine bewusste erneute Anfrage. Vorschläge dürfen behalten und später nach neuer Ziel-/Wertprüfung angewendet werden.
Dokumentinitialisierung: ausdrücklich 1000 × 640 Pixel; Zoom initial 75 Prozent. Größenänderung des Fensters ändert diese Maße nie. Fachliche Box-Module sind Eltern in diesem Modell, keine Softwaremodule. Alle Kinder eines Moduls müssen auf derselben Ebene liegen; Umbenennung eines Eltern-Moduls in einen anderen Typ ist bei Kindern gesperrt. Keine automatische Skalierung/Verteilung von Kindern. Explizite Modul-Hintergrundentscheidungen (Grundfarbe, Palette, Helligkeit) gelten auch für zugeordnete Kinder; Identität, Text und Geometrie werden dadurch nicht übernommen. Partielle Schriftaktionen dürfen ausschließlich family/size/color ändern; ungenannte Werte bleiben erhalten und der Dokumentzustand hat immer vollständige Schriftattribute. T überträgt allgemeine Gestaltungsattribute; Schrift/Beschriftung auf texttragende Typen (alles außer Checkbox), keine funktionalen Bindungen.

### Kleine freigegebene Schritte
Jedes Paket wiegt 12,5 Prozent; jeder der beiden Schritte 6,25 Prozent am Gesamtauftrag. Verantwortlich ist jeweils die oben genannte aktive Codex-Session. Eingaben sind Konzeptquellen und die abgeschlossenen Abhängigkeiten. `claimed`, `progress`, `result`/`problem` tragen Paket-task_id und step_id; Gesamtpings tragen zusätzlich `bd-build-20261014`. Belege liegen im Code, Git-Verlauf und `docs/acceptance/`.

| step_id | Dateien / Ziel | Abhängigkeit | Abschlusskriterium |
| --- | --- | --- | --- |
| BD-01.1 | bestehender Pre-Plan; Modul/Repo/Design/Whiteboard prüfen | keine | Quellen vollständig gelesen, begründete Zuordnung und konkrete Verträge versioniert; automatische Sicherung abgeglichen. |
| BD-01.2 | `scripts/host.py`, `server.py`, `module.json`, `start.command`, `index.html` | 01.1 | Leere drei Spaces sichtbar startbar; Hostmanifest geprüft; echte Whiteboard-Zustellung und Feedback-Timer getestet. |
| BD-02.1 | `core/model.js`, `store.js`, `actions.js` | 01 | Ein validiertes Dokument/Revision, aktive Ebene, Identität/Nummer, Auswahlreihenfolge. |
| BD-02.2 | `workspace/render.js`, `layers-grid.js` | 02.1 | B=50×50 Mitte/+5 ohne Raster; Erschöpfungshinweis, helle Linie/Nummer/1-Pixel-Mitte, Ebenensperren sichtbar geprüft. |
| BD-03.1 | `input/controller.js`, `core/geometry.js` | 02 | nächster Mittelpunkt, deterministischer Gleichstand, virtueller Greifer, relative Bewegung, D/F/D+F samt festem Anker. |
| BD-03.2 | `core/actions.js`, `geometry.js` | 03.1 | ±1,1/Kehrwert, min.4, proportionale Gesamtbegrenzung, harte Grenzen einschließlich Kinder; Browserablauf bestanden. |
| BD-04.1 | `layers-grid.js`, `geometry.js` | 03 | 20/2, 10/1, Kantenfang ohne Achsen-/Grenzverletzung, positive Rasterwerte geprüft. |
| BD-04.2 | `monitor.js`, `render.js` | 04.1 | frei platzierbarer Monitor mit letzten tatsächlichen Werten; Zoom lässt Koordinaten unverändert. |
| BD-05.1 | `panels/selection.js`, `core/actions.js` | 02/03 | Typwechsel erhalten Identität; Shift/T, passende Attribute inkl. Text, 16-Farben-Quelle. |
| BD-05.2 | dieselben Dateien / fachliche Gruppierung | 05.1 | Kinderzuordnung, Zyklensperre, Modulbewegung mit Kindern, keine Kindskalierung; Grenzen bestanden. |
| BD-06.1 | `render.js`, `app.js` | 05 | beide Ansichten zeigen denselben Zustand, typische Inhaltsdarstellung ohne neue Spezialwerkzeuge. |
| BD-06.2 | `controller.js`, Palette/Attributpanel | 06.1 | A halten, Grundfarbe wählen, Rad=Helligkeit, sofortige Vorschau, Loslassen=Übernahme, Escape=Ausgangswert; Fokuswächter. |
| BD-07.1 | `ai_adapter.py`, `bridge/whiteboard.js`, `ai-space.js` | 01/02 | echter Whiteboardauftrag mit Kontext, Übernahme und Modellantwort; gültige Aktion bewirkt sichtbare Änderung. |
| BD-07.2 | dieselben Dateien, `myspace.js`, Prüfungen | 07.1 | Vorschlag auswählen/behalten/anwenden; ungültig/gesperrt/doppelt/veraltet/Abbruch sicher und sichtbar behandelt. |
| BD-08.1 | `tests/`, `docs/acceptance/` | 01–07 | echte Browserfolge über alle Module; DE/EN, Fokus, Zoom, kleinere Ausschnitte, Langtext und alle Fehlerfälle; Fehler beheben/wiederholen. |
| BD-08.2 | README, Abnahmebericht, bestehender Pre-Plan | 08.1 | startbarer Commit, Tastenhilfe, gewichteter Abschluss mit Belegen und Grenzen, Konzeptsicherung nach finaler Planänderung bestätigt. |

### Konflikte, Testvarianten und Rückmeldungen
Die historischen weißen 1280×768-Flächen und verzögerte Darstellung aus der README sind durch die Konzeptquellen und die spätere Zwei-Ansichten-/Desktop-Regel ersetzt. Der Destillat-Konflikt Struktur/Design ist damit für diesen Prototyp aufgelöst. Abstandsvorgabe/automatische Kinderverteilung bleiben laut BD-05 spätere Verfeinerungen. Browser können den Systemmauszeiger nicht beliebig versetzen; virtueller Greifer und relative Bewegung sind die festgelegte Umsetzung, kein behaupteter Systemzeigersprung.
A ist vorläufige, konfliktfreie Testtaste. Farbmodus zuerst, Helligkeit fein per Rad. Diese Festlegung bleibt austauschbar. Drag des Monitor-Kopfs oder Tastaturpfeile verschieben das Monitorfenster. Shift-Klick ergänzt/toggelt Auswahl, Entfernen der Primary macht die nächste ausgewählte Box zur Primary. Leerer Klick leert Auswahl; Monitor behält zuletzt gewählte Werte. Freie Typen werden als Textetiketten dargestellt, ohne erfundene Funktion.
Die allgemeine Workflow-Anweisung zur gegenseitigen neuen Codex/Grok-Session gilt für jene ausdrücklich beauftragte Konstellation; dieser direkte Auftrag verlangt keine neuen Sessions und verbietet Rekursion. Übernahme der laufenden Session ist durch direkte Zustellung und erste tatsächliche Arbeit belegt. Vorhandenen `whiteboard_feedback_watch.py` als begrenzten lokalen Timer nutzen, dessen Funktion mit kurzer Testfrist und die 60-Sekunden-Konfiguration separat nachweisen. Queue-Zustellung nur bei tatsächlich bestätigter Session-Verbindung behaupten; Whiteboard wird von dieser Session aktiv gelesen und Rückmeldungen read-back-geprüft. Kein automatisches Wecken dieser Chat-Sitzung behaupten.



## Technischer Abschlussstand · 14.10.2026
Implementiert im vorgesehenen Workspace, vorhandenes Remote `landjunge/blockdesign`, Branch `feat/modular-block-designer`, Produktversion 0.1.0. Geprüfter Produktcode `df2550390af3cd6c77b79cc5911d7c8c0b9e4d0f`; spätere Beleg-/Konzeptcommits ändern diesen geprüften Produktcode nicht. Start: `cd /Users/landjunge/blockdesigner && ./start.command`, Browser `http://127.0.0.1:5190`.

| Paket | Ergebnis / konkrete Abnahme |
| --- | --- |
| BD-01 | Hostmanifest/Modulkontext, tatsächliche Repository-Zuordnung, Start und Whiteboardzustellung nachgewiesen. |
| BD-02 | Ein Zustand/Revision, drei Ebenen, B=50×50 Mitte/+5, IDs/Nummern/Farben/Mitte, geordnete Auswahl und Erschöpfungsprüfung bestanden. |
| BD-03 | Nächster Mittelpunkt/Space/virtueller Greifer, relative Bewegung, D/F/D+F, proportionale Stufen, Minimum und harte Dokument-/Kindergrenzen bestanden. |
| BD-04 | 20/2→10/1, Kantenfang, positive Werte, frei beweglicher Monitor und letzter Wertestand, Dokumentzoom und echte Browservergrößerung bestanden. |
| BD-05 | Typen, Primary/T einschließlich Beschriftung, Farbtrennung, Gruppierung/Zuordnung/Zyklen, mitbewegte unskalierte Kinder und Modul-Hintergrundübernahme bestanden. |
| BD-06 | Struktur/Gestaltung aus einem Zustand; vorläufiges A/Farbe/Rad/Übernahme/Abbruch, Texteingabefokus und Modalität bestanden. |
| BD-07 | Echte lokale KI: task/read-back/claimed/progress/result → geprüfte sichtbare Änderung; echte Vorschläge → Behalten/Anwenden. Ungültig/doppelt/veraltet/Abbruch bestanden. Keine Stichwortdemo oder simulierte Erfolgsantwort. |
| BD-08 | Final 13 Kernprüfungen, 8 Adapterprüfungen, 11 Chrome-Abläufe und 3 echte Chrome-Vergrößerungen bestanden, einschließlich visueller Kinderprüfung. Auslieferungs-/Remote-/Sicherungsbeleg wird abschließend unter `bd-08` / `BD-08.2` geführt. |

Abnahmebericht: `/Users/landjunge/blockdesigner/docs/acceptance/REPORT.md`; maschinenlesbare Ergebnisse, echte KI-Auftrags-/Modellbelege, Screenshots und Whiteboard-Timernachweise daneben. 35 Prüfungen bestanden, keine offenen technischen Pflichtfehler. Die folgenden Grenzen sind erhalten: nur laufender Tab für Dokument/MySpace, lokale KI mit begrenzten deklarativen Aktionen und Kontext, keine Garantie der Absicht jeder freien Formulierung, kein Systemzeigersprung, keine automatische Kindskalierung; Mikrofon, Webseiten-/Dateiimport, Export/Speichern, Symbolbibliothek und MCP bleiben spätere Stufen. Andere Browser/Plattformen, native Apps und die anschließende Nutzerbewertung sind nicht geprüft. A und die nummerierte Palette v1 bleiben dokumentierte Testvarianten.

Praktische Korrekturen: fehlenden Playwright-Browser durch tatsächlich installierten Chrome ersetzt; falsche Prüfkoordinaten und Retina-Zoommessung korrigiert. Echte leere/ungültige Modellantworten nicht als Erfüllung gezählt; Systeminstruktion/Nutzerdaten und Kontextbudget bereinigt, partielle Schriftfelder mit Werterhalt validiert. Modulhintergründe zunächst über Kindern gezeichnet; in `df25503` Eltern hinter Kindern, danach Hit-/Sichtbarkeitsprüfung und echte KI-Folge erneut bestanden. Keine echte ungelöste Pflichtwiderspruchslage übrig: historische README/Weißfläche, verzögerte Sichtbarkeit und Mobilstapeln sind durch die späteren Konzeptpräzisierungen ersetzt; Vision und spätere Verfeinerungen bleiben erhalten.

Rückmeldebetrieb: aktive Codex-Session `01a13ae2-819a-7442-8789-a7e7c4f1cc94` hat den direkten Nutzerauftrag tatsächlich übernommen, erste Arbeit belegt und alle Schritte über Modulkontext zurückgemeldet. Bestehender Feedback-Watcher mit 60 Sekunden läuft für den Bau; zwei kurze Funktionsprüfungen erzeugten tatsächliche Nachfragen. Der lokale Wrapper drosselt dessen frühere CPU-intensive Poll-Schleife auf 250 ms, ohne die bestehende ThreadDesk-Quelldatei zu ändern. Belegte Betriebschecks im 40-Sekunden-Abstand; keine unbelegte Queue-/Voice-Zustellung behauptet. Der abschließende Gesamt-result beendet den begrenzten Timer. Keine weiteren oder rekursiven Agentenstarts.

Auslieferung ist erst nach erfolgreich geprüftem automatischem Abgleich dieser Planänderung und dem abschließenden Versions-/Whiteboard-result vollständig. Technische Erfüllung aller acht Pakete ist ausdrücklich keine vorweggenommene Nutzerakzeptanz oder vollständige Erfüllung der Gesamtvision.

## Verbindlicher Umbau · Nutzerauftrag 14.10.2026 · Version 0.2
Diese spätere Nutzerentscheidung ersetzt im aktiven Umfang die frühere Tab-Beschränkung und den Ausschluss des lokalen Speicherns. Export, Import, Mikrofon, Symbolbibliothek und MCP bleiben spätere Stufen. Produktname: **BlockDesigner**. Die Abnahme 0.1.0 oben bleibt historische Evidenz, keine Abnahme des Umbaus. Vorbestand sauber bei `181e893`, Remote `landjunge/blockdesign`; Umsetzung im vorhandenen Workspace auf `feat/compact-project-history`, keine Neuentwicklung/weiteren Projektkopien.

### Verträge und Entscheidungen
- Vorhandene Kern-, Render-, Panel- und Whiteboardmodule bleiben erhalten. Neues `shell/header.js` montiert die kompakte Kopfleiste; `shell/sidebars.js` verwaltet unabhängige Sichtbarkeit/Breiten; `shell/help.js` verwendet dieselbe `input/shortcuts.js`-Definition wie die Eingabe. ThreadDesk-Vorbild: nebeneinanderliegende DE/EN-Schalter aus `base.html`. Gemeinsamer unveränderter CSS-Kern, 40-Pixel-Bedienhöhe und bestehende Tokens bleiben; Platzersparnis durch Anordnung, keine unlesbar verkleinerten Knöpfe. Headerbeweglichkeit bleibt offene Idee.
- Mehrfachgreifen nimmt die geordnete gesamte Auswahl. Ausgewählte Eltern/Kinder werden in eine eindeutige Familienmenge aufgelöst, ein gemeinsamer Rasterversatz und gemeinsame Begrenzung erhalten Abstände. Einzelauswahl folgt weiter dem nächsten Mittelpunkt. D/F wirken wie bisher auf den gegriffenen Primary. Monitor benutzt Fensterkoordinaten und wird bei Fensteränderung erreichbar begrenzt. Sidebarpräferenzen/Monitorposition liegen versioniert im lokalen Browser, Dokumentdaten dauerhaft auf dem Mac.
- Rasteruntergrenze 0,25, Obergrenze 1000 Dokumentpixel; Halbieren/Verdoppeln ändern Abstand und Fangbereich gemeinsam. Schalter vor Grenzüberschreitung deaktivieren. Browserreproduktion 0.1.0: sechsmal Feiner ergibt 0,3125/0,03125; siebtes Klicken erzeugt invalidGrid. Erster Klick funktioniert im geprüften Bestand; darüber hinaus gemeldeter Fehler nicht behauptet reproduziert.
- `core/store.js`: atomare Aktionen plus Undo/Redo; Bewegung/Attributgeste und sämtliche Aktionen einer KI-Rückgabe jeweils ein Schritt. Revisionen bleiben beim Undo/Wiederherstellen monoton, damit alte Antworten niemals wieder aktuell werden. Ein Restore spielt keine Aufgaben erneut ab.
- `scripts/project_store.py` / `bridge/projects.js`: lokales Projektformat 1, getrennt vom unveränderten Boxformat 1. Vorhandene `ContentAddressedArtifacts` für unveränderliche Inhalte weiterverwenden; nur eigener Produktordner, keine fremde DB. Modulkontext `read_own_data`/`write_own_record` nur für eigene Speicheranbindung über deklariertes `projects:write`. Standard `~/Library/Application Support/BlockDesigner`, atomar veröffentlichte JSON-Commits mit SHA-256-Inhaltsverweisen, fsync/replace, Schreibserialisierung und optimistische Head-Prüfung gegen konkurrierende Tabs. Dokument, MySpace, Gespräch und Undo-Daten getrennt referenzieren; unveränderte Inhalte wiederverwenden. Keine automatische Löschung. Unterbrochene temporäre Schreibvorgänge ignorieren, beschädigte Commits erhalten und letzten lesbaren Stand anbieten. Unbekannte künftige Formate sichtbar ablehnen; Migrationen explizit ergänzen, Format 1 weiterhin lesen. Testdaten über ausdrücklich isolierten lokalen Speicherpfad, nie Nutzerprojekte überschreiben.
- Vor jedem Chatversand dauerhafter Vorher-Snapshot mit Auftrag/Task/Revision/Auswahl/Gesprächsbezug/Zeitpunkt/stabiler Kennung; erst danach Whiteboardversand. Ergebnis/Frage/Fehler/Verwerfen mit Bezug sichern. Vor KI-Übernahme Kandidaten atomar validieren und dauerhaft sichern; fehlgeschlagene Sicherung lässt Dokument unverändert. Normale Editoränderungen automatisch speichern, Fehler und ausstehende Speicherung sichtbar. Wiederherstellung sichert vorher den aktuellen Stand und erzeugt einen neuen Stand mit restore_of; neuere Stände bleiben sichtbar. Lokale Historie schützt nicht vor Ausfall desselben Datenträgers.
- Projektgespräch verwendet bisherige Aufträge, Resultate und aktuelle geordnete Auswahl. KI-Paket-Erweiterung versioniert/optional für alte Tests: Projekt-/Snapshot-/Gesprächsbezug und begrenzte relevante Vorgeschichte. Auswahlwechsel ausdrücklich kennzeichnen; nie frühere IDs als neue Ziele übernehmen. Wesentlich mehrdeutige Aufträge dürfen eine Rückfrage ohne Aktionen liefern. Antworten auf Rückfragen gehen als neuer Auftrag mit Bezug durch denselben Snapshotweg.
- Direkte kleine KI-Änderung ausschließlich bei genau einer Zielbox, ohne mitbetroffene Kinder, höchstens zwei geprüften Attributen; kurze eindeutige Beschriftung bis 80 Zeichen, oder eine einzelne Breiten-/Höhenänderung bis 10 Prozent. Alles Weitere erhält sichtbare räumliche/Attribut-Vorschau und Übernehmen/Verwerfen. Revision/Auswahl/Ebene beim Übernehmen erneut prüfen. Rückfrage und Vorschau sind keine angewendete Änderung. Technische Validierung ersetzt keine Garantie richtigen Sprachverständnisses.

### Abhängige kleine Schritte
Verantwortlich: aktive Codex-Session, Gesamt-task_id `bd-upgrade-20261014`; keine Agentenstarts. Je Schritt Übernahme/Fortschritt/Ergebnis mit gleicher step_id und Beleg im bestehenden Whiteboard. Bestehender begrenzter Feedback-Watcher, read-back-geprüfte Zustellung; keinen automatischen Neustart dieser Sitzung behaupten.
| Schritt | Dateien / Verantwortung | Abhängigkeit | Abschlusskriterium |
|---|---|---|---|
| BU-01 | bestehender Pre-Plan, Bestand/Verträge/Tests | keine | Quellen/Branch/Remote/ungesicherte Arbeit geprüft, Plan an Ort aktualisiert, Konzeptsicherung abgeglichen |
| BU-02 | shell, input, geometry/actions, monitor, CSS/index/i18n | BU-01 | Header/Sidebars/Hilfe/Fokus, Mehrfachbewegung, Raster/Monitor im Browser geprüft |
| BU-03 | project_store/server/host/manifest, projects-Bridge, store/History | BU-02 | dauerhafte Projekte/MySpace, Vorher/Ergebnis-Snapshot, Undo/Redo, atomarer Wiederanlauf/Fehler/Restore im Browser geprüft |
| BU-04 | bestehender AIAdapter/Whiteboard/AI-Space | BU-03 | Gespräch/Folge/Rückfrage/Vorschau/Verwerfen, sichere persistente Übernahme und echte lokale KI geprüft |
| BU-05 | bestehende und neue zielgerichtete tests, Architektur/README/Abnahme | BU-02–04 | echte durchgängige Browserregression, Zoom/DE/EN/kleines Fenster/Fehler, eindeutige Version und erfolgreicher finaler Konzeptabgleich |
Schritte gleich gewichtet; 100 Prozent erst nach allen Abschlusskriterien. Reiner Backend-Erfolg zählt nicht als Browserabnahme. Nutzerbewertung folgt separat.


## Gesprächs-Zwischenstand · 14.10.2026 · 18:58 Europe/Berlin

### Auftrag und Quellen
Der Nutzer hat den Umbau-Prompt erhalten; am 14.10.2026 wurde dessen vollständiger Inhalt in die Mac-Zwischenablage geschrieben und zurückgelesen (9135 Zeichen). Der bereits oben enthaltene Abschnitt „Verbindlicher Umbau · Nutzerauftrag 14.10.2026 · Version 0.2“ enthält den konkreten Ausführungsplan. Dieser Gesprächsstand ersetzt keine Implementierungsabnahme und startet keine zusätzliche KI-Session.

### Vollständiger besprochener Änderungsumfang
- Name BlockDesigner: ein Wort, B und D groß.
- Kompaktes eigenständiges Header-Modul: Ebenen, Struktur/Gestaltung, Raster, kompakter DE/EN-Wechsel nach ThreadDesk, Hilfe und Sidebar-Schalter. Verschiebbarkeit des Headers bleibt offene Idee.
- Beide Sidebars unabhängig aus-/einblendbar und in der Breite verstellbar; Workspace erhält frei werdende Breite. Sichtbarkeit und Breiten merken.
- H öffnet übersichtliche Hilfe mit sämtlichen tatsächlich verfügbaren Shortcuts; gemeinsame Definition mit Eingabesteuerung, Fokus-/Escape-Verhalten beachten.
- Shift-Mehrfachauswahl gemeinsam mit Space greifen, bewegen und absetzen; Abstände erhalten, Eltern/Kinder nicht doppelt bewegen, ganze Auswahl am Rand begrenzen.
- Monitor über gesamte App-Sicht frei verschiebbar; Position merken und nach Fensterverkleinerung erreichbar halten.
- Raster feiner/gröber mit kompakter Abstandsanzeige; gemeldeten Feiner-Fehler konkret prüfen. Behauptete Erstklick-Reproduktion nicht mit dem im Plan dokumentierten Grenzfehler verwechseln.
- Kompakte Farbauswahl und niedrig startende, automatisch wachsende und wieder schrumpfende Chateingabe; weniger Scrollbedarf.
- Dauertexte unter der Entwurfsfläche in Hilfe verlagern; wichtige Status-/Fehlermeldungen bei Bedarf zugänglich lassen.
- Projektbezogener KI-Gesprächsverlauf mit verständlichen Folgeaufträgen, Rückfragen bei wesentlicher Mehrdeutigkeit, Vorschau/Übernehmen/Verwerfen für größere Änderungen und klarer Status/Zielauswahl.
- Undo/Redo: zusammengehörige KI-Aktionen als ein Schritt, außerdem sinnvolle Gestengrenzen.
- Dauerhaftes Speichern/Wiederöffnen von Projekt und MySpace; automatische dauerhafte Snapshots vor jeder abgeschickten Chateingabe und zugehöriger Ergebnisstand nach Übernahme. Auftrag, Auswahl, Revision, Gesprächsbezug und Zeitpunkt erhalten.
- Frühere Stände wie eine lokale Wiederherstellungshistorie aufrufbar. Vor Restore aktuellen Zustand sichern; neuere Stände erhalten; Wiederherstellung als neuer Stand ohne erneute Ausführung alter KI-Aufträge. Speicherfehler sichtbar; keine ungesicherte KI-Übernahme. Kein Schutz vor Datenträgerverlust durch bloße lokale Snapshots behaupten.
- Für diesen, den nächsten und übernächsten Umbau: bestehende Module weiterverwenden, kleine Schnittstellen, eine Shortcutquelle, gemeinsame Design-Tokens, versionierte Datenformate/Migrationen, wiederverwendbare echte Nutzerablauf-Prüfungen und knappe aktualisierte Architekturdokumentation. Kein pauschales Refactoring, keine neue Frameworkschicht ohne Bedarf.

### Stand und Grenzen
Der Nutzer hat Version 0.1.0 grundsätzlich positiv bewertet, ausdrücklich ohne vollständige eigene Prüfung. Gemeldete Bedienprobleme sind Nutzerfeedback; die frühere technische 35-Prüfungen-Abnahme ersetzt diese Bewertung nicht. Im aktuellen Pre-Plan liegt bereits ein konkreter BU-01–BU-05-Umbauplan vor. Der jetzige Sicherungsschritt hat den laufenden Umbau weder verändert noch dessen Fortschritt oder Fertigstellung geprüft. Status ausschließlich aus aktuellen Code-/Abnahmebelegen ableiten.
Mikrofon, Webseiten-/Dateiimport, Export, Symbolbibliothek, MCP und native Apps bleiben spätere Ausbaustufen; lokales Speichern und Snapshots sind durch den aktuellen Auftrag jetzt ausdrücklich in den Umfang aufgenommen.

### Wiederfinden und Sicherung
Maßgebliche Quellen bleiben die drei BD-Dateien im bestehenden Ordner. Notion „Plan — Design Editor“ und „Brainstorm — Design Editor“ sind Wegweiser. Versionierte Sicherung unter landjunge/blockdesign/docs/concept; dort keine unabhängig gepflegte Konzeptkopie. Automatischer einseitiger Abgleich alle 300 Sekunden bei angemeldetem Benutzer; manuell über sync-concepts.py --verify. Konflikte/Fehler in .git/concept-sync-state.json prüfen, nicht überschreiben. Keine Garantie einer automatischen Wiederaufnahme dieses Chats.
