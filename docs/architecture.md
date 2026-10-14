# Modul- und Startvertrag · Block Designer 0.1.0

Der verbindliche Bauplan steht im bestehenden **BD Pre-Plan.md**. Diese Datei beschreibt die implementierten Schnittstellen, keine konkurrierende Planung.

## Host

`start.command` startet einen Loopback-HTTP-Host auf 127.0.0.1:5190; alternative Ports sind explizit. Der vorhandene Python-3.12-Interpreter und ThreadDesk-Checkout `/Users/landjunge/threaddesk-worktrees/ordinal-lock/src` (Commit `3b6f3fa`) sind Laufzeitvoraussetzungen. `BD_THREADDESK_SOURCE` und `BD_WHITEBOARD_ROOT` dienen einer ausdrücklich gewählten anderen/testweisen Hostbindung, nicht dem Auftragstext. Der Server nimmt keine Host-/Repository-/Modellwechsel aus Modellantworten an.

`module.json` entspricht ThreadDesks `ModuleManifest` v1. `ModuleRegistry` installiert und aktiviert ausschließlich `block-designer`, `ModuleRuntime` isoliert dessen Aktionen, `ModuleContext` gewährt nur `whiteboard:read` und `whiteboard:append`. Kein Zugriff auf fremde Datenbanken, keine zusätzlichen Kernrechte und kein zweiter Orchestrator. Der vorhandene Store des gepinnten Checkouts serialisiert Whiteboard-Appends. Der Adapter liest keine fremden Thread-Inhalte. Die erstmalige Einrichtung legt einen eigenen Block-Designer-Thread an und erhält den vorher gewählten Thread.

Lokale Bindung und Aufgabenjournal liegen in `.runtime/`, sind Git-ignoriert und werden nicht statisch ausgeliefert. Das Journal verhindert erneuten Modellstart für dieselbe Task-ID; andere Daten unter derselben ID werden abgelehnt. Beim Serverneustart bleiben unklare laufende Aufgaben zurückgestellt und werden nicht automatisch neu gestartet. Das Journal ist kein Speichern-/Exportfeature für Dokumente.

## Browsermodule

| Dateien | Schnittstelle |
| --- | --- |
| `core/model.js` | Datenvertrag v1, Boxidentität, gemeinsame Patchvalidierung, Ebenen-/Wert-/Zyklengrenzen |
| `core/geometry.js` | Reine Mittelpunkt-, Fang-, Bewegungs-, Resize- und Skalierungsfunktionen |
| `core/actions.js` | Atomarer Reducer; ein dokumentbezogener Zustand und Revision, keine DOM-Zugriffe |
| `core/store.js` | `getState()` liefert eine Kopie; `dispatch({version:1,type,…})`; `subscribe(fn)`; Ablehnung verändert keine Boxdaten |
| `input/controller.js` | Maus/Tasten/Fokus, virtuelle Greifposition und relative Bewegung; keine eigene Boxkopie |
| `workspace/render.js` | Struktur und Gestaltung aus demselben Zustand, stabile DOM-Knoten mit Box-ID; Dokumentkoordinaten↔Darstellungskoordinaten |
| `workspace/layers-grid.js` | Ebenen-/Raster-/Zoomsteuerung über Kernaktionen |
| `workspace/monitor.js` | Frei platzierbare Darstellung der zuletzt explizit gewählten/gegriffenen Box; Werte bleiben nach Absetzen/Leerauswahl |
| `panels/selection.js` | Typ/Beschriftung, Primary/T, Gruppierung/Zuordnung, A-Palette |
| `panels/myspace.js`, `proposal.js` | Behalten und explizit anwenden aus dem einen Tabzustand; keine parallelen Boxdaten |
| `panels/ai-space.js` | Texteingabe, sichtbare Aufgaben-/Verbindungszustände und Vorschlagsauswahl |
| `bridge/whiteboard.js` | JSON-HTTP-Vertrag, zweite Rückgabeprüfung, Revision/Task/Zielbindung, Idempotenz und Veraltungsanzeige |
| `app.js` | Einmalige Montage der Module und Dialogfokus |

Softwaremodule sind von fachlichen Modulboxen verschieden. Fachliche Module sind Eltern im Boxmodell; Kinder müssen zur gleichen Ebene gehören. Gruppierung erzeugt eine räumlich passende Elternbox. Zuordnung ist zyklusfrei und bei Zuordnung auf enthaltene Kinder beschränkt. Nach einer Modulverkleinerung dürfen Kinder über die Elternfläche hinausragen, bleiben aber innerhalb der harten Dokumentgrenzen; es gibt keine automatische Kindskalierung. Explizite Hintergrundentscheidungen eines Moduls (Grundfarbe/Palette/Helligkeit) gelten auch für dessen Kinder; Text, Schrift, Identität und Geometrie werden dabei nicht automatisch übernommen.

Die Dokumentrevision ändert sich bei semantischen Box-/Auswahl-/Ebenen-/Rasteraktionen. Ansicht, Zoom, Monitorposition und flüchtige Attributvorschau ändern sie nicht. Loslassen von A übernimmt den Vorschauwert atomar und erhöht die Revision einmal. Texteingabefokus, Modalität, Fensterverlust und versteckter Tab beenden bzw. verhindern die entsprechende Motorik. Die Mindestgreiffläche ist 28 CSS-Pixel unabhängig vom Dokumentzoom.

## KI- und Whiteboard-Vertrag

POST `/api/tasks`: `task_id`, `instruction`, `box_ids`, `revision`, `snapshot`. Der Snapshot enthält Dokumentmaße, tatsächliche Boxattribute, aktive Ebene, geordnete Auswahl, Raster, Zoom und Sprache sowie explizit Ursprung (0,0), X rechts, Y unten, Einheit px, Pixelmaßstab 1. Es werden keine Positionen aus Bildern geschätzt. Ein Greif-/Attributvorgang muss vor Auftrag abgeschlossen sein.

Der vorhandene lokale Whiteboard-Service erhält den Task. Der Adapter liest denselben Eintrag durch den Modulkontext zurück, validiert die Bindung erneut, meldet `claimed` und startet **keinen Agenten**, sondern einen begrenzten Aufruf des vorhandenen lokalen `services.ollama_local.complete`-Transports. `ai-config.json` wählt das vorhandene lokale Modell ausschließlich für diesen Produktadapter. Globale Hausmeister-Einstellungen bleiben erhalten.

Modellantwort: `summary`, `actions`, `proposals`. Die Antwort ist untrusted data. Zulässige Aktionen:

- `patch`: exakt beauftragte `box_id` und erlaubte `changes`; kein ID-/Nummer-/Orientierungsfarben-/Ebenen-/Zuordnungswechsel.
- `scale`: exakt beauftragte `box_id`, endlicher positiver Faktor bis 10, proportional insgesamt durch Mindestmaß und Dokumentgrenzen begrenzt.
- `grid`: positive Rasterweite 0,25–1000 px und Fangbereich 0 bis halbe Rasterweite.

Patchattribute: x/y, Breite/Höhe, Rundung, Gestaltungsfarbe als #RRGGBB, Paletteverweis, Helligkeit, Gestaltungsrahmenfarbe/-breite, Systemschriftfamilie/-größe/-farbe, Beschriftung, Typetikett. Keine HTML-/CSS-/JavaScript-Ausführung aus Modelltext. Schriftfamilien sind eine feste Liste. Schriftpatches dürfen eine nichtleere Teilmenge aus family/size/color enthalten; ungenannte Werte bleiben vom aktuellen Ziel erhalten, der resultierende Dokumentzustand enthält stets vollständige Schriftattribute. Vorschläge enthalten Titel, Beschreibung und validierte Styleattribute ohne Position. Alle Änderungen werden vor dem Whiteboard-result auf einem temporären Dokument durchgerechnet; ungültige Batches werden vollständig verworfen.

Der Adapter bindet Rückgaben an vertrauenswürdige Task-ID, Revision und Box-IDs, vergibt Vorschlagsidentitäten, protokolliert Modell-/Token-/Dauermetadaten und einen Antwortdigest. GET `/api/tasks/{id}` liest diesen Status. Der Browser prüft dieselbe Bindung und aktuelle Ebenensperren/Geometrie erneut. Änderungen werden atomar über den Kern angewendet. Eine empfangene Rückgabe wird nicht zweimal verarbeitet. Eine veraltete Rückgabe verändert das Dokument nicht und bleibt rechts sichtbar. Explizit ausgewählte Vorschläge können nach neuer Ziel-/Wertprüfung im aktuellen Zustand eingesetzt werden.

Es läuft höchstens ein Modellauftrag je Host. Fehler und Verbindungsverlust führen zu sichtbaren Zuständen; Statusabfrage startet keinen neuen Auftrag. Ein Timeout beendet die lokale Annahme des Ergebnisses, beweist nicht den sofortigen Stopp der internen Ollama-Inferenz. Kein automatischer Retry oder Wechsel auf externe Schlüssel/Anbieter. Das bestehende Whiteboard begrenzt Metadaten auf 16k Zeichen; der Produktadapter reserviert dafür Platz und lehnt zu großen Kontext sichtbar ab. Keine still gekürzten Koordinaten oder Beschriftungen. Der Modellprompt enthält die tatsächlich relevanten Ziele mit Attributen und Kindergeometrie; die vollständige Dokumentstruktur bleibt im Whiteboard-Auftrag. Eine konservative UTF-8-Byte-Obergrenze reserviert im 4096-Token-Modellkontext auch Antwort- und Nachrichtenplatz; zu große Modellkontexte werden vor dem Aufruf sichtbar abgelehnt.

Die lokale Chat-API und ihr JSON-Ausgabeformat wurden gegen [Ollama Chat](https://docs.ollama.com/api/chat) und [Structured Outputs](https://docs.ollama.com/capabilities/structured-outputs) geprüft. JSON-Format ersetzt nicht die unabhängigen Produktvalidatoren. Eine getestete grammatische Beschränkung der IDs führte bei der kleinsten Modellvariante zu schlechteren Vorschlagsantworten und wurde verworfen; maßgeblich sind die unabhängigen Ziel-/Wertvalidatoren.

## Design und offene Testvarianten

`styles/networkpunkt.css` ist unverändert von ThreadDesk `b0b6815`, SHA-256 `98371bd9edc96fb940a0e0de34933740fed1062b510aa516498fcb53e112591e`. `blockdesigner.css` ergänzt Produktflächen und den bearbeiteten Inhalt, keine konkurrierenden UI-Tokens. Systemschrift 12/14/16/24, 40 px Bedienhöhe, feste Desktopspalten, versteckte Scrollbalken bei erhaltener Scrollbarkeit.

Für die 16 Grundfarben war in den geprüften vorhandenen Ressourcen keine vollständige verbindliche nummerierte Palette enthalten. Vorläufige Palette v1 in `core/palette.js`: Schwarz, Grau, Silber, Weiß, Dunkelrot, Rot, Orange, Gelb, Oliv, Grün, Hellgrün, Petrol, Cyan, Dunkelblau, bestehendes Produktblau #42a5f5, Violett. Paletteverweise und Helligkeit werden gemeinsam verwendet; Orientierungsfarben stammen unabhängig aus einer hellen eindeutigen Huefolge.

A ist ausdrücklich vorläufige Testtaste, Farbe zuerst, Rad=Helligkeit. Checkboxen übernehmen keine Beschriftung/Schrift über T; die übrigen texttragenden Typen tun dies. Der Systemmauszeiger wird im Browser nicht versetzt. Dokument 1000×640 px, initial 75% Zoom, Fenstergrößen ändern die Dokumentmaße nicht.
