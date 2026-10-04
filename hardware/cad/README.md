# 3D-Druck-Teile (CadQuery)

**Aktueller Stand für die Hauptplatine Rev. 3: Endgerät v3 (44 × 100 × 10 mm), siehe Abschnitt „Endgerät v3“ am Ende.** Alle Teile sind parametrisch in `params.py` definiert (Maße in mm). Quellen: `prototyp.py` (Phase 1), `endgeraet.py` (Konzeptgehäuse laut Render/`TEILE.md`), `build.py` (Export, Vorschau, Prüfung).

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

---

# Endgerät v2 (Dünnbau Variante A, 40 × 90 × 8,5 mm)

Grundlage: `docs/DUENNBAU.md`. Quellen: `endgeraet_v2.py` (Geometrie), `params.py` (Block „ENDGERAET v2“, Präfix `E2_`), `build_v2.py` (Export, DXF, Vorschau, Prüfung). Der Entwurf v1 (`endgeraet.py`, 12,2 mm) bleibt unverändert.

```
.venv/bin/python build_v2.py   # schreibt stl/endgeraet_v2/, dxf/endgeraet_v2/, vorschau/endgeraet_v2_*.png; Exitcode 1 bei Fehler
```

**Alle Maße der Hauptplatine, Lagen von Klinke/USB-C/Modul/Akku/Klickrad und das Display-Fenster sind VORLÄUFIG** (aus DUENNBAU.md, Floorplan ungeprüft). Sie stehen mit `# VORLAEUFIG` / `# PLATZHALTER` in `params.py`.

## Teileliste v2

| Teil | Datei | Fertigung | Maß (B × L × H) |
|---|---|---|---|
| Rahmen | `stl/endgeraet_v2/rahmen.stl` | Druck, ASA (Voron) oder PETG (SV06 Ace) | 40 × 90 × 8,5; Wand 1,2; Randsteg 0,8; 5 Schraubdome; Öffnungen Klinke, USB-C, Ein/Aus |
| Rückwand | `rueckwand.stl` | Druck, ASA | 38,2 × 88,2 × 1,0 (+ Akku-Haltestege 2,0 hoch); 5 Senkungen für M1,6 |
| Ein/Aus-Taste | `power_taste.stl` | Druck, 100 % | Flansch 6,4 × 2,8 innen, Schaft 4,8 × 1,8 außen |
| Frontplatte | `dxf/endgeraet_v2/frontplatte.dxf` (+ `stl/…/frontplatte.stl` nur zur Prüfung) | Zuschnitt, Acryl/PC 0,8 oder Glas 0,7–0,8 | 38,2 × 88,2, Klickrad-Ausschnitt Ø 30,6, Ecken R 4,5 − 0,9 |
| Display-Druckmaske | Layer `DRUCKMASKE_FENSTER` derselben DXF | Siebdruck/Digitaldruck, Rückseite | Fenster 33,9 × 41,3 (aktive Fläche 33,1 × 40,5 + 2 × 0,4), R 1,5 |
| Klickrad-Abdeckung | `klickrad_abdeckung.dxf` | FR4 0,6 (PCB-Fertiger, Tangara-Vorbild) | Ø 30 |
| Rückwand FR4 (Alternative) | `rueckwand_fr4.dxf` | FR4 0,8, 5 Bohrungen Ø 1,8 (Senkung Ø 3,2 beim Fertiger angeben) | 38,2 × 88,2 |
| Schrauben | – | 5 × M1,6 × 3 Senkkopf (ISO 14581), selbstschneidend in Ø 1,4 | |
| Klebefilm | – | VHB/OCA 0,1 mm: Frontplatte↔Rahmenfalz, Display↔Frontplatte, Klickrad-Platine↔Frontplatte, Abdeckung↔Klickrad-Platine | |

DXF: Einheit mm, Ursprung = Gehäusemitte, Ansicht von vorn (Frontplatte). Layer `SCHNITT` ausschneiden, `DRUCKMASKE_FENSTER` nicht schneiden (Kontur für den Druck, außerhalb bedrucken), `BOHRUNG`, `INFO` (Text, vor dem Versand entfernen). Rundungen sind LWPOLYLINE mit Bulge, Kreise als CIRCLE. Vorschau: `vorschau/endgeraet_v2_zuschnitt_dxf.png`.

## Druck

| Teil | Material | Schicht | Wände/Infill | Ausrichtung | Stützen |
|---|---|---|---|---|---|
| Rahmen | ASA (Voron, geschlossen, 250 °C / 100 °C) bevorzugt, sonst PETG | 0,12 bis 0,16 | 3 Perimeter (0,4-Düse: 1,2 mm), 100 % Infill (die Wände sind so dünn, dass es keinen Infill gibt) | **Rückseite (z = 0) auf das Bett.** Auflagesteg vorn hat eine 45°-Schräge, die Dome wachsen von unten nach oben | nein |
| Rückwand | ASA | 0,2 | 5 Schichten, 100 % | flach, Außenseite auf das Bett, Stege nach oben | nein |
| Ein/Aus-Taste | wie Rahmen | 0,12 | 100 % | flach auf der Flanschseite | nein |

Hinweise: ASA schrumpft 0,3 bis 0,5 %, Falz-Spiel ist 0,1 je Seite (`E2_FIT`). Erst einen Probedruck des Rahmens und der Rückwand machen und das Falzspiel messen. Elefantenfuß-Kompensation 0,1 aktivieren (die Rückwand sitzt im Falz). Der Auflagesteg der Frontplatte ist nur 0,8 breit und an der Innenkante 0,4 hoch: nicht zu stark säubern.

## Zuschnitt (Acryl oder Glas)

1. `frontplatte.dxf` an einen Laserdienst (Acryl/PC) oder einen Glas-Zuschnitt senden. Dicke 0,8 mm (Glas 0,7 bis 0,8). Toleranz ±0,1 verlangen, Innenausschnitt Ø 30,6 und Außenkontur.
2. Glas: Schneiden mit Wasserstrahl oder Ritzen, Innenausschnitt Ø 30,6 in 0,8 mm Glas ist aufwendig und teuer; dann Acryl/PC nehmen. Dünnes Acryl (0,8) hat wenig Steifigkeit; beim Laserschnitt entstehen Kantenspannungen, Schutzfolie bis zur Montage lassen.
3. Display-Druckmaske: Layer `DRUCKMASKE_FENSTER` als Grafik an den Drucker; Rückseite außerhalb des Fensters schwarz, Fensterkante 0,4 größer als die aktive Fläche. Klickrad-Ausschnitt mit Rückdruck oder Klebering abdecken.
4. Klickrad-Abdeckung (FR4 0,6) und optional Rückwand (FR4 0,8) werden mit den Platinen beim PCB-Fertiger bestellt.

## Montage

1. Ein/Aus-Taste von innen in die Öffnung der rechten Wand legen (Flansch hält sie).
2. Platinenreihenfolge von vorn: Frontplatte mit der Innenseite nach oben legen. Display mit Klebefilm einkleben (Fenster zentrieren), FPC nach unten führen. Klickrad-Platine (LRA bereits auf der Rückseite) und Abdeckung aufkleben.
3. Frontplatte mit dem Display in den vorderen Falz des Rahmens kleben (Auflagesteg).
4. Hauptplatine (Bauteile hinten, Klinke von hinten in den Randausschnitt) auf die vier Auflager legen, FPC des Displays einstecken/anlöten, Klickrad-FFC anschließen.
5. Akku (303450) in das Fach zwischen die Haltestege der Rückwand legen, Litzen an die Platine, Ein/Aus-Taster prüfen.
6. Rückwand in den hinteren Falz setzen, 5 × M1,6 × 3 anziehen (nicht überdrehen, Dom ist weich).

## Stack-up (Z von hinten, Rückseite außen = 0)

| Lage | von … bis | Dicke |
|---|---|---|
| Rückwand | 0,00 … 1,00 | 1,00 |
| Luft | 1,00 … 1,20 | 0,20 |
| Rückzone (Akku 3,3 / ESP 3,1 / USB-C 3,18 / Klinke 3,1 unter der Platine) | 1,20 … 4,50 | 3,30 |
| Hauptplatine | 4,50 … 5,30 | 0,80 |
| Luft bzw. flache Bauteile vorn (unter dem Display nur ≤ 0,25) | 5,30 … 5,55 | 0,25 |
| Display-Modul mit Touch | 5,55 … 7,60 | 2,05 |
| Klebefilm | 7,60 … 7,70 | 0,10 |
| Frontplatte | 7,70 … 8,50 | 0,80 |
| **Summe laut Modell** | | **8,50** |

Klickrad (im Bereich um y = −22): Platine Ø 32 × 0,8 bei z 6,8 … 7,6, 0,1 Klebefilm bis zur Frontplattenunterkante (7,7), FR4-Abdeckung Ø 30 × 0,6 bei z 7,7 … 8,3 **im Ausschnitt** der Frontplatte (0,2 unter der Frontfläche, tastbare Mulde). Die Platine hält nur der Klebering (Ø 32 gegen Ø 30,6, 0,7 breit).

Klinke (SJ-43504, Pads auf B.Cu, Ursprung = Pad-Ebene, UNGEPRÜFT): z 1,4 … 6,4, ragt 1,1 über die Platinenvorderseite, 0,4 Luft zur Klickrad-Platine. Fällt der Überstand auf 1,9 aus (Variante B), wird das Gerät 9,0 mm dick; `E2_JACK_Z0/Z1`, `E2_T` und die Schichten entsprechend setzen.

Die Reserve von 0,3 gegenüber den nominal 8,2 mm steckt im 0,25-mm-Luftspalt unter dem Display und in den 0,4 mm über der Klinke.

## Prüfergebnis v2 (`build_v2.py`, zuletzt gelaufen: ALLES OK)

- 5 STL wasserdicht (trimesh), Bounding-Boxen stimmen mit Soll (±0,05). Gesamtmaß laut Modell **40,00 × 90,00 × 8,50**.
- Rückseitenhöhe: Akku 3,30, USB-C 3,18, ESP 3,10, Klinke 3,10 unter der Platine (Grenze 3,3), tiefste Kante z = 1,20 (Klinke 1,40).
- Kollision per Boolean-Schnitt, 14 Körper (3 gedruckte Teile, Frontplatte, Abdeckung, 9 Attrappen): keine Überschneidung > 0,02 mm³. Die Attrappen berühren sich nur flächig (Platine auf Auflager).
- DXF: Außenkontur gegen Soll gelesen und stimmt; Steg Displayfenster → Klickrad-Ausschnitt 6,5 mm.
- Wandsondierung (Strahlen nach innen, Stichprobe): Rahmen ohne Auflagesteg 99,8 % der Punkte ≥ 0,8 mm; die Ausreißer sind Kanten- und Facettenartefakte. **Bekannt dünn:** Auflagesteg-Innenkante 0,4 hoch, Restwand unter der M1,6-Senkung in der 1,0-mm-Rückwand nur 0,3 mm (dann lieber FR4 0,8 oder Senkung flacher).
- **Nicht geprüft:** Passung an echten Teilen, Slicer, Steifigkeit der 1,0-Rückwand und der 0,8-Frontplatte, Touch durch die Abdeckung, Haptik, Stecker-Zugang (Klinke/USB-C).

## Platzhalter und Annahmen v2

| Parameter | Wert | Anmerkung |
|---|---|---|
| `E2_PCB` | 37 × 84, R 4 | Floorplan nicht final |
| `E2_ESP*` | 25,5 × 18 × 3,1, um 90° gedreht, oben | gedreht, damit Akku (50 lang) neben die Klinke passt; Pinprüfung WROOM-1 offen |
| `E2_JACK_X`, `E2_JACK_Z0/Z1` | −12 / 1,4 … 6,4 | Einbaulage (Pads hinten) ungeprüft; Platinenausschnitt = ganze Buchse (9,1 × 14) + 0,45, nicht nur 10,55 × 9,3 |
| `E2_USB_X` | +10 | |
| `E2_BATT`, `E2_BATT_Y` | 34 × 50 × 3,3, y = −3,5 | Zellendatenblatt fehlt |
| `E2_DISP_Y`, `E2_DISP_ACTIVE_DY` | 20,43 / 0 | aktive Fläche mittig im Modul angenommen; FPC-Seite ungeprüft |
| `E2_PCB_SLOT` | 14 × 1,2 bei (0, −3,2) | FPC-Schlitz |
| `E2_WHEEL_Y`, `E2_LRA*` | −22 / 10 × 10 × 1,0 bei +6 | |
| `E2_PWR_*` | y 22,5, z 3,0, Taster 2,1 × 2,0 × 1,5 | Tastertyp offen |
| `E2_SCREWS` | 5 Positionen | selbstschneidendes Kernloch Ø 1,4 ungeprüft |
| `E2_R` | 4,5 | statt 6: die Klinken-Öffnung bei x = −12 braucht Wand vor der Ecke |

## Offene Punkte v2

- **Abstand unter dem Display nur 0,25 mm:** Bauteile auf der Platinenvorderseite im Displaybereich sind faktisch nicht möglich (Display 2,05 mit Touch). Vorn nur unter dem Klickrad (1,5 mm Luft, minus Bauteilhöhe der Radrückseite 0,8 bzw. LRA 1,0).
- **Akku 303450 neben Klinke:** passt nur, weil das ESP-Modul gedreht oben liegt (25,5 breit statt lang). Mit 18 × 25,5 aufrecht fehlen etwa 2,7 mm.
- Klinke/USB-C: Stecker mit dickem Kragen kommen nicht an die Buchse (Öffnung 9,6 × 5,5 bzw. 9,4 × 3,65 in 1,2 mm Wand, Buchse 0,8 bzw. 1,0 zurückgesetzt). Schlanke Stecker nötig; ungeprüft.
- Klickrad-Platine nur geklebt (Ring 0,7); Haltefüße/Schraubdome in der Hauptplatine offen.
- Mitteltaste entfällt als Bauteil (kapazitiv), keine mechanische Taste im Modell.
- Platine liegt nur auf vier 0,8-mm-Auflagern; Andruck von vorn (Schaumstoffband) offen.
- Hauptplatine braucht Sperrzonen: Schraubdome (Ø 3,6 an 5 Stellen, Rückseite), Rückseite der Klickrad-Platine über der Klinke (x −16,5 … −7,5, y −43 … −29).


# Endgerät v3 (44 × 100 × 10 mm, für Hauptplatine Rev. 3)

Grundlage: `TEILE.md` (Ziel-Maße, Klickrad v2, Hauptplatine Stand 2026-10-04) und `hardware/pcb/hauptplatine/README.md` (Abschnitt „Mechanik und Übergabe an das CAD“). Quellen: `endgeraet_v3.py` (Geometrie), `params.py` (Block ENDGERAET v3, Präfix `V3_`), `build_v3.py` (Export, DXF, Vorschau, Prüfung). v1 und v2 bleiben unverändert (v2 gilt für die alte 37 × 84-Platine und ist damit überholt).

```
.venv/bin/python build_v3.py   # schreibt stl/endgeraet_v3/, dxf/endgeraet_v3/, vorschau/endgeraet_v3_*.png; Exitcode 1 bei Fehler (ca. 30 s)
```

Koordinaten = Board-Koordinaten des Platinen-README (Platinenmitte = Gerätemitte = 0, Blick von vorn, x rechts, y oben). Z: Rückseite außen = 0, Front außen = 10,0. STL liegen in Einbaulage = Druckausrichtung (Rückseite auf dem Bett).

## Dicke 10,0 mm (Herleitung)

| Schicht (von hinten) | von … bis | Dicke |
|---|---|---|
| Rückwand (gedruckt) | 0,00 … 1,00 | 1,00 |
| Rückzone (Akku, Modul, USB-C, Klinke hinten, microSD, C29) | 1,00 … 4,95 | **3,95** |
| Hauptplatine | 4,95 … 5,95 | 1,00 |
| Luft (Display-Abstand, Vorgabe ≥ 1,1) | 5,95 … 7,05 | 1,10 |
| Display-Modul mit Touch | 7,05 … 9,10 | 2,05 |
| Klebefilm OCA/VHB | 9,10 … 9,20 | 0,10 |
| Frontplatte Acryl/Glas | 9,20 … 10,00 | 0,80 |

`build_v3.py` rechnet diese Summe nach und bricht ab, wenn sie nicht 10,00 ergibt oder die Luft unter 1,1 fällt. Engste Anforderung hinten: USB-C 3,18, Modul 3,10, Klinke 3,10 (alle passen in 3,95); der Akku darf höchstens 3,95 − 0,3 Luft = **3,65 mm** dick sein.

**Abweichung zur Hauptplatine/TEILE.md:** Dort steht Rückzone 4,05 mm und Zelle ≤ 3,7 mm. Der Wert 4,05 ergibt sich nur ohne den 0,1-mm-Klebefilm zwischen Display und Frontplatte (hat v2 auch). Bei „bis 10 mm“ bleiben mit Klebefilm 3,95 mm. Wer die 4,05/3,7 halten will, braucht 10,1 mm Gerätedicke (`V3_T = 10.1`, alles andere rechnet sich mit) oder verzichtet auf den Klebefilm (Rahmen-Klebung der Frontplatte allein, Display lose). Vorschlag für TEILE.md: „Rückzone 3,95 mm, Zelle ≤ 3,65 mm“ (nicht geändert, da TEILE.md tabu).

## Teile

| Teil | Datei | Fertigung | Maß (B × L × H) |
|---|---|---|---|
| Rahmen | `stl/endgeraet_v3/rahmen.stl` | Druck, ASA (Voron) oder PETG (SV06 Ace) | 44 × 100 × 10, Ecken R 5,5 (Platine R 4 + 1,5), Wand 1,2, Randsteg 0,8; Öffnungen Klinke, USB-C, microSD (links); 3 vordere Dome mit Rippen |
| Rückwand | `rueckwand.stl` | Druck, ASA/PETG | 42,2 × 98,2 × 1,0 (+ 3 Stege bis z 4,95, Akku-Haltestege 1,0 hoch, Biegezunge für SW1 mit Stößel bis z 3,55) |
| Frontplatte | `dxf/endgeraet_v3/frontplatte.dxf` (STL nur zur Prüfung) | Zuschnitt Acryl/PC 0,8 oder Glas | 42,2 × 98,2, Klickrad-Ausschnitt Ø 30,6 bei (0, −25), Ecken R 4,6 |
| Display-Druckmaske | Layer `DRUCKMASKE_FENSTER` derselben DXF | Rückdruck schwarz außerhalb | 33,9 × 41,3 (aktive Fläche 33,1 × 40,5 + 2 × 0,4), Mitte y = 19,45 (ANNAHME) |
| Klickrad-Abdeckung | `dxf/endgeraet_v3/klickrad_abdeckung.dxf` | FR4 0,6 | Ø 30 |
| Schrauben | – | 3 × M1,6 × 8 Senkkopf, selbstschneidend in Ø 1,4 | |
| Klebefilm 0,1 | – | Frontplatte↔Rahmenlippe, Display↔Frontplatte, Klickrad-Platine↔Frontplatte, Abdeckung↔Klickrad-Platine | |

**Kein DXF für die Rückwand:** Sie trägt die hinteren Stege, die Akku-Haltestege und die Taste, eine FR4-Variante wie in v2 geht damit nicht. Die DXF für Frontplatte (mit Druckmaske) und Abdeckung sind sinnvoll und enthalten (Layer `SCHNITT`, `DRUCKMASKE_FENSTER`, `INFO`; `INFO`-Text vor dem Versand entfernen).

## Umsetzung der Vorgaben aus TEILE.md / Platinen-README

| Vorgabe | Umsetzung |
|---|---|
| Klinke SJ-43504, x = −12, Randschlitz 6,8 | Wandöffnung 9,6 breit im Boden, von Rückwand-Oberkante bis Klinke oben + 0,1 (z 1,0 … 6,95), oben R 1,5 |
| USB-C x = +9, Ausschnitt 9,24 × 6 | Wandöffnung 9,4 breit, z 1,0 … 5,1 (Annahme: Buchse komplett hinter der Platine) |
| microSD (−13,7; 37,5), Einschub von links | Öffnung linke Wand 12,0 × 2,3 (z 2,85 … 5,15), Mitte y = 37,5 |
| SW1 (15; −30), Rückseite | **Biegezunge in der Rückwand** (5 × 12 mm, U-Schlitz 0,6, Gelenk am +y-Ende), Stößel Ø 1,8 bis 0,2 mm unter den Taster; Federrate grob 7 N/mm, Randfaser 1,4 % (Rechnung im Build, UNGEPRÜFT) |
| Antennen-Keepout nicht durch Metall/Kohle | Im Keepout (x 12,7 … 20,7, y 28 … 47, volle Innenhöhe) liegt nur Kunststoff (Wand/Lippe); Schrauben, Akku, Taste, Stege sind ausgeschlossen (Build prüft per Boolean). Druck mit **normalem ASA/PETG, kein Carbon-/Metallic-/Kupferfilament**, Frontplatte Acryl oder Glas |
| LRA-Ausschnitt 14 × 10 um (0, −19) | in der Platinen-Attrappe; LRA-Attrappe 12 × 6 × 3,0 ragt 0,65 mm in den Ausschnitt, 4,3 mm Luft zur Rückwand |
| Klickrad Ø 32, Mitte (0, −25), Abdeckung Ø 30 / 0,6 FR4 | Platine 8,30 … 9,10 per Klebefilm unter der Front, Abdeckung 9,2 … 9,8 im Ausschnitt (0,2 unter der Frontfläche) |
| Display-Fenster 2,06" | Modul 34,8 × 43,1 (Maße aus v2, **nicht** an der Zeichnung des gekauften Moduls geprüft), Oberkante y = 41,0, Luft nach hinten 1,1 |
| Akkufach x −16 … 16, y −12 … 26,5 | Attrappe 32 × 38,5 × 3,65 auf der Rückwand; Haltestege 0,8 × 1,0 außerhalb (0,2 Spiel), Litzenlücke bei BT1 (x −12,5) |
| 3 Befestigungslöcher Ø 1,8 | siehe nächster Abschnitt |
| Display-Luft ≥ 1,1 | genau 1,10 (Assertion im Build) |

## Befestigung (3 Schrauben, Platine wird geklemmt)

Von hinten: M1,6 × 8 Senkkopf (Senkung Ø 3,2 in der Rückwand) → **hinterer Steg** Ø 3,2 (Rückwand, z 1,0 … 4,95, Bohrung Ø 1,8) → Platinenloch → **vorderer Dom** Ø 4,0 (Rahmen, z 5,95 … 9,2, Kernloch Ø 1,4, 2,5 tief). Rückwand und Platine werden in einem Zug zwischen Steg und Dom geklemmt; der Dom hängt über eine 2,4 × 1,2 mm Rippe an der Seitenwand und stützt die Frontplatte. Steg-Durchmesser 3,2 (nicht 4,0), weil der Klinkenkörper hinten bei x = −16,5 beginnt (Steg bei x = −18,2 endet bei −16,6).

- **Eingriff nur 2,05 mm** (1,3 × Ø), unter dem Richtwert 2 × Ø für Kunststoff. M1,6 × 10 stieße an die Frontplatte. Falls es nicht hält: Gewindeeinsatz M1,6 (Dom bis 9,2 hoch, Loch Ø 2,4) oder eine Schraube mit Gewindefurchung (z. B. PT/Delta) für Kunststoff. UNGEPRÜFT.
- **Vierte Ecke (+18,2; +46,2) hat kein Loch** (Antennen-Keepout), die Rückwand ist dort nur im Falz geführt: Klebepunkt oder Rastnase wäre nötig, falls sie klappert. Offen.
- Die Platine liegt sonst nur mit 0,3 mm Spiel in der Wand; Biegung der 1,0-mm-Platine zwischen den Ecken (z. B. beim Stecken des USB-Kabels) nicht bewertet.

## Prüfergebnis v3 (`build_v3.py`, zuletzt gelaufen: ALLES OK, 1 Hinweis)

- 4 STL wasserdicht (trimesh), Bounding-Boxen stimmen (±0,05). Gesamtmaß laut Modell **44,00 × 100,00 × 10,00**.
- Höhenstapel nachgerechnet (Summe 10,00, Luft 1,10). Rückseite: Akku 3,65 (liegt auf der Rückwand, 0,3 Luft zur Platine), USB-C 3,18, Modul 3,10, Klinke 3,10, microSD 1,90, C29 2,70 (Position aus `hauptplatine.kicad_pcb` gelesen), SW1 1,20.
- **Kollisionen:** 19 Körper (2 gedruckte Teile, Frontplatte, Abdeckung, 15 Attrappen: Platine mit Ausschnitten, Display, Akku, Klinke, USB-C, Modul, microSD, SW1, C29, Klickrad-Platine, Rad-Rückseitenbauteile als Vollscheibe, LRA, 3 Schrauben), 43 Paare per Boolean geprüft: keine Überschneidung > 0,02 mm³.
- **Engste Stelle:** Klinke oben (z 6,85) → Rad-Rückseitenbauteile (Unterkante 7,20): **0,35 mm**, wenn die Radrückseite als Vollscheibe mit 1,1 mm Bauteilhöhe angenommen wird (Lage der Teile nicht bekannt; real nur an einzelnen Stellen). Zweitengste: USB-C zur Rückwand 0,77, Modul/Klinke 0,85.
- **Antennen-Keepout:** kein Metall, Akku, Schraube oder Taste darin. **Hinweis (kein Gehäusefehler):** Das Display-Modul (34,8 × 43,1, Oberkante y = 41) überlappt den Keepout (x 12,7 … 17,4, y 28 … 41). Das gilt auch für das Platinen-README (Display-Zone x ±18,5). Wie stark das die Antenne bedämpft, ist offen und gehört in die Platinenprüfung. Der Akku liegt 1,5 mm unterhalb (in y) des Keepouts, aber unter dem Antennenbereich in x.
- Wandsondierung: Rahmen ohne Auflagesteg alle Stichproben ≥ 0,8 mm; der Auflagesteg der Frontplatte ist ein Keil (0,4 mm hoch an der Innenkante), wie in v2. Rückwand ≥ 0,7 mm (Wand um die Stegbohrung).
- Maße: Rahmen 44 × 100 × 10 und Rückwand 42,2 × 98,2 × 4,95 passen auf den SV06 Ace (220 × 220) und den Voron.

## Druck (Einbaulage = Ausrichtung, Rückseite z = 0 auf dem Bett)

| Teil | Material | Schicht | Wände/Infill | Stützen |
|---|---|---|---|---|
| Rahmen | ASA (Voron) bevorzugt, sonst PETG; **kein Carbon/Metallic** (Antenne) | 0,12 … 0,16 | 3 Perimeter, 100 % (Wände sind zu dünn für Infill) | **ja, lokal:** unter den 3 vorderen Domen mit Rippen (z 5,95; Rippe überbrückt 0,6 … 1,3 mm von der Wand). Alternativ ohne Stützen drucken und die 1-mm-Brücke akzeptieren |
| Rückwand | wie Rahmen | 0,2 | 5 Schichten oben/unten, 100 % | nein (Senkungen sind 45°-Kegel) |

Brücken/Überhänge in Einbaulage (aus `build_v3.py`): Öffnungen Klinke (7 mm im Scheitel, R 1,5), USB-C (9,4), microSD (12,0 breit, 12-mm-Brücke, an der Grenze), Stufe Wand/Randsteg bei z = 1,0 (0,4 mm), Dome/Rippen bei z = 5,95 (siehe oben), 45°-Keil unter der Lippe (z 8,4 … 8,8). Elefantenfuß-Kompensation 0,1 an der Rückwand aktivieren (sie sitzt im Falz, Spiel 0,1 je Seite). ASA-Schrumpf 0,3 … 0,5 %: Probedruck von Rahmen und Rückwand zuerst. Biegezunge: Schichtlinien liegen in der Ebene der Zunge (günstig), Probedruck nötig.

## Montage

1. Frontplatte mit der Innenseite nach oben: Display mit Klebefilm einkleben (Fenster zentrieren, FPC nach unten), Klickrad-Platine (LRA bereits auf der Rückseite) und Abdeckung aufkleben.
2. Frontplatte mit Display in den vorderen Falz des Rahmens kleben (Lippe).
3. Hauptplatine von hinten einsetzen (Klinke/USB-C in die Wandöffnungen, die 3 Löcher über den vorderen Domen), Display-FPC und Klickrad-FFC anschließen, Akku-Litzen an BT1.
4. Akku (≤ 3,65 mm) zwischen die Haltestege der Rückwand legen, Rückwand in den hinteren Falz setzen, 3 × M1,6 × 8 anziehen (nicht überdrehen).

Die FFC-/FPC-Verlegung (J20 Display-FPC, J21 Klickrad-FFC) ist **nicht modelliert**; zwischen Platinenvorderseite (5,95) und Rad-Rückseite (8,30, Bauteile bis 7,20) bleiben 1,25 … 2,35 mm.

## Abweichungen und Vorschläge (TEILE.md/Platinen-Ordner nicht geändert)

1. **Rückzone 3,95 statt 4,05, Zelle ≤ 3,65 statt ≤ 3,7** (Klebefilm 0,1, s. o.). Vorschlag: in TEILE.md übernehmen oder Gerätedicke 10,1 mm festlegen.
2. **LRA:** Klickrad-README nennt die Freifläche 16 × 6 mm (x ±8), der Ausschnitt in der Hauptplatine ist nur 14 mm breit (x ±7, Platinen-README/TEILE.md). Ein 16 mm breiter LRA ragt über den Ausschnitt in die Platine. Das Modell nimmt einen 12 × 6 × 3,0-LRA (Klasse VL120628H); Vorschlag: Ausschnitt auf ≥ 16,5 × 6,5 vergrößern (Antennen-/Routing-Folgen prüfen) oder nur LRAs ≤ 13 mm Länge zulassen. Ein 3,0-mm-LRA reicht von z 5,3 bis 8,3 und taucht 0,65 mm in den Ausschnitt.
3. **Antennen-Keepout:** TEILE.md nennt x 12,9 … 20,5 / y 28,2 … 46,8, das Platinen-README x 12,7 … 20,7 / y 28 … 47. Das CAD nimmt die größere Fläche. Display überlappt, s. o.
4. **Klickrad-Mitte (0, −25)** statt −22 (v2). Der Steg zwischen Display-Fenster (unten y = −1,2) und Rad-Ausschnitt (oben y = −9,7) ist 8,5 mm.
5. **Klickrad-Platine nur geklebt** (Ring 0,7 mm zwischen Ø 32 und Ø 30,6): Das Klickrad-README nennt 3 Befestigungslöcher in der Platine, sie werden hier nicht genutzt. Vorschlag: Haltefüße vom Rahmen oder Klickrad-Halter später.
6. Nur 3 Schrauben, Eingriff 2,05 mm (s. o.).
7. Ein/Aus-Taste hinten als Biegezunge statt Seitentaste (SW1 sitzt laut Platine auf der Rückseite bei (15; −30), v1/v2 hatten eine Seitentaste).
8. Rahmen-Außenradius 5,5 (Platine 4,0 + 1,5), nicht 7 oder 4,5 wie v1/v2.

## Nicht geprüft (v3)

- Alles Physische: Passung an echten Teilen, Slicer, Steifigkeit der 1,0-mm-Rückwand und der 0,8-mm-Frontplatte, Biegezunge und Taster-Hub, Schrauben-Eingriff/Auszugskraft, Brücken im Druck, Touch durch die Abdeckung, Haptik.
- Mechanik der Steckverbinder: Klinke (STEP-Versatz +1,9 / −3,1, Körper hinten 9 breit, im Schlitz 6,8 breit als Annahme; Stecker-Zugang durch 1,5 mm tiefen Wandkanal, dicke Stecker passen evtl. nicht) und USB-C (Annahme „komplett hinten“; wenn die Buchse in der Platinenebene sitzt, muss die Öffnung `USB_OPEN_TOP` höher, dann Wandrest über der Öffnung prüfen), microSD (Hüllkörper 13 × 14 × 1,9 ist Platzhalter, Öffnung 12 × 2,3, Karte ragt aus der Wand).
- Lage von Display und aktiver Fläche (FPC-Seite) und damit das Druckfenster; Bauteile auf der Radrückseite (Vollscheibe = Worst Case).
- Rückseitenbauteile der Hauptplatine außer C29, Modul, Klinke, USB-C, microSD, SW1 sind nicht einzeln modelliert (alle ≤ 1,5 mm, Haltestege nur 1,0 hoch; gegen die KiCad-Positionen gelesen: kein B.Cu-Bauteil steht auf den Haltestegen, z. B. R37 bei (17,2; −13,0) liegt außerhalb).
- Antennenverstimmung durch Display, Akku, Schrauben, Wand: nicht gemessen.
- FPC-/FFC-Führung, Litzen, Kleberdicken in der Praxis (±0,05 beeinflussen die Luft von 1,10 direkt).
