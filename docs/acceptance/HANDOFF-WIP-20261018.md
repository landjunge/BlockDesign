# BD-C04 – lokaler Zwischenstand vor Internetunterbrechung

Auf ausdrückliche Pause durch Root am18.10.2026 lokal gesichert. **Nicht fertig,
nicht gepusht/in main integriert, keine Nutzer-Runtime geändert.**

Eigener Worktree `.worktrees/seven-tools-handoff-20261018`, Branch
`feat/seven-tools-handoff-20261018`, Ausgangspunkt privater main29a5681.
Canonical1357416, vorhandene Import-/Review-Worktrees und fremde Stände unverändert.

## Implementierter Zwischenstand

- `scripts/design_workflow.py`: serverseitig aus tatsächlichem gespeicherten
  Projekt/Snapshot erzeugter CAS-Descriptor, genaue Revision/Quell-/PNG-/Elementhashes;
  `source_commit:null` bleibt unbekannt. Begrenzte persistierte Zuordnungen neben
  vorhandenen Projektcommits, keine Worker/Queue und kein Wiederanlauf-Dispatch.
- Expliziter fester Backend-Fachclient verwendet vorhandenen KiraBridge-MCP-Client,
  lokale Betreiberkonfiguration und ausschließlich bestehende Task-/M2-Operationen.
  Browser liefert weder Peer, Konfiguration, Token, Sourcepfad, Issued-Beleg noch Run.
  Defaultserver hat **keinen** Fachclient/Projektprofile und verweigert Ausführung.
- ThreadDesk create/set_note/add_file bindet unveränderlichen Descriptor samt SHA256
  und tatsächlichen HTML/PNG-CAS-Dateien. Tatsächliche Issued-source_refs müssen
  verified mit passenden Hashes sein; Ausstellen startet keinen Agenten.
- Getrennter Start/Antwort/Status/Inbox/Entscheidung; stabile Taskkennung vor Versand,
  nach Antwortverlust ausschließlich task_get. Anderer aktiver/unklarer Start im
  selben Quellprojekt blockiert neuen Lauf. Eigene Code-/PNG-Dateinamen werden nur
  aus dem festen Betreiberprofil gelesen, keine frei wählbaren Ergebnisdateien.
- Rückgabe bleibt unverified; tatsächlicher Run/Original-Task/Thread/Handoff/Hash
  werden geprüft. Veralteter Entwurf oder geänderte wiederholte Rückgabebytes werden
  abgelehnt. Keine Rückgabe oder Entscheidung verändert automatisch den Entwurf.
- Additive Host-APIs und kompaktes DE/EN-Panel im vorhandenen MySpace; vorhandene
  Boxen/Whiteboard/Ollama-/Speicherwege bleiben erhalten. Neue UI noch nicht visuell
  abgenommen. Keine KiraBridge-Dateien/Runtime/Secrets geändert.

## Tatsächliche bisherige gezielte Nachweise

`tests/design_workflow_test.py` mit lokalem Python3.11.15/KiraBridge-MCP SDK1.30.0:

- Drei neue rein lokale CAS-/Descriptor-/Missing-profile-/stale-/foreignID-Fälle
  bestanden im ersten Lauf. Danach wurden weitere Kontrollen ergänzt; kein finaler
  Wiederholungslauf dieser unveränderten Fälle gestartet.
- Tatsächliche isolierte MCP-HTTP Bridge mit tatsächlichem ThreadDesk-Stdio16b2ccb
  (`seven-tools-m2-pinned-20261018/src`) und eigenem synthetischem Codex-CLI-Ersatz:
  HTML im eigenen temporären Quellprojekt tatsächlich vonleft20/top40 auf
  left100/top80 geändert; gebundene PNG-Rückgabe bleibt ausdrücklich synthetisch und
  ihre Bild-/HTML-Beziehung ist noch nicht unabhängig gerendert. Keine Modelle/API.
- Direkter Ergebnisfall mit verlorenem Startreply, erneutem task_get, neuem
  Fachclient, genau einem Start, Wiederholungsschutz, getrennter Betreiberentscheidung,
  später veränderten Ergebnisbytes und neuer Entwurfsrevision bestand.
- Anschließend neuer parametrisierter Rückfragefall `[True]` bestand: eigener
  erster Durchgang wartet ohne Quelländerung; explizite Antwort setzt dieselbe
  beobachtete Session-UUID fort; zwei Durchgänge, ein Lauf, kein doppelter Start.
  Letzter Toolaufruf: `1 passed in4.65s`. Der gesamte parametrisierte Test wurde
  nicht erneut als Gesamtserie gestartet.
- Node-Syntaxcheck der neuen Workflow-UI und i18n bestand vor den letzten kleinen
  UI-/Kontrollergänzungen. Finale Syntax-/Lint-/Formatprüfung noch offen.

Anfänglicher Harnessfehler wurde korrigiert: Bridge-Tasks enthalten regulär
`error:null`; dies ist keine Toolablehnung. Das zuerst gewählte TD0540391 besaß
noch keinen get_return; der echte geprüfte M2-Quellpin16b2ccb wurde verwendet.
Kein Produktfehler wurde aus diesem fehlenden alten Testquellpin behauptet.

Alle gestarteten eigenen pytest-/HTTP-/Bridge-/TD-Proben sind beendet; kein eigener
Probeprozess soll weiterlaufen. Keine fremde Sitzung wurde beendet.

## Nach ausdrücklichem Root-OK noch erforderlich

1. Änderungen vollständig korrektheits-/sicherheitsprüfen: atomare Zuordnung,
   Actor-/Task-/Inhaltsprüfung, JSON-/Dateilimits, Status-/Antwortverlust, fremde
   Rückgabe, Projektwechsel und doppelte Entscheidung. Keine weitere Architektur.
2. Kleine fokussierte Gegenfälle ergänzen; finale Ruff/Syntax-/Diffchecks und nur
   durch neue Änderungen erforderliche Tests. Keine breite unveränderte Testserie.
3. Tatsächliche isolierte Browserabnahme DE/EN und1180×760; eigener fester Backend-
   Client/Testprojekt, echte harmlose HTML-Demo im Quellprojekt, unabhängiges Rendern
   der tatsächlichen Codeänderung und hashgebundene PNG-Rückvorschau. Fehlendes Profil
   sichtbar gesperrt, kein erfundener Produktiv-/Modell-/ChatGPT-Erfolg.
4. README/Architektur/Vertrag und finalen Abnahmebericht fertigstellen. Ungetestete
   Runtime-/Installationsanbindung als offen ausweisen: optionaler SDK-Fachclient
   benötigt kontrolliertes Betreiber-Embedding und eng freigegebene TD-CAS-Roots.
5. Erst nach Freigabe der Internetfortsetzung finalen privaten Commit/Push/PR.
   Root integriert; keine Runtimefreigabe/-änderung durch diesen Worker.

Letzter Testbefehl (nur zur nachvollziehbaren Fortsetzung, jetzt nicht erneut starten):

```sh
BD_TEST_THREADDESK_SOURCE=/Users/landjunge/threaddesk-worktrees/seven-tools-m2-pinned-20261018/src \
BD_THREADDESK_SOURCE=/Users/landjunge/threaddesk-worktrees/seven-tools-m2-pinned-20261018/src \
PYTHONPATH=/Users/landjunge/KiraBridge-project-control-20261018/src:scripts \
/Users/landjunge/KiraBridge/.venv/bin/python -m pytest -q \
'tests/design_workflow_test.py::test_real_mcp_td_issued_bound_demo_return_reconnect_and_no_duplicate[True]'
```
