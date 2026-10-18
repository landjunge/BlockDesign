# BD-Legacy-Ausführungsbelege / Legacy execution evidence

Folgekorrektur nach unabhängigem Source-Review von PR3/b0b63aa. Basis dieses
isolierten Branchs ist tatsächlich gefetchtes privates main
`e6e81b0bf75161d035dc572c1e27726ee794baae` (PR3-Merge). Vorhandene Canonical-/
Worktree-Arbeit, Originalbelege, Nutzerprojekte und Runtime bleiben unverändert.

## Befund und Korrektur

`guard_start` übersprang bisher jeden früheren Record ohne `operations.start`.
Ein historischer unbekannter Lauf mit `bridge_task_id`, `run_id` oder
`active_task_id`, aber fehlender alter Operationskarte, konnte dadurch bei einem
neuen Design denselben Quellpfad unbemerkt wieder benutzen. PR3 verhinderte bereits
unbelegte nachträgliche Profilpins, sein Overlap-Guard wählte solche Legacybelege
jedoch noch nicht aus.

Der Guard bewertet nun ausschließlich mögliche Ausführungsbelege: gespeicherte
Start-/Antwortoperation, historische technische Task-/Run-/Returnreferenzen oder
eine ehrliche mögliche Ausführungsphase wie unknown/running/awaiting_answer.
Diese Angaben sind **keine verifizierten Starts oder Funktionsnachweise**; sie
belegen gerade nicht, dass eine neue parallele Ausführung sicher wäre. Die bereits
vorhandene Prüfung des ursprünglichen kanonischen Quellpfads/Verzeichnisidentität
bleibt. Fehlender ursprünglicher Pin blockiert konservativ; heutige Profile füllen
historische Lücken nicht aus. Entfernte/umgeordnete Profile verstecken keine Sperre.

Reines prepared/issued_no_execution ohne zusätzliche Ausführungsbelege bleibt ohne
Startbehauptung und ohne erfundene Ausführungssperre. Eine vorhandene separat
aufgezeichnete abschließende Betreiberentscheidung behält ihren bisherigen Effekt;
keine automatische Entscheidung, Bereinigung oder Datenmigration wird ergänzt.
Keine neue Queue, Agenteninstanz, Backend-/Browseranbindung oder neue Bedienfunktion.

## Tatsächlich enge Prüfung

Neue Datei `tests/design_legacy_barrier_test.py`, ausschließlich temporäre eigene
ProjectStore-/CAS-Daten, MemoryClient und bestehende reine Fixturefunktionen:

-8 erste Fälle bestanden in1.92s: drei historische IDs ohne Startkarte, Originalpin
  bzw. konservativ fehlender Pin, entferntes Altprofil, bekannte Abschlussentscheidung,
  drei mögliche Ausführungsphasen und zwei reine Prepare-/Issue-Phasen.
-2 gezielte zusätzliche Fälle derselben Lücke bestanden in1.49s (8 deselected):
  historische return_id und gespeicherte answer_*-Operation ohne ersten Startindex.
- Insgesamt10 spezifische neue Fälle. Keine bereits unveränderte Suite wiederholt.
- Python3.11.15, vorhandene Umgebung und importierte Bibliotheken. ThreadDesk-Quelle
  `05403916e549e1060f839ccbaf36a5cb90413776` nur für vorhandene Artifactklasse;
  kein ThreadDesk-/Bridge-/HTTP-Dienst oder CLI-Agent gestartet. Kein Modell,
  Provideraufruf, Browserharness oder Nutzer-/Produktivobjekt verwendet.
- RuffF/I/Format der beiden betroffenen Pythondateien und git diff --check bestanden.
  Das Repository enthält hier keinen eingerichteten GitHub-Actions-Workflow;
  fehlende CI wird nicht als bestanden ausgegeben.

Originale Rundreise-/Browser-/Profilbelege bleiben datierte Nachweise ihrer
ursprünglichen Quellstände. Dieser Nachtrag behauptet keine neue Gesamtabnahme
oder aktivierte Nutzerinstallation. Rückweg ist gezielter Quellrevert; vorhandene
historische Bindungen/Audit-/CAS-/Nutzerdaten erhalten, nichts löschen oder resetten.

## English

The review found that guard_start skipped historical records missing the initial
operations.start index, even when a legacy task/run/active-task reference and an
unknown execution state remained. The guard now considers persisted start/answer
operations, task/run/return references and possible execution phases. These are
uncertain claims, not verified starts, functional proof or authority grants.

The existing original source path/directory-identity comparison remains in use.
Missing original profile evidence blocks conservatively; current configuration
never backfills it. Removed/remapped profiles cannot hide prior possible execution.
Pure prepared/issued_no_execution records without additional execution evidence
still make no start claim and do not create a fabricated execution barrier. Existing
explicit terminal operator decisions retain their prior semantics.

Ten new focused synthetic local cases passed in two targeted rounds, without
services, real agents/models, browsers, provider calls, runtime changes or user data.
No unchanged suite was repeated; existing proof artifacts were preserved. Source
and tests passed RuffF/I/format and diff checks. No configured GitHub Actions workflow
is present here, so no CI success is claimed. This is a narrow private source fix;
Root owns review/merge and any later delivery decision.
