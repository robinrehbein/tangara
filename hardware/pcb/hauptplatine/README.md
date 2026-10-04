# Hauptplatine Endgerät (Nano-Player)

4-Lagen-Leiterplatte 38 × 89 × 1,0 mm, Ecken r = 5, Bestückung beidseitig, bestellfertig für PCBWay (Leiterplatte plus PCBA).
KiCad 9, Schaltplan und Platine werden aus Python-Skripten erzeugt (`tools/`).

> **Status: nicht in Hardware getestet. Vor der Bestellung muss ein Mensch Schaltplan, Footprints, Bestückungsdrehungen und Gehäuseänderungen prüfen.**
> ERC und DRC laufen (Ergebnis unten), aber das heißt nur: keine formalen Regelverletzungen. Ob die Schaltung funktioniert, ob die Antenne funkt, ob der Klang gut ist und ob jeder Footprint zum echten Bauteil passt, ist **nicht geprüft**. Siehe Abschnitt „Geprüft / nicht geprüft“.

## Inhalt des Ordners

| Pfad | Inhalt |
|---|---|
| `hauptplatine.kicad_pro`, `.kicad_sch`, `.kicad_pcb` | KiCad-Projekt (Schaltplan A1, eine Seite) |
| `lib/` | eigene Symbole (`Hauptplatine.kicad_sym`) und Footprints (`Hauptplatine.pretty`: Tangara-Footprints, Espressif-Modul, FPC-Buchse, X2QFN) |
| `fertigung/hauptplatine_gerber_bohrdaten.zip` | Gerber (4 Lagen, Maske, Paste, Silkscreen, Kontur) und Bohrdaten (Excellon, PTH/NPTH getrennt) |
| `fertigung/hauptplatine_BOM_PCBWay.csv` | Stückliste im PCBWay-Format (Designator, Menge, Hersteller, MPN, Beschreibung, Gehäuseform, LCSC/Digi-Key nur wo geprüft; DNP markiert) |
| `fertigung/hauptplatine_CPL_PCBWay.csv` | Bestückungsdatei (Designator, Mid X/Y, Layer Top/Bottom, Rotation), Ursprung = Plattenmitte, ohne DNP-Teile |
| `fertigung/hauptplatine_schaltplan.pdf` | Schaltplan als PDF |
| `vorschau/` | SVG/PNG der Ober- und Unterseite |
| `pruefung/erc.rpt`, `pruefung/drc.rpt` | Berichte von `kicad-cli` |
| `quellen/` | Kopien der Quellen: Tangara-Netzliste (Rev. 5, JSON), Tangara-Footprints, Espressif-Footprint, Lizenztexte |
| `tools/` | Generatoren (siehe „Neuaufbau“) |
| `LICENSE` | CERN-OHL-S-2.0 |

## Blockschaltbild

```
                        +-------------------------------------------+
 USB-C (J6) ---CC1/CC2--| TUSB320LAI (U12)  DRP, I2C 0x47           |--INT/ID--+
   |  |  D+/D-          +-------------------------------------------+          |
   |  +-----R102/R103------------------------------------+                    |
   | VBUS                                                  v                    v
   +--> PE1605 (U5, ESD)--> Q1 (PMOS Eingangsschalter) --> MCP73871 (U10) <--> LiPo 1S (J7, NTC)
   |            ^ HOST_EN                                     |  Power-Path           |
   |            |                                             v                       v
   +<-- TPS2553 (U21, 0,5 A) <-- TPS61023 (U20, 5,1 V) <-- SYS_POWER ---> MAX17048 (U22, I2C 0x36)
                                                              |
                                      TLV75733 (U4, 3V3, 1 A) |  Power-Latch: SW1 -> LDO_EN, S31 haelt SYS_PWR_EN
                                                              v
   +------------------------ 3V3 -------------------------------------------------------------+
   |                                                                                           |
   |   ESP32-S31-WROOM-3-N16R16V (U15)                                                         |
   |   WLAN 6, BT 5.4 Classic + LE Audio, USB 2.0 HS OTG, 16 MB Flash, 16 MB PSRAM            |
   |     |                |                 |                 |                   |           |
   |   QSPI+Touch-I2C   I2S + MCLK      SDMMC 4 Bit        I2C                 BT-Antenne      |
   |     v                v                 v                 v                (Platinenkante)  |
   |  AMOLED (J20)    WM8523 (U17) -> INA1620 (U1) -> 3,5-mm-Klinke (J1)    microSD (J4)      |
   |  CO5300 FPC         ^ (V5A/VN5A aus TPS65133, U7)           Klickrad (J21, JST-SH 6)      |
   |                                                              AT42QT2120 + DRV2605L        |
   +-------------------------------------------------------------------------------------------+

 Audio-Weg A (Kabel, Hi-Res): S31 --I2S--> WM8523 (24 Bit / 192 kHz) --> INA1620 --> Klinke
 Audio-Weg B (digital):       S31 --USB-HS-OTG (Host, UAC2)--> USB-C --> externer USB-DAC / Kopfhoerer-Adapter
                              (TUSB320 stellt Rolle Quelle ein, TPS61023 + TPS2553 liefern 5 V auf VBUS)
 Weg C (drahtlos):            S31 --Bluetooth--> Kopfhoerer (A2DP/SBC; LC3 nur mit LE Audio auf beiden Seiten)
```

## Festgelegte Chips

Alle Chips der Liste aus `TEILE.md` („Hauptplatine Endgerät: festgelegte Chips“) sind verbaut, mit einer Abweichung (3V3-Regler, siehe unten).

| Funktion | Chip | Bezeichner | Herkunft |
|---|---|---|---|
| MCU | ESP32-S31-WROOM-3-N16R16V (16 MB PSRAM) | U15 | neu (festgelegt) |
| DAC | WM8523 | U17 | Tangara 1:1 |
| Kopfhörerverstärker | INA1620 | U1 | Tangara 1:1 |
| ±5-V-Wandler | TPS65133 | U7 | Tangara 1:1 |
| Klinke | SJ-3506-SMT | J1 | Tangara 1:1 |
| ESD Klinke | D5V0L2B3T-7 | U3 | Tangara 1:1 |
| Lader mit Power-Path | MCP73871-2CCI/ML | U10 | Tangara 1:1 |
| 3V3-Regler | TLV75733PDBV (1 A) | U4 | angepasst (Tangara: TLV75533, 500 mA) |
| USB-C-Buchse | USB4510-03-1-A | J6 | Tangara 1:1 |
| USB-C-Rollenumschaltung | TUSB320LAI | U12 | neu (festgelegt), **eigene Entwicklung, ungeprüft** |
| 5-V-Boost für Host | TPS61023 | U20 | neu (festgelegt), **eigene Entwicklung, ungeprüft** |
| Lastschalter 0,5 A | TPS2553 | U21 | neu (festgelegt), **eigene Entwicklung, ungeprüft** |
| Akkustand | MAX17048G+T10 | U22 | neu (festgelegt) |
| Touch-Rad / Haptik | AT42QT2120 / DRV2605L auf dem Klickrad-Modul | – | Tangara (Modul v2) |

Nicht verbaut (laut Vorgabe): 74CBTLV3257-Multiplexer und SAMD21 (der S31 hat eigenes USB und eigene SD-Schnittstelle).

## Übernommen von Tangara / angepasst / neu entwickelt

Quelle: Tangara-Hardware Rev. 5 (cool tech zone, CERN-OHL-S-2.0), Netzliste in `quellen/tangara_netlist_rev5.json`. Die Spalte „Anzahl“ zählt Bauteile der Stückliste (ohne Testpunkte und Bohrungen).

| Block | Anzahl | Bauteile | Änderung |
|---|---|---|---|
| **Übernommen 1:1** (Werte, Netze, Footprints aus Tangara) | @@N_TG@@ | Audio komplett (U17, U1, U7, U3, J1, L1, L2, Q3, R2/R3/R5/R6/R8/R15/R22, C2…C19), Ladeschaltung (U10, Q1, D4, U5, R1, R7, R34/R35/R37/R38/R39/R41, C24/C25/C27/C29/C37), USB-C J6, SD-Versorgung U16 mit Pull-ups und Kondensatoren, 3V3-Kondensatoren | nur Netznamen vereinheitlicht |
| **Angepasst** | @@N_ANG@@ | U4 (TLV75733P statt TLV75533: 1 A, S31 zieht bis ca. 375 mA beim Senden, dazu Display und Haptik); J7 (JST-SH 3-polig SMD statt JST-PH THT); J4 (microSD Molex statt Vollformat-SD Hirose, 4-Bit-SDMMC direkt am S31 statt SPI über Multiplexer); SW1 (Taster B3U-3000P statt Schiebeschalter, Power-Latch); R4 (10 k statt 100 k wegen Taster); R36/R43 (feste Pull-ups statt SAMD21-Steuerung); R210 (MCLK-Brücke) | Begründung je Teil im Feld „Beschreibung“ der Stückliste |
| **Neu: Espressif-Beschaltung** | @@N_ESP@@ | EN-RC (R100, C100), 22 µF/100 nF am Modul (C101, C102), Taster EN/BOOT (SW10, SW11), Pull-up BOOT (R101, C103), Serienplätze USB (R102, R103), Testpunkte TP10…TP15 | nach Datenblatt v0.7 (vorläufig) |
| **Neu: USB-Host-Zweig** | @@N_USB@@ | U12 TUSB320LAI, U20 TPS61023, U21 TPS2553, L20, Q10, Q11, D10, R110…R119, C110…C114 | **eigene Entwicklung, ungeprüft** |
| **Neu: Sonstiges** | @@N_NEU@@ | MAX17048 (U22), Display-FPC (J20) mit Beschaltung, Klickrad-Stecker J21 mit Pull-ups R136/R137 und I²C-Pull-ups R120/R121, Power-Latch-Widerstände R200…R202, MCLK-Oszillator-Option (X1, R211, C211; DNP) | – |

Power-Latch (Schaltung neu, Bauteile teilweise von Tangara): Der Taster SW1 zieht `KEY_LOCK` über R4 auf `SYS_POWER`; das schaltet `LDO_EN` (Tangara-Schaltung mit D4). Sobald der S31 läuft, setzt er `SYS_PWR_EN` (GPIO, LP-fähig) und hält so den Regler an; er kann sich selbst abschalten, indem er `SYS_PWR_EN` löscht. R202 (100 k) zieht `SYS_PWR_EN` nach Masse, wenn der S31 aus ist. `KEY_LOCK_MCU` liest den Taster (über R201).

## GPIO-Belegung ESP32-S31

Automatisch vergeben (`tools/gpio_assign.py`, Zuordnung nach kürzester Leitung zu den Zielpads; Randbedingungen: Weck-/Haltesignale auf LP-GPIO IO0…IO7, nicht verwendet: Strapping IO36/IO37/IO60/IO61, USB-Serial/JTAG IO33/IO34, IO35). Fest verdrahtet: SD_D0…D3/CLK/CMD an den dedizierten SDMMC-Pins (27…32), USB-HS D+/D− an den Pins 40/41 (über R102/R103 zu J6), EN, IO61 = BOOT, TX0/RX0 und IO33/IO34 auf Testpunkten.

@@GPIO_TABLE@@

Alle Zuordnungen sind **ungeprüft** gegen das endgültige Datenblatt (v0.7, vorläufig): Welche Peripherie auf welche GPIOs gelegt werden darf, folgt der GPIO-Matrix; die IO-MUX-Sonderfunktionen (SDMMC, USB, LP) sind oben berücksichtigt, Octal-Flash/-PSRAM liegen im Modul. Vor der Bestellung gegen Datenblatt-Tabelle 3-1 und die IDF-6-Dokumentation prüfen.

## Bauteil-Begründungen (Auszug)

- **S31-Modul mit 16 MB PSRAM** (N16R16V): Firmware-Portierung (`docs/FIRMWARE-PORTIERUNG.md`) braucht den Speicher für LVGL-Framebuffer (368 × 448) und Audiopuffer. Verfügbarkeit des Moduls bei Mouser/Digi-Key konnte nicht bestätigt werden; es gibt keine LCSC-/Digi-Key-Nummer in der Stückliste.
- **TLV75733P statt TLV75533**: Reserve für WLAN-Sendespitzen. Gleiche Anschlussbelegung (SOT-23-5), LCSC C485517.
- **MCLK**: Der WM8523 braucht einen Master-Takt (128…1152 × fs). Der S31 liefert ihn aus der GPIO-Matrix/I²S, ohne Audio-PLL (ESP-IDF 6, kein APLL). Der Takt wird aus dem Digitaltakt geteilt und hat dadurch mehr Jitter. Deshalb Option: Oszillator X1 (3,2 × 2,5 mm, z. B. 22,5792 MHz für die 44,1-kHz-Familie) mit R211 statt R210 bestücken. Standard: R210 (S31-MCLK), X1/R211/C211 nicht bestückt (DNP). Bei 48-kHz-Familie zweiter Oszillator nötig; ungeklärt, ob der WM8523 den Takt asynchron verträgt.
- **Bluetooth-Audio**: Der ESP32-Stack liefert für A2DP in der Regel nur SBC. LC3 (LE Audio) funktioniert nur, wenn Kopfhörer und Firmware LE Audio unterstützen. Für hochauflösenden Klang bleibt der Kabelweg A oder B.
- **USB-Port wird geteilt**: Es gibt nur einen OTG-Port. Entweder ist der Player USB-Speichergerät (MSC) am PC, oder USB-Audio-Host (UAC2) am externen DAC. Beides gleichzeitig geht nicht; die Firmware muss die Rolle (TUSB320-INT/ID) umschalten. Flashen läuft über das USB-Serial/JTAG (Testpunkte TP12/TP13, IO33/IO34) oder über den HS-Port im Download-Modus (BOOT-Taste SW11 beim Einstecken); beides ungeprüft.

## Mechanik und Änderungen an Gehäuse/CAD

Koordinaten: Ursprung = Plattenmitte, x nach rechts, y nach oben, Blick auf die Display-Seite. Das Klickrad-Modul wird unverändert übernommen (`hardware/pcb/klickrad/` wurde nicht verändert).

**Übernommen** (wie gefordert): 38 × 89 × 1,0 mm, Ecken r = 5; Aussparung Ø 26 mm mittig bei (0, −27); drei NPTH Ø 2,2 mm auf r = 14,6 mm um (0, −27) bei 90°, 210°, 330° = (0, −12,4), (−12,64, −34,3), (12,64, −34,3); Klickrad-Anschluss J21 JST-SH 6-polig mit der Belegung 1 3V3, 2 GND, 3 SDA, 4 SCL, 5 INT/CHANGE, 6 BTN; I²C-Pull-ups 2,2 k auf der Hauptplatine.

**Abweichungen und nötige Änderungen** (alle in der Gehäuse-CAD nachzuziehen):

@@MECH@@

## Geprüft / nicht geprüft

**Geprüft (automatisch, `pruefung/`):**
@@CHECKED@@

**Nicht geprüft:**
- Funktion der Schaltung (nie aufgebaut, keine Simulation). Besonders die eigene USB-C-Rollen-/Host-Schaltung (U12, U20, U21, Q10, Q11, D10), der Power-Latch und der MCLK-Pfad.
- Antenne: Das Modul hängt mit der Antenne über die Plattenkante (kein Kupfer unter dem Antennenbereich, Keepout aus dem Espressif-Footprint). HF-Verhalten im Gehäuse, Abstand zu Akku und Display, Verstimmung: ungemessen.
- Audioqualität: Layout der Analogteile (WM8523, INA1620, ±5 V) folgt nur der Platzierungsoptimierung, nicht den Tangara-Lagenplänen; Rauschen, Übersprechen, Schaltreglerstörungen ungemessen.
- USB-HS-Leitung: 90 Ω differenziell wurde nicht berechnet; Lagenaufbau (Dicke Prepreg) bei PCBWay erfragen. Leitung ist kurz, aber ungeprüft.
- Footprint-Genauigkeit: Tangara-Footprints (USB4510, SJ-3506, WM8523-SON, TPS65133, SOT-Teile) aus Tangara übernommen; Espressif-Modul aus dem Espressif-Repository (Format von KiCad 10 auf 9 gewandelt); **FPC-Buchse AXE534124 und TUSB320-X2QFN: Landmuster aus Datenblattangaben abgeleitet, nicht nach Herstellerzeichnung geprüft**; KiCad-Standardfootprints für Passive, JST-SH, microSD (Molex 104031-0811 nahe, nicht identisch geprüft), Taster B3U, Oszillator.
- Bestückungsdrehungen: Die CPL-Datei nutzt die KiCad-Drehung. PCBWay verlangt bei manchen Bauteilen (ICs, Stecker, Dioden) eine andere Nullstellung; die Vorschau der Bestückung bei PCBWay prüfen und gegebenenfalls Drehungen korrigieren lassen.
- Höhenstapel im Gehäuse (siehe oben), Lieferbarkeit aller Bauteile (außer wo in der Stückliste eine Nummer steht), Preise.

**Menschliche Prüfung vor der Bestellung ist Pflicht.** Mindestens: Schaltplan gegen Datenblätter lesen, alle Footprints gegen Zeichnungen, CPL-Vorschau bei PCBWay, Gehäusestapel.

## PCBWay-Bestellung Schritt für Schritt

1. Auf pcbway.com „PCB Assembly“ → „Quote Now“ wählen (Leiterplatte plus Bestückung).
2. Gerber hochladen: `fertigung/hauptplatine_gerber_bohrdaten.zip`.
3. Leiterplatte: Lagen **4**, Dicke **1,0 mm**, Maße 38 × 89 mm, Material FR-4 (Tg 150 genügt), Lötstopplack nach Wunsch (z. B. schwarz/grün), Silkscreen weiß, Oberfläche **ENIG** (wegen der feinen Pads und der Pads ohne Hand-Nachlöten), Kupfer außen 1 oz, innen 0,5 oz, kleinste Leiterbahn/Abstand 0,15/0,15 mm (Standard), Via-Bohrung 0,3 mm, Kantenmetallisierung nein, Impedanzkontrolle: für USB-HS anfragen (Wunsch 90 Ω differenziell, Lagenaufbau von PCBWay bestätigen lassen).
4. Bestückung: **beidseitig** (Top und Bottom), Anzahl der Teile laut Stückliste (@@N_PARTS@@ Bauteile, @@N_LINES@@ Positionen), Montage „Standard“, Passermarken sind auf beiden Seiten vorhanden. Bleifreies Löten.
5. Stückliste `fertigung/hauptplatine_BOM_PCBWay.csv` und Bestückungsdatei `fertigung/hauptplatine_CPL_PCBWay.csv` hochladen. Teile ohne Lieferantennummer (S31-Modul, mehrere Tangara-Teile) von PCBWay beschaffen lassen oder selbst liefern (Kit/Consigned). Nicht bestückt werden: X1, R211, C211 (DNP, in der Stückliste markiert). Das S31-Modul und die THT-Teile (Klinke J1, USB-C J6) braucht PCBWay als Sonderprozess (THT-Laschen), im Angebot ausdrücklich bestätigen lassen.
6. Vorschau der Bestückung bei PCBWay prüfen: Polarität/Drehung von U1, U3, U4, U5, U7, U10, U12, U15, U17, U20, U21, U22, D4, D10, Q1, Q3, Q10, Q11 und aller Stecker. Fehler per Rückfrage melden, nicht stillschweigend bestätigen.
7. Gerber-Vorschau (Kontur mit Aussparung und Ausbuchtung, NPTH-Bohrungen) prüfen, dann bestellen. Für den ersten Aufbau 5 Platinen, davon 2 bestückt reichen.

## Kosten (grobe Schätzung, nicht geprüft)

@@COST@@

## Offene Risiken

@@RISKS@@

## Neuaufbau

Voraussetzungen: KiCad 9 (Python `pcbnew`, `kicad-cli`), Python-Pakete `shapely`, `numpy`, `scipy`; Java und `freerouting-2.1.0.jar` für das Routing; `rsvg-convert` für PNG.

```
tools/make.sh                 # nutzt gespeicherte Platzierung und GPIO-Zuordnung
PLACE=1 tools/make.sh         # Platzierung (Simulated Annealing, ca. 10 min) und GPIO-Zuordnung neu
SKIPROUTE=1 tools/make.sh     # vorhandenes Routing (tools/routed_freerouting.kicad_pcb) verwenden
```

Reihenfolge: `netlist.py` (alle Bauteile und Netze, einzige Quelle) → `place_sa.py` (Platzierung, `placement.json`) → `gpio_assign.py` (`gpio_map.json`) → `build_pcb.py` (Platine) → Freerouting → `finish.py` (Zonen, Passermarken, Beschriftung) → `gen_sch.py` (Schaltplan) → `export.py` (Gerber, Stückliste, Bestückung, Berichte).

## Herkunft und Lizenz

- Dieses Design ist ein abgeleitetes Werk der **Tangara-Hardware** (cool tech zone, jacqueline, <https://cooltech.zone/tangara/>, Quelle <https://codeberg.org/cool-tech-zone/tangara-hw>), lizenziert unter **CERN-OHL-S-2.0**; es steht daher ebenfalls unter CERN-OHL-S-2.0 (Datei `LICENSE`). Die Namensnennung steht im Titelblatt des Schaltplans.
- Der Footprint des ESP32-S31-WROOM-3 stammt aus den Espressif-KiCad-Bibliotheken (CC-BY-SA 4.0 mit Ausnahme für Designs, Text in `quellen/LICENSE_espressif-kicad-libraries.md`).
- Standardfootprints und -symbole: KiCad-Bibliotheken (CC-BY-SA 4.0 mit Ausnahme für Designs).
- Die Platzierungs- und Erzeugungsskripte in `tools/` sind neu geschrieben.
