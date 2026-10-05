# Klickrad-Modul v2 (KiCad 9)

Runde Platine (Ø 32 mm, **0,8 mm** (1,0 mm als Alternative), **2 Lagen**) mit Touch-Rad, kapazitiver Mitteltaste, Guard-Kanal, Haptik-Treiber und Lötpads für den aufgeklebten LRA. Touch-Controller **AT42QT2120** (I²C 0x1C, Wheel-Modus), Haptik **DRV2605L** (0x5A): Schaltung, Elektrodenform und Firmware-Belegung stammen so weit wie möglich von der **Tangara-Faceplate** (cool tech zone). Schnittstelle und Maße folgen `TEILE.md`, Abschnitt „Klickrad-Modul“, mit den unten genannten Abweichungen.

Stand: 2026-10-05, Revision 2 (v1 mit MPR121 bleibt in der git-Historie; 2026-10-05: J1-Footprint, Steckerausrichtung und LRA-Freifläche nach `docs/REVIEW-HAUPTPLATINE.md` K1/H6 geändert, neu geroutet). Erstellt und geprüft mit KiCad 9.0.9 (`kicad-cli`) im Container. **Nichts davon wurde an echter Hardware getestet.**

## Lizenz und Herkunft

Dieses Modul übernimmt Schaltung, Elektrodengeometrie (als Algorithmus), Symbol und Pinbelegung aus der Tangara-Faceplate (`tangara-hw/tangara-faceplate`, `tangara-hw/touchwheel-cover`) von **cool tech zone** (https://cooltech.zone/tangara/), lizenziert unter **CERN-OHL-S-2.0**. Das Modul ist deshalb ebenfalls **CERN-OHL-S-2.0** (Lizenztext: `LICENSE` in diesem Ordner, Kopie aus dem Tangara-Repository; Quellenangabe und Änderungen sind hier und im Schaltplan-Titelblock vermerkt, alle Quelldateien liegen im Repository). Die Firmware-Treiber von Tangara (`touchwheel.cpp`, `haptics.cpp`) sind GPL-3.0 und nicht Teil dieses Ordners.

Quellen: Blogartikel „A Deep Dive Into the Design of Tangara's Touchwheel“ (https://cooltech.zone/tangara/blog/2024-02-07-touchwheel/), „Interpolated Electrode SVG Tool“ (https://cooltech.zone/tangara/labs/touchwheel-electrode-tool/, der Quelltext steht in der Seite), AT42QT2120-Datenblatt (Atmel 9634E–AT42–06/12), Microchip „Capacitive Touch Sensor Design Guide“ DS00002934.

## Übernommen von Tangara / angepasst / neu

| Teil | Status | Tangara-Faceplate | Klickrad v2 |
|---|---|---|---|
| Touch-Controller | **übernommen** | AT42QT2120, VQFN-20 (`VQFN-20-1EP_3x3mm_P0.45mm_EP1.55x1.55mm`), Comms-Modus (MODE an GND), I²C 0x1C, Exposed Pad hier auf GND (Abweichung) | gleich (Symbol aus `faceplate-symbols.kicad_sym`, nur Footprint-/Datenblattfeld ergänzt) |
| Tastenbelegung | **übernommen** | KEY0–2 = Wheel, KEY3 = Mitteltaste, KEY4 = Guard, KEY5–11 unbenutzt | gleich (Firmware-Treiber `touchwheel.cpp` läuft unverändert) |
| Serienwiderstände | **übernommen** (Bauform angepasst) | 10 kΩ 0603 in jeder Elektrodenleitung (R1–R3 Wheel, R5 Taste, R6 Guard) | 10 kΩ **0402** (R1–R3 Wheel, R4 Taste, R5 Guard); Datenblatt 3.1: 4,7 … 20 kΩ |
| Cs-Kondensatoren | **entfällt wie bei Tangara** | keine | keine (Datenblatt: „no external Cs required“) |
| RESET | **übernommen** | R7 10 kΩ nach 3V3 | R6 10 kΩ nach 3V3 |
| CHANGE | **übernommen** | direkt an Stecker, Pull-up in der MCU | direkt an J1 Pin 5 (kein Pull-up auf dem Modul) |
| Entkopplung QT2120 | **übernommen** | 0,1 µF + 1 µF an VDD | C1 0,1 µF + C2 1 µF (0402) |
| DRV2605L | **übernommen** | VSSOP-10, VDD 1 µF, REG 1 µF, IN/TRIG an GND, EN über 10 kΩ nach 3V3, OUT± auf Lötpads | gleich (U2, C3, C4, R7, Lötpads TP1/TP2); EN jetzt wie bei Tangara über 10 kΩ statt fest an 3V3 |
| Wheel-Elektroden | **übernommen, skaliert** | 3 verschachtelte Elektroden (3 Ringe), r = 7,9 … 19,9 mm, Abstand 0,29 mm, Deadzone 2 mm | gleicher Algorithmus (SVG-Tool), r = 6,3 … 12,3 mm (Ringbreite 12 → 6 mm), Abstand 0,25 mm, Deadzone 1,5 mm, Spitzen < 0,2 mm abgerundet |
| Mitteltaste | **übernommen** | kapazitive Scheibe r = 2,5 mm (`qtouch-button`) | gleich, r = 2,5 mm (Ø 5 mm) |
| Guard | **übernommen, angepasst** | Ring r = 22,2 mm, Linie 1 mm, 2,35 mm vom Rad entfernt, über 10 kΩ an KEY4 | ein Kupferpolygon: drei Kreisbögen r = 13,5 … 15,4 mm (wegen der drei Befestigungslöcher geteilt), innen durch zwei schmale Stege (0,2 mm) verbunden, 1 Via, 1,2 mm Abstand zum Rad, über 10 kΩ an KEY4 |
| GND unter dem Rad | **übernommen** | GND-Gitter auf B.Cu (Linie 0,127 mm, Lücke 1,016 mm, 45°), Vorderseite unter dem Rad ohne Kupferfüllung | gleich (Gitter), Vorderseite ohne Füllung |
| Lagenzahl | **übernommen** | 2 Lagen | 2 Lagen, 1,0 mm statt 1,6 mm |
| Wheel-Position 0 / Drehsinn | **übernommen** | 0 oben, steigend gegen den Uhrzeigersinn | gleich, siehe Abschnitt „Wheel-Position“ |
| Abdeckung | **übernommen** | 0,6 mm FR4 mit Siebdruck (`touchwheel-cover`) | KiCad-Projekt `abdeckung/` (Ø 30), Beschriftung MENU / ◄◄ / ►► / ►II |
| I²C-Pull-ups | neu | auf der Hauptplatine | R8/R9 4,7 kΩ, **DNP** |
| 10 µF am DRV2605L | entfällt | – | nicht auf dem Modul (Platzmangel auf 2 Lagen); bei Spannungseinbruch beim LRA 10 µF auf der Hauptplatine nahe dem Stecker ergänzen |
| Stecker | neu | FFC 15-polig (Molex 505278-1533) | **Molex 503480-0600**, FFC/FPC 0,5 mm, 6-polig, Dual Contact, Bauhöhe 1,0 mm, Pin 6 = Reserve; Landmuster wie J21 der Hauptplatine, Kabelmündung nach Süden |
| Rundform, Löcher, LRA-Fläche | neu | Rechteck mit Display | Ø 32, 3 Löcher, LRA-Freifläche 14 × 6 mm für flachen LRA (passt in den Ausschnitt 14 × 10 der Hauptplatine) |
| Display, LCD-Treiber, Backlight | entfällt | JD-T1800, Q1 … | nicht vorhanden |

## Änderungen gegenüber v1

| | v1 | v2 |
|---|---|---|
| Touch-Controller | MPR121 (0x5B), 12 Segmente à 30° | AT42QT2120 (0x1C), 3 Wheel-Elektroden + Taste + Guard |
| Auswertung | Rohwerte → Winkelberechnung in der Firmware | Wheel-Position 0 … 255 direkt vom Chip (Tangara-Treiber) |
| Mitteltaste | SMD-Taster (Omron B3U-1000P) auf J1 Pin 6 | kapazitiv (KEY3, wie Tangara); **J1 Pin 6 ist Reserve und nicht beschaltet** |
| Lagen / Dicke | 4 Lagen, 1,0 mm | **2 Lagen, 0,8 mm** (GND-Gitter auf B.Cu) |
| Stecker | JST-SH 1,0 mm seitlich (>1,5 mm hoch) | **Molex 503480-0600** FFC 0,5 mm, 1,0 mm hoch (Dünnbau, Gerätedicke 8,5 mm) |
| LRA-Fläche | 16 × 6 mm, LRA 3,6 mm hoch | 14 × 6 mm (x −7 … +7, y +3 … +9; in Rev. 2 zuerst 16 × 6), LRA **bis 3,0 mm Höhe**, flache Typen siehe Abschnitt Mechanik |
| Touch-Ring | r = 6,5 … 12,8 mm | r = 6,3 … 12,3 mm; zusätzlich Guard r = 13,5 … 15,4 mm |
| Haptik EN | fest an 3V3 | über 10 kΩ an 3V3 (wie Tangara) |
| Pull-ups | R2/R3 4,7 kΩ (DNP) | R8/R9 4,7 kΩ (DNP); CHANGE-Pull-up entfällt (MCU-intern, wie Tangara) |
| Router | Freerouting | eigener Gitter-Router `tools/route.py` (Freerouting fand keine vollständige Lösung) |
| Abdeckung | nur gedruckt (Ø 30 / Ø 11,6, 1,95 mm) | zusätzlich FR4-Abdeckung 0,6 mm, siehe unten |

## Funktion

| Block | Bauteil | Beschaltung |
|---|---|---|
| Touch-Controller | U1 AT42QT2120 (VQFN-20) | MODE (Pin 10) und VSS an GND, VDD 0,1 µF (C1) + 1 µF (C2), RESET über 10 kΩ (R6) an 3V3, KEY0–2 über je 10 kΩ an die drei Wheel-Elektroden, KEY3 über 10 kΩ an die Mitteltaste, KEY4 über 10 kΩ an den Guard, KEY5–11 offen, CHANGE → J1 Pin 5 |
| Haptik-Treiber | U2 DRV2605LDGSR (VSSOP-10) | VDD (Pin 6, 10) an 3V3 mit 1 µF (C3, wie Tangara), REG 1 µF (C4), IN/TRIG an GND, EN über 10 kΩ (R7) an 3V3, OUT+/OUT− → Lötpads TP1/TP2 |
| Stecker | J1 Molex 503480-0600, FFC/FPC 0,5 mm, 6-polig, Rückseite | siehe unten |
| Pull-ups | R8 (SDA), R9 (SCL) 4,7 kΩ | **DNP**, nur für den Einzeltest des Moduls (Waveshare-Board hat 2,2 kΩ) |

### Pinbelegung J1

| Pin | Signal | Hinweis |
|---|---|---|
| 1 | 3V3 | versorgt AT42QT2120 und DRV2605L |
| 2 | GND | |
| 3 | SDA | |
| 4 | SCL | |
| 5 | CHANGE | AT42QT2120, open drain, aktiv low, **kein Pull-up auf dem Modul** (MCU-interner Pull-up wie bei Tangara, GPIO17 am Waveshare-Board) |
| 6 | (BTN) Reserve | nicht beschaltet. Die Mitteltaste ist kapazitiv (KEY3 des QT2120). Pin bleibt belegt/frei, falls später ein mechanischer Taster nach GND ergänzt wird; KEY3 bleibt dann trotzdem für die Berührung frei. |

### Firmware-Hinweise (aus `tangara-fw/src/drivers/touchwheel.cpp` und `haptics.cpp`)

- Adresse 0x1C. Registerfolge wie Tangara: `RESET` schreiben, 300 ms warten; `SLIDER_OPTIONS = 0xC0` (Wheel an, Keys 0–2); Key-Control KEY0–2 = `0b100` (AKS-Gruppe 1), KEY3 = `0` (Mitteltaste ohne AKS, Software-Entkopplung), KEY4 = `0b10100` (Guard, AKS-Gruppe 1), KEY5–11 = `1` (aus); `RECALIBRATION_DELAY = 0` (Finger nicht wegkalibrieren); `CHARGE_TIME = 0x10`. Status: Bit 7 Kalibrierung, Bit 1 Wheel erkannt (Register `SLIDER_POSITION`), Bit 0 Taste; `KEY_STATUS_A` Bit 3 = Mitteltaste, Bits 0–2 = Wheel berührt.
- Die Mitteltaste liefert **Berührung**, keinen Klick. Der Haptik-Klick (DRV2605L „Strong Click“/„Sharp Click“) wird von der Firmware ausgelöst, wie bei Tangara.
- DRV2605L LRA: Nennspannung `0x46`, Overdrive `0x7B`, Treiberzeit für 235-Hz-LRAs `0b10010000`, geschlossene Regelung, einmalig Auto-Kalibrierung und Ergebnis speichern. Der DRV2605L läuft hier mit EN über 10 kΩ an 3V3, Standby per Register 0x01.

### Wheel-Position (Abstimmung mit der Firmware)

Tangara-Konvention, hier übernommen: **Position 0 = oben, steigend gegen den Uhrzeigersinn**, in Draufsicht auf das Modul (von vorn). „Oben“ ist die Seite gegenüber dem Stecker. Der Stecker J1 liegt bei 270° (unten).

| Position | 0 | 64 | 128 | 192 |
|---|---|---|---|---|
| Richtung (Tangara: up / left / down / right) | oben (90°) | links (180°) | **unten, Stecker-Seite (270°)** | rechts (0°) |

Lage der Elektroden (Maxima der Antwort bei einem Finger auf dem mittleren Radius, Winkel gegen den Uhrzeigersinn ab rechts, von vorn):

| Taste | Elektrode (Pad in `qtouch-wheel`) | Maximum bei |
|---|---|---|
| KEY0 | 1 | 206° (unten links) |
| KEY1 | 2 | 326° (unten rechts) |
| KEY2 | 3 | 86° (oben) |

Herleitung: Die Elektrodenform ist um 120° drehsymmetrisch. Die drei Maxima wurden so gedreht, dass sie an denselben Stellen liegen wie bei der Tangara-Faceplate nach deren Einbaudrehung von −148° (dort Maxima bei 206,3° / 326,3° / 86,3° für KEY0/1/2); damit sind Zuordnung und Drehsinn der Tangara-Firmware (`up = 0`, `left = 64`, `down = 128`, `right = 192` in `input_touch_wheel.cpp`) gültig. **Ungeprüft:** Das ist aus den Footprint-Daten gerechnet (Modell: Überdeckung Finger–Elektrode), nicht gemessen. Falls die Position am echten Rad um einen festen Winkel versetzt ist, in der Firmware einen Offset setzen.

## Elektroden-Geometrie (skaliert von Tangara)

Erzeugt durch `tools/wheel_geometry.py` (Port des Tangara-SVG-Werkzeugs). Parameter von Tangara aus dem Footprint `qtouch-wheel` zurückgerechnet (Flächen 3 × 295 mm², kleinster Abstand 0,29 mm, r = 7,9 … 19,86 mm: innen 8, Breite 12, 3 Ringe, Abstand ≈ 0,3, Deadzone 2).

| Größe | Tangara | Klickrad v2 |
|---|---|---|
| Radius innen / außen | 7,9 / 19,9 mm | 6,3 / 12,3 mm |
| Elektrodenzahl, Ringe | 3, 3 | 3, 3 |
| Abstand zwischen Elektroden | 0,29 mm | 0,25 mm |
| Deadzone | 2 mm | 1,5 mm |
| Fläche je Elektrode | 295 mm² | 87,6 mm² |
| Mitteltaste | r 2,5 mm (19,6 mm²) | r 2,5 mm (19,6 mm²), wie Tangara |
| Guard | Ring r 22,2 mm, 1 mm breit (≈ 140 mm²) | 3 Bögen + Stege r 13,5 … 15,4 mm, 151 mm² (größer als eine Wheel-Elektrode, wie im Datenblatt gefordert) |
| Abstand Rad – Guard | 2,35 mm | 1,2 mm |
| Abstand Rad – Taste | 5,4 mm | 3,8 mm |
| Kleinste Struktur | 0,29 mm | 0,25 mm Abstand, ≥ 0,2 mm Breite |

Das Datenblatt nennt für Wheels „typisch 30 … 50 mm Durchmesser, Segmentbreite typisch 12 mm“. Unser Rad hat 24,6 mm Durchmesser und 6 mm Breite und liegt damit **unter dem typischen Bereich**; ein Modell (Finger als Scheibe, Vektorsumme der drei Elektroden) ergibt für die Winkelauflösung ähnliche Werte wie die Tangara-Geometrie (maximale Abweichung ≈ 12° gegenüber ≈ 14° bei Tangara). **Das ersetzt keinen Test am Rad.**

## Mechanik

- Umriss Ø 32,0 mm, Dicke **0,8 mm** (Bestellung: 0,8 mm; 1,0 mm geht ebenfalls, dann sind Platine und Gerät 0,2 mm dicker und die Touch-Grundkapazität etwas kleiner). Drei Löcher Ø 2,2 mm (NPTH) auf r = 14,6 mm bei 90°, 210°, 330° (wie v1).
- **Stecker J1: Molex 503480-0600** (FFC/FPC 0,5 mm, 6-polig, Easy-On, Dual Contact, 1,0 mm hoch; Molex-Teilenummer bestätigt, DigiKey 5034800600 / 2356622). Lage bei 270° (6-Uhr-Richtung), Mitte bei (0; −10,8) mm, Rückseite. **Footprint (Review K1/H6, geändert):** `lib/Klickrad.pretty/Molex_503480-0600_Hauptplatine` ist das Landmuster von J21 der Hauptplatine (Signalpads 0,3 × 0,7, Nagelpads 0,8 × 1,0 bei x ±2,045, 1,2 mm hinter der Pad-Mitte); der frühere Hirose-FH12-Nachbau (Nagelpads 1,8 × 2,2 bei x ±3,15) ist entfernt. **Ungeprüft:** Nagelpad-Form und -Lage in Y (Molex-Zeichnung SD-503480-001 ist nur als Text lesbar, die Grafik nicht), beide Platinen müssen bei einer Korrektur gemeinsam geändert werden.
  - **Kabelmündung zeigt nach Süden (weg vom Radmittelpunkt)**, Signalpads bei y = −12,8 mm, Nagelpads bei y = −9,6 mm. Vorher (Hirose-Footprint) zeigte die Mündung nach Norden zum Rad; das war falsch: J21 der Hauptplatine hat die Mündung ebenfalls nach Norden (Richtung Klickrad), ein Kabel zwischen zwei nach Norden zeigenden Mündungen bräuchte eine 180°-Haarnadel (Reihenfolge der Adern spiegelt sich, Platz 1,25 … 2,35 mm reicht dafür nicht). Mit Mündung Süden an J1 und Norden an J21 läuft das Kabel **gerade und ungedreht** zwischen beiden: Mündung J1 bei y = −37,8 mm (Hauptplatine-Koordinaten, Rad-Mitte bei −25), Mündung J21 bei −44,2 mm, freie Länge ca. 6,4 mm (frühere Angabe der Hauptplatine „3,5 mm“ galt für eine andere Lage; ungeprüft).
  - **Pin 1 auf Pin 1:** J1 Pin 1 (3V3) liegt in der Ansicht von vorn bei x = +1,25 mm, J21 Pin 1 ebenfalls bei x = +1,25 mm (Ansicht von vorn auf die Hauptplatine). Bei geradem, ungedrehtem Kabel gehen alle sechs Adern auf die gleiche Seitenlage: 1 → 1 (3V3), 2 → 2 (GND), 3 → 3 (SDA), 4 → 4 (SCL), 5 → 5 (CHANGE), 6 → 6 (Reserve). Die Pin-Nummern sind nur Beschriftung (der Stecker hat keine Polung), maßgeblich ist die Seitenlage der Pads: x = +1,25 / +0,75 / +0,25 / −0,25 / −0,75 / −1,25 mm = 3V3 / GND / SDA / SCL / CHANGE / Reserve auf beiden Platinen.
  - **Kabelvariante:** FFC 0,5 mm, 6 Adern, 0,3 mm dick, **gerade und ungedreht** (kein Verdrehen, keine Querfalte, nur ein flacher S-Bogen in der Höhe). Beide Stecker sind Dual Contact (Kontakte oben und unten, Anm. 9 der Zeichnung, nur aus dem Text gelesen): Das Kabel darf an beiden Enden mit den Kontakten nach oben **oder** unten stecken, daher sind **Typ A (Kontakte auf gleicher Seite) und Typ B (Kontakte gegenüber) beide zulässig**; ohne Falte ist Typ A bei beiden Steckern (Kontakte des Kabels zur selben Seite) die naheliegende Wahl. Eine Falte quer zum Kabel oder eine 180°-Drehung vertauscht 1 ↔ 6 und ist **nicht** erlaubt. Abgeleitet aus der Geometrie, **nicht an Hardware geprüft**; vor dem Einschalten Pin für Pin durchklingeln (3V3 an Pin 1 beider Stecker, GND an Pin 2 usw.).
  - **Für den Waveshare-Prototyp:** 6-polige FFC-Breakout-Platine, 0,5 mm Raster, auf 2,54-mm-Stifte (Adapter „FPC 0,5 mm 6P“) und passendes FFC-Kabel 0,5 mm, 6-polig; Pin 1 des Adapters ist ebenfalls zu durchklingeln.
- **LRA-Freifläche** (Rückseite, nur Bauteile gesperrt): x = −7 … +7 mm, y = +3 … +9 mm (**14 × 6 mm**, Mitte 6 mm oberhalb des Radmittelpunkts), für einen LRA **bis 3,0 mm Höhe**, bevorzugt X-Achse. Die Hauptplatine hat dort einen Ausschnitt 14 × 10 mm (Mitte 0 / −19 mm, im Klickrad-Bezug y = +1 … +11): Der LRA muss **höchstens 14 mm lang** sein, sonst stößt er an die Ausschnittkante (Review K-Fund LRA-Freifläche; die Freifläche war zuerst 16 × 6 mm und ist an den Ausschnitt angeglichen, ein größerer Ausschnitt in der Hauptplatine wäre die Alternative). Kandidaten (Maße, Achse und Resonanzfrequenz vor der Bestellung im Datenblatt prüfen; Treiberzeit im DRV2605L passend setzen): Vybronics VL120628H (12 × 6 × 2,0 mm, ca. 200 Hz, laut Koordinator), Vybronics VG0832022D (Tangaras BOM-Empfehlung, Maße ungeprüft), 4,5 × 12 × 3,0 (235 Hz) aus `TEILE.md`. Der 8 × 15 × 3,0-LRA (170 Hz) aus `TEILE.md` ist mit 15 mm **zu lang** für den Ausschnitt 14 × 10 und entfällt (ohne Änderung der Hauptplatine). Ein 10 × 10 × 1,0-LRA (Vybronics VLV101040J) braucht y = +1 … +11 und passt wegen der Widerstände R3 … R5 bei y ≈ 0 … 1 **nicht** in diese Revision (nicht umgesetzt). Lötpads TP1 (LRA+) und TP2 (LRA−) liegen **auf der Ostseite** bei x = +13,1 mm, y = −2,4 / −4,8 mm (v1: westlich bei x = −12,3): U2 sitzt östlich, die LRA-Leitungen sind so kurz; die Litzen müssen im CAD zur Ostseite geführt werden. Unter dem LRA liegen das GND-Gitter, Leiterbahnen und Vias unter Lötstopplack.
- Bauteile auf der Rückseite: 0402-Teile 0,5 mm, U1 VQFN 0,85 mm (nominal), **U2 DRV2605L im VSSOP-10 ca. 1,1 mm** und J1 1,0 mm liegen **über der Vorgabe 0,8 mm** (J1 innerhalb der Stecker-Vorgabe ≤ 1,2 mm). Das DSBGA-9-Gehäuse (DRV2605LYZFR, 0,5 mm Raster, ca. 0,6 mm hoch, bei TI als lieferbar gelistet) wäre flacher, wurde aber nicht umgesetzt (Hand- und Routingaufwand; ungeprüft). Vorderseite: nur Kupferflächen unter Lötstopplack, keine Bauteile.
- Bauteilpositionen für CAD: `fertigung/bauteilpositionen.csv` (Bezug Platinenmitte, mm, y nach oben in der Ansicht von vorn).
- **Guard und Schrauben:** Die Guard-Bögen halten 2,2 mm Abstand zur Lochmitte (Schraubenkopf Ø 3,5, Abdeckungstasche Ø 4,0), sie reichen bis r = 15,4 mm, also 0,4 mm über den Rand der Abdeckung (Ø 30) hinaus.
- **Änderungsbedarf in `TEILE.md` / CAD** (nicht Teil dieses Auftrags, deshalb hier gemeldet): 2 statt 4 Lagen; Touch-Ring r = 6,3 … 12,3 mm plus Guard r = 13,5 … 15,4 mm; Mitteltaste kapazitiv statt SMD-Taster (Höhenvorgabe ≤ 1,5 mm entfällt, die Mitteltaste-Kappe Ø 11,0 und das Loch Ø 11,6 in der Abdeckung entfallen); Stecker Pin 5 = CHANGE, Pin 6 = Reserve; I²C-Adresse 0x1C; Wheel-Positions-Konvention.

### Abdeckung: gedruckt (1,95 mm) oder FR4 (0,6 mm)?

Tangara deckt das Rad mit einer 0,6 mm dicken FR4-Platte ab (`touchwheel-cover`: nur Umriss und Siebdruck, kein Kupfer).

- **Gedruckte Abdeckung 1,95 mm passt formal:** Das Datenblatt erlaubt für Wheels/Slider „bis 3 mm Kunststoff“. Sie ist aber mehr als dreimal so dick wie Tangaras 0,6 mm, und unser Rad ist nur halb so breit. Das Signal wird kleiner und weicher. Zusätzlich darf zwischen Platine und Abdeckung **keine Luft** liegen (dünnes doppelseitiges Klebeband 0,05 … 0,1 mm vollflächig; gedruckt mit 100 % Füllung, glatte Seite zur Platine). Mit Druckabdeckung die Schwellen (DTHR-Register 16 … 27) senken und `CHARGE_TIME` prüfen.
- **Empfehlung: FR4-Abdeckung mitbestellen** (`abdeckung/`, wenige Euro, gleiche Platinenfertiger), als erste Wahl für den Prototyp, die gedruckte Abdeckung als Rückfall. Die FR4-Abdeckung ist eben, gleichmäßig dick, hat Siebdruck-Beschriftung und entspricht dem bei Tangara erprobten Aufbau. Aufkleben mit demselben dünnen Klebeband.
- Folge für die Mechanik: Die Oberfläche liegt mit 0,6 mm um **1,35 mm tiefer** als mit der gedruckten Abdeckung. Der Distanzring bzw. die Frontöffnung im CAD (Parameter `E_COVER_T`, `COVER_T`) muss angepasst werden, sonst sitzt das Rad zu tief.

`abdeckung/klickrad-abdeckung.kicad_pcb`: Ø 30 mm, ohne Mittenloch, drei Aussparungen r = 2,1 mm um die Schraubenköpfe der Platine (r = 14,6 mm bei 90°/210°/330°). Siebdruck (F.SilkS): Kreis Ø 11,6 mm (Mitteltaste), Kreis r = 12,4 mm (Außenkante des Rads), „MENU“ oben, ◄◄ links, ►► rechts, ►II unten (Konvention des iPod nano), „v2“. Bestellung: 2 Lagen, **0,6 mm**, ohne Kupfer (beide Lagen leer), Lötstopplack und Siebdruck nach Wunsch (z. B. schwarz/weiß), `abdeckung/fertigung/klickrad_abdeckung_gerber.zip`. Orientierung: oben = Seite gegenüber dem Stecker.

## Lagenaufbau (2 Lagen, Begründung)

Die Tangara-Faceplate ist 2-lagig (1,6 mm, F.Cu und B.Cu, geprüft in `tangara-faceplate.kicad_pcb`), obwohl sie ein 40-mm-Rad trägt. Das gleiche Prinzip genügt hier:

| Lage | Inhalt |
|---|---|
| F.Cu | Wheel (3 Elektroden), Mitteltaste, Guard (3 Bögen); sonst nur wenige kurze Leiterbahnen im Innenring r = 3,65 … 6,15 mm zwischen Taste und Rad (Prüfskript `tools/pruefe_vorderseite.py`) |
| B.Cu | alle Bauteile, Leiterbahnen, **GND-Gitter** (Linie 0,127 mm, Lücke 1,016 mm, 45°, Glättung 2, wie bei Tangara) |

Gründe für 2 statt 4 Lagen: (1) Es gibt nur 6 Durchkontaktierungen zur Vorderseite (3 Wheel, Taste, Guard 3 Bögen = 7 Vias); die Verdrahtung der 20 Netze passt auf die Rückseite, weil der AT42QT2120 nur 5 Tasten verdrahtet und keine Referenzwiderstände braucht (MPR121 v1: REXT, VREG, 12 Elektroden). (2) Die Touch-Flächen brauchen unten eine möglichst unbelegte Masse, das Gitter bei Tangara ist erprobt. (3) Zwei Lagen sind billiger und überall bestellbar.

**Ungeprüft:** Abstand zwischen Elektroden und GND-Gitter ist bei 1,0 mm Dicke kleiner als bei Tangaras 1,6 mm (Grundkapazität höher, Empfindlichkeit etwas geringer). Die Wirkung wurde nicht gemessen. Notfalls das Gitter unter dem Rad ausdünnen (größere Lücke) oder die Schwellen senken.

## Bestückung (Handlötung)

1. Platine mit der Vorderseite auf die Heizplatte oder vorheizen (100 … 120 °C), Rückseite oben.
2. **U1 AT42QT2120 (VQFN-20, 0,45 mm, Exposed Pad 1,55 mm, auf GND):** Paste dünn auftragen (Schablone aus dem Paste-Layer oder Spritze), Pin 1 nach der Silkscreen-Marke, Heißluft ca. 240 … 250 °C. Danach Brücken mit Flussmittel entfernen. Flussmittel-Reste anschließend gründlich reinigen (Datenblatt 3.3: Rückstände stören die Touch-Messung).
3. **U2 DRV2605L (VSSOP-10):** Pin 1 nach der Dreiecksmarke, Schlepplöten oder wie U1.
4. 0402-Teile mit Paste. R8/R9 **nicht** bestücken (DNP).
5. J1 zuletzt, wenig Hitze; die Montagefüße (MP) gut anlöten.
6. Messen: 3V3 gegen GND auf Kurzschluss prüfen, 3V3 anlegen, per I²C auf 0x1C und 0x5A antworten lassen.
7. LRA mit doppelseitigem Klebeband in die markierte Freifläche kleben, Litzen an TP1/TP2 löten.
8. Abdeckung aufkleben (siehe oben).

## Bestellung

`fertigung/klickrad_v2_gerber_jlcpcb.zip` (für JLCPCB) und `fertigung/klickrad_v2_gerber_pcbway.zip` (für PCBWay, identischer Inhalt): Gerber X2 (Protel-Endungen) mit Bohrdaten PTH/NPTH, Paste-Lagen für eine Schablone und `.gbrjob`. Alle Daten, Gerber, Bohrungen und Bestückungsdatei, haben den Ursprung in der Platinenmitte.

| Einstellung | Wert |
|---|---|
| Lagen | 2 |
| Dicke | **0,8 mm** (Alternative 1,0 mm) |
| Maße | rund, Ø 32 mm (Umriss ist ein Kreis auf Edge.Cuts) |
| Kupfer | 1 oz |
| Oberfläche | ENIG empfohlen (ebene Pads für das 0,45-mm-VQFN), bleifreies HASL geht auch |
| Via | 0,6 / 0,3 mm, Tenting (Standard) |
| Lötstopplack | Farbe frei; die Touch-Flächen sind absichtlich **ohne Öffnung** |
| Platinen | 5 Stück Mindestmenge |

Kleinste Strukturen: Leiterbahn 0,15 mm, Abstand 0,15 mm (DRC-Mindestwert 0,127 mm), Elektrodenabstand 0,25 mm, GND-Gitter 0,127 mm, Bohrung 0,3 mm, Randabstand Kupfer 0,3 mm.

Bestückung durch den Hersteller ist nicht vorgesehen. Stückliste: `klickrad_bom.csv` (alle Spalten), `fertigung/klickrad_v2_bom_jlcpcb.csv` (JLCPCB-Format), `fertigung/klickrad_v2_cpl_jlcpcb.csv` (Bestückungsdatei, **Drehwinkel der Gehäuse nicht gegen den JLCPCB-Bibliothekswinkel geprüft**). LCSC-Nummern wurden am 2026-10-04 auf lcsc.com bestätigt; **AT42QT2120-MMH (C617900) war dort nicht auf Lager**, Alternativen: Mouser/DigiKey (ca. 5 USD).

## Was geprüft ist und was nicht

Geprüft (mit `kicad-cli` 9.0.9):

- **ERC** (`kicad-cli sch erc`): 0 Fehler, 0 Warnungen (nach der J1-Umstellung 2026-10-05 wiederholt).
- **DRC** (`kicad-cli pcb drc --schematic-parity --all-track-errors`) auf der fertigen `klickrad.kicad_pcb` (nach der J1-Umstellung und dem Neuverlegen 2026-10-05 wiederholt): 0 Fehler, 0 nicht verbundene Anschlüsse, Schaltplan-Abgleich ohne Abweichung (die Meldung `net_conflict` zu U1 Pad 21 ist die bekannte Warnung wegen des GND-Exposed-Pads). Es bleiben 5 Warnungen `courtyards_overlap` (C1/C2, R8/R9 und U1 mit R3/R4/R5): Die Kondensator- und Widerstandspaare sitzen absichtlich dicht (0402, Pads berühren sich nur im gleichen Netz bzw. mit >= 0,127 mm Abstand), die Courtyards der 0402-Teile sind größer als nötig. Löten und Bestücken von Hand bleibt möglich, kein elektrischer Fehler.
- Rechnerprüfung `tools/pruefe_vorderseite.py`: alle Vorderseiten-Leiterbahnen liegen innerhalb des Rings, keine außerhalb.
- **Neu verlegt 2026-10-05:** `tools/route_order.txt` jetzt mit GND an erster Stelle (sonst blieben drei GND-Inseln ohne Anbindung); ein Via-Paar (3V3/SDA bei x +3,4 … +3,95, y −3,15 … −3,65) wurde von Hand um 0,12 mm auseinandergezogen (Bohrabstand 0,44 statt 0,5 mm), ebenfalls in `tools/routed.kicad_pcb`. Die Leiterbahnen wurden nur über DRC und Bildansicht geprüft.
- Gerber-ZIPs für JLCPCB und PCBWay, Abdeckung (Gerber-ZIP), Schaltplan-PDF, Vorschaubilder und 3D-Renderings wurden erzeugt; das Gerber-Bild wurde nicht in einem fremden Viewer (z. B. Hersteller-Vorschau) gegengeprüft.
- Das Exposed Pad von U1 (Pad 21) liegt auf GND und ist mit den freien Pins 8/10 verbunden (**Abweichung von Tangara**, wo es unbeschaltet bleibt; Datenblatt-Empfehlung ungeprüft).
- Die letzte offene Verbindung des Routers (SCL an U1 Pin 14) wurde von Hand gezogen und GND-Stummel wurden von Hand entfernt, danach DRC wiederholt.

Nicht geprüft:

- **Keine Hardware gebaut oder gemessen.** Touch-Empfindlichkeit, Winkelauflösung, Wheel-Nullpunkt und Drehsinn, Störungen durch den LRA, Haptik-Kalibrierung, Verhalten mit gedruckter Abdeckung: offen.
- Das Rad liegt unter der typischen Größe des Datenblatts (24,6 mm statt 30 … 50 mm, Ringbreite 6 mm statt 12 mm).
- Footprints der Standardbibliothek (VSSOP-10, VQFN-20, 0402/0603) und der Molex-503480-Footprint J1 (Landmuster von J21, Nagelpads 0,8 × 1,0 geschätzt, Zeichnungsgrafik nicht lesbar) wurden nicht gegen die Herstellerzeichnungen vermessen. Das Exposed Pad von U1 liegt auf GND (anders als bei Tangara).
- Höhen von U1/U2/J1 aus dem Datenblatt bzw. aus dem Gedächtnis.
- Der Router (`tools/route.py`) ist eigener Code; die Leiterbahnen wurden nur über DRC und Bildansicht geprüft; SCL an U1 Pin 14 ist von Hand ergänzt. Einige Bahnen laufen länger als nötig. Die Guard-Verbindung läuft als lange Bahn über die Rückseite; sie liegt nicht unter den Elektroden einer anderen Funktion, ihre Länge wurde nicht bewertet.
- Das GND-Gitter erzeugt Kupferinseln; deren Warnungen siehe oben.
- Stromaufnahme: Der LRA wird aus der 3V3-Schiene des Waveshare-Boards versorgt, deren Belastbarkeit ungeprüft ist. Spannungseinbruch bei der Auto-Kalibrierung beobachten.
- **Pin 1 ↔ Pin 1 und Kabelführung (gerade, ungedreht, Mündungen gegenläufig) sind aus der Geometrie von Hauptplatine und Klickrad abgeleitet, nicht mit einem echten Kabel und Stecker geprüft.** Ob die Mündung des echten Molex-503480 wirklich auf der Seite der Signalpads liegt, folgt aus dem Footprint der Hauptplatine (Zeichnungsgrafik nicht lesbar) und ist **ungeprüft**; stimmt es nicht, wäre J1 um 180° zu drehen (Pin-1-Lage dann ebenfalls prüfen). CPL-Drehung von J1 (0°, Bottom) ist nicht gegen die JLCPCB-Konvention geprüft; J1 wird ohnehin von Hand bestückt.
- LCSC-Verfügbarkeit und Preise (Stand 2026-10-04, U1 nicht auf Lager).

## Neu erzeugen

Voraussetzungen: KiCad 9 (Python-Modul `pcbnew`, `kicad-cli`), Python-Pakete `shapely`, `numpy`, `scipy`, `Pillow`; `rsvg-convert` für PNG-Vorschauen.

```sh
python3 tools/make_lib.py                 # lib/Klickrad.pretty (Touch-Flächen, Loch), lib/Klickrad.kicad_sym (AT42QT2120)
SKIPROUTE=1 tools/make.sh                 # abgegebene Platine neu füllen und beschriften (ohne Router)
tools/make.sh                             # komplette Neuberechnung inkl. Router (dauert mehrere Minuten, Ergebnis kann abweichen; GND steht in route_order.txt vorn)
tools/export.sh                           # Schaltplan, ERC/DRC-Berichte, Gerber, Positionsdatei, Vorschau, Stückliste, Abdeckung
python3 tools/pruefe_vorderseite.py       # F.Cu-Prüfung
```

| Ordner/Datei | Inhalt |
|---|---|
| `klickrad.kicad_pro/.kicad_sch/.kicad_pcb` | KiCad-Projekt |
| `lib/Klickrad.pretty`, `lib/Klickrad.kicad_sym`, `fp-lib-table`, `sym-lib-table` | eigene Footprints/Symbol, Bibliothekstabellen; der Molex-Footprint `Molex_503480-0600_Hauptplatine` ist eine Kopie aus der Hauptplatine und wird von `make_lib.py` nicht erzeugt |
| `tools/` | Python-Skripte; `netlist.py` ist die einzige Quelle für Bauteile und Netze, `wheel_geometry.py` für die Elektroden, `placement.py` für die Platzierung, `route.py`/`route_loop.py` für die Verdrahtung |
| `tools/routed.kicad_pcb` | Platzierung + Routing-Ergebnis, Ausgangspunkt für `SKIPROUTE=1` |
| `abdeckung/` | KiCad-Projekt der FR4-Abdeckung, `fertigung/` (Gerber-ZIP), `vorschau/` |
| `fertigung/` | Gerber-ZIPs (JLCPCB, PCBWay), Bohrdaten, Bauteilpositionen, JLCPCB-BOM und -CPL |
| `vorschau/` | SVG/PNG von Vorderseite, Rückseite, Kupfer, 3D-Ansichten, Schaltplan als PNG und PDF |
| `pruefung/` | ERC- und DRC-Bericht |
| `klickrad_bom.csv` | Stückliste |
| `LICENSE` | CERN-OHL-S-2.0 |

Der Schaltplan wird per Skript erzeugt und ist übersichtlich, aber nicht von Hand gezeichnet; Änderungen am besten in `tools/netlist.py` und `tools/gen_sch.py` machen und neu erzeugen, nicht im Editor.
