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
Plan konsolidiert. Noch kein Whiteboard-Bauauftrag zugestellt und keine ausführende KI-Übernahme bestätigt. Nächster Schritt: bestehende Partner/Session prüfen, BD-01 mit konkreten Teilaufgaben übergeben und den oben beschriebenen Rückmeldezyklus tatsächlich beobachten.
