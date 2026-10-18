# BlockDesigner – BD-C01 / D01 / R01 · 18.10.2026

Auftrag `seven-tools-build-20261018-1833`; tatsächlicher Codex-Unteragent
`threaddesk_m1`, abgegrenzt auf BlockDesigner. Privates Remote nachgelesen:
`landjunge/blockdesign`. Canonical Root und fremde Sitzungen unverändert.
Eigener Worktree `.worktrees/seven-tools-20261018`, Branch
`feat/seven-tools-consolidation-20261018` von Produktstand
`135741679fc8c92fe15804d94aa47bed3a4c0636`.

## Bestand und Integration

main `0bf820969e8eb6d5b7db134bf91ce08b3f0ff6c9` ist echter Vorfahr des
vollständigen Produktstands und enthält den historischen Ein-Datei-Prototyp.
Der Konsolidierungsbranch verwendet die vorhandenen0.2-Module; Ebenen, IDs,
monotone Revision, Undo/Redo, MySpace, Projekte/atomare Historie und bestehende
Whiteboard-/Ollama-Aufträge wurden nicht neu implementiert. Der private PR
führt diese Linie Richtung main; bis tatsächlichem Merge gilt Integration als
ausstehend. Keine Repo-Umbenennung, öffentliche Freigabe oder Release.

Drei maßgebliche Originalkonzepte im bestehenden ThreadDesk-Ordner vollständig
gelesen. Repository-Sicherung byteidentisch; keine divergierende Konzeptkopie:

| Original | SHA256 |
|---|---|
| BD Ziel Idee.md | cf67c4bc594b2f89147899805b93042bfd473205e6d0dcfbf564c80a4d17c13a |
| BD Brainstorm Destillat.md | a8557fb6a210c8be4905e8db86af86070cd352493a9072c2fa8e4a58a7c3cea9 |
| BD Pre-Plan.md | 885114089f5a3085edec751e7315f7d2d04dc9b19bd29e64a09c889080e0bdd8 |

NP-Basis war bereits identisch mit aktueller TG-/FP-Kopie:
Gitblob `673f4e265c8c46618ba86d9e98f8da09fd0bf107`, SHA256
`98371bd9edc96fb940a0e0de34933740fed1062b510aa516498fcb53e112591e`.
Kein neuer Designkern, keine zusätzlichen Logos oder Toolbar.

## Konkrete Korrekturen

- Start verwendet vorhandenen Pythoninterpreter im PATH oder explizit BD_PYTHON,
  nicht einen fest verdrahteten Nutzer-/Intelpfad. `--check`/`--help` bleiben lesend;
  fehlender Interpreter, inkompatibler ThreadDesk-Source, Registry und Bindung
  werden verständlich vor Setup/Serverstart eingeordnet. Kein Installieren/sudo.
- Reeller Rechtefehler behoben: explizites oder automatisches setup aktivierte
  bisher ein bereits deaktiviertes Modul erneut. Nur eine neue eigene Installation
  wird aktiviert; deaktivierter Bestand bleibt gesperrt. Bestehende Bindungen
  werden nicht überschrieben. Rechte-/Quellenwahl bleibt Operatorentscheidung.
- Die vorhandenen Undo/Redo-Buttons tragen entsprechend Originalbeschluss gebogene
  Pfeile, lokalisierte DE/EN-Aria-Namen und Titel. Dieselbe bestehende Aktion,
  Tastatursteuerung und40px-Höhe; keine zweite History oder Undo-Logik.
- README/Architektur trennen Quelllinie, historische Abnahme, derzeitigen Start,
  Editorfenster, Dokumentmaße/Zoom und Zielseiten-Viewport. DE/EN-Kernbedienweg.
- [Vorbereiteter Vertrag](../contracts/design-source-v1.md) plus JSON-Schema für
  spätere context.design-Erweiterung des vorhandenen ThreadDesk-Handoffs:
  Quellhash/optionalerCommit, Snapshot/Revision, Referenzviewport, genaue Box- und
  Elementzuordnung move/replace/new, unaufgelöster Bezug→Rückfrage, inerte Vorschau.
  Keine laufende HTML-/MCP-/Bridge-Implementierung dadurch behauptet.

## Tatsächlich geprüft

Gezielt3 neue Startup- und2 vorhandene Host-/Rechtegrenzfälle bestanden:
fehlender Source legt keinen Workspace an, fehlender Interpreter startet nicht,
deaktiviertes Modul bleibt inklusive bestehender Registrybytes unverändert;
bestehendes Manifestupgrade erhält Daten/Rechte, deaktivierter Host verweigert
Kontextzugriff. Ruff auf neuen Prüf-/Startdateien; JavaScript-Syntax auf geändertem
Header/i18n; JSON-Syntax des vorbereiteten Schemas; git diff --check.

`tests/consolidation_browser.py`: echter Google Chrome155.0.8059.85 auf diesem
Mac, temporärer Whiteboard-/Projekt-/Taskworkspace, eigener Loopbackserver auf
freier Portnummer. Keine Userprojekte oder fremden Prozesse verändert. Belegt:

- `--check` meldet fehlende Bindung, ohne Workspace zu erzeugen; isoliertes Setup
  und anschließender Bereitschaftsabruf funktionieren über neuen normalen Start.
- Tatsächlicher modularer Einstieg lädt ohne JavaScriptfehler; B erstellt50×50,
  drei Ebenen bleiben getrennt bedienbar; echte Undo/Redo-Buttons wirken.
- DE/EN-Namen und40px-Kontrollen, Hilfedialog/Escape/Rückfokus.
- Dokument1000×640 bleibt bei150%Darstellungszoom unverändert;1180×760Fenster
  bleibt mit derselben Editor-Komposition und schaltbaren Sidebars erreichbar.
- Private `.runtime`-Datei wird404 abgelehnt, fremde POST-Origin403.

14 benannte Assertionsgruppen in `.runtime/consolidation-20261018/<run>/checks.json`,
Screenshots `desktop-de.png`, `desktop-en.png`, `small-window.png` im selben Laufordner. Sie wurden
visuell angesehen; Monitor, Hauptarbeitsfläche und gebogene Headeraktionen klar,
fehlende KI-Verbindung tatsächlich als Text ausgewiesen. Neue Belege bleiben wie
bisher lokal ignoriert. Aktuell keine neue Modellinferenz; `ai_requests_sent=0`.
Die erste Versionierung der Probe hatte einen Harnessfehler: ein String-Prädikat
in Playwright verlangte unter der bestehenden CSP verbotenes unsafe-eval. Nur
das Prüfprädikat wurde zur Funktion geändert, CSP unverändert. Der fehlgeschlagene
Lauf ist separat dokumentiert; Folgeproben erhalten eindeutige Laufordner und
speichern Fehlerstatus, statt frühere Belege zu überschreiben. Die korrigierte
versionierte Probe wurde erneut tatsächlich ausgeführt.
Diese Probe wiederholt nicht die historische vollständige64-Prüfungen-Abnahme.

## Lieferstand und Grenzen

Implementiert und gezielt geprüft; private Main-Integration/Review bis Merge
separat. Keine neue Nutzerabnahme, laufende Nutzereinrichtung, Plattform-/Native-
Abnahme, Veröffentlichung oder garantierte KI-Verfügbarkeit. Neues Setup und
Server wurden ausschließlich im isolierten Worktree geprüft; gesundes bestehendes
Nutzersystem nicht neu eingerichtet. Die lokale Historie bleibt kein externes
Backup; ältere Daten/Belege erhalten.

BD-C02–04 und der vollständige neue D01-Import-/Element-/Rückvorschauzustand hängen
von der noch zu bauenden Quellen-/Auftragsanbindung ab. Der hier geprüfte D01-Anteil
ist vorhandener Produkt-/Familienabgleich plus konkret korrigierte Headerbedienung.
HTML-Import, Elementmapping, Webseitenexport, Mikrofon oder MCP werden nicht als
vorhanden umetikettiert. Gültiger Source-Vertrag ist Vorbereitung, keine Abnahme.
