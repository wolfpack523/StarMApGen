# StarMapGen

StarMapGen ist ein grafisches Windows-Programm zum Erstellen und Bearbeiten
von dreidimensionalen Sternenkarten für Science-Fiction-Settings.

Das Programm verwaltet die Kartendaten in einer `.dat`-Datei und erzeugt
daraus eine frei skalierbare SVG-Karte.

## Funktionen

- Zufällige Sternenkarten erzeugen
- Vorhandene Karten aus einer `.dat`-Datei laden
- Kartengrenzen in alle sechs Richtungen erweitern
- Sternensysteme hinzufügen, bearbeiten und löschen
- Fraktionen für Sternensysteme hinterlegen
- Mehrfachsternsysteme darstellen
- Verschiedene Stern- und Objekttypen darstellen
- Planeten zu Sternensystemen hinzufügen, bearbeiten und entfernen
- Planetentypen und Weltklassifizierungen verwalten
- Sprungverbindungen hinzufügen, bearbeiten und entfernen
- Unterschiedliche Zustände für Sprungverbindungen anzeigen
- Nebelregionen hinzufügen, bearbeiten und löschen
- Nebel als Cloud, Haze oder Outline darstellen
- Nebel über frei definierbare Stützpunkte formen
- X- und Y-Koordinaten direkt an der Karte anzeigen
- Systeminformationen inklusive Planeten per Hover anzeigen
- SVG-Karte direkt im Programm anzeigen
- Karten zusätzlich als PNG exportieren
- DAT- und SVG-Datei nach Änderungen automatisch aktualisieren

## Was ist neu?

- Nebelregionen können jetzt angelegt, bearbeitet, gelöscht, gespeichert und wieder geladen werden.
- Nebel werden über frei definierbare Stützpunkte geformt und können als **Cloud**, **Haze** oder **Outline** dargestellt werden.
- Die Karte zeigt nun X- und Y-Koordinaten zur besseren Orientierung.
- Karten können zusätzlich als PNG exportiert werden.
- Für Sprungverbindungen steht jetzt der zusätzliche Status **Lost** zur Verfügung.
- Spektraltypen können im Systemeditor zufällig neu erzeugt werden.
- Sternensystemen kann jetzt eine Fraktion zugewiesen werden.
- Sternensysteme können Planeten enthalten.
- Planeten besitzen einen Planetentyp und eine Weltklassifizierung.
- Systeminformationen und Planeten werden in der SVG-Ansicht beim Überfahren eines Systems angezeigt.
- Die Kartenansicht wurde verbessert: Zoomen und Scrollposition bleiben beim Aktualisieren der SVG-Karte erhalten.

Außerdem wurde die interne Projektstruktur grundlegend überarbeitet.
Benutzeroberfläche, Datenmodelle, Dateioperationen und SVG-Rendering sind
nun klar voneinander getrennt, wodurch zukünftige Erweiterungen und
Wartungsarbeiten erleichtert werden.

## TODOs
- Textexport für Systeminformationen und Planeten für Figma
- Pasagen über mehrere Systeme hinweg darstellen
- Planetentypen und Weltklassifizierungen hinzufügen, bearbeiten und löschen
- Synchronisation von DAT-datein von verschiedenen Benutzern (Import/Export)
- Versionsverwaltung für DAT-Dateien

## Bekannte Einschränkungen

- Kartengrenzen können derzeit erweitert, aber nicht verkleinert werden.
- Änderungen an Systemdaten und Planeten werden über `Apply Changes`
  gespeichert, während Änderungen an Sprungverbindungen derzeit sofort
  übernommen werden. Dieses Verhalten soll zukünftig vereinheitlicht werden.

## Programm starten

### Windows-Version

Die Datei

```text
StarMapGen.exe
```
kann direkt gestartet werden.

Eine separate Installation von Python ist nicht erforderlich.

Relative Dateinamen werden im Verzeichnis der EXE verwendet. Wird
beispielsweise als Dateiname sector.dat angegeben, wird die Datei neben
der EXE gespeichert beziehungsweise dort gesucht.

## Aus dem Quellcode

Voraussetzungen:

- Python 3.11 oder neuer
- wxPython 4.2.x
- resvg-py

Abhängigkeiten installieren:

```text
python -m pip install wxPython resvg-py
```

Programm starten:

```text
python StarMapGen/src/StarMapGen.py
```

Bei Verwendung der virtuellen Umgebung des Projekts:

```text
.\.venv\Scripts\python.exe .\StarMapGen\src\StarMapGen.py
```

## Benutzeroberfläche

Die Benutzeroberfläche besteht aus zwei Bereichen:

- Links befinden sich die Einstellungen und der Systemeditor.
- Rechts wird die aktuelle SVG-Karte angezeigt.

Die linke Spalte kann gescrollt werden.

Folgende Bereiche können ein- und ausgeklappt werden:

- Map Files and Display
- Random Generation
- Map Bounds

Der Bereich Star Systems bleibt dauerhaft verfügbar.

### Neue Zufallskarte erzeugen

Den Bereich Random Generation öffnen.

#### Map Width (x)

Breite der Karte auf der X-Achse.

#### Map Height (y)

Höhe der Karte auf der Y-Achse.

#### Map Thickness (z)

Ausdehnung der Karte auf der Z-Achse.

Die Z-Achse wird um 0 herum aufgebaut.

Bei einer Tiefe von 20 entstehen beispielsweise folgende Grenzen:

```text
Z = -10 bis 9
```

#### Stellar Density

Bestimmt die durchschnittliche Anzahl der erzeugten Sternensysteme.

Ein höherer Wert erzeugt mehr Systeme.

Nach Eingabe der Werte:```Generate Random Map```anklicken.

Die Karte wird erzeugt, als DAT-Datei gespeichert und als SVG dargestellt.

### Vorhandene Karte laden

Den Bereich Map Files and Display öffnen.

Unter Data Filename den Namen der zu ladenden Datei eintragen.

Beispiel:```sampleMap.dat```
Danach:```Load Map```anklicken.

Beim Laden werden folgende Daten übernommen:

- Kartengrenzen
- Sternensysteme
- Systempositionen
- Spektraltypen
- Fraktionen
- Planeten
- Planetentypen
- Weltklassifizierungen
- Sprungverbindungen
- Zustände der Sprungverbindungen
- Nebelregionen
- Form, Farbe, Transparenz und Darstellungsstil der Nebel

Ältere DAT-Dateien ohne gespeicherte Kartengrenzen werden ebenfalls
unterstützt. In diesem Fall ermittelt StarMapGen die Grenzen aus den
vorhandenen Systempositionen.

### Dateien und Darstellung
#### Output Map Filename

Name der zu erzeugenden SVG-Datei.

Beispiel:```sampleMap.svg```

#### Data Filename

Name der DAT-Datei, die geladen und gespeichert wird.

Beispiel:```sampleMap.dat```

#### Text Scale

Skalierung der Systemnamen und Koordinaten innerhalb der SVG-Karte.

#### Print Z coordinate

Legt fest, ob die Z-Koordinate an den Sternensystemen angezeigt wird.

#### Export PNG

Die aktuelle SVG-Karte kann zusätzlich als PNG-Datei exportiert werden.

Dazu im Bereich `Map Files and Display` auf ```Export PNG```
klicken.

Die PNG-Datei wird unter demselben Namen wie die SVG-Datei gespeichert.

Beispiel:

```text
sampleMap.svg
sampleMap.png
```

Der SVG-Export bleibt weiterhin das primäre Kartenformat. Das PNG eignet sich
beispielsweise für Bilder, Dokumente oder Anwendungen, die kein SVG
unterstützen.


### Kartengrenzen

Der Bereich Map Bounds zeigt die aktuellen Grenzen der Karte:

```text
X: Minimum bis Maximum
Y: Minimum bis Maximum
Z: Minimum bis Maximum
```

Unter Extend by wird festgelegt, um wie viele Einheiten die Karte
erweitert werden soll.

|Schaltfläche|Wirkung|
|---------|---------|
|```X -```|Karte in negative X-Richtung erweitern|
|```X +```|Karte in positive X-Richtung erweitern|
|```Y -```|Karte in negative Y-Richtung erweitern|
|```Y +```|Karte in positive Y-Richtung erweitern|
|```Z -```|Karte in negative Z-Richtung erweitern|
|```Z +```|Karte in positive Z-Richtung erweitern|

Beim Erweitern werden bestehende Sternensysteme nicht verschoben. Es werden
ausschließlich die äußeren Grenzen der Karte verändert.

Die Karte kann derzeit erweitert, aber nicht verkleinert werden.

### Koordinaten auf der Karte

Zur besseren Orientierung werden die X-Koordinaten am oberen Kartenrand
und die Y-Koordinaten am linken Kartenrand angezeigt.

Die Beschriftungen entsprechen den tatsächlichen Kartenkoordinaten und
berücksichtigen auch negative beziehungsweise nachträglich erweiterte
Kartengrenzen.

Dadurch lassen sich insbesondere Sternsysteme und Nebel-Stützpunkte leichter
auf der Karte einordnen.

### Sternensysteme bearbeiten

Im Bereich Star Systems werden alle Systeme der aktuellen Karte
aufgelistet.

Nach Auswahl eines Systems können folgende Werte bearbeitet werden:

- Name
- Fraktion
- X-Koordinate
- Y-Koordinate
- Z-Koordinate
- Spektraltypen
- Planeten

Änderungen werden mit```Apply Changes```übernommen.

Die Koordinaten müssen innerhalb der aktuellen Map Bounds liegen.

Systemnamen müssen eindeutig sein.

### Neues Sternensystem anlegen

Auf```New System```klicken.

StarMapGen vergibt automatisch einen fortlaufenden Systemnamen:

```text
S000
S001
S002
...
S009
S010
```

Andere Namen können anschließend manuell eingetragen werden.

Gelöschte Nummern werden nicht erneut vergeben. Existiert beispielsweise
bereits ```S010```, erhält das nächste System den Namen ```S011```.

Position und Spektraltypen eintragen und anschließend```Create System```anklicken.

### Sternensystem löschen

Das zu löschende System auswählen und```Delete System```anklicken.

Alle Sprungverbindungen, die mit diesem System verbunden sind, werden
ebenfalls entfernt.

## Spektraltypen

Mehrere Sterne können durch Kommas, Semikolons oder Zeilenumbrüche getrennt
werden.

Beispiel:```G2, M4, WD```

### Hauptreihensterne

```text
O0 bis O9
B0 bis B9
A0 bis A9
F0 bis F9
G0 bis G9
K0 bis K9
M0 bis M9
```

### Riesen

```text
F0III bis F9III
G0III bis G9III
K0III bis K9III
M0III bis M9III
```

### Überriesen

```text
F0I bis F9I
G0I bis G9I
K0I bis K9I
M0I bis M9I
```

### Besondere Objekte


|Kürzel|Bedeutung|
|---|---|
|```BD```|Brauner Zwerg|
|```WD```|Weißer Zwerg|
|```NS```|Neutronenstern|
|```BH```|Schwarzes Loch|

### Sprungverbindungen

Für das ausgewählte Sternensystem können Sprungverbindungen hinzugefügt,
bearbeitet und entfernt werden.

Verfügbare Zustände:

|Status| Darstellung           |
|---|-----------------------|
|Normal| Weiße durchgezogene Linie |
|Caution| Gelbe gestrichelte Linie |
|Dangerous| Orange hervorgehobene Linie |
|Blocked| Rote, deutlich gestrichelte Linie |
|Lost| Blau, gepunktete Linie|

Eine Verbindung wird nur einmal gespeichert, gilt aber für beide
beteiligten Systeme.


## Planeten

Zu jedem Sternensystem können beliebig viele Planeten hinzugefügt werden.

Ein Planet besitzt derzeit folgende Eigenschaften:

- Name
- Typ
- Klassifizierung

### Planet hinzufügen

Das gewünschte Sternensystem auswählen und anschließend auf ```Add Planet```
klicken.

Im Dialog können Name, Planetentyp und Klassifizierung ausgewählt werden.

Die Änderungen am Planetensystem werden erst mit ```Apply Changes``` dauerhaft übernommen.

#### Planetentypen

Folgende Planetentypen stehen zur Verfügung:

- Terran
- Karge bzw. lebensarme Welt
- Gasriese
- Eiswelt
- Ozeanwelt
- Wüstenwelt
- Vulkanische Welt
- Sonstiger Planetentyp

### Weltklassifizierungen

Zusätzlich zum physikalischen Planetentyp kann eine Weltklassifizierung vergeben werden.

Verfügbare Klassifizierungen:

- Agrarwelt
- Bergwerksplanet
- Bibliothekswelt
- Dschungelplanet
- Eiswelt
- Fabrikwelt
- Festungswelt
- Feudalwelt
- Forschungsstation
- Gartenwelt
- Grenzwelt
- Höhlenwelt
- Industriewelt
- Leblose Welt
- Makropolwelt
- Munitorumswelt
- Nachtwelt
- Ordenswelt
- Ozeanwelt
- Ritterwelt
- Schreinwelt
- Todeswelt
- Trophäenwelt
- Urzeitwelt
- Waldplanet
- Wüstenplanet
- Zivilisierte Welt
- Dämonenwelt
- Exoditenwelt
- Gasriese
- Gruftwelt
- Hexenwelt
- Jungfernwelt
- Orkwelten
- Tauwelten
- Weltenschiff
- Sonstige Welt


## Systeminformationen in der SVG-Ansicht

Sternensysteme können zusätzliche Informationen enthalten.

Wird der Mauszeiger über ein Sternensystem bewegt, zeigt die Kartenansicht einen Tooltip mit:

- Systemname
- Fraktion
- Spektraltypen
- Planeten
- Planetentypen
- Weltklassifizierungen

Die Tooltip-Daten werden direkt aus den gespeicherten Kartendaten erzeugt.

## Nebelregionen


Im Bereich `Nebulae` können Nebelregionen für die aktuelle Karte angelegt,
bearbeitet und gelöscht werden.


Ein Nebel besitzt folgende Eigenschaften:


- Name
- Darstellungsstil
- Farbe
- Transparenz
- eine Liste von Stützpunkten


### Neuen Nebel anlegen


Auf```New Nebula```klicken.

Anschließend Name, Stil, Farbe, Transparenz und mindestens drei
Stützpunkte eintragen.

Beispiel:
```text
4,4
8,3
11,6
10,10
7,12
3,9
```
Die Punkte werden in der angegebenen Reihenfolge miteinander verbunden.
Der letzte Punkt wird automatisch wieder mit dem ersten Punkt verbunden.

Die Punktreihenfolge bestimmt damit direkt die Form des Nebels.

#### Nebel-Stile

Folgende Darstellungsarten stehen zur Verfügung:

|Stil|Beschreibung|
|---|---|
|Cloud|Gefüllte, weich geschwungene Nebelregion|
|Haze|Transparentere und stärker geglättete Nebelregion mit breiterem Rand|
|Outline|Zeigt nur die äußere Kontur des Nebels|

#### Farbe

Die Farbe wird als hexadezimaler RGB-Wert angegeben.

Beispiel:```#7a2f8f```

#### Opacity

Die Transparenz wird als Wert zwischen ```0.0``` und ```1.0``` angegeben.

Beispiele:
```text
0.20
0.35
0.75
1.00
```
Ein kleiner Wert erzeugt einen transparenteren Nebel.

#### Stützpunkte

Jeder Punkt wird als X- und Y-Koordinate angegeben:```x,y```

Beispiel:```5,7```

Die Koordinaten müssen innerhalb der aktuellen Kartengrenzen liegen.

Ein Nebel benötigt mindestens drei unterschiedliche Punkte.

Die Stützpunkte werden nicht automatisch sortiert. Ihre Reihenfolge ist
wichtig, da sie die Kontur des Nebels festlegt.

Änderungen werden mit ```Apply Changes``` dauerhaft
übernommen und anschließend sowohl in der DAT-Datei als auch in der
SVG-Karte gespeichert.

## DAT-Datei

Aktuelle DAT-Dateien enthalten die vollständigen Kartengrenzen:

```text 
Map Minimum: (1,1,-10)
Map Maximum: (20,20,9)
```

Danach folgen die Sternensysteme, Sprungverbindungen und Nebelregionen.

Die Datei kann grundsätzlich mit einem Texteditor geöffnet werden. Für
manuelle Änderungen sollte vorher eine Sicherungskopie erstellt werden.

### Automatisches Speichern

Nach Änderungen an

- Sternensystemen,
- Fraktionen,
- Planeten,
- Sprungverbindungen,
- Nebelregionen oder
- Kartengrenzen

werden die DAT-Datei und die SVG-Karte automatisch neu geschrieben.

Vor umfangreichen Änderungen empfiehlt sich trotzdem eine Sicherungskopie
der DAT-Datei.

Zusätzlich zu Sternensystemen, Sprungverbindungen und Nebeln können
Fraktionen und Planeten gespeichert werden.

Beispiel:

```text
Name: Sol
Coordinates: (4,5,0)
Number of Stars: 1
Spectral Types: G2

Faction: "Sol" "Imperium"

Planet: "Sol" "Terra" "terran" "Zivilisierte Welt"
Planet: "Sol" "Mars" "barren" "Bergwerksplanet"

Link: "Sol" "Alpha Centauri" "normal"
```

Ältere DAT-Dateien ohne Fraktions- oder Planetendaten können weiterhin geladen werden.

### SVG-Datei weiterbearbeiten

Die erzeugte SVG-Datei kann beispielsweise mit folgenden Programmen
geöffnet werden:

- Inkscape
- Affinity Designer
- Adobe Illustrator
- modernen Webbrowsern
- geeigneten Texteditoren

Systemnamen und Koordinaten werden als SVG-Text gespeichert und können in
einem SVG-Editor direkt bearbeitet werden.

## Windows-EXE erstellen

PyInstaller installieren:

```text
.\.venv\Scripts\python.exe -m pip install --upgrade pyinstaller
```

### Testbare Ordner-Version

```text
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --onedir --console --name StarMapGen --paths ".\StarMapGen\src" --collect-all wx ".\StarMapGen\src\StarMapGen.py"
```

Das Ergebnis befindet sich anschließend unter:

```text
dist\StarMapGen\StarMapGen.exe
```

### Einzelne EXE

```text
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --onefile --windowed --name StarMapGen --paths ".\StarMapGen\src" --collect-all wx ".\StarMapGen\src\StarMapGen.py"
```

Das Ergebnis befindet sich anschließend unter:

```text
dist\StarMapGen.exe
```

## Projektstruktur
```text
StarMapGen/src/
├── StarMapGen.py
├── domain/
├── files/
├── rendering/
└── ui/
│   ├── dialogs/
│   └── panels/
├── build/
├── dist/
└── README.md
```

## Credits und Lizenz

Dieses Projekt basiert auf dem ursprünglichen StarMapGen-Projekt von
dagorym:

https://github.com/dagorym/StarMapGen

Vor einer öffentlichen Weitergabe oder Veröffentlichung sollte geprüft
werden, unter welcher Lizenz der ursprüngliche Quellcode verwendet und
verbreitet werden darf.

Sobald die Lizenzfrage geklärt ist, sollte dem Projekt eine passende
LICENSE-Datei hinzugefügt werden.
