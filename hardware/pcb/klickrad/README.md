# Klickrad-Modul (KiCad 9)

Runde Platine (Ø 32 mm, 1,0 mm, **4 Lagen**) mit Touch-Ring, Mitteltaste, Haptik-Treiber und Lötpads für den aufgeklebten LRA. Schnittstelle und Maße folgen `TEILE.md`, Abschnitt „Klickrad-Modul“.

Stand: 2026-10-04, Revision 1. Erstellt und geprüft mit KiCad 9.0.9 (`kicad-cli`) im Container. **Nichts davon wurde an echter Hardware getestet.**

## Funktion

| Block | Bauteil | Beschaltung |
|---|---|---|
| Touch-Controller | U1 MPR121QR2 (QFN-20, I²C **0x5B**) | ADDR an VDD, REXT 75 kΩ (R1), VREG 0,1 µF (C2), VDD 0,1 µF (C1) + 1 µF (C3), IRQ → J1 Pin 5 |
| Touch-Ring | 12 Kupfersegmente vorn, r = 6,5 … 12,8 mm | je 30°, 0,4 mm Spalt, Lötstopplack bleibt **geschlossen**, Anschluss von innen über F.Cu-Leitungen |
| Haptik-Treiber | U2 DRV2605LDGS (MSOP-10, I²C **0x5A**) | EN und VDD/NC an 3V3, IN/TRIG an GND, VDD 1 µF (C4) + 10 µF (C6), REG 1 µF (C5), OUT+/OUT− → Lötpads TP1/TP2 |
| Mitteltaste | SW1 Omron B3U-1000P (3,0 × 2,5 × 1,2 mm) | nach GND und J1 Pin 6, Pull-up auf der MCU-Seite |
| Stecker | J1 JST-SH 1,0 mm, 6-polig (SM06B-SRSS-TB, seitlich) | siehe unten |
| Pull-ups | R2/R3 4,7 kΩ an SDA/SCL | **DNP** (das Waveshare-Board hat 2,2 kΩ auf dem Bus) |

### Pinbelegung J1

| Pin | Signal | Hinweis |
|---|---|---|
| 1 | 3V3 | versorgt MPR121 und DRV2605L |
| 2 | GND | |
| 3 | SDA | |
| 4 | SCL | |
| 5 | INT | MPR121 IRQ, open drain, aktiv low (kein Pull-up auf dem Modul) |
| 6 | BTN | Mitteltaste, aktiv low (kein Pull-up auf dem Modul) |

### Segmente und MPR121-Elektroden

Winkel in der Draufsicht von vorn, 0° = rechts, gegen den Uhrzeigersinn (wie in `TEILE.md`). Segmentmitte = angegebener Winkel.

| Segment | Winkel | MPR121 | | Segment | Winkel | MPR121 |
|---|---|---|---|---|---|---|
| SEG1 | 15° | ELE8 | | SEG7 | 195° | ELE2 |
| SEG2 | 45° | ELE7 | | SEG8 | 225° | ELE1 |
| SEG3 | 75° | ELE6 | | SEG9 | 255° | ELE0 |
| SEG4 | 105° | ELE5 | | SEG10 | 285° | ELE11 |
| SEG5 | 135° | ELE4 | | SEG11 | 315° | ELE10 |
| SEG6 | 165° | ELE3 | | SEG12 | 345° | ELE9 |

Die Elektrodennummer **steigt im Uhrzeigersinn** (Winkel sinkt um 30° je Schritt). Alle zwölf Eingänge ELE0 … ELE11 sind Touch-Elektroden, ELE11 ist deshalb nicht als GPIO nutzbar (Elektrodenzahl im ECR-Register auf 12 setzen). Die Zuordnung steht in `tools/seg_map.json`; wer sie ändern will, muss das Layout neu erzeugen.

### Firmware-Hinweise (DRV2605L)

- LRA-Modus: Bit `N_ERM_LRA` in Register 0x1A (Feedback Control) auf 1, LRA-Effektbibliothek wählen (Library 6), Auto-Kalibrierung (Modus 7) einmal je LRA-Typ durchführen und die Ergebnisse speichern.
- Der gewählte Haptik-Effekt „Click“ entspricht den Effekten 1 („Strong Click 100 %“) bzw. 4 („Sharp Click 100 %“) der internen Bibliothek.
- EN ist fest auf 3V3. Standby also nur per I²C (Register 0x01, Bit STANDBY).

## Mechanik

- Umriss Ø 32,0 mm, Dicke 1,0 mm. Drei Löcher Ø 2,2 mm (NPTH) auf r = 14,6 mm bei 90°, 210°, 330°.
- Touch-Ring r = 6,5 … 12,8 mm. Die gedruckte Abdeckung (Ø 30 / Ø 11,6) deckt ihn ab. Im Innenkreis r < 5,8 mm sitzt vorn nur der Taster (Höhe 1,2 mm); darunter liegen auf der Vorderseite dünne Leiterbahnen unter Lötstopplack.
- **Stecker J1** sitzt am Rand bei 270° (6-Uhr-Richtung, gegenüber dem Loch bei 90°). Der Steckerkörper belegt auf der Rückseite x = −4,9 … +4,9 mm, y = −14,7 … −8,1 mm. Das Kabel verlässt die Platine nach unten. Der Stecker ist **höher als 1,5 mm** (seitlich steckender SH-Header, Höhe laut Datenblatt prüfen) und damit das einzige Rückseitenbauteil über der Vorgabe. Bei Bedarf stattdessen die Top-Entry-Variante BM06B-SRSS-TB prüfen, sie hat andere Maße.
- **LRA-Freifläche** (Rückseite, nur Bauteile gesperrt, auf der Platine als Rechteck mit Kreuz in der Silkscreen markiert): x = −8 … +8 mm, y = +3 … +9 mm (16 × 6 mm, oberer Platinenbereich). Darunter liegen nur die Masse-Gitterlage und wenige Leiterbahnen unter Lack.
- Lötpads für die LRA-Litzen: TP1 (LRA+, bei x = −12,3 / y = −3,0 mm) und TP2 (LRA−, y = −0,4 mm), links außen auf der Rückseite, 1 × 2 mm.
- Alle übrigen Rückseitenbauteile: 0402-Widerstände/-Kondensatoren (0,5 mm), C6 in 0603 (0,8 mm), U1 ca. 0,8 mm, U2 ca. 1,1 mm (Höhen aus dem Gedächtnis, vor Bestellung im Datenblatt prüfen).
- Bauteilpositionen für CAD: `fertigung/bauteilpositionen.csv` (Bezug Platinenmitte, mm, y nach oben in der Ansicht von vorn).

## Lagenaufbau und Masse unter dem Touch-Ring (Entscheidung)

Die Platine ist **4-lagig**, nicht 2-lagig. Gründe: Die Pinreihenfolge des MPR121 (IRQ, SCL, SDA) ist gegenüber dem Stecker (SDA, SCL, INT) umgekehrt, die zwölf Elektrodenleitungen müssen aus dem Innenkreis zu den Segmenten, und der DRV2605L braucht saubere 3V3-/GND-Zuführung. Eine 2-lagige Variante ließ sich mit Autorouter und Handverdrahtung nicht sauber schließen (Masse-Inseln, Pull-ups). Mit Innenlagen entfällt das.

| Lage | Inhalt |
|---|---|
| F.Cu | 12 Touch-Segmente, Taster, Elektrodenleitungen im Innenkreis (r < 6 mm), kurze F.Cu-Brücken |
| In1.Cu | **GND, gerastert (hatched)** über die ganze Platine: 0,3 mm Stege, 0,7 mm Lücken, 45° (ca. 35 % Deckung) |
| In2.Cu | 3V3, massiv |
| B.Cu | Bauteile, Signalleitungen, **keine** Massefläche |

Die Masse liegt damit wie gefordert unter den Segmenten und ist dort als Gitter ausgeführt, damit die Grundkapazität der Segmente klein bleibt. Die massive 3V3-Lage liegt dahinter, vom Gitter abgeschirmt.

**Ungeprüft:** Der Abstand F.Cu zu In1.Cu hängt vom Lagenaufbau des Herstellers ab (bei JLCPCB 4 Lagen / 1,0 mm vor der Bestellung im Lagenaufbau-Dialog nachsehen). Je dünner, desto mehr Grundkapazität und desto weniger Empfindlichkeit. Falls der Ring im Test zu unempfindlich ist, In1 unter dem Ring ausschneiden (Kreisring r = 6,0 … 13,3 mm aussparen) und im MPR121 die Ladeströme höher einstellen. Die Auswirkung auf die Empfindlichkeit wurde nicht gemessen.

## Bestückung (Handlötung)

Reihenfolge: erst Rückseite, zuletzt Taster.

1. Platine mit der Vorderseite auf die Heizplatte (oder Platte vorheizen, ca. 100–120 °C), Rückseite liegt oben. Mit Heizplatte und Heißluft ist U1 deutlich leichter als mit dem Kolben.
2. **U1 MPR121 (QFN-20, Raster 0,4 mm, kein Exposed Pad)**: Lötpaste dünn auf die 20 Pads (Schablone aus dem Paste-Layer oder aus Spritze), U1 mit Pin 1 nach der Silkscreen-Marke (Dreieck an der Ecke) ausrichten, Heißluft ca. 240–250 °C bis die Paste fließt. Danach Brücken mit Flussmittel und Entlötlitze entfernen. Das Footprint ist aus dem KiCad-Footprint für QFN-20 3 × 3 mm / 0,4 mm abgeleitet, **ohne** Exposed Pad; Maße vor der Bestellung mit der NXP-Gehäusezeichnung (MPR121 Datenblatt, QFN-20) vergleichen.
3. **U2 DRV2605L (MSOP-10)**: Pin 1 nach der Dreiecksmarke. Mit Kolben und Flussmittel (Drag-Soldering) oder wie U1.
4. 0402-Teile (C1–C5, R1) und C6 (0603) mit Paste und Pinzette, danach R2/R3 **nicht** bestücken (DNP).
5. J1 zuletzt, mit wenig Hitze (Kunststoff). Die Metall-Montagefüße (MP) gut anlöten, sie nehmen die Steckkräfte auf.
6. Vorderseite: Taster SW1 mit dem Kolben (2 große Pads, Taster vorher mit Pinzette halten).
7. Messen: GND gegen 3V3 auf Kurzschluss prüfen, danach 3V3 anlegen und per I²C auf 0x5A und 0x5B antworten lassen.
8. Zuletzt den LRA mit doppelseitigem Klebeband in die markierte Freifläche kleben und die Litzen an TP1/TP2 löten.

## Bestellung bei JLCPCB

Datei: `fertigung/klickrad_gerber_jlcpcb.zip` (Gerber X2 mit Bohrdaten PTH/NPTH, enthält auch Paste-Lagen für eine Schablone und die `.gbrjob`).

| Einstellung | Wert |
|---|---|
| Lagen | 4 |
| Dicke | **1,0 mm** |
| Maße | rund, Ø 32 mm (Umriss ist ein Kreis auf Edge.Cuts) |
| Kupfer | außen 1 oz, innen Standard |
| Oberfläche | ENIG empfohlen (ebene Pads für das 0,4-mm-QFN), bleifreies HASL geht auch |
| Via-Abdeckung | Tenting (Standard), kleinste Bohrung 0,3 mm |
| Impedanz | keine Kontrolle nötig |
| Lötstopplack | Farbe frei; Segmente sind absichtlich **ohne Öffnung** |
| Platinen | 5 Stück Mindestmenge |

Kleinste Strukturen: Leiterbahn 0,15 mm, Abstand 0,15 mm, Via 0,6/0,3 mm, Randabstand Kupfer 0,3 mm (DRC-Einstellung in `klickrad.kicad_pro`). Silkscreen-Schrift 0,9 – 1,0 mm hoch, 0,15 mm Strich; die Pinbeschriftung am Stecker (0,9 mm) ist die kleinste.

Bestückung durch JLCPCB ist nicht vorgesehen. Stückliste mit Hersteller- und LCSC-Nummern: `klickrad_bom.csv` (LCSC-Nummern nur dort, wo sie am 2026-10-04 über lcsc.com bestätigt wurden; bei R1 leer).

## Was geprüft ist und was nicht

Geprüft (mit `kicad-cli` 9.0.9):

- ERC des Schaltplans: 0 Fehler, 0 Warnungen (`pruefung/erc.rpt`).
- DRC der Platine mit Abgleich gegen den Schaltplan (Parität): 0 Fehler, 0 nicht verbundene Netze, 0 Paritätsabweichungen. Zwei Warnungen „Courtyards overlap“ (C4/C5 liegen im Hüllbereich von U2, bewusst nah am IC wegen der Entkopplung) (`pruefung/drc.rpt`).
- Netzliste aus dem Schaltplan stimmt mit den Pads der Platine überein (Parität), Pinbelegung J1 laut `TEILE.md`, MPR121-Pins und DRV2605L-Pins laut KiCad-Symbolen, die aus den Herstellerdatenblättern stammen. Beschaltung des MPR121 (REXT 75 kΩ 1 % nach VSS, 0,1 µF an VREG und VDD, ADDR an VDD = 0x5B, Pinbelegung QFN-20) gegen das MPR121-Datenblatt (Rev. 5, Resurgent-Kopie des NXP-Datenblatts) und die Beschaltung des DRV2605L (1 µF an VDD und REG, IN/TRIG an GND, VDD/NC an VDD) gegen das TI-Datenblatt (SLOS854D) geprüft.
- Gerber und Bohrdaten werden ohne Fehler erzeugt. In der Vorderseiten-Lötstopplage gibt es nur Öffnungen für die zwei Tasterpads und die drei Montagelöcher, die Segmente sind abgedeckt.

Nicht geprüft:

- **Keine Hardware gebaut oder gemessen.** Touch-Empfindlichkeit, Winkelauflösung, Störungen durch den LRA, Haptik-Kalibrierung: offen.
- Footprints der Standardbibliothek (B3U-1000P, SM06B-SRSS-TB, MSOP-10, 0402/0603) und das eigene QFN-Footprint wurden nicht gegen die Herstellerzeichnungen vermessen.
- Lagenaufbau und Abstand F.Cu–In1.Cu beim Hersteller; Höhen von U1/U2/J1.
- Stromaufnahme: Der LRA wird aus der 3V3-Schiene des Waveshare-Boards versorgt, deren Belastbarkeit ungeprüft ist. Deshalb VDD des DRV2605L mit 1 µF + 10 µF abgeblockt. Beim Einschalten der Auto-Kalibrierung kann kurz ein deutlicher Strom fließen; Spannungseinbruch am 3V3 des Hauptboards beobachten.
- Die Position und Ausrichtung des Steckers (6-Uhr-Seite) ist eine Annahme und muss zum Gehäuse und zur Kabelführung passen. Die Montagelöcher sind gleichmäßig verteilt, die Platine lässt sich deshalb in 120°-Schritten anders ins Gehäuse setzen, der Stecker bleibt aber an seiner Stelle auf der Platine.
- LCSC-Verfügbarkeit und Preise.

## Neu erzeugen

Voraussetzungen: KiCad 9 (Python-Modul `pcbnew`, `kicad-cli`), Python-Pakete `shapely`, `Pillow`; für Layout-Neuberechnung zusätzlich Java und `freerouting-2.1.0.jar` (https://github.com/freerouting/freerouting/releases) sowie `/tmp/freerouting/freerouting.json` mit Zeitlimit 3 min; `rsvg-convert` für PNG-Vorschauen.

```sh
python3 tools/make_lib.py                 # lib/Klickrad.pretty (Segmente, QFN ohne EP, Montageloch)
SKIPROUTE=1 tools/make.sh                 # abgegebene Platine neu füllen und beschriften (ohne Router)
FREEROUTING=/pfad/freerouting.jar tools/make.sh   # komplette Neuberechnung inkl. Autorouter (Ergebnis kann abweichen)
tools/export.sh                           # Schaltplan, ERC/DRC-Berichte, Gerber, Positionsdatei, Vorschau, Stückliste
```

| Ordner/Datei | Inhalt |
|---|---|
| `klickrad.kicad_pro/.kicad_sch/.kicad_pcb` | KiCad-Projekt |
| `lib/Klickrad.pretty`, `fp-lib-table`, `sym-lib-table` | eigene Footprints, Bibliothekstabellen |
| `tools/` | Python-Skripte, die Schaltplan und Platine erzeugen (`netlist.py` ist die einzige Quelle für Bauteile und Netze) |
| `tools/routed_freerouting.kicad_pcb` | Platzierung + Routing-Ergebnis, Ausgangspunkt für `SKIPROUTE=1` |
| `fertigung/` | Gerber-ZIP, Bohrdaten, Bauteilpositionen |
| `vorschau/` | SVG/PNG von Vorderseite, Rückseite, Kupfer, 3D-Ansichten, Schaltplan |
| `pruefung/` | ERC- und DRC-Bericht |
| `klickrad_bom.csv` | Stückliste |

Der Schaltplan wird per Skript erzeugt und ist übersichtlich, aber nicht von Hand gezeichnet; Änderungen am besten in `tools/netlist.py` und `tools/gen_sch.py` machen und neu erzeugen, nicht im Editor, sonst weicht das Layout beim nächsten Lauf ab.
