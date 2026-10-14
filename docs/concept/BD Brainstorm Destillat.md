# BlockDesigner

Die Komplexität steckt in der KI, nicht in der Oberfläche. Der Mensch kennt sein gewünschtes Ergebnis, steuert die Box und beschreibt die Handlung. Er muss weder ein Bearbeitungswerkzeug suchen noch dessen Fachnamen kennen. Die KI wählt und benutzt die nötigen Werkzeuge.
Linke Hand: wenige feste Tasten. Rechte Hand: Mausführung. Mikrofon: Handlungen, Vorschläge und Änderungen beschreiben.
Der erste Geschwindigkeitshebel ist wegfallende Lern- und Sucharbeit vor dem eigentlichen Gestalten. Weitere Hebel sind genaue gemeinsame Änderungen, wiederverwendete Entscheidungen und übernommene Gestaltung. 
„Funktion bleibt, Optik darf tanzen.“ Bestehende Webseiten sollen originalgetreu geladen werden. Verständliche Teile werden modular bearbeitbar, komplexe Teile bleiben intakt gekapselt. Funktionsbindungen sollen bei Gestaltung erhalten bleiben.

## Drei Spaces
Links MySpace: Bereich der eigenen Dateien, einschließlich behaltener Entwürfe und Vorlagen.
Mitte Workspace: Arbeitsfläche zum Gestalten.
Rechts KI-Space: Vorschläge und Informationen der KI.
Die drei Spaces dürfen nicht mit den drei Bearbeitungsebenen gleichgesetzt werden.
Der Mensch fordert Vorschläge an. Die KI entscheidet, ob sie Vorhandenes beschafft oder Neues erzeugt. Ausgewähltes kann in MySpace behalten und sofort oder später im Workspace eingesetzt werden. Behalten erzwingt keine Wartephase.
Beispiel: „Zeig mir zwanzig Button-Vorschläge.“ Auch hundert verschiedene Button-Designs können angefordert werden. „Das ist der Standard“ wendet die gewählte Gestaltung auf die übrigen Buttons an. Auswahl ansehen, gewünschtes Layout und einzelne Buttons übernehmen; nicht selbst Ordner und Vorlagensammlungen durchsuchen.

## Die Box
Grundobjekt Rechteck; Quadrat als Sonderform. Kreise wurden als selten erwähnt. Rundung ist ein Attribut.
Der Mensch steuert Position, Breite und Höhe der Box. Sprache bestimmt, was in beziehungsweise mit ihr passiert.
Die Box ist gleichzeitig räumlicher Bezug, Greiffläche und bearbeitbares Objekt; ihre Verwendung ist nicht auf einen Zeiger beschränkt.
Beispiel aus dem heutigen Gespräch: Bild auf eine Ebene legen, Box über den gewünschten Schalter ziehen, „ausschneiden, Rest weg“. Die gewählte Fläche ist das Grunddesign des Buttons. Kein manuelles Suchen nach Schere oder Auswahlwerkzeug. Eine obligatorische vorherige Typbenennung ist damit nicht verlangt.
Die KI muss anhand von Auswahl, Kontext und Sprache verstehen, welche Handlung gemeint ist. Eine bloße Folge von benannten Spezialwerkzeugen würde das Prinzip verfehlen.
Jede Box hat Attribute: Nummer, Farbe, Typ, Breite, Höhe, Position, Rundung, Umrandungsfarbe; Schrift und Inhalt/Beschriftung gehören zu den vorgesehenen übernehmbaren Eigenschaften.
Nummern machen die Kommunikation eindeutig. Typ und Identität sind getrennt: ein Typwechsel lässt Nummer und Orientierungsfarbe bestehen.
Typen: Button, Textfeld, Checkbox, Dropdown, Modul, Karte, Leiste, Header, Footer, Sidebar sowie frei benannte weitere Typen. Typen sind Etiketten desselben Objekts, keine fest getrennten Werkzeugklassen.
Explizite Typzuweisung ist möglich, aber nicht für jede Handlung Pflicht. Bestehende funktional belegte Elemente sollen automatisch erkannt werden.
Ein Modul kann Kinder enthalten. Zugehörigkeiten und vorhandene Funktionen werden erhalten.

## Identitäten und Informationsdarstellung
Jede Box besitzt eine eigene ID, eine fortlaufende Nummer und eine eigene Rahmenfarbe. Die Nummer steht klein oben links in der Rahmenfarbe. Identität, sichtbare Nummer und veränderbarer Typ bleiben verschiedene Eigenschaften. Beim Typwechsel bleiben Nummer und Orientierungsfarbe erhalten.
Neue Boxen entstehen mittig auf der zuvor aktivierten Ebene, jeweils mit neuer Rahmenfarbe.
Die Box wird als Umrandung ohne Füllung dargestellt. Module und deren Farben dienen in der Strukturansicht der Orientierung, nicht einer verpflichtenden fertigen Gestaltung.
Ein sichtbarer Rahmen markiert die Auswahl. Mehrere ausgewählte Boxen bilden den räumlich eindeutigen Bezug für die KI.
Das schwebende Monitorfenster ist frei platzierbar. Es zeigt einzeln die Nummer, X-Position und Y-Position in Pixeln, Breite, Höhe und Rahmen-/Linienfarbe des ausgewählten Objekts. Bei Auswahl einer anderen Box erscheinen deren Werte. Ohne neue Auswahl behält der Monitor den letzten Zustand.

## Drei Ebenen und Tasten
Drei getrennte Bearbeitungsebenen werden mit 1, 2, 3 angewählt. Nur die aktive Ebene ist bearbeitbar; die beiden anderen sind gesperrt. Neue Boxen liegen auf der zuvor aktivierten Ebene. Die Ebenen sind nicht die drei Spaces.
Shift: Mehrfachauswahl; erste Auswahl ist Vorgabe.
T: passende Eigenschaften der Vorgabe übernehmen.
M: Mikrofon.
B: Box.
1, 2, 3: die drei Ebenen anwählen.
D: nur Höhe verändern, Breite bleibt gleich.
F: nur Breite verändern, Höhe bleibt gleich.
Space/Leertaste: gewählte Box anheften, Mauszeiger sofort in die Boxmitte versetzen, Box mit der Maus bewegen und mit erneutem Space absetzen/lösen. Plus/Minus dient der Skalierung.
Nie beide Achsen gleichzeitig bei der jeweiligen Achsensteuerung verändern.

## Primary-Box und Übernehmen
erste gewählte Box heißt Primary-Box. Übernehmen überträgt ihre Eigenschaften und Größe auf per Shift markierte Boxen; Beschriftung/Text wird übernommen.
bei Textfeldern Größe übertragen, nicht automatisch Position; erste Schrift gibt Größe und Farbe vor; Rundungen gemeinsam angleichen.
Zwei Buttons bestimmen einen Abstand für weitere Buttons. Übernehmen verändert nicht Position oder Identität der Zielboxen. Jede Zielbox bleibt ein eigenständiges Objekt.
Design-/Hintergrundattribute eines Moduls übertragen sich mit passenden Farbwerten auf enthaltene Darstellungselemente.
Bei Strukturübernahme bekommt jedes Element eine eigene kleine Box innerhalb der Modul-Box; Verteilung und Größe passen zum Modul, Beispiel 20 × 20 statt 50 × 50. Die Zuordnung bleibt erhalten. Beim Verschieben eines Moduls bewegen sich zugeordnete Elemente mit.

## Raster, Symbole, Palette und Größen
Leicht magnetisches Grid über der Arbeitsfläche; „feiner um Faktor zwei“ halbiert Rasterabstand samt Magnetisierung.
Screenshot als Hintergrund, Grid darüber, Boxen darüberlegen.
Symbole: fertige transparente Bilder, per Sprache in Symbolbibliothek aufnehmen und platzieren. Beispiel Herz mit transparentem Rest. Umgebende Box bleibt Greiffläche. Geplant: Farbe ohne Neugenerierung ändern.
Palette: 16 Grundfarben, gemeinsame Quelle für alle Werkzeuge; Elemente referenzieren Farben. „Farbe sieben für die Umrandung.“
Relative Größenbefehle: kleiner, größer, breiter, höher; sinnvolle nächste Stufe, sichtbares Ergebnis; „das ist jetzt die Größe“ fixiert den Wert.
Oberfläche ruhig, eindeutig, vertraut, lesbar; wenige Schalter mit erklärbarer Wirkung. Schwarz/weiß und Plus/Minus nicht umdeuten. „Weniger ist weniger und mehr ist mehr“ ist keine pauschale Aufforderung, Informationen zu streichen.

## Struktur und Darstellung
Früher Plan: zuerst Objektmodell, dann Sprachschicht, Oberfläche, Rendering. Rechtecke/Attribute werden in Layout und CSS umgesetzt.
Frühe Darstellungsidee: Struktur zuerst, tatsächliches Design erst am Ende sichtbar.
Spätere Abläufe verlangen sichtbare Varianten, Bildvorlagen und direkt sichtbare Änderungen. Beide Aussagen bleiben stehen; genaue Umschaltung zwischen Struktur und fertiger Darstellung ist abzugleichen.

## Durchgängiger Bedienablauf
Der Mensch arbeitet in der Mitte im Workspace. Links liegen seine Dateien im MySpace; rechts zeigt die KI im KI-Space Vorschläge. Die drei Bearbeitungsebenen liegen innerhalb der Arbeitslogik und sind davon unabhängig.
Mit 1, 2 oder 3 wird die gewünschte Ebene aktiviert. Nur diese Ebene ist bearbeitbar. Mit B entsteht eine Box mittig auf der aktiven Ebene: eigene ID, nächste fortlaufende Nummer und eigene Rahmenfarbe. Die Nummer steht klein oben links in derselben Farbe. Die Box ist zunächst eine Umrandung ohne Füllung.
Auswahl macht die Box zum eindeutigen Bezug. Space heftet die gewählte Box an die Maus; der Mauszeiger springt zur Boxmitte. Die rechte Hand bewegt sie. Erneutes Space setzt sie ab. D verändert ausschließlich die Höhe; F ausschließlich die Breite. Das magnetische Raster hilft bei genauer Positionierung. Der frei platzierbare Monitor zeigt Nummer, X/Y, Breite, Höhe und Rahmenfarbe; er bleibt beim zuletzt ausgewählten Objekt, bis eine andere Auswahl erfolgt.
Die Sprache beschreibt die gewünschte Handlung. Die KI übernimmt Werkzeugwahl und Ausführung. Ein Bild kann auf einer Ebene liegen: Box über den gewünschten Ausschnitt steuern, „ausschneiden, Rest weg“. Der Ausschnitt liefert das Grunddesign. Die Boxsteuerung bleibt dieselbe wie beim Anlegen, Verschieben und Bearbeiten anderer Elemente.
Für Gestaltungsvorschläge genügt eine Anforderung an die KI. Die KI beschafft oder erzeugt passende Vorschläge rechts im KI-Space. Der Mensch wählt aus; gewünschte Dateien/Designs kommen nach MySpace und können sofort oder später im Workspace verwendet werden. Er kann ein Layout und einzelne darin gefallende Buttons auswählen. Eigene Dateien und wiederverwendete Entwürfe bleiben im persönlichen Bereich verfügbar.
Boxen können zu Buttons, Modulen, Textfeldern oder weiteren frei benannten Typen werden. Typen sind Eigenschaften, keine getrennten Bedienwerkzeuge. Bereits vorhandene Funktionen und Zugehörigkeiten bleiben gebunden. Ausgewählte Elemente können in ein Modul gruppiert werden. Beim Verschieben des Moduls kommen die zugeordneten Elemente mit. Die Greiffläche bleibt eine Box, auch wenn sichtbar ein transparentes Symbol steht.
Bei Mehrfachauswahl mit Shift ist die erste Box die Primary-Box. T/„Übernehmen“ überträgt die vereinbarten passenden Eigenschaften auf die weiteren ausgewählten Boxen. Die wiedergefundene Text-/Beschriftungsübernahme gehört ausdrücklich dazu. Position und Identität werden nicht übernommen. Bei Textfeldern nennt die Quelle Größenübernahme ohne Positionsübernahme. Zwei Buttons geben einen Abstand für weitere vor. Modulgestaltung gibt passende Design-/Hintergrundattribute an enthaltene Darstellungselemente weiter. Welche Attribute in jedem Einzelfall gemeint sind, richtet sich nach den erhaltenen Typregeln; ungelöste Abgrenzungen stehen weiterhin im Konzept.
Palette, Rundungen, Schriften und Symbole werden über dieselbe Auswahl-/Sprachlogik verändert. Die 16 Grundfarben stammen aus einer gemeinsamen Quelle. Relative Größenbefehle bleiben möglich; der Mensch kann einen passenden Zustand als Größe beziehungsweise Standard festlegen.
Bei vorhandenen Webseiten soll derselbe Ablauf für die Gestaltung gelten: verständliche Teile modular bearbeiten, komplexe Teile intakt gekapselt erhalten. „Funktion bleibt, Optik darf tanzen.“ Der strukturierte Aufbau wird in Layout und CSS überführt. Die noch nicht geklärte Umschaltung zwischen Strukturansicht und fertiger Darstellung bleibt ausdrücklich offen.
Damit verbindet das Konzept die konkrete Motorik der Boxsteuerung mit der Handlungsbeschreibung per Sprache. Lernen vieler Einzelwerkzeuge, Suchen ihrer Funktionen und Durchblättern fremder Vorlagen sollen durch diese gleichbleibende Bedienung und die Beschaffung durch die KI ersetzt werden.
