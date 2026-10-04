# Hauptplatine Endgerät (Nano-Player), Rev. 3

> **STATUS: geroutet, DRC sauber (0 Fehler, 0 unverbundene Verbindungen) – trotzdem NICHT ungeprüft bestellbar: menschlicher bzw. Opus-Review vor der Bestellung zwingend.**
> - Platine **41 × 97 × 1,0 mm, 4 Lagen** (F.Cu / In1 GND-Fläche / In2 Signale + GND-Fläche / B.Cu), Ecken r = 4, Gerät ca. 44 × 100 × bis 10 mm. Antenne des WROOM-1 liegt **innerhalb** der Kante (Keepout 18,6 × 7,6 mm, alle vier Kupferlagen, zusätzlich als Platinen-Regelbereich `antenna_keepout_board`; per Skript geprüft: Kupferfüllung In1/In2 im Keepout 0 mm², Bahnen/Vias darin 0). 6 Lagen waren nicht nötig.
> - **DRC (kicad-cli, mit Abgleich gegen den Schaltplan): 0 Verstöße, 0 unverbundene Pads, 0 Footprint-Hinweise.** ERC: 0 Meldungen. Regeln: Bahn/Abstand 0,127 mm, Via 0,45/0,2 mm, **Kupfer–Kante 0,3 mm** (PCBWay-Standard; nur die Pads von Klinke/USB-C/microSD dürfen per eigener Regel in `hauptplatine.kicad_dru` bis 0,2 mm = PCBWay-Minimum an den Randausschnitt), Loch–Loch 0,3 mm. Abgeschaltet und begründet: `silk_over_copper`, `silk_overlap`, `silk_edge_clearance` (PCBWay schneidet Siebdruck über Pads/Kante automatisch ab), `nonmirrored_text_on_back_layer` (betraf nur ausgeblendete Fab-Texte). Alle Referenzbezeichner sind absichtlich **nicht** im Siebdruck (PCBWay arbeitet nach CPL); der Siebdruck zeigt nur Bauteilumrisse, Pin 1 und „Antenne“.
> - **Wie das Routing entstand (ehrlich):** Freerouting 1.9.0 (Java, `xvfb`) legte in zwei Läufen (12 Durchgänge, dann 20 Durchgänge als Fortsetzung auf dem Zwischenstand, je ca. 5–10 min) alle Verbindungen bis auf wenige (vorher waren sechs Läufe mit schlechteren Platzierungen nötig); GND-Anbindung an die Fläche In1 macht ein Skript (`tools/previa.py`, 144 gesperrte Vias vor dem Router, der Router nutzt die Plane nicht selbst), die letzten ca. 10 Verbindungen (CHG_PROG1/3, GND/3V3 am Display-Stecker J20) wurden mit einem eigenen Mini-Maze-Router (`tools/maze.py`) von Hand-Skript nachgezogen, drei GND-Vias von der Kante weggeschoben (`tools/fixup.py`). Nach einer späteren Korrektur (Klickrad-Stecker J21 auf x = 0 mit neu orientiertem Molex-Footprint, Pads an der Kabelmündung) wurden die J21-Netze und eine Bahn (CHG_STAT1) aus dem Antennen-Keepout ebenfalls mit `maze.py` neu gezogen (`tools/j21fix.py`). Der Weg ist **nicht** per Knopfdruck reproduzierbar: Zwischenstände liegen in `tools/routing/`, die Schritte stehen unter „Neuaufbau“.
> - **Nicht geprüft / Risiken:** keine Hardware, keine Simulation; USB-HS-Paar **nicht als 90-Ω-Paar geführt**: auf der fertigen Platine gemessen USB_DP 89,1 mm (6 Vias), USB_DN 90,0 mm (4 Vias), Versatz ca. 0,9 mm, Lagenwechsel F.Cu/In2/B.Cu, überwiegend ungekoppelt (Router) – für 480 Mbit/s **ein Risiko**; Impedanz nicht berechnet, bei PCBWay anfragen; Analogführung (HPREFA/B, Ladungspumpe) vom Router, nicht nach Cirrus-Layoutregeln von Hand; Footprint des **Molex 503480-0600**: Signalpads 0,3 × 0,7 (Raster 0,5) und Körper 4,0 mm tief aus dem Zeichnungstext SD-503480-001 und dem Datenblatt-Foto, die Zeichnungsgrafik war nicht lesbar. **Nagelpads (hier 0,8 × 1,0 an den hinteren Ecken, x ±2,045) sind geschätzt; der Zeichnungstext nennt eine Maskenöffnung 1,0 × 0,3 und den Mittenversatz 0,79 – Form und Y-Lage UNGEPRÜFT, vor der Bestellung gegen die Molex-Zeichnung prüfen**; CPL-Drehungen nicht gegen PCBWay geprüft; LCSC-Nummern in der Stückliste stammen vom Vorgänger und sind **nicht verifiziert** (Spalte „Nummer geprueft“), nur Digi-Key `WM1387CT-ND` für den Molex-Stecker wurde auf der Produktseite gesehen.
> - Die Gerber-ZIP heißt nur dann ohne „NICHT_BESTELLEN“, wenn `tools/export.py` einen sauberen DRC sieht (hier der Fall).

Grundlage: `docs/AUDIO.md` (Audio-Kette), `TEILE.md` (Chipliste, Ziel-Maße). KiCad 9, Schaltplan und Platine werden aus Python-Skripten erzeugt (`tools/`). Rev. 2 (37 × 86 × 0,8) ist ersetzt, weil dort die Fläche nicht reichte und das Routing scheiterte.

## Inhalt des Ordners

| Pfad | Inhalt |
|---|---|
| `hauptplatine.kicad_pro`, `.kicad_sch`, `.kicad_pcb` | KiCad-Projekt (Schaltplan A1, eine Seite) |
| `lib/` | eigene Symbole (`Hauptplatine.kicad_sym`) und Footprints (`Hauptplatine.pretty`: ESP32-S31-WROOM-1 selbst erzeugt, Klinke und USB-C aus Tangara, X2QFN, Akkupads, Befestigungsloch) |
| `fertigung/hauptplatine_gerber_bohrdaten.zip` | Gerber (4 Lagen, 1,0 mm, Maske, Paste, Silkscreen, Kontur) und Bohrdaten (Excellon, PTH/NPTH getrennt) |
| `fertigung/hauptplatine_BOM_PCBWay.csv` | Stückliste im PCBWay-Format (Designator, Menge, Hersteller, MPN, Beschreibung, Gehäuseform, LCSC/Digi-Key nur wo geprüft; DNP markiert) |
| `fertigung/hauptplatine_CPL_PCBWay.csv` | Bestückungsdatei Oberseite und Unterseite (Designator, Mid X/Y, Layer, Rotation), ohne DNP-Teile |
| `fertigung/hauptplatine_schaltplan.pdf` | Schaltplan als PDF |
| `vorschau/` | SVG/PNG der Ober- und Unterseite |
| `pruefung/erc.rpt`, `pruefung/drc.rpt` | Berichte von `kicad-cli` |
| `quellen/` | Quellen: Tangara-Netzliste (Rev. 5), Tangara-Footprints, Lizenztexte |
| `tools/` | Generatoren, Routing-Skripte, `routing/` (Zwischenstände des Routings) |
| `LICENSE` | CERN-OHL-S-2.0 |

## Blockschaltbild

```
USB-C (J6, GCT USB4510) --CC1/CC2--> TUSB320LAI (U12, DRP) --ID/INT--> S31
   | D+/D- (R102/R103)                       |
   |                                          v HOST_EN
   +--VBUS--> PE1605 (U5) --> Q1 --> MCP73871 (U10, Power-Path) <--> LiPo 303450 (BT1-Pads, NTC)
   |                                |  SYS_POWER                         |
   +<-- TPS2553 (U21) <-- TPS61023 (U20, 5,1 V) <-- SYS_POWER           MAX17048 (U22, I2C 0x36)
                                    |
              SW1 -> LDO_EN / S31 haelt SYS_PWR_EN (Power-Latch)
                                    v
                      TLV75733 (U4, 3V3, 1 A) ----------------------------------------+
                                    |                                                    |
 ESP32-S31-WROOM-1-N16R16V (U15)  3V3                                                    |
  WLAN 6, BT 5.4 Classic + LE Audio, USB-HS-OTG, 16 MB Flash + 16 MB PSRAM               |
    |QSPI+I2C+INT      |I2S (Slave)         |SDMMC 4 Bit        |I2C                      |
    v                  v                    v                   v                         |
 AMOLED 2,06" (J20)   Pegelwandler U31-U33  microSD (J4)        Klickrad (J21, Molex 503480-0600)     |
 CO5300 410x502       1,8 V <-> 3,3 V       (TPS22948 U16)      AT42QT2120 + DRV2605L     |
                           |                                                              |
                  CS43131 (U17), I2S-Master, Quarz 22,5792 MHz (X1) <-- 1,8-V-LDO (U34) <-+
                  VP aus SYS_POWER, I2C ueber PCA9306 (U30)
                           |HPOUTA/B + HPREFA/B + HP_DETECT
                           v
                  Klinke SJ-43504-SMT-TR (J1, Randausschnitt) + ESD D5V0L2B3T-7 (U3)

 Audio-Weg A (Kabel, Hi-Res): S31 --I2S--> CS43131 (24 Bit/192 kHz, Class-H-Verstaerker) --> Klinke
 Audio-Weg B (digital):       S31 --USB-HS-OTG (Host, UAC2)--> USB-C --> externer USB-DAC (TUSB320 stellt "Quelle" ein, TPS61023 + TPS2553 liefern 5 V)
 Weg C (drahtlos):            S31 --Bluetooth--> Kopfhoerer (A2DP, in der Regel SBC; LC3 nur mit LE Audio auf beiden Seiten)
```

## Festgelegte Chips

| Funktion | Chip | Bezeichner | Herkunft |
|---|---|---|---|
| MCU | ESP32-S31-**WROOM-1**-N16R16V (18 × 25,5 × 3,1 mm, 16 MB Flash, 16 MB PSRAM) | U15 | neu (WROOM-3 nicht nötig, siehe GPIO-Prüfung) |
| DAC + Kopfhörerverstärker | Cirrus **CS43131**-CNZR (QFN-40), Quarz 22,5792 MHz, DAC = I²S-Master | U17, X1 | neu (`docs/AUDIO.md`; Tangara: WM8523 + INA1620 + TPS65133) |
| 1,8-V-Schiene | TLV75518PDRV (LDO, rauscharm) | U34 | neu |
| Klinke | Same Sky SJ-43504-SMT-TR (5,0 mm hoch) im Randausschnitt | J1 | angepasst (Tangara: SJ-3506-SMT, 6,0 mm; Footprint aus der Tangara-Bibliothek) |
| ESD Klinke | D5V0L2B3T-7 | U3 | Tangara |
| Lader mit Power-Path | MCP73871-2CCI/ML | U10 | Tangara |
| 3V3 | TLV75733PDRV (1 A) | U4 | angepasst (Tangara: TLV75533PDBV, 500 mA) |
| USB-C-Buchse | GCT USB4510-03-1-A | J6 | Tangara |
| USB-C-Rollenumschaltung | TUSB320LAI | U12 | neu, **eigene Entwicklung, ungeprüft** |
| 5-V-Boost für Host | TPS61023 | U20 | neu, **eigene Entwicklung, ungeprüft** |
| Lastschalter 0,5 A | TPS2553 (WSON) | U21 | neu, **eigene Entwicklung, ungeprüft** |
| Akkustand | MAX17048G+T10 | U22 | neu |
| Touch-Rad / Haptik | AT42QT2120 / DRV2605L auf dem Klickrad-Modul v2 | – | Tangara |

Nicht verbaut: WM8523, INA1620, TPS65133 samt Spulen (±5 V entfällt), 74CBTLV3257 und SAMD21 (der S31 hat eigenes USB und eigene SD-Schnittstelle).

## Übernommen von Tangara / angepasst / neu entwickelt

Quelle: Tangara-Hardware Rev. 5 (cool tech zone, CERN-OHL-S-2.0, <https://codeberg.org/cool-tech-zone/tangara-hw>), Netzliste in `quellen/tangara_netlist_rev5.json`. Anzahl = Bauteile der Stückliste (ohne Testpunkte und Bohrungen); gesamt 134 Bauteile in 69 Positionen.

| Block | Anzahl | Bauteile | Änderung |
|---|---|---|---|
| **Übernommen 1:1** (Werte, Netze, Footprints aus Tangara) | 25 | Ladeschaltung MCP73871 (U10) mit Q1, D4, U5, R1, R7, R34/R35/R37/R38/R39/R41, C37; USB-C-Buchse J6; ESD U3; SD-Versorgung U16 mit Pull-ups R9/R11/R12/R57/R61; 3V3-Kondensatoren; Bulk C29 | nur Netznamen vereinheitlicht |
| **Angepasst** | 14 | U4 (TLV75733P in WSON statt TLV75533 in SOT-23: 1 A, flach); J1 (SJ-43504 statt SJ-3506, Pads verschmälert); J4 (microSD Molex statt Vollformat-SD Hirose, 4-Bit-SDMMC statt SPI + Multiplexer); SW1 (Taster B3U-3000P statt Schiebeschalter, Power-Latch); R4 (10 k statt 100 k); R36/R43 (feste Pull-ups statt SAMD21-Steuerung); BT1 (Lötpads statt JST-PH-Stecker, Rückseite ist neben dem Akku nur 3,3 mm hoch); alle 0805-Kondensatoren als 0603 (Oberseite nur bis 1,0 mm Höhe) | Begründung je Teil im Feld „Beschreibung“ der Stückliste |
| **Neu: Cirrus-Beschaltung** | 19 | CS43131-Entkopplung nach Datenblatt Abb. 2-1, Quarz X1 mit Lastkondensatoren, Ferritperle FB1 | nach DS1155F2, Werte aus dem Bild gelesen |
| **Neu: Espressif-Beschaltung** | 8 | EN-RC (R100, C100), 22 µF/100 nF am Modul, BOOT-Pull-up, Serienplätze USB (R102, R103), Testpunkte | nach Datenblatt v0.5 (vorläufig) |
| **Neu: alles Übrige** | 67 | CS43131 (U17), Pegelwandler U30 (PCA9306) und U31-U33 (SN74AXC1T45), Reset-Transistor Q20, 1,8-V-LDO U34, DNP-Quarz X2, USB-Host-Zweig (U12, U20, U21, L20, Q10, Q11, D10, R110...R119, C110...C114), MAX17048 (U22), Display-FPC (J20), Klickrad-Stecker (J21), Power-Latch-Widerstände R200...R202 | USB-Host-Zweig **eigene Entwicklung, ungeprüft** |

Power-Latch: Der Taster SW1 zieht `KEY_LOCK` über R4 auf `SYS_POWER`; das schaltet `LDO_EN` (Tangara-Schaltung mit D4). Sobald der S31 läuft, setzt er `SYS_PWR_EN` (LP-GPIO) und hält den Regler an; zum Ausschalten löscht er `SYS_PWR_EN`. R202 (100 k) zieht `SYS_PWR_EN` nach Masse, wenn der S31 aus ist. `KEY_LOCK_MCU` liest den Taster (über R201).

## GPIO-Prüfung ESP32-S31-WROOM-1 und Belegung

Das WROOM-1 führt 52 GPIOs heraus (Datenblatt v0.5 Tab. 3-1: 40 Randpads und 20 kleine Pads im Feld unter dem Modul, davon 3 GND/3V3/EN). Alles, was verlangt war, ist vorhanden, **das größere WROOM-3 wird nicht gebraucht**:
Display-QSPI 6 (+ Reset, TE, Touch-INT), I²C 2, Klickrad-CHANGE, I²S 3 (als Slave), SDMMC 6 (dedizierte Pads IO35...IO40), USB-HS (DP/DM, Pads 55/54), Power-Latch 2, MCP73871-Status 3 (+ SEL, PROG2), Klinkenerkennung (im DAC, Pin HP_DETECT, über DAC_INT), DAC RESET/INT. Verwendet: 30 freie GPIOs plus die festen Pads unten.
Die USB-HS-Pins DM/DP (Pads 54/55) und die meisten anderen GPIO liegen auf den kleinen Pads im Feld unter dem Modul (Raster 0,8 mm, nur 0,4 mm Pad-Breite); sie werden mit Durchkontaktierungen nach innen geführt. **Das ist eine Eigenheit des WROOM-1**, die bei Handlötung auffiele, bei PCBA unkritisch ist.

Vermieden: Strapping IO36 (intern hochgezogen, SD-DAT1 liegt trotzdem dort: Pull-up passt zum Standard), IO37 (JTAG-Auswahl, SD-DAT2 hat einen Pull-up: **prüfen**, ob das die JTAG-Quelle ungewollt umschaltet), IO60/IO61 (Boot-Modus; IO61 = BOOT-Pad), IO33/IO34 (USB-Serial/JTAG), TX0/RX0 (Testpunkte). Wecksignale (Power-Latch, Taster, Klickrad-CHANGE) liegen auf LP-GPIO IO0...IO7.

Freie GPIOs (automatisch vergeben, `tools/gpio_assign.py`: kürzeste Leitung zu den Zielpads):

| Signal | S31-GPIO | Modulpad | Funktion |
|---|---|---|---|
| WHEEL_INT | IO0 | 8 | Klickrad CHANGE, Weckquelle (LP-GPIO) |
| FG_ALRT | IO1 | 9 | MAX17048 ALRT |
| HOST_EN | IO2 | 4 | Host-VBUS an/aus (Boost + Schalter) |
| TUSB_ID | IO3 | 5 | TUSB320 ID (low = wir sind Quelle) |
| SYS_PWR_EN | IO4 | 6 | Power-Latch: haelt die Versorgung (LP-GPIO) |
| KEY_LOCK_MCU | IO5 | 7 | Ein/Aus-Taster lesen (LP-GPIO, Weckquelle) |
| SDA | IO6 | 10 | I2C SDA (Display-Touch, Klickrad, MAX17048, TUSB320, CS43131 ueber PCA9306) |
| SCL | IO7 | 11 | I2C SCL |
| LCD_D2 | IO9 | 43 | Display QSPI D2 |
| LCD_D1 | IO10 | 44 | Display QSPI D1 |
| LCD_D0 | IO11 | 45 | Display QSPI D0 |
| LCD_TE | IO12 | 46 | Display Tearing-Effect |
| CHG_STAT1 | IO13 | 47 | MCP73871 STAT1 |
| CHG_PROG2 | IO14 | 48 | MCP73871 PROG2 (USB-Strom), Pull-up 100 k |
| CHG_SEL | IO15 | 49 | MCP73871 SEL (hoch = USB), Pull-up 10 k |
| CHG_STAT2 | IO16 | 50 | MCP73871 STAT2 |
| CHG_PG | IO17 | 51 | MCP73871 PG |
| TUSB_INT | IO18 | 52 | TUSB320 INT_N |
| LCD_RST | IO19 | 53 | Display Reset |
| DAC_RESET | IO20 | 15 | CS43131 RESET (1 = Betrieb, ueber Q20) |
| DAC_INT | IO21 | 16 | CS43131 INT (aktiv low, 10 k Pull-up) |
| I2S_BCLK | IO22 | 17 | I2S Bitclock vom DAC (S31 = Slave) ueber Pegelwandler U31 |
| I2S_LRCK | IO23 | 18 | I2S Wordclock vom DAC ueber Pegelwandler U32 |
| I2S_DOUT | IO24 | 19 | I2S Daten S31 -> DAC ueber Pegelwandler U33 |
| SD_CD | IO25 | 20 | microSD Karte erkannt |
| SD_VDD_EN | IO42 | 28 | microSD Versorgung (TPS22948 ON) |
| LCD_SCK | IO48 | 56 | Display QSPI SCK |
| LCD_CS | IO49 | 57 | Display QSPI CS |
| TP_INT | IO50 | 58 | Touch-Interrupt Display |
| LCD_D3 | IO51 | 59 | Display QSPI D3 |

Feste Pads:

| Signal | S31-GPIO | Modulpad | Funktion |
|---|---|---|---|
| SD_D0 ... SD_D3, SD_CLK, SD_CMD | IO35 ... IO40 | 12, 21 ... 25 | SDMMC-Slot 2 (feste Pads laut Datenblatt: SD2_CDATA0 ... SD2_CCMD) |
| USB_HS_DP / USB_HS_DM | DP / DM | 55 / 54 | USB-2.0-HS-OTG, ueber R102/R103 zur USB-C-Buchse |
| BOOT | IO61 | 27 | Download-Modus: nach GND kurzschliessen (TP15 gegen TP17) |
| ESP_EN | EN | 3 | Reset: RC 10 k / 1 uF, TP14 gegen TP16 kurzschliessen |
| UART_TX0 / UART_RX0 | TX0 / RX0 | 37 / 36 | Testpunkte TP10 / TP11 |
| USBJ_DP / USBJ_DM | IO34 / IO33 | 14 / 13 | USB-Serial/JTAG, Testpunkte TP12 / TP13 |

Alle Zuordnungen sind **ungeprüft** gegen das endgültige Datenblatt (v0.5, vorläufig) und die IDF-6-Dokumentation: Welche Peripherie auf welche GPIOs gelegt werden darf (GPIO-Matrix, LP-IO, SDMMC-Slot 2), vor der Bestellung gegenprüfen.

## Audio: CS43131

- **Taktkonzept** (`docs/AUDIO.md` 5.3): Quarz X1 22,5792 MHz (NDK NX2016SA 22.5792M EXS00A-CS09116, laut Datenblatt Tab. 5-1 geeignet, Register 0x20052 = 0x02) direkt am DAC; der DAC ist I²S-Master (SCLK1, LRCK1 sind Ausgänge), der S31 ist Slave und braucht weder MCLK noch APLL. Die Lastkondensatoren C255/C256 (10 pF C0G) sind ein Startwert für CL = 8 pF und nach Datenblatt Abschnitt 5.3 am Aufbau abzustimmen.
- **Zweiter Quarz** X2 24,576 MHz (NDK NX2016SA 24.576M EXS00A-CS09117) als **DNP**-Option: statt R240/R241 dann R242/R243 (je 0 Ω) bestücken. Das ist die Umschaltung als Lötbrücke; ein 2:1-Taktumschalter-IC wurde nicht eingebaut (weniger Fläche, kein Jitter-Beitrag), auf dem ersten Aufbau werden beide Varianten gemessen.
- **Pegel**: Alle Digitalpins des DAC arbeiten mit VL = 1,8 V (zulässig 1,66...1,94 V, abs. max. 2,33 V). Deshalb: PCA9306 (U30) für I²C (200 k an EN, 4,7 k Pull-ups auf der 1,8-V-Seite), je ein SN74AXC1T45 (U31 BCLK, U32 LRCK: DAC → S31; U33 Daten: S31 → DAC) für I²S. INT liegt in der VP-Domäne (offener Drain, 10 k nach 3V3). RESET liegt ebenfalls in der VP-Domäne (Pegel relativ zu VP bis 5,25 V): Transistor Q20 mit 100 k an VP, Gate-Pull-up 100 k nach 3V3 hält den DAC im Reset, bis der S31 `DAC_RESET` auf low zieht.
- **Versorgung**: VP = SYS_POWER (Batterie bzw. USB-seitig geführter Ausgang des MCP73871, 3,0...5,25 V), 0,1 µF + 4,7 µF. 1,8 V aus U34 (TLV75518P, aus 3V3), VA und VCP über Ferritperle FB1 (BLM15) getrennt von VL/VD. Reihenfolge laut Datenblatt: VP zuerst, dann 1,8 V, dann RESET lösen.
- **Entkopplung** (Fig. 2-1, Zuordnung der Werte aus dem Bild gelesen, vor Bestellung gegen das Datenblatt prüfen): VL, VD, VA je 100 nF; VA, VCP, −VA, VCP_FILT+/−, Flying-Caps je 2,2 µF; FILT+ und FILT− je 15 µF (0603); VP 100 nF + 4,7 µF. Die 15-µF-Typen haben keine verifizierte MPN (Typ nach Verfügbarkeit wählen).
- **Klinke** (SJ-43504: 1 Hülse, 2 Spitze, 3 Ring 1, 4 Ring 2, 5 Spitzenschalter, 6 Ringschalter): HPOUTA → Spitze, HPOUTB → Ring 1, HPREFA → Hülse (1), HPREFB → Ring 2 (4). Ein TRS-Stecker verbindet 1 und 4. HPREFA und HPREFB sind **eigene Netze**, die einzeln bis zur Buchse laufen und dort über je einen Net-Tie (NT1, NT2: Kupferbrücke im Footprint, kein Bauteil) mit der Massefläche (GND) verbunden sind (Datenblatt Abschnitt 8.3: Masse am Buchsenpin). Der Spitzenschalter (5) geht auf HP_DETECT; er ist im Ruhezustand mit der Spitze verbunden, deshalb muss im DAC `HPDETECT_INV` gesetzt werden. ESD: U3 auf HPOUTA/HPOUTB.
- **Erwartete Werte** (Datenblatt, nicht an dieser Platine gemessen): Dynamikumfang 125 dB an 32 Ω, THD+N −110 dB, 30,8 mW an 32 Ω, Ruheleistung ca. 29 mW (statt ca. 100...110 mW bei Tangara). Ausgangsimpedanz: im Datenblatt nicht gefunden, messen.
- **Plan B** (nur beschrieben, nicht verbaut): CS43198 (gleiches QFN-40, Line-Out) + OPA1622 (VSON-10) + TPS65133 mit 2 × 4,7 µH für ±5 V, wie bei Tangara. Würde auf der Rückseite rund 60...80 mm² mehr Fläche brauchen; Pin-Vergleich vor dem Layout nötig. Plan C: Tangara-Kette 1:1 (WM8523 + INA1620), dann wieder MCLK vom S31 oder Oszillator.
- **Bluetooth-Audio**: Der ESP32-Stack liefert für A2DP in der Regel nur SBC; LC3 (LE Audio) nur, wenn Kopfhörer und Firmware LE Audio unterstützen. Für hochauflösenden Klang bleibt der Kabelweg A oder B.
- **USB-Port wird geteilt**: Es gibt nur einen OTG-Port. Entweder ist der Player USB-Speichergerät (MSC) am PC, oder USB-Audio-Host (UAC2) am externen DAC. Beides gleichzeitig geht nicht; die Firmware muss die Rolle (TUSB320 INT/ID) umschalten. Flashen: über USB-Serial/JTAG (Testpunkte TP12/TP13) oder den HS-Port im Download-Modus (TP15 gegen TP17 kurzschließen beim Einstecken); beides ungeprüft.

## Display

2,06" AMOLED 410 × 502, CO5300, QSPI + Touch-I²C. Belegung des 30-poligen 0,5-mm-FPC aus dem Waveshare-Schaltplan ESP32-S3-Touch-AMOLED-2.06 V1.0 (Stecker J3), Stecker auf unserer Platine J20 = Hirose FH12-30S-0.5SH(55), Oberseite, Mundloch zur Displayunterkante (das FPC wird unter dem Panel zurückgefaltet):

| FPC-Pin | Signal | Netz | FPC-Pin | Signal | Netz |
|---|---|---|---|---|---|
| 1, 2 | GND | GND | 16 | GND | GND |
| 3 | TP_SCL | SCL | 17 | IM0 | 10 k nach GND |
| 4 | QSPI_SCL | LCD_SCK | 18, 20, 22, 24, 26, 28 | MIPI-Pins (QSPI-Modus) | GND |
| 5 | TP_SDA | SDA | 19 | LCD_RESET | LCD_RST (100 k Pull-up) |
| 6 | LCD_CS | LCD_CS | 21 | DSI_PWR_EN | 4,7 k nach 3V3 |
| 7 | TP_INT | TP_INT | 23 | VCI | 3V3 |
| 8 | QSPI_SIO3 | LCD_D3 | 25 | VDDIO | 3V3 |
| 9 | TP_RESET | 10 k nach 3V3 | 27 | LCD_TE | LCD_TE |
| 10 | QSPI_SIO2 | LCD_D2 | 29, 30 | 3V3 | 3V3 |
| 11 | TP_VDD | 3V3 | 31...34 | Schirm | GND (MP) |
| 12 | QSPI_SIO1 | LCD_D1 | 13 | NC | – |
| 14 | QSPI_SIO0 | LCD_D0 | 15 | IM1 | 10 k nach 3V3 |

Nicht geprüft: ob der gekaufte Panel-FPC (Kontaktseite oben/unten, Dicke 0,3 mm, Pin-Reihenfolge) zu diesem Stecker passt, genaue Lage und Länge des FPC (Maßzeichnung des Moduls besorgen; DUENNBAU.md nennt 1,7 mm Zusatz an der FPC-Seite). Alternative laut DUENNBAU.md: FPC durch einen Schlitz auf die Rückseite.

## Flächenbilanz (vor dem Routing, `tools/flaechenbilanz.py`)

Platine 41 × 97 mm = 3681 mm² (nach Ecken und Ausschnitten). Courtyard-Fläche mit 0,25 mm Aufschlag:

| Block | Bedarf |
|---|---|
| feste Teile: WROOM-1 496, microSD 188, Klinke 173, USB-C 113, Display-FPC 177, Taster 22, Akkupads 22, Klickrad-Stecker 27 | 1218 mm² |
| hohe Teile (> 1,0 mm: C29, D4, D10, Q1, U5, U16) | 94 mm² |
| flache Teile (130 Stück: DAC-Kette ca. 230, Lader/USB/Boost ca. 250, Rest) | 654 mm² |
| **Summe** | **ca. 1966 mm²** |

Nutzbar nach Abzug von Sperrzonen (Rand 0,7 mm, Akkufach 32 × 38,5 mm, Klickrad-Kreis r 16,3 vorn, LRA-Ausschnitt + 1 mm, Befestigungslöcher r 2,0, Antennen-Keepout): Rückseite 1415 mm², Vorderseite 2424 mm² (mit flachen Teilen unter dem Display). Reserve für die beweglichen Teile (748 mm²): **über 400 %** mit Vorderseite unter dem Display, **218 %** wenn unter dem Display nichts stehen darf (nur Rückseite + Vorderseite außerhalb Display: Rückseite allein 89 %). Die 15-%-Reserve ist damit weit übertroffen; eng wurde es trotzdem im Analogblock (siehe Routing), nicht wegen der Gesamtfläche, sondern wegen der Dichte um den CS43131 (QFN-40, 0,4 mm Raster).

Gruppen (harte Bereiche, `layout.GROUPS`): Analog (DAC, Quarz, Pegelwandler, Klinke) links unten neben der Klinke; Lader/USB-Rollen/Boost rechts unten neben dem USB-C; Display-Anschluss und 3V3/Fuel-Gauge Mitte Vorderseite; Modul-Beschaltung und SD-Versorgung oben Vorderseite (Vias zur Rückseite). Schaltregler-Schleifen kompakt (U20/L20/C111–C113 und U10 liegen mit ihren Kondensatoren je in wenigen mm). Digital/Funk (oben) und Analog (unten) sind durch Akku (32 × 38,5 mm) getrennt.

## Klickrad-Anschluss

**Molex 503480-0600** (Easy-On BackFlip, FFC/FPC 0,5 mm, 6-polig, **Dual Contact**, 1,0 mm hoch; Datenblatt/Zeichnung SD-503480-001 gelesen; Digi-Key `WM1387CT-ND` / Herstellernr. 5034800600 auf der Produktseite gesehen; **LCSC-Nummer nicht geprüft**). J21 sitzt auf der **Vorderseite** bei (0, −46,2), Kabelmündung nach oben (Richtung Klickrad). Weil der Stecker **Dual Contact** ist (Anm. 9 der Zeichnung), passt **Kabeltyp A oder B**; in der BOM als eigene, nicht bestückte Zeile „FFC-Kabel 6 Pin 0,5 mm“ (Kabel FFC 6 Pin 0,5 mm, 0,3 mm dick, Länge 25–40 mm; Digi-Key führt z. B. Molex 0150200056, 6 Pos., 76,2 mm – Typ nicht geprüft). Das Klickrad-Modul hat denselben Stecker auf seiner Rückseite bei (0, −35,8) (Mundloch nach unten, Pin 1 bei x = +1,25). J21 liegt genau darunter bei x = 0, Pin 1 ebenfalls bei x = +1,25; das Kabel läuft **ungedreht und gerade** von der Mündung des Moduls (y ≈ −40,7) nach unten bis zur Mündung von J21 (y ≈ −44,2): freie Länge ca. 3,5 mm + 2 × 1,6 mm Einstecktiefe, also ein enger S-Bogen von 1,5–2 mm Höhe mit 0,3-mm-FFC; ein größerer Plattenabstand (bei 10 mm Gerätedicke möglich) ist besser. R120/R121/R136 (0,35 mm hoch) liegen unter dem Kabelweg. Belegung 1 3V3, 2 GND, 3 SDA, 4 SCL, 5 CHANGE, 6 Reserve. Pull-ups R120/R121 (2,2 k), R136 (10 k) in der Nähe.

## Mechanik und Übergabe an das CAD

Koordinaten: Ursprung = Plattenmitte, x nach rechts, y nach oben, Blick auf die Display-Seite (Vorderseite). Rückseitenteile erscheinen unten gespiegelt „durchgesehen“. Platine 41,0 × 97,0 × 1,0 mm, Ecken r = 4,0.

| Element | Lage / Maß | Höhe über Platine |
|---|---|---|
| Klinke J1 SJ-43504-SMT-TR (Mid-Mount, Pads auf B.Cu) | Achse x = −12,0, Randausschnitt 6,8 mm breit von y = −48,5 bis y = −35,75, Körper ca. 9 × 14 mm | gesamt 5,0 mm; nach STEP-Versatz (+1,9 / −3,1 um die Pad-Ebene, Lage des STEP-Ursprungs **ungeprüft**) ca. **3,1 mm hinter die Rückseite** und **0,9 mm vor die Vorderseite** (bei 1,0 mm Platine) |
| USB-C J6 GCT USB4510 (im Randausschnitt, Pads/Laschen B.Cu) | Achse x = +9,0, Randausschnitt 9,24 × 6,0 mm an der Unterkante | gesamt 3,18 mm, Aufteilung vorn/hinten ungeprüft |
| WROOM-1 U15 (Rückseite, gedreht) | Mitte (+6,5, +37,5), Körper x −6,25…+19,25, y +28,5…+46,5 (25,5 × 18) | 3,1 mm |
| Antennen-Keepout | x +12,7…+20,7, y +28,0…+47,0 (alle Lagen, Platte + Vorder-/Rückseite frei von Metall, Display-Rahmen/Akku/Metall fernhalten) | – |
| microSD J4 (Rückseite) | Mitte (−13,7, +37,5), Karte wird von der linken Kante eingeschoben, Öffnung in der linken Wand bei y ≈ +37,5 | 1,9 mm |
| Akkuanschluss BT1 (Rückseite) | Lötpads bei (−12,5, +28,8) | 0,2 mm |
| Taster SW1 B3U-3000P (Rückseite) | (+15,0, −30,0), von der Rückseite zu drücken | 1,2 mm |
| Akkufach (Rückseite, bauteilfrei) | x −16,0…+16,0, y −12,0…+26,5 (32 × 38,5 mm) | Zelle ≤ 3,7 mm bei 10 mm Gerät (s. u.) |
| LRA-Ausschnitt (innen, r = 1) | Mitte (0, −19), 14 × 10 mm, beidseitig 1,0 mm bauteilfrei | LRA bis 3,0 mm |
| Klickrad | Mitte (0, −25), Platine Ø 32; Vorderseite im Kreis r 16,3 bauteilfrei | – |
| Klickrad-Stecker J21 (Vorderseite) | (0,0, −46,2), Kabelmündung (Signalpads) nach oben, Körper x ±2,35, y −48,2…−44,2 | 1,0 mm |
| Display-FPC-Stecker J20 (Vorderseite) | (0, −0,5), FH12-30S, Mundloch nach unten, Körper x ±10,6, y −5,4…+2,5 | 1,0 mm |
| Display-Zone | x ±18,5, y −6,5…+40,5 (Annahme für das 2,06"-Modul); darunter nur Teile ≤ 1,0 mm (flache 0402/0603, QFN, SOT-523, J20), Luft darunter ≥ 1,1 mm | ≤ 1,0 mm |
| Befestigungslöcher (NPTH Ø 1,8, M1,6) | (−18,2, +46,2), (+18,2, −46,2), (−18,2, −46,2); je r 2,0 bauteilfrei | – |
| Vorderseite oberhalb des Displays | y > 41,0: auch höhere Teile erlaubt (Bauhöhe ≤ 1,5 mm) | – |

**Bauteilhöhen > 3 mm:** nur Klinke (gesamt 5,0 mm, hinten ca. 3,1 mm), USB-C (3,18 mm) und Modul (3,1 mm); nicht vermeidbar (SJ-3506-SMT hätte 6,0 mm). C29 (100 µF) 2,7 mm, alles andere ≤ 1,5 mm. **Passung Plattendicke:** Klinke und USB-C sind Mid-Mount-Teile mit Aussparung für eine bestimmte Plattendicke; der Vorgänger plante 0,8 mm, hier sind es 1,0 mm. Ob SJ-43504 und USB4510-03 1,0 mm vertragen, ist **nicht geprüft** (Datenblätter prüfen; falls nicht, ist das der Fall „0,8 mm nur wenn nötig“).

**Höhenstapel bei Gerätedicke bis 10 mm (neues Ziel):** Front 0,8 + Display 2,05 (Modul mit Touch; Panel allein 1,0) + Luft 1,1 + Platine 1,0 = 4,95 mm; Rückwand 1,0 → Rückzone **4,05 mm** (5,1 mm mit 1,0-mm-Panel). Die Klinke ragt nach STEP-Versatz ca. 3,1 mm hinter die Platine (passt in 4,05 mm), vorn 0,9 mm (sie sitzt unterhalb des Displays); der Akku hat im Mittelbereich höchstens ca. 3,7 mm (Zelle + 0,3 mm Luft) – **eine 4,0-mm-Zelle passt nur mit dem 1,0-mm-Panel (Rückzone 5,1 mm) oder bei 10,3 mm Gerätedicke**. Akkukapazität bei 32 × 38,5 × 3,7…4,0 mm: grob **ca. 450–550 mAh** (Schätzung aus typischer Energiedichte, keine Datenblattwerte) – **unter dem Ziel von 600 mAh**. Verbesserung nur durch längeren Akku: Das Modul (Antenne rechts) braucht die oberen 18,5 mm, der LRA-Ausschnitt die unteren; ein Wegfall des SD-Slots oder ein Modul über dem Display (Vorderseite, y > 41) gäbe ca. 10 mm mehr Zellenlänge.

Randabstände: Teile ≥ 0,7 mm von der Kante, außer Stecker mit Mündung im Randausschnitt.

## Pin-Tabelle

Siehe „GPIO-Prüfung und Belegung“ (Signale ↔ S31-GPIO ↔ Modulpad) und „Display“ (30-poliger FPC). Klickrad: J21-Pins 1 3V3, 2 GND, 3 SDA, 4 SCL, 5 CHANGE, 6 Reserve.

## Geprüft / nicht geprüft

**Geprüft (automatisch):** DRC 0 Verstöße/0 unverbunden (Bericht `pruefung/drc.rpt`), ERC 0 (`pruefung/erc.rpt`), Netzliste Schaltplan = Platine (Parität, 0 Footprint-Hinweise); Gerber/Bohrdaten mit `kicad-cli` erzeugt, Gerber-Vorschau (`vorschau/`) angesehen (Siebdruck bereinigt); Datenblattwerte der Pinbelegungen wie unter „Festgelegte Chips“.

**Nicht geprüft:** Funktion der Schaltung (nie aufgebaut), eigene USB-C-Rollen/Host-Schaltung (U12, U20, U21, Q10, Q11, D10), Power-Latch, Reset-Transistor Q20, Pegelwandler am CS43131, Quarzstart; **Antenne** im Gehäuse (Akku 3 mm unter dem Modul, Metall in der Nähe); Audioqualität; **USB-HS 90 Ω** (nicht berechnet; PCBWay-Lagenaufbau 1,0 mm erfragen, Paar ca. 80 mm lang, vom Router geführt); Rückleitung/Masse unter dem Analogblock (In1 durchgehend, aber Vias und Spuren des Routers); Footprint-Genauigkeit (Molex 503480 s. o., WROOM-1 selbst erzeugt, X2QFN nach TI-Beispiel, L20 Näherungs-Footprint); CPL-Drehungen/Polarität bei PCBWay (Vorschau prüfen); Höhenstapel/Kollisionen im CAD; Lieferbarkeit und Preise; LCSC-Nummern; die 15-µF-Typen ohne MPN; Gehäuse-Dicke (Stapel oben).

**Menschlicher bzw. Opus-Review vor der Bestellung ist Pflicht** (Schaltplan gegen Datenblätter, Footprints gegen Zeichnungen, CPL-Vorschau bei PCBWay, Antennenfreiraum, Gehäusestapel).

## PCBWay-Bestellung Schritt für Schritt

1. pcbway.com → „PCB Assembly“ → „Quote Now“ (Leiterplatte plus Bestückung).
2. Gerber: `fertigung/hauptplatine_gerber_bohrdaten.zip`.
3. Leiterplatte: **4 Lagen**, **1,0 mm**, 41 × 97 mm, FR-4 Tg 150, Oberfläche **ENIG**, Kupfer außen 1 oz / innen 0,5 oz, Lötstopp/Siebdruck nach Wunsch, kleinste Bahn/Abstand 0,127/0,127 mm (PCBWay-Standard 4 Lagen ca. 0,1 mm), kleinste Bohrung 0,2 mm (Vias 0,45/0,2), Kupfer–Kante 0,3 mm (Steckerpads 0,2 mm), Impedanzkontrolle für USB-HS 90 Ω anfragen. Gefräste Innen-/Randausschnitte (LRA, Klinke, USB-C), NPTH getrennt in der Bohrdatei. **Mehrpreis 6 Lagen wäre nicht nötig; 0,8 mm wird nicht gebraucht.**
4. Bestückung beidseitig: 133 bestückte Bauteile in 68 Positionen (+ 1 Kabelzeile ohne Bestückung; CPL: 68 oben, 61 unten, DNP-Teile X2, R242, R243 ausgenommen); Passermarken auf beiden Seiten.
5. `fertigung/hauptplatine_BOM_PCBWay.csv` und `fertigung/hauptplatine_CPL_PCBWay.csv` hochladen. Teile ohne Lieferantennummer (S31-Modul, CS43131, mehrere Tangara-Teile) von PCBWay beschaffen lassen oder liefern. Akku wird nicht bestückt (Litzen von Hand an BT1).
6. Bestückungsvorschau prüfen: Polarität/Drehung von U3, U4, U5, U10, U12, U15, U17, U20–U22, U30–U34, D4, D10, Q1, Q10, Q11, Q20, X1 und aller Stecker (J20, J21!). Fehler melden, nicht stillschweigend bestätigen.
7. Gerber-Vorschau prüfen, dann bestellen. Erster Aufbau: 5 Platinen, 2 bestückt.

## Kosten (grobe Schätzung, nicht geprüft)

| Posten | Schätzung |
|---|---|
| Bauteile je Platine (S31-Modul 12–18 €, CS43131 ca. 17 €, übrige ICs ca. 14 €, Stecker ca. 10 €, Passive/Quarze ca. 8 €) | ca. 60–70 € |
| Leiterplatte 4 Lagen 41 × 97 mm, ENIG, 1,0 mm, 5 Stück | ca. 60–90 € (6 Lagen: etwa +30–60 %; wird nicht gebraucht) |
| Bestückung beidseitig: Rüstkosten, Schablone, Bestückung, THT (USB-C-Laschen) | ca. 100–180 € |
| Versand, Zoll | ca. 30–50 € |
| **Summe 5 Platinen, 2 bestückt** | **ca. 400–550 €, ca. 110–140 € je bestückter Platine** |

Das liegt über dem Projektbudget von 100–150 € (CS43131: Digi-Key ca. 18 USD, Lieferzeit bis 20 Wochen).

## Offene Risiken

1. **Antenne**: Modul innerhalb der Kante, Keepout eingehalten, aber Akku 3 mm unter dem Modul und rechter Display-Rahmen daneben: Reichweite ungemessen.
2. **Akkukapazität** unter dem Ziel (s. o.) und Rückzone nur 4,05 mm bei 10 mm Gerät.
3. **Analog-Block** vom Router geführt; HPREFA/B einzeln zur Buchse, aber nicht von Hand optimiert. USB-HS lang (≈ 80 mm).
4. **Molex-Footprint** nicht gegen das Zeichnungsbild geprüft.
5. **Eigene USB-C-Rollenlogik** (U12, U20, U21, Q10, Q11, D10) ungebaut; Q1 bleibt im Host-Betrieb ggf. leitend; Boost-Start bei leerem Akku.
6. **ESP32-S31-WROOM-1**: Datenblatt v0.5 vorläufig; Footprint selbst erzeugt; USB und viele GPIO auf den kleinen Pads im Feld (0,8 mm Raster).
7. **3V3-Regler** TLV75733 (1 A, WSON) statt Tangaras TLV75533 (500 mA) bewusst beibehalten (WLAN-Spitzen).
8. **Display**: Panel-FPC (Kontaktseite, Reihenfolge) ungeprüft; Display-Zone mit Teilen unter dem Panel verlangt ≥ 1,1 mm Luft (CAD-Stand 0,25 mm muss angepasst werden), sonst J20 nur lokal.
9. **Taster SW1** auf der Rückseite, Stößel/Seitentaster im CAD klären.
10. **Takt**: Quarz-Lastkondensatoren und Register 0x20052 abstimmen.

## Neuaufbau

Voraussetzungen: KiCad 9 (`pcbnew`, `kicad-cli`), Python: `shapely`, `numpy`, `scipy`, `Pillow`; Java + `xvfb` + Freerouting **1.9.0** (`freerouting-1.9.0.jar`, 2.1.0 ist unbrauchbar); `rsvg-convert`.

```
tools/make_lib.py ; tools/make_pro.py                     # Footprints, Projekt, Regeln
GAP=0.7 SEED=2 ITER=150000 OUT=p.json tools/place_sa.py   # Platzierung (4 Seeds parallel, ca. 5 min), Ergebnis nach tools/placement.json kopieren
tools/gpio_assign.py ; MODE=place tools/build_pcb.py      # GPIO-Zuordnung, Platine + GND-Vias (previa.py) -> /tmp/hp/pre.kicad_pcb, pre_nr.kicad_pcb
tools/route.sh <ordner> <pre.kicad_pcb> <durchgaenge>      # DSN -> Freerouting 1.9.0 -> SES; mehrfach auf dem Zwischenstand fortsetzen
BASE=<pre_nr.kicad_pcb> tools/post.sh <ordner>             # SES importieren, Zonen fuellen, DRC, GND-Nachbesserung
tools/maze.py / fixup.py / cleanup.py / polish.py          # Restverbindungen, Kantenvias, Bahnreste, Beschriftung
tools/gen_sch.py ; tools/export.py ; tools/gen_readme.py   # Schaltplan, Gerber/BOM/CPL/Vorschau/DRC, README
```

`tools/make.sh` ist veraltet (Freerouting 2.1.0, ein Lauf) und wird nicht mehr benutzt. Die Zwischenstände dieser Platine (SES, Platine vor dem Routing) liegen in `tools/routing/`; die Handschritte nach dem Router waren: `maze.py` für CHG_PROG3 (R35.1→U10.12), CHG_PROG1 (R39.1→U10.13), GND (J20.26→J20.24, J20.28→J20.26) und 3V3 (J20.29→J20.30, J20.25→J20.29, J20.23→J20.25, C131.1→J20.29 und → Bahnende bei (5,85; 4,48)), nach `rip.py` im Bereich um J20; `fixup.py`; `cleanup.py`; `polish.py`.

## Herkunft und Lizenz

- Dieses Design ist ein abgeleitetes Werk der **Tangara-Hardware** (cool tech zone, jacqueline, <https://cooltech.zone/tangara/>, Quelle <https://codeberg.org/cool-tech-zone/tangara-hw>), lizenziert unter **CERN-OHL-S-2.0**; es steht daher ebenfalls unter CERN-OHL-S-2.0 (Datei `LICENSE`). Die Namensnennung steht im Titelblatt des Schaltplans. Aus Tangara kommen Ladeschaltung, USB-C-Beschaltung, SD-Versorgung, Klinkenfootprint und ESD-Schutz.
- Audio-Schaltung des CS43131 nach dem Cirrus-Datenblatt DS1155F2; Klinken-Footprint von Same Sky/CUI Devices (über die Tangara-Bibliothek).
- Standardfootprints und -symbole: KiCad-Bibliotheken (CC-BY-SA 4.0 mit Ausnahme für Designs).
- Die Platzierungs- und Erzeugungsskripte in `tools/` sind neu geschrieben.
