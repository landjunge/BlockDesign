# BlockDesigner: vorhandener Benutzerstart · 19.10.2026

Fortsetzung von `seven-tools-build-20261018-1833`, Paket BD-C04. Der optionale
Betreiberprofil-Loader samt HTTP-Dateigrenze war bereits über den privaten
[PR5](https://github.com/landjunge/blockdesign/pull/5) integriert. Diese Funktion
wurde nicht erneut gebaut. Der noch alte kanonische Benutzercheckout zeigte auf
`135741679fc8c92fe15804d94aa47bed3a4c0636`; dort fehlte der neue lesende Startcheck.

## Tatsächlich aktiviert und geprüft

`/Users/landjunge/blockdesigner` wurde ohne Force/Reset auf den vorhandenen Branch
`main` und per Fast-forward auf `4c15299ebe71429c53de6af7534734542d8c23d0`
gebracht. Der historische Branch `feat/compact-project-history` bleibt unverändert
bei `1357416`. Vorher gab es keine Änderungen an versionierten Dateien und keine
BlockDesigner-Server auf 5190/5193. Kein fremder Prozess wurde beendet.

Alle 1761 unversionierten/ignorierten Dateien außerhalb der bestehenden Worktrees
wurden vorab privat gesichert. Zusammen mit der vorhandenen BlockDesigner-
Nutzerablage und den beiden ausgewählten bestehenden Hostdateien wurden 1772
Dateien nach Inhalt, Dateirechten und Eigentümer verglichen: keine Änderung.
Die privaten Erhaltungsbelege liegen unter
`~/.local/share/blockdesigner/operator-activation/20261019T030748Z/`.
Die öffentliche Quittung enthält nur Anzahl und Manifesthash, keine Nutzerinhalte.
Die Sicherung liegt auf demselben Mac und ersetzt kein externes Backup.

Der echte Aufruf `./start.command --check` im Benutzerpfad bestand mit Exit 0:
Python, ThreadDesk-Modulvertrag und bestehende eigene Bindung bereit;
`setup_required=false`. Kein Setup, Server, Agent, Modell, Provider oder Bridge-
Auftrag wurde für diesen Nachweis gestartet. KiraBridge blieb unverändert.
Vorhandene Prüfserien wurden nicht wiederholt. Die historischen Browser-/Modell-
und Handoffbelege behalten ihren jeweiligen Quell- und Laufzeitbezug.
[Minimierte technische Quittung](USER-START-20261019.json).

## Benutzen

```sh
cd /Users/landjunge/blockdesigner
./start.command --check
./start.command
```

Nach bewusstem Serverstart öffnet der eigene Browser `http://127.0.0.1:5190`;
das zugehörige Terminal bleibt offen. Ctrl+C beendet diesen eigenen Server.
Bei einem belegten Port einen freien Port ausdrücklich wählen, zum Beispiel
`./start.command --port 5193`; keine fremden Prozesse beenden.

Im normalen Benutzerstart ist weiterhin kein optionales Coding-Betreiberprofil
eingerichtet. Lokale Editorbereitschaft bedeutet keinen nachgewiesenen Coding-
Dispatch. Der bereits implementierte [private Profilweg](../WORKFLOW-PROFILE.md)
kann später ausdrücklich mit bestehender eigener Projekt-/Zugangskonfiguration
verwendet werden. Der derzeit zurückgestellte KiraBridge-Anschluss wurde nicht
verändert oder erneut beauftragt. Dies ist keine neue Browser-/Modellabnahme,
kein öffentlicher Release und keine Nutzerabnahme.

## English

The canonical user checkout now uses integrated main `4c15299`; the former
historical branch and all 1772 preserved local files remain unchanged. The actual
read-only shell preflight exits 0 with the existing binding and requires no setup.
No server, model, provider or Bridge task was launched. Start deliberately with
`./start.command`, then open the printed loopback URL; stop only that own server
with Ctrl+C. The optional coding profile remains unconfigured. No live coding,
new browser/model verification, public release or user acceptance is implied.
