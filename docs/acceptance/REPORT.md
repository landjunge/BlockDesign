# Technische Browserabnahme · Block Designer 0.1.0

Geprüfter Produktcode: `df2550390af3cd6c77b79cc5911d7c8c0b9e4d0f` (nach `7101aee` mit korrigierter Zeichenreihenfolge). Spätere Auslieferungscommits enthalten Konzeptabgleich und Abnahmebelege. Releasekennung: `v0.1.0`, Branch `feat/modular-block-designer`, Remote `landjunge/blockdesign`.

Umgebung: dieser Mac, Google Chrome 155.0.8059.40, vorhandene ThreadDesk-Playwright-Installation, Python 3.12, statische ES-Module ohne Framework/Buildschritt. Synthetische Dokumente und echte lokale Ollama-Aufrufe mit `llama3.2:3b`. Vorhandener Modulhost `/Users/landjunge/threaddesk-worktrees/ordinal-lock/src` bei `3b6f3fa`; gemeinsamer Designkern unverändert von `b0b6815`.

## Ergebnis und Paketzuordnung

13 Kernprüfungen, 8 Adapterprüfungen, 11 durchgängige Chrome-Browserfälle und 3 native Chrome-Zoomstufen bestanden: **35 Prüfungen**. Aktuell fehlgeschlagen: **0 Pflichtfälle**. Alle acht Pakete einschließlich echter KI-Anbindung technisch erfüllt. Die Auslieferung wird mit dem abschließenden Whiteboard-result für `bd-08` / `BD-08.2` und der geprüften Remoteversion belegt. Dies ersetzt die anschließende Nutzerbewertung nicht.

| Paket | Status | Beleg |
| --- | --- | --- |
| BD-01 · Host/Start/Repository | bestanden | `module.json`, `start.command`, `docs/architecture.md`; echter Start/read-back im Whiteboard |
| BD-02 · Zustand/Ebenen/Erstellen | bestanden | `BD-02-BROWSER`, Kern: Identität/Versatz/Erschöpfung; sichtbare 1-Pixel-Mitte |
| BD-03 · Greifen/Bewegen/D/F/Skalieren | bestanden | `BD-03-AXES`, `BD-03-BOUNDS`; D+F ohne Größenänderung, 4 px und proportionale Randbegrenzung |
| BD-04 · Raster/Monitor/Zoom | bestanden | `BD-04-GRID-MONITOR-ZOOM`, `native-zoom.json`; 20/2→10/1, freie Monitorposition, letzte Werte |
| BD-05 · T/Typen/Kinder | bestanden | `BD-05-TRANSFER-CHILDREN`; Primary, Textübernahme ohne Identitätsverlust, Gruppierung, Kindbewegung ohne Skalierung; Kinder bleiben in Gestaltung sichtbar |
| BD-06 · Ansichten/Attributtest | bestanden | `BD-06-ATTR-FOCUS-VIEWS`; A/Farbe/Rad/Übernahme/Escape, gemeinsamer Zustand, Fokus/Modalität |
| BD-07 · echte KI/Vorschläge/Schutz | bestanden | `BD-07-LIVE-CHANGE`, `BD-07-LIVE-PROPOSALS`, beide ausdrücklich gekennzeichneten negativen Fixturefälle, 8 Adapterprüfungen |
| BD-08 · Gesamtintegration/Auslieferung | bestanden | gesamter finaler Browserlauf, native Vergrößerung, Codeversion, bestehender Plan und Konzeptsicherung; abschließender Zustell-/Remote-Beleg im Whiteboard |

[Browserergebnisse](browser-results.json), [Kernprüfungen](core-results.txt), [Adapterprüfungen](adapter-results.txt), [native Browservergrößerung](native-zoom.json), [Whiteboard-Zustellung und Timer](whiteboard-evidence.json).

## Tatsächliche Bedienung und echte KI

`BD-07-LIVE-CHANGE` führt in einem Tab Ebenenwahl/Erstellung, Space/Bewegung, D/F/D+F, Skalierung, Rasterverfeinerung, Typ/Beschriftung, Shift/T, fachliche Gruppierung, A-Farbtest und beide Ansichten aus. Anschließend wird ein Kind explizit ausgewählt und tatsächlich über das Whiteboard beauftragt. Die lokal generierte, validierte Aktion beschriftet genau diese Box mit „Weiter“; die Änderung ist in der Gestaltungsansicht und im Attributpanel sichtbar.

`BD-07-LIVE-PROPOSALS` fordert zwei unterschiedliche Buttongestaltungen an. Die echte Modellantwort liefert blaue und orange Gestaltungsvorschläge. Ein Vorschlag wird angesehen, in MySpace behalten und daraus auf die aktuelle Auswahl angewendet. Kein simuliertes Ergebnis und kein Stichwort-Befehlsparser.

Die Belege enthalten task_id, Ausgangsrevision, Box-IDs, tatsächliche Modell-/Token-/Dauermetadaten, Antwortdigest und Whiteboard-task/claimed/progress/result. Der Adapter liest denselben unveränderlichen Task vor Ausführung zurück. Negative JSON-/Netzwerkfixtures prüfen ausschließlich Ablehnung, Veraltung, Idempotenz und Wiederverbindung und zählen nicht als echter KI-Erfolg.

[Ergebnis des echten Auftrags](live-ai.json), [sichtbare Änderung](live-ai.png), [echte Vorschläge](live-proposals.json), [MySpace und Anwendung](live-proposals-myspace.png).

## Ergänzende Prüfungen

- DE/EN, Referenz 1440×900, Mindestfläche 1180×760, kleiner Ausschnitt 900×600; unveränderte Spaltenkomposition, Aktionen per Scrollen erreichbar, 40-px-Bedienhöhe.
- Lange Beschriftungen und freier Typ; Text bleibt Text, kein ausgeführter eingebetteter Inhalt.
- Kürzel lösen in Text-/Select-Fokus und Dialogen keine Boxaktion aus; Dialogfokus hinein/zurück, Escape schließt.
- Dokumentzoom und native Chrome-Vergrößerung 125/150/200 Prozent: echte Chrome-Einstellung in frischem temporären Profil, gemessene Retina-DPR 2,5/3/4; relative Bewegung liefert unveränderte Dokumentwerte (495,315), 50×50 px bleiben 50×50 px. Alle benötigten Aktionen erreichbar.
- Falsche Ziele, Identitäts-/Ebenen-/Zuordnungsänderungen, ungültige Farben/Schriften, nichtendliche Werte, Mindestmaß/Ränder, Rastergrenzen, Elternzyklen und große Kontexte werden abgelehnt. Batches bleiben atomar.
- Doppelte Rückgabe wirkt nicht zweimal; veraltete Antwort bleibt sichtbar zurückgestellt. Verbindungsabbruch zeigt unbekannten Ausgang; „Status abrufen“ holt denselben Auftrag, startet keinen neuen.
- Modulbewegung begrenzt die ganze Familie; Modulskalierung verändert Kinder nicht. Modul-Hintergrundentscheidungen erhalten Kindidentität/Text/Geometrie. Partielle Schriftpatches erhalten ungenannte Werte.
- Bestehender Feedback-Watcher tatsächlich gestartet. Zwei kurze 2-Sekunden-Funktionstests erzeugten echte Whiteboard-question-Einträge; der Bau-Timer lief mit 60 Sekunden. Factual operating pings im 40-Sekunden-Abstand wurden zugestellt und zurückgelesen. Eine CPU-intensive alte Poll-Schleife wurde nur im lokalen Wrapper auf 250 ms gedrosselt, die bestehende Quelle blieb erhalten. Keine behauptete automatische Wiederbelebung dieser Chat-Sitzung oder unbewiesene Queue-Zustellung.

## Gefundene und behobene Probleme

Der alte Ein-Datei-Prototyp war syntaktisch defekt und nutzte nur Stichwörter. Er wurde durch getrennte Module und den echten Whiteboard-Adapter ersetzt; im Git-Verlauf bleibt er erhalten.

Ein erster Playwright-Start scheiterte am fehlenden gebundenen Chromium-Paket. Die vorzeitige Whiteboard-Erfolgsmeldung wurde ausdrücklich korrigiert; alle Abnahmen verwenden den tatsächlich installierten Chrome. Zwei Prüfkoordinaten lagen außerhalb des Fensters bzw. des bei 150 Prozent sichtbaren Dokuments; diese Prüffehler wurden berichtigt und die Fälle wiederholt. Native Zoommessung wurde auf die vorhandene Retina-DPR kalibriert.

Erste Modellantworten waren leer, zu langsam, hatten falsche IDs oder eine unvollständige Schriftangabe. Sie wurden nicht angewendet und nicht als Erfolg gezählt. Ein längerer statischer Antwortvertrag und die kleinste 1b-Variante waren für den Gesamtauftrag ungeeignet. Der endgültige Adapter trennt Systeminstruktion/Nutzerdaten, gibt nur relevante Zielattribute/Kindergeometrie an das vorhandene 3b-Modell, reserviert Kontextplatz und unterstützt geprüfte partielle Schriftpatches. Die erfolgreichen finalen Durchläufe belegen das gewählte Produktprofil. Es gibt keinen automatischen Modell-/Anbieter-Fallback und keine globalen Modelländerungen.

Bei der visuellen Nachprüfung einer zunächst grünen Suite verdeckte der Modulhintergrund seine Kinder. `df25503` ordnet Eltern vor Kindern. Eine echte Hit-/Sichtbarkeitsprüfung wurde ergänzt und die betroffenen Abläufe einschließlich des echten KI-Endpunkts wiederholt. Alte Fehlerscreenshots und `browser-history.jsonl` sind historische Diagnosebelege, keine offenen aktuellen Fehler.

## Nicht geprüft und Grenzen

| Gegenstand | Status / Grenze |
| --- | --- |
| Nutzerbewertung / gesamte Vision | nicht geprüft; folgt durch den Nutzer |
| Safari, Firefox, Windows, Linux | nicht geprüft; technische Abnahme dieses Mac mit Chrome |
| Mikrofon, Webseiten-/Dateiimport, Export/Speichern, Symbolbibliothek, MCP, native Apps | außerhalb des aktuellen Pre-Plans, nicht implementiert und nicht als geprüft ausgegeben |
| MySpace/Dokument nach Tabende | bewusst keine Persistenz/Exports im Prototyp; nur laufender Tab |
| Automatische Kinderverteilung/Abstandsvorgaben/Kindskalierung | spätere Verfeinerungen; Kindskalierung ausdrücklich ausgeschlossen |
| Attributtaste/Palette | A und nummerierte Palette v1 sind dokumentierte vorläufige Testentscheidungen |
| Lokale KI | benötigt den vorhandenen ThreadDesk-Checkout, Ollama und installiertes 3b-Modell; unterstützt deklarative Box-/Rasteraktionen und Styles, keine beliebige Werkzeugausführung |
| Modellqualität | validierte Syntax/Rechte/Werte garantieren nicht die inhaltliche Absicht jeder freien Formulierung; fehlerhafte Antworten werden sichtbar zurückgestellt/abgelehnt, keine Visionserfüllung behauptet |
| Umfang/Timeout | konservativer Kontext-/Metadatenrahmen, höchstens ein Auftrag, begrenzte Ausgabe und 180-s-Aufruf; Timeout beweist keinen sofortigen internen Inferenzstopp. Kein blindes Retry. |
| Systemmauszeiger | Browser versetzt ihn nicht; virtueller Greifer und relative Bewegung geprüft |

Startweg und Tastenübersicht stehen in der [README](../../README.md), die implementierten Schnittstellen im [Modulvertrag](../architecture.md). Die maßgeblichen Konzepte bleiben ausschließlich im bestehenden ThreadDesk-Ordner gepflegt; `docs/concept` erhält nur den automatischen Abgleich.
