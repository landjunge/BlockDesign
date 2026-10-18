# Optionales Betreiberprofil / Optional operator workflow profile

## Deutsch

Der normale Editorstart bleibt ohne Profil unverändert. Das Coding-Panel kann
Entwürfe vorbereiten, aber ohne fest eingerichteten Client kein Coding ausführen.
Ein lokaler Betreiber kann **beim Start** eine private JSON-Datei auswählen.
Dieser Weg ersetzt das bisher nötige Python-Embedding; er installiert nichts,
startet beim Laden keinen Agenten und erweitert keine Bridge-Rechte.

Voraussetzungen:

- Vorhandene Python-Umgebung mit Python >=3.12, kompatiblem ThreadDesk-Modulhost
  und optionalem kompatiblem KiraBridge-SDK samt Abhängigkeiten. `BD_PYTHON` wählt
  einen vorhandenen Interpreter; das Skript installiert oder verändert ihn nicht.
- Bereits vorhandene eigene Bridge-Konfiguration und ein dort eingerichteter
  Principal. Seine Zugangsdaten kommen ausschließlich aus dessen vorhandener
  privater Credentials-Datei bzw. konfigurierter Umgebung, nicht aus diesem Profil.
  Der feste Client akzeptiert nur den lokalen Loopback-Dienst. Keine URL/Tokenfelder.
- Ein vorhandenes eigenes BD-Projekt und dessen echte Projekt-UUID aus dem bestehenden
  `/api/projects`-Abruf des eigenen lokalen Editors. Die Beispiel-UUID ersetzen;
  eine UUID ist kein Identitäts-/Rechtebeleg.
- Kanonischer absoluter Quellordner innerhalb der **vorhandenen** Principal-Roots.
  `source_file` und `preview_file` sind verschiedene feste einzelne Dateinamen,
  keine Pfade. HTML-Quelle und importierter Entwurf müssen im vorhandenen
  Workflow exakt passen. Die Rückvorschau darf erst nach dem Agentenlauf entstehen.

Beispiel ohne Geheimnisse; nur als Vorlage, nicht als aktive Nutzerkonfiguration:

```json
{
  "format": "blockdesigner.workflow-profile.v1",
  "bridge_config": "/absolute/private/kirabridge/config.toml",
  "principal": "operator",
  "projects": {
    "11111111-1111-4111-8111-111111111111": {
      "cwd": "/absolute/authorized/own-project",
      "source_file": "own-page.html",
      "preview_file": "own-page-preview.png"
    }
  }
}
```

In einer **neuen eigenen** privaten Datei außerhalb des Repos speichern; vorhandene
Profile nicht überschreiben. JSON-Profil und referenzierte Bridge-Konfiguration
müssen dem eigenen OS-Konto gehören, regulär, nur für den Eigentümer zugänglich
(z.B.0600) und über absolute kanonische Pfade ohne Symlinks erreichbar sein.
Der Start prüft und verändert keine Dateirechte. Höchstens64KiB pro Datei,
1–32 Projekte; unbekannte/doppelte Felder und unzulässige Namen werden abgewiesen.
Das JSON ist kein Browser-/HTTP-Eingabeformat.

Zuerst prüfen, erst anschließend bewusst den vorhandenen Host starten:

```sh
./start.command --check --workflow-profile /absolute/private/blockdesigner/workflow.json
./start.command --workflow-profile /absolute/private/blockdesigner/workflow.json
# Gleichwertige explizite Betreiberumgebung; Startoption hat Vorrang:
BD_WORKFLOW_PROFILE=/absolute/private/blockdesigner/workflow.json ./start.command --check
```

`--check` richtet weder Modulbindung noch Projekt-/Bridge-Datenbank ein, bindet
keinen Port und verbindet sich nicht zum Bridge-Dienst. `workflow_profile.configured`
belegt nur lokale Dateirechte, Schema, Client-/Profilvoraussetzungen.
`network_checked=false` und `dispatch_verified=false` bleiben ausdrücklich bestehen.
Andere bestehende Hostvoraussetzungen können den Start weiterhin blockieren.
Fehlendes SDK: vorhandene passende Umgebung auswählen; keine automatische Installation.
Fehlende/ungültige/zu offene Konfiguration: lokal gezielt prüfen, niemals rohe
Konfigurationsfehler, Zugangsdaten oder komplette Dateien in Chat/Logs ausgeben.

Im gestarteten Editor: genau gespeicherten Entwurf vorbereiten, Übergabe ausdrücklich
über ThreadDesk ausstellen, danach **Start** separat beauftragen. Laden/Serverstart
führt weder issue noch start aus. Bridge-Rechte für jede tatsächliche Operation
(`threaddesk.manage`, `handoff.issue/start/answer/status/inbox/decide`, `task.read`)
werden weiterhin serverseitig geprüft; dieses Profil erteilt sie nicht. Lokale
Readiness ist weder Agentenlogin noch Modell-/Projektabnahme. Bei unbekanntem Versand
Status derselben bestehenden Taskkennung abfragen, keinen neuen Auftrag erfinden.

Vor dem ersten Versand pinnt der bestehende Workflow Quell-CWD samt dev/inode,
Dateinamen und lokale Backend-/Config-/Principalreferenzen. Folgeaktionen prüfen
gegen dieses Originalprofil. Ein Neustart lädt das Profil erneut; geänderte
Zuordnung umgeht keine Pin-/Legacy-Sperren. Bestehende ungeklärte Starts sperren ihr
ursprüngliches Quellprojekt weiterhin, auch bei entfernten Profilen. Keine zweite
Queue, keine automatische Wiederholung und keine OS-weite Sperrbehauptung.
Der Browser erhält weder Rohprofil noch Zugangsdaten. Lieferung/PNG bleibt ungeprüft;
ein Betreiberentscheid ist kein Funktionstest. [Vorhandener Workflowvertrag](acceptance/HANDOFF-20261018.md).

Rückweg: nur den eigenen Host geordnet beenden, danach ohne Option/ohne
`BD_WORKFLOW_PROFILE` starten. Das deaktiviert neue konfigurationsabhängige Aktionen,
löscht aber weder Profil, Historie, Queue noch bestehende Sperren und stoppt keinen
bereits extern laufenden Agenten. Keine unbekannten Starts durch Konfigurationswechsel
wiederholen. Andere Projekte/Sitzungen und Bridge-Dienste bleiben unangetastet.

## English

Without a profile, normal editor startup remains unchanged and coding dispatch is
unavailable. An operator can now select a private JSON profile **at startup**, using
`--workflow-profile` or `BD_WORKFLOW_PROFILE`; the explicit option takes precedence.
This reuses the existing fixed client and DesignWorkflow instead of requiring custom
Python embedding. No SDK installation, new rights, queue or automatic agent start.

Use an existing Python >=3.12 environment with the compatible ThreadDesk module API
and optional KiraBridge SDK/dependencies. Select it with `BD_PYTHON`. The profile
references an existing private Bridge configuration and configured principal; its
credentials remain in the existing credentials/environment store. The fixed peer is
loopback-only. The JSON example above contains no secrets, URL or token fields.
Replace the example UUID with your own existing BD project ID from the editor's
existing `/api/projects` response. UUIDs do not prove identity or authority.

Save a **new owned** private profile outside the repository. Both profile and Bridge
config must be owner-only regular files (e.g.0600), with absolute canonical paths
and no symlinks. No automatic chmod. Maximum64KiB per file,1–32 projects; unknown/
duplicate fields fail closed. Map each project to an existing canonical source CWD
inside the principal's existing roots and two distinct simple filenames. This is
not a browser configuration API. Source HTML must match the actual imported design;
the returned preview can be created later by the explicitly started workflow.

Run the shown `--check` command first. It reads local prerequisites only: no network,
port, module setup, database creation, Bridge task or agent launch. A configured
profile is not a remote permission, login or execution proof; the report retains
`network_checked=false` and `dispatch_verified=false`. Missing SDK or incompatible
config blocks startup with a bounded safe diagnosis; select/inspect the existing
local environment without dumping credentials or raw configuration. The regular
Host/ThreadDesk prerequisites still apply.

Then start deliberately with the same profile. In Coding task, prepare the saved
design, issue the handoff through ThreadDesk, then start explicitly. Loading the
profile never issues or starts work. The actual Bridge checks its configured rights
for every operation; startup grants none. Original source-directory identity,
filenames and local peer/config/principal references are pinned before dispatch and
checked again on follow-ups. Restart/reconfiguration does not bypass changed-profile
or legacy unknown-execution barriers. Read an uncertain existing task by its original
ID instead of submitting another. Returned source/PNG and project completion remain
unverified until independently checked; an operator decision is not a function test.

To disable, stop only your own host normally and restart without the option and
environment variable. Preserve profiles, history, tasks and barriers. This does not
stop an already external agent or authorize replay. No other services/sessions are
changed. The existing [dated workflow evidence](acceptance/HANDOFF-20261018.md) remains
historical; no model, installed-user-runtime or new ChatGPT acceptance follows here.

## Begrenzte Quellabnahme / Bounded source acceptance · 19.10.2026

[Quell-/Prüfquittung](acceptance/WORKFLOW-PROFILE-20261019.json): Basis
`eb3df8d1c556a8355ff28667d061e3e02d1a8670`,26 neue fokussierte Tests bestanden
unter eigener isolierter Python3.12.13-Umgebung im Worktree. Keine bestehende
Funktions-/Browser-/Modellsuite wiederholt. SDK-Quelle
`f19797b2e1b7e34b73de1180734a6b9c93ab07e5` (Verhaltensbasis `7af39cd`),
ThreadDesk-Quelle `05403916e549e1060f839ccbaf36a5cb90413776`.
Die29 SDK-Abhängigkeiten wurden aus dem vorhandenen KB-`uv.lock` mit Hashprüfung
übernommen, darunter MCP1.30.0 und auf diesem Intel-Mac cryptography48.0.1;
nur fünf gepinnte pytest-Testabhängigkeiten zusätzlich. Fremde Umgebungen unverändert.

Der tatsächliche Shellweg `start.command --check` meldete Python-/Modulvertrag und
privates Profil bereit, jedoch erwartungsgemäß Exit2/`binding_ready=false`: Die
synthetische Hostbindung wurde **nicht** angelegt. Kein Port, Setup, Task oder
Datenbank entstand. Ein weiterer echter Shellcheck wies ein0644-Testprofil mit
`workflow_profile_file` ohne Pfad-/Tokenausgabe ab. Normale Server-Parser/Host-
Verdrahtung wurde mit injiziertem nicht lauschendem Server/Host/Store geprüft,
mit und ohne Profil; keine produktive Aktivierung. Die referenzierten JSON-Belege
halten lokale Voraussetzungen getrennt von weiterhin ungeprüftem Dispatch.

The receipt records26 focused tests in an isolated Python3.12 environment and the
actual shell preflight, including rejection of a shared-readable synthetic profile.
It does not claim user installation, a live server/model/ChatGPT call or project
acceptance. Existing user's profiles, services, queues and historical evidence were
not changed. The deliberately absent synthetic host binding explains exit2; this is
not an unresolved SDK failure or a fabricated fully-ready runtime. Source lint,
format, example/link and diff checks cover only the changed scope.
