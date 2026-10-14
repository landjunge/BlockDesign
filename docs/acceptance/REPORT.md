# BlockDesigner 0.2.0 · technische Browser-Abnahme

Stand: 14.10.2026. Geprüfter Produktcode **d38415bc5fa77db039a682b2fa45bc8dcc901f25**, Branch `feat/compact-project-history`, vorhandenes Remote `landjunge/blockdesign`. Nachfolgende Konzept-/Belegcommits ändern diesen Produktcode nicht. Die [Abnahme 0.1.0](REPORT-v0.1.0.md) bleibt historisch erhalten.

**64 Prüfungen bestanden, 0 im endgültigen Prüfstand fehlgeschlagen.** Tatsächlich installierter Google Chrome 155 auf diesem Mac, echte Maus-/Tastaturbedienung mit Playwright. Browserzoom zusätzlich über die nativen Chrome-Einstellungen eines temporären Profils. Technische Abnahme ersetzt die anschließende Nutzerbewertung nicht.

| Prüfung | Bestanden | Fehlgeschlagen |
|---|---:|---:|
| Kern / Geometrie / Aktionen / Undo | 19 | 0 |
| KI-Verträge / Kontext / Antwortprüfung | 12 | 0 |
| Speichern / Recovery / Deduplizierung | 5 | 0 |
| Vorhandener Host / Modulrechte / Upgrade | 2 | 0 |
| Bisherige durchgängige Chrome-Abläufe | 11 | 0 |
| Neue Chrome-Bedien-/Projekt-/Gesprächsabläufe | 12 | 0 |
| Echte Chrome-Vergrößerung 125 / 150 / 200 % | 3 | 0 |

Die einzelnen Ablauf-IDs und Ergebnisse stehen in [v0.2.0-checks.json](v0.2.0-checks.json). Negative HTTP-Rückgaben sind ausdrücklich Sicherheitsfixtures und zählen nicht als echte KI-Erfolge. Sechs Browserabläufe enthalten tatsächliche Whiteboard-/Ollama-Aufträge; lokale Auswahlfragen sind als Produktrückfragen gekennzeichnet. Speicherfehler wurden durch wirklich verweigerte Schreibrechte im isolierten Testordner verursacht.

## Beobachtetes Ergebnis

- Kompakter eigener Header; 40-Pixel-Bedienhöhe und gemeinsamer Designkern erhalten. Sidebars unabhängig schaltbar und per Rand verstellbar, gesamte freie Breite geht an den Workspace. Palette kompakt, Chateingabe wächst und schrumpft. DE/EN, lange Texte, kleine Fensterausschnitte und Browserzoom bestanden.
- H zeigt alle tatsächlichen Kürzel aus derselben Definition wie die Eingabe. Texteingaben lösen keine Editoraktionen aus; Escape und Rückfokus funktionieren. Ctrl- und Mac-Cmd-Undo/Redo geprüft.
- Space bewegt die Mehrfachauswahl mit einem gemeinsamen begrenzten Versatz. Eltern/Kinder werden einmal bewegt. Einzelbedienung, D/F/D+F, Skalierung, Ebenen, T, Gruppierung und beide Ansichten bleiben bedienbar. Monitor ist über Header/Sidebars/Workspace beweglich, seine Position bleibt bei Verkleinerung erreichbar.
- Raster feiner/gröber ändert Abstand und Fangbereich gemeinsam; Dokumentwerte bleiben bei Zoom unverändert. Im Ausgangsstand funktionierte der erste Feiner-Klick; reproduzierbar fehlerhaft war der siebte Schritt unter die Untergrenze. Unzulässige Folgeschritte sind jetzt deaktiviert.
- Dokument, MySpace und Gespräch nach Reload erhalten; Projekt nach echtem Serverneustart geöffnet und zwischen Projekten gewechselt. Vor Chat dauerhafter Snapshot, nach Übernahme dauerhafter Ergebnisstand. Ansehen zeigt einen gespeicherten Entwurf. Restore sichert vorher den aktuellen Stand, erhält neuere Stände und startet keine alten Aufträge. Undo/Redo umfasst einen ganzen KI-Batch.
- Echte Folgeanweisung mit vorherigem Ergebnis/aktueller Auswahl, Auswahlwechsel, echte Modellrückfrage samt Antwort, Vorschau/Verwerfen/Übernehmen und echte Gestaltungsvorschläge mit MySpace bestanden. Ziele, Revision, Ebenen, ungültige/doppelte/veraltete Rückgaben und Verbindungsunterbrechung geprüft. Wirkungsloser Inhalt wird als „keine Änderung“ ausgewiesen.
- Fehlgeschlagene Vorher-Sicherung verhindert den KI-Versand. Fehlgeschlagene Ergebnissicherung lässt Boxen unverändert. Beschädigte/unterbrochene Commits führen zum letzten lesbaren Stand; Dateien bleiben erhalten. Konkurrierende Tabs überschreiben den neueren Stand nicht.

Frühere rote Zwischenläufe bleiben in den lokalen Prüfhistorien: Monitorüberdeckung, falsche Grid-Spalte beim Ausblenden, veraltete Prüf-Fokus-/Warteannahmen sowie Modellverwechslungen zwischen Aktionen/Vorschlägen sowie übernommenen und verworfenen Änderungen. Betroffene Abläufe nach Korrektur wiederholt. Im selben vorhandenen KI-Adapter erfolgen jetzt begrenzte lokale Absichtserkennung und passende Antworterzeugung. Keine simulierten Erfolgsantworten, kein weiterer Orchestrator oder Agent und kein Modellcode.

## Start und Wiederherstellung

`cd /Users/landjunge/blockdesigner` → `./start.command` → `http://127.0.0.1:5190`. Bei belegtem Port beispielsweise `--port 5193`. **H** öffnet die Tastenübersicht. Weitere Start-/Prüfbefehle in [README](../../README.md), Modul-/Datenverträge in [architecture.md](../architecture.md).

Projekte ausschließlich lokal unter `~/Library/Application Support/BlockDesigner/`. MySpace → Historie → Ansehen/Wiederherstellen. Unveränderte Inhalte werden über SHA256-Verweise wiederverwendet. Format 1, atomare Commitpublikation mit Dateisynchronisierung, Filelock/Head-Prüfung; frühere Format-1-Varianten bleiben lesbar. Keine automatische Löschung alter Stände. Neue Projektdaten, Auftragsbelege und Screenshots bleiben Git-ignoriert unter `.runtime/`.

## Grenzen / nicht geprüft

- Lokale Historie schützt nicht vor Ausfall desselben Datenträgers; keine externe Backupsicherheit. Physischer Stromausfall und Hardwaredefekt nicht getestet.
- Normale Eingaben werden nach 500 ms Ruhe gesichert; der Header zeigt ausstehende Sicherung. Bei abruptem Abbruch können noch ungesicherte Eingaben fehlen. KI-Versand und sichtbare KI-Übernahme benötigen zuvor erfolgreiche dauerhafte Sicherung.
- Lokales `llama3.2:3b` bleibt sprachlich fehlbar, Antwortzeit variiert. Kleine qualifizierte Einzeländerungen dürfen direkt angewendet werden; größere/mehrteilige Antworten benötigen die Vorschauentscheidung. Kontext und Rückfragen sind keine Garantie jedes freien Sprachverständnisses. KI-Kontext ist begrenzt; zu große Aufträge werden sichtbar abgelehnt, nicht still gekürzt.
- Keine automatische Kindskalierung, kein Systemmauszeigersprung. Mikrofon, Import/Export, Symbolbibliothek und MCP bleiben spätere Ausbaustufen. Headerbeweglichkeit bleibt eine offene Idee.
- Andere Browser/Betriebssysteme, native Anwendungen und die anschließende Nutzerbewertung nicht geprüft. Keine externen technischen Blocker im abgenommenen Umfang.

Rückmeldebelege liegen im bestehenden Whiteboard und lokal. Die erste Timer-Auslöseprobe erzeugte tatsächliche Nachfragen. Ein Teilergebnis hatte den ersten Gesamttimer vorzeitig beendet; anschließend Schrittkennungen getrennt und den vorhandenen 60-Sekunden-Watcher neu gestartet. Keine durchgehende ursprüngliche Timerlaufzeit oder automatische Wiederbelebung dieser Sitzung behauptet.
