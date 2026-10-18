# BD-PR3 · Betreiberprofil und ursprüngliche Startsperre

Unabhängige Review des ersten BD-C04-Standes `c2282c7` fand zwei echte Lücken:

1. Die spätere Rückgabe nutzte das heute konfigurierte CWD und die heutigen
   Quell-/PNG-Dateinamen. Ein Profilwechsel vor der ersten Rückgabe hätte dadurch
   einen alten Run fälschlich neuen Dateien zuordnen können.
2. Die Startsperre suchte nur unter heute vorhandenen, gleich zugeordneten Profilen.
   Ein entferntes oder umgeordnetes Profil hätte den ungeklärten ursprünglichen
   Quelllauf unsichtbar machen können.

## Korrektur

Vor der ersten ausgehenden `issue`-Operation wird in der bestehenden privaten
Zuordnung ein `blockdesigner.operator-profile.v1`-Pin gespeichert:

- Kanonisches absolutes Quell-CWD, tatsächlich beobachtetes dev/inode des
  Verzeichnisses und feste direkte Quell-/PNG-Dateinamen.
- Konfigurierte lokale Peerkennung, Hash der Endpointreferenz, Principal,
  vorhandener geladener Konfigquellhash (oder explizit null, falls unbekannt) und
  Hash der konfigurierten Statewurzel. **Keine Tokens oder Credentialinhalte.**
- Die Backenddaten sind ausdrücklich `configured_local_peer_not_remote_attestation`.
  Sie belegen den beobachteten lokalen Clientvertrag, keine kryptografische
  Remote-/OS-/Daemonattestierung. Tatsächliche MCP-Authentifizierung und gespeicherte
  Taskprincipals bleiben zusätzlich erforderlich.

Nur ein bisher rein vorbereiteter Stand ohne Operations-/Issued-/Run-/Returnbelege
darf erstmals gepinnt werden. Historische fehlende Pins werden niemals rückwirkend
aus der jetzigen Konfiguration ergänzt. Ein fehlender/historisch unbekannter Pin
benötigt tatsächliche ursprüngliche Betreiberbelege; kein Reset oder Löschen.

Jede Folgeaktion (`issue/start/answer/refresh/decision`) prüft den Pin vor dem
Backendaufruf, auch die **erste** Rückvorschau/Entscheidung. Ausgehende Clientcalls
prüfen davor/danach erneut. Die Dateiübernahme prüft nochmals nach dem RPC und
nach dem Dateilesen. Ihre Pfade stammen aus einer Kopie des unveränderten Pins,
nicht aus einer nachträglich veränderten Profilreferenz. Drift ist
`designProfileChanged`; Browserdarstellung DE/EN und `profile_drift` sperren den
Zugang. Interne Pfade/Backenddaten bleiben privat, öffentlich ist nur der Pinhash.

Die Startsperre scannt jetzt die **persistierten ursprünglichen** Bindungen aller
eigenen Workflows im vorhandenen Projektstore. Heutige Profile sind dafür kein
Index mehr. Ein ungeklärter Start mit gleichem ursprünglichem kanonischem CWD oder
gleicher beobachteter Verzeichnisidentität blockiert weiterhin, auch wenn das alte
Profil entfernt, umgeordnet oder sein Verzeichnis umbenannt wurde. Eine belegte
abschließende Betreiberentscheidung löst diese lokale Sperre. Unbekannte/fehlende
historische Quelle blockiert konservativ, statt durch neue Konfiguration zu
verschwinden. Es entsteht keine weitere Queue oder automatische Wiederholung.

Der Scan ist auf4096 Einträge und16MiB begrenzt; zwischen lokalen Dateiprüfungen
wird ein2s-Budget geprüft. Eine überschrittene Grenze blockiert. Keine harte
Echtzeitgarantie für blockierende Dateisystemoperationen und keine OS-weite
Sperre gegen fremde Programme oder andere Datenspeicher.

## Tatsächlich gezielt geprüft

`tests/design_profile_test.py` enthält **45 neue synthetische lokale Fälle**:

- Drift von CWD, Quellname, PNG-Name, Principal, Endpoint-, Konfig- oder State-
  Referenz vor jeder der fünf Folgeaktionen. Gerade vor erster Rückgabe bzw.
  Entscheidung: null Backendcalls, keine neue Dateizuordnung/Entwurfsänderung.
- Unveränderter Pin bleibt nach erneutem Öffnen gültig; dieselbe Operation wird
  einmal eingereicht und anschließend nur gelesen.
- Entferntes und umgeordnetes Profil verstecken den ursprünglichen ungeklärten
  Lauf nicht. Tatsächlich dokumentierte abschließende Entscheidung löst die Sperre.
- Legacy-Unknown ohne Pin sowie historische Issued-/Run-/Returnkennungen ohne
  Operationskarte werden nicht aus der neuen Konfiguration nachgepinnt.
- Profilwechsel während einer ausstehenden Quittung wird ebenfalls abgewiesen;
  keine Übernahme neuer Ergebnisdateien.
- Identitätsmetadaten exportieren keinen Token; ihr begrenzter Belegumfang bleibt
  explizit. Überschrittenes Scanbudget verweigert den Start.

Alle diese neuen Fälle bestanden in gezielten lokalen Läufen; zusätzlich die
**sechs für das Pinmodell angepassten lokalen Countertests**. Python3.11.15,
vorhandenes MCP SDK1.30.0 nur als importierte Bibliothek; **keine Dienste, Modelle,
Provider, Agentenprozesse, echte Konten oder Nutzerprojekte gestartet**. Die
vorhandenen vollständigen MCP-/HTML-/Browserbelege wurden nicht wiederholt und
nicht auf den neuen Quellstand umgeschrieben. Ihre historische Aussage bleibt
beim damaligen Quellstand; dieser Nachtrag belegt gezielt die beiden Reviewfixes.
RuffF/I/Format, Node-Syntax und Diffcheck der betroffenen Dateien bestanden.

Vor unabhängiger Nachprüfung bleibt PR3 offen. Nutzer-Runtime/Bridge-Konfiguration
sind unverändert, normaler BD-Start ohne vertrauenswürdiges Backendprofil weiterhin
unavailable. Keine zusätzliche Auslieferungs-/Modell-/ChatGPT-Gesamtabnahme behauptet.

## English

The review identified real source-correlation and overlap-guard defects. The adapter
now persists the canonical original operator profile before its first outbound
operation: source CWD/directory identity, fixed filenames and explicitly configured
local peer/principal/config/state references, excluding credentials. Every follow-up
and result adoption checks this pin; drift fails closed, including before the first
returned preview. These configured references are not remote attestation.

Unknown prior starts are found through all persisted original bindings, independent
of profiles being removed or remapped. Missing historical evidence is never guessed
from new configuration. Scanning is bounded and fails closed; this is local-store
coordination, not OS-wide isolation. Forty-five focused new synthetic cases and six
adapted local countercases passed without services/models/runtime changes. Prior
successful full MCP/HTML/browser acceptance was preserved, not repeated or relabeled
as a new full acceptance. Independent review and any runtime activation remain separate.
