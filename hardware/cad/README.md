# 3D-Druck-Teile (CadQuery)

Alle Teile sind parametrisch in `params.py` definiert (Maße in mm). Quellen: `prototyp.py` (Phase 1), `endgeraet.py` (Konzeptgehäuse laut Render/`TEILE.md`), `build.py` (Export, Vorschau, Prüfung).

```
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python build.py      # schreibt stl/ und vorschau/, prüft alles, Exitcode 1 bei Fehler
```

Ausgabe: `stl/prototyp/*.stl`, `stl/endgeraet/*.stl`, `vorschau/*.png` (je Teil, Explosion, Zusammenbau mit Attrappen; der Zusammenbau-Renderer sortiert nur grob, Artefakte sind normal).

Koordinaten: X rechts, Y oben (Display oben), Z nach vorn, Rückseite außen bei Z = 0. Alle STL liegen in Einbaulage und müssen im Slicer gedreht werden (Ausrichtung siehe unten).

## Prüfergebnis (`build.py`, zuletzt gelaufen)

- Alle 12 STL wasserdicht (trimesh `is_watertight`, Winkelkonsistenz, Volumen > 0).
- Bounding-Boxen stimmen mit den Sollmaßen aus `params.py` (Toleranz 0,05).
- Kollisionstest per Boolean-Schnitt, paarweise über alle Teile und Attrappen (Board, Akku, Klickrad-Platine, LRA, Schrauben, Hauptplatine, Display): keine Überschneidung > 0,05 mm³.
- **Nicht geprüft:** Passung an echten Teilen, Schrauben-/Einsatz-Sitz, Druckbarkeit im Slicer, Rastnasen am Endgerät. Alles ist am Rechner entstanden.

## Teile Prototyp v1 (`stl/prototyp/`)

Entwurfsentscheidung: Das Waveshare-Board wird **mit seinem schwarzen Originalgehäuse** eingesetzt (Wiki-Maßzeichnung 37,6 × 45,2 × 15,0, Ecken R1,8). Das sind die einzigen verifizierten Maße. Die nackte Platine passt auch (dann mehr Luft, ggf. Schaumstoff).

Gesamtmaß zusammengebaut: **43,4 × 92,3 × 19,1 mm**.

| Teil | Datei | Maß (B × L × H) | Hinweis |
|---|---|---|---|
| Vorderschale | `vorderschale.stl` | 43,4 × 92,3 × 8,1 | Frontplatte 1,6, Display-Fenster 29,7 × 35,9, Rad-Öffnung Ø 30,6, 4 Dome für Einsätze, Falz für Lippe, Öffnungen USB-C (oben) und BOOT/PWR (Seiten) |
| Rückschale | `rueckschale.stl` | 43,4 × 92,3 × 13,5 | Boden 2,0, Lippe 1,2 × 2,5 hoch, 4 Schraubrohre mit Senkung, Akku-Führungsrippen, Andruckrippen fürs Board |
| Klickrad-Abdeckung | `klickrad_abdeckung.stl` | Ø 30 / Ø 11,6 × 2,4 | liegt direkt auf der Platine, 3 Taschen Ø 4,0 × 1,5 für Schraubenköpfe |
| Mitteltaste | `mitteltaste.stl` | Ø 11 × 1,15 | Unterseite mit Tasche 4,4 × 4,4 für den Taster |
| Klickrad-Halter | `klickrad_halter.stl` | 37,0 × 33,7 × 6,0 | Basis Ø 32,6 × 2,0, 3 Schraubdome Ø 5,6 auf r 14,6 (90/210/330°), 2 Ohren zu den unteren Gehäuseschrauben, Kabelschlitz 8 × 5 |

Aufbau von vorn nach hinten: Frontplatte, 1,5 mm Luft (Schraubenköpfe der Platine), Klickrad-Platine, Halter mit LRA-Freiraum 0,5 mm, darunter der Akku (3,85 × 24 × 28). Das Board liegt neben dem Rad, direkt an der Frontplatte.

Warum der Halter steif ist: Er ist zwischen den Rohren der Rückschale und den Domen der Vorderschale **eingeklemmt** (die beiden unteren Gehäuseschrauben gehen durch seine Ohren) und trägt die Platine auf drei Domen. Der Tick des LRA geht so über Platine, Dome und Ohren direkt ins Gehäuse.

Das Rad liegt dadurch 0,7 mm **unter** der Frontfläche (Mulde). Wer es bündig will, setzt `COVER_T` auf 3,1 (Touch-Empfindlichkeit dann prüfen, das Endgerät hat 1,95).

## Teile Endgerät (`stl/endgeraet/`, erster Entwurf)

Maße nach Render/`TEILE.md`: 42 × 95 × 12,2, Ecken r 7, Wand 1,4, Fuge z = 6, Display-Fenster 30,2 × 36,7 bei y +21, Rad-Öffnung Ø 30,6 bei y −27, Frame-Dome bei (±15, ±40).

| Teil | Datei | Maß | Hinweis |
|---|---|---|---|
| Oberschale | `oberschale.stl` | 42 × 95 × 6,2 (z 6 bis 12,2) | Platte 1,2, Fenster, Rad-Öffnung, Öffnungen USB-C/Klinke unten, microSD rechts, Taste oben, 4 Rastnasen |
| Rückschale | `rueckschale.stl` | 42 × 95 × 6,0 | Boden 1,2, 4 Senkungen für M2 |
| Innenrahmen | `innenrahmen.stl` | 38,8 × 91,8 × 6,2 | 0,2 Spiel je Seite, 4 Dome mit Einsatz (von oben) und Durchgangsloch, Quersteg, Sockel unter dem LRA, Rastmulden |
| Klickrad-Abdeckung | `klickrad_abdeckung.stl` | Ø 30 / Ø 11,6 × 1,95 | |
| Mitteltaste | `mitteltaste.stl` | Ø 11 × 1,15 | Taschentiefe aus `E_SWITCH_H` |
| Distanzring | `distanzring.stl` | Ø 32 / Ø 27 × 0,8 | trägt die Klickrad-Platine auf der Hauptplatine (neu, nicht im Render) |
| Ein/Aus-Taste | `power_taste.stl` | 9,6 × 3,2 × 3,2 | Schaft 8 × 3, Flansch hält sie im Gehäuse |

Abweichungen vom Render (begründet):
- Ein/Aus-Taste Mitte z = 9,2 statt 10,3: bei 10,3 bliebe über der Öffnung weniger als 1,2 mm Wand (Platte beginnt bei z = 11). 9,2 entspricht der Höhe des Tasters in der Hauptplatine.
- Die Oberschale hat **keine** Schraubdome, weil das Display (33 × 42) die Stellen (±15, ±40) belegt. Sie wird über Innenrahmen (Zentrierung), Rastnasen (0,4 mm) und Rückschale gehalten; die 4 Schrauben ziehen Innenrahmen und Rückschale zusammen. Ob die Rastnasen reichen, ist ungeprüft (Alternative: Klebepunkte).
- Frame-Dome tragen den Einsatz am **oberen** Ende (Einsatz von oben einschmelzen), Schraube M2 × 8 von hinten.

## Druckeinstellungen

Gemeinsam: Düse 0,4, 3 Perimeter (1,2 mm), Fuge/Passungen mit 0,2 bis 0,3 Spiel konstruiert, Elefantenfuß-Kompensation ca. 0,1 aktivieren. Keine Stützen nötig, wenn wie unten ausgerichtet (Öffnungen in Wänden überbrücken 12 mm oder weniger).

| Teil | Material | Schicht | Infill | Ausrichtung | Stützen |
|---|---|---|---|---|---|
| Vorderschale / Oberschale | SV06 Ace: PETG. Voron: ASA, sehr gut für Sichtflächen | 0,12 bis 0,16 | 20 % Gyroid, 4 Perimeter wenn möglich | Front nach unten auf das Bett | nein |
| Rückschale | wie oben | 0,2 | 20 % | Boden nach unten | nein |
| Klickrad-Halter (steif!) | PETG oder ASA | 0,16 | **50 % oder 100 %**, 5 Perimeter | Basis unten, Dome nach oben | nein |
| Innenrahmen | PETG/ASA | 0,16 | 40 % | flach, Unterseite unten | nein |
| Klickrad-Abdeckung | PETG/ASA, hell (kein transparentes Filament, sonst Streulicht) | 0,08 bis 0,12 | 100 % | Oberseite nach unten (Sichtfläche zum Bett, glatte Platte) | nein |
| Mitteltaste | wie Abdeckung | 0,08 | 100 % | Oberseite nach unten | nein |
| Distanzring, Ein/Aus-Taste | PETG/ASA | 0,16 | 100 % | flach | nein |

ASA/ABS nur auf dem Voron (geschlossen, 250 °C Düse, 100 °C Bett, Schrumpf 0,3 bis 0,5 % beachten: Passmaße an Probedruck prüfen). Auf dem SV06 Ace PETG (235 °C, 75 °C).

Tipp: Vorderschale und Abdeckung zuerst als Probedruck mit 0,2 mm und 2 Wänden, um Fenster und Spiel zu prüfen.

## Gewindeeinsätze einsetzen

- Einsatz M2, außen etwa Ø 3,2 mm, Länge 3 bis 4 mm (Bohrung Ø `INSERT_HOLE_D` = 3,2 × `INSERT_HOLE_DEPTH` = 4,0 als Parameter).
- Lötkolben mit Einsatz-Spitze auf 220 bis 240 °C (PETG) bzw. 250 °C (ASA). Einsatz auf die Bohrung setzen, senkrecht mit leichtem Druck einschmelzen, bis er bündig ist, dann 5 Sekunden abkühlen lassen, nicht verkanten.
- Bohrung vorher mit Ø 3,0 aufreiben, falls der Druck enger ist. Schmelzreste nicht in das Gewinde laufen lassen.
- Prototyp: 4 Einsätze von unten in die Dome der **Vorderschale** (Fugenseite), 3 Einsätze von oben in die Dome des **Klickrad-Halters**. Endgerät: 4 Einsätze von oben in die Dome des **Innenrahmens**.

## Schrauben

| Verwendung | Schraube |
|---|---|
| Prototyp Gehäuse (4 Stück) | M2 × 12 Senkkopf (ISO 14581 oder DIN 965), von hinten |
| Prototyp Klickrad-Platine (3 Stück) | M2 × 5 Linsen-/Flachkopf (ISO 7380, Kopf Ø 3,5 × 1,3), von vorn durch die Platine in den Halter |
| Endgerät (4 Stück) | M2 × 8 Senkkopf, von hinten |

## Montagereihenfolge Prototyp

1. Einsätze einsetzen (Vorderschale, Halter).
2. LRA auf die Rückseite der Klickrad-Platine kleben, Litzen anlöten und durch den Kabelschlitz des Halters nach hinten führen. Platine mit 3 × M2 × 5 auf den Halter schrauben.
3. Abdeckung mit doppelseitigem Klebeband (0,1 mm) auf die Platine kleben, Mitteltaste in das Loch setzen (Tropfen Klebstoff auf den Taster oder Klebeband).
4. Vorderschale mit der Front nach unten legen, Halter-Einheit einlegen (Abdeckung durch die Rad-Öffnung).
5. Board (im Originalgehäuse) einlegen, USB-C nach oben. Litzen an die Pads löten, Akku anstecken (Polung prüfen!) und hinter den Halter legen. 1 mm Schaumstoff auf das Board-Gehäuse für Andruck.
6. Rückschale aufsetzen (Lippe in den Falz), 4 × M2 × 12 durch die Rohre und die Ohren des Halters in die Einsätze der Vorderschale schrauben.

## Montagereihenfolge Endgerät

1. Einsätze in den Innenrahmen. 2. LRA auf Klickrad-Platine, Platine mit Distanzring auf die Hauptplatine, Abdeckung und Taste aufkleben. 3. Hauptplatine mit Display in die Oberschale (Fenster nach unten), Ein/Aus-Taste einlegen. 4. Innenrahmen mit Akku einsetzen (Rastnasen einrasten lassen). 5. Rückschale aufsetzen, 4 × M2 × 8 von hinten.

## Platzhalter-Maße (nach dem Nachmessen in `params.py` ändern)

| Parameter | Wert | Grund |
|---|---|---|
| `BOARD_W/L/T` | 37,6 × 45,2 × 15,0 | Wiki-Zeichnung **mit** Originalgehäuse; nackte Platine unbekannt |
| `DISP_CY_FROM_BOARD_TOP`, `DISP_CX_OFFSET` | 22,6 / 0 | Lage des Displays im Board geschätzt (mittig) |
| `USB_X`, `USB_Z_FROM_FRONT`, `USB_OPEN_W/H` | 0 / 7,5 / 12 × 7 | USB-C nur grob bekannt (Schmalseite, mittig) |
| `SIDEBTN_Y_FROM_TOP`, `SIDEBTN_Z_FROM_FRONT`, `SIDEBTN_OPEN` | 6,0 / 7,5 / 4,0 | BOOT/PWR-Seitentaster, Lage nur grob bekannt |
| `LRA_L/W/H` | 15 × 9,5 × 3,5 | Obergrenze der Kandidaten; bestimmt `DOME_H` |
| `CABLE_SLOT`, `CABLE_SLOT_POS` | 8 × 5 bei (−7,8; 4,5) | Lage der Litzen/Pads |
| `SWITCH_H` | 1,5 | Maximalhöhe Mitteltaster laut `TEILE.md` |
| `LIPO_*` | 24 × 28 × 3,85 | empfohlener Akku laut Wiki, Liegeplatz hinter dem Halter |
| `E_BATT*`, `E_SWITCH_H`, `E_USB`, `E_JACK_D`, `E_SD` | siehe Datei | Annahmen für das Endgerät (Akku-Platzhalter 30 × 34 × 4,6) |

## Offene Punkte

- Das Board ist 15 mm dick (mit Gehäuse); das Prototyp-Gehäuse wird dadurch 19,1 mm dick. Ohne Originalgehäuse lässt sich `BOARD_T` verkleinern.
- Klickrad-Platine im Endgerät: Befestigung ist offen (Entwurf: Distanzring + Klebeband). Eine saubere Lösung braucht 3 Aussparungen in der Hauptplatine oder Haltefüße; mit dem Platinen-Paket abstimmen.
- Rastnasen am Endgerät und Taschentiefe der Mitteltaste (Haut 0,6 mm) nur rechnerisch.
- USB-C-Öffnung im Prototyp ist bewusst groß (12 × 7) für Stecker mit Hülle.
