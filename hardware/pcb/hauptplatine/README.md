# Hauptplatine Endgerät (Nano-Player), Rev. 3b

> **STATUS Rev. 3b (2026-10-05): Review-Korrekturen eingearbeitet, neu exportiert, ERC 0 / DRC 0 (Abgleich gegen den Schaltplan), 0 offene Verbindungen – trotzdem NICHT bestellbar:** Blocker **B4** (ESP32-S31-WROOM-1 nicht lieferbar, 21 Wochen) ist offen, ein **Opus-Zweitreview der geänderten Schaltung/Platine ist Pflicht**, und die „Offenen Punkte“ unten (u. a. H2 VDDPST_SD, H3-Rest, H5-Impedanz, H6 Molex-Footprint, H10 USB4510/1,0 mm) sind nicht erledigt. Die Fertigungsdateien in `fertigung/` sind **Entwürfe**, keine Bestelldateien.
> - Platine **41 × 97 × 1,0 mm, 4 Lagen** (F.Cu / In1 GND-Fläche / In2 Signale + GND-Fläche / B.Cu), Ecken r = 4, Gerät ca. 44 × 100 × bis 10 mm; Plattenumriss, Ausschnitte, Löcher und hohe Teile **unverändert** gegenüber Rev. 3; **für das CAD neu**: Display-Stecker J20 (Molex, Körper x ±8,35 statt ±10,6, 1,0 mm statt 2,0 mm hoch) und zwei Rückseiten-Taster SW2/SW3 (Rückwand-Löcher), siehe Tabelle „Mechanik und Übergabe an das CAD“. Antenne des WROOM-1 liegt **innerhalb** der Kante (Keepout 18,6 × 7,6 mm, alle vier Kupferlagen, Regelbereich `antenna_keepout_board`). Lagenaufbau-Referenz (PCBWay 1,0 mm, aussen/innen 1 oz, Prepreg 7628 0,1855 mm, Kern 0,43 mm) ist in der Platinendatei hinterlegt, **von PCBWay für diese Bestellung nicht bestätigt**.
> - **DRC (kicad-cli, mit Abgleich gegen den Schaltplan): 0 Verstöße, 0 unverbundene Pads, 0 Footprint-Hinweise.** ERC: 0 Meldungen. Regeln: Bahn/Abstand 0,127 mm, Via 0,45/0,2 mm, **Kupfer–Kante 0,3 mm** (PCBWay-Standard; nur die Pads von Klinke/USB-C/microSD dürfen per eigener Regel in `hauptplatine.kicad_dru` bis 0,2 mm an den Randausschnitt), Loch–Loch 0,3 mm. Abgeschaltet und begründet: `silk_over_copper`, `silk_overlap`, `silk_edge_clearance` (PCBWay schneidet Siebdruck über Pads/Kante automatisch ab), `nonmirrored_text_on_back_layer`. Referenzbezeichner sind absichtlich **nicht** im Siebdruck (PCBWay arbeitet nach CPL).
> - **Was Rev. 3b gegenüber Rev. 3 ändert (Review `docs/REVIEW-HAUPTPLATINE.md`, Abschnitt 7):** B1 PCA9306 VREF2 = EN (ein 200 k, 100 pF); B2 R57 nicht bestückt; B3 Lader SEL = GND, PROG2 fest 500 mA, R39 2,7 k (ca. 370 mA); H1 Reset-Sicherung Q21/Q22/R250 (RESET bleibt ohne 3V3 low); H3 Leistungsnetze verbreitert (VBAT und VBUS jetzt fast durchgehend ≥ 0,4 mm, SYS_POWER zu 59 %, V5_HOST zu 59 %, VBUS_SW zu 66 %, 3V3-Zuleitung und BOOST_SW nur stellenweise bzw. weiter schmal); H4 J20 = Molex 503480-30 (1,0 mm) statt Hirose FH12 (2,0 mm); H5 USB-HS-Paar ca. 72 mm gekoppelt auf F.Cu; H7 R1 DNP-Option; H8 BOOT-/EN-Taster SW2/SW3 auf der Rückseite.
> - **Wie die Änderungen entstanden (ehrlich):** Der Ausgangsstand (Rev. 3, Router Freerouting 1.9.0 plus Handnacharbeit, siehe „Neuaufbau“) wurde **nicht neu geroutet**, sondern mit einem eigenen Raster-A*-Router (`tools/rt.py`, `tools/rev3b_stage*.py`, Ablauf `tools/rev3b_make.sh`) gezielt geändert: betroffene Pads umgenetzt, Bahnen entfernt/neu gezogen, USB-Paar neu verlegt (dabei wurde ein 3V3-Abschnitt auf andere Lagen verlegt). Alles ist per DRC mit exakter Abstandsprüfung geprüft, aber **nicht** von Hand nachgeprüft; Vorschaubilder ansehen.
> - **Nicht geprüft / Risiken:** keine Hardware, keine Simulation. USB-HS: Paar gekoppelt, **Impedanz nicht bestätigt** (Aufbau- und Breitenwahl bei PCBWay, Abschnitt „USB-HS“); Analogführung (HPREFA/B, Ladungspumpe) vom Router; Footprint des **Molex 503480** (J21, J20): Nagelpads geschätzt, **Form und Y-Lage ungeprüft**; Pegel der neuen Reset-Sicherung (2N7002T Vgs(th) nur aus dem Gedächtnis); CPL-Drehungen nicht gegen PCBWay geprüft; LCSC-Nummern größtenteils nicht verifiziert (Spalte „Nummer geprueft“).
> - Die Gerber-ZIP heißt nur dann ohne „NICHT_BESTELLEN“, wenn `tools/export.py` einen sauberen DRC sieht (hier der Fall); das heißt **nicht**, dass sie bestellbar ist.

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
| `tools/` | Generatoren, Routing-Skripte (`rt.py`, `rev3b_*.py` für die Review-Korrekturen), `routing/` (Zwischenstände; `stand_vor_review_fixes.kicad_pcb` = Rev. 3 vor den Korrekturen) |
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

Quelle: Tangara-Hardware Rev. 5 (cool tech zone, CERN-OHL-S-2.0, <https://codeberg.org/cool-tech-zone/tangara-hw>), Netzliste in `quellen/tangara_netlist_rev5.json`. Anzahl = Bauteile der Stückliste (ohne Testpunkte und Bohrungen); gesamt 139 Bauteile in 72 Positionen.

| Block | Anzahl | Bauteile | Änderung |
|---|---|---|---|
| **Übernommen 1:1** (Werte, Netze, Footprints aus Tangara) | 22 | Ladeschaltung MCP73871 (U10) mit Q1, D4, U5, R1, R7, R34/R35/R37/R38/R39/R41, C37; USB-C-Buchse J6; ESD U3; SD-Versorgung U16 mit Pull-ups R9/R11/R12/R57/R61; 3V3-Kondensatoren; Bulk C29 | nur Netznamen vereinheitlicht |
| **Angepasst** | 17 | U4 (TLV75733P in WSON statt TLV75533 in SOT-23: 1 A, flach); J1 (SJ-43504 statt SJ-3506, Pads verschmälert); J4 (microSD Molex statt Vollformat-SD Hirose, 4-Bit-SDMMC statt SPI + Multiplexer); SW1 (Taster B3U-3000P statt Schiebeschalter, Power-Latch); R4 (10 k statt 100 k); R36/R43 (fest verdrahtet: PROG2 an VBUS_SW, SEL an GND, keine GPIO); R39 (2,7 k statt 1 k: ca. 370 mA); R57 (nicht bestückt), R1 (DNP-Option); SW2/SW3 (BOOT/EN-Taster); BT1 (Lötpads statt JST-PH-Stecker, Rückseite ist neben dem Akku nur 3,3 mm hoch); alle 0805-Kondensatoren als 0603 (Oberseite nur bis 1,0 mm Höhe) | Begründung je Teil im Feld „Beschreibung“ der Stückliste |
| **Neu: Cirrus-Beschaltung** | 19 | CS43131-Entkopplung nach Datenblatt Abb. 2-1, Quarz X1 mit Lastkondensatoren, Ferritperle FB1 | nach DS1155F2, Werte aus dem Bild gelesen |
| **Neu: Espressif-Beschaltung** | 8 | EN-RC (R100, C100), 22 µF/100 nF am Modul, BOOT-Pull-up, Serienplätze USB (R102, R103), Testpunkte | nach Datenblatt v0.5 (vorläufig) |
| **Neu: alles Übrige** | 72 | CS43131 (U17), Pegelwandler U30 (PCA9306) und U31-U33 (SN74AXC1T45), Reset-Transistor Q20 und Reset-Sicherung Q21/Q22/R250, 1,8-V-LDO U34, DNP-Quarz X2, USB-Host-Zweig (U12, U20, U21, L20, Q10, Q11, D10, R110...R119, C110...C114), MAX17048 (U22), Display-FPC (J20, Molex 5034803000), Klickrad-Stecker (J21), Power-Latch-Widerstände R200...R202 | USB-Host-Zweig **eigene Entwicklung, ungeprüft** |

Power-Latch: Der Taster SW1 zieht `KEY_LOCK` über R4 auf `SYS_POWER`; das schaltet `LDO_EN` (Tangara-Schaltung mit D4). Sobald der S31 läuft, setzt er `SYS_PWR_EN` (LP-GPIO) und hält den Regler an; zum Ausschalten löscht er `SYS_PWR_EN`. R202 (100 k) zieht `SYS_PWR_EN` nach Masse, wenn der S31 aus ist. `KEY_LOCK_MCU` liest den Taster (über R201).

## GPIO-Prüfung ESP32-S31-WROOM-1 und Belegung

Das WROOM-1 führt 52 GPIOs heraus (Datenblatt v0.5 Tab. 3-1: 40 Randpads und 20 kleine Pads im Feld unter dem Modul, davon 3 GND/3V3/EN). Alles, was verlangt war, ist vorhanden, **das größere WROOM-3 wird nicht gebraucht**:
Display-QSPI 6 (+ Reset, TE, Touch-INT), I²C 2, Klickrad-CHANGE, I²S 3 (als Slave), SDMMC 6 (dedizierte Pads IO35...IO40), USB-HS (DP/DM, Pads 55/54), Power-Latch 2, MCP73871-Status 3 (SEL und PROG2 sind fest verdrahtet, keine GPIO; IO14/IO15 frei), Klinkenerkennung (im DAC, Pin HP_DETECT, über DAC_INT), DAC RESET/INT. Verwendet: 28 freie GPIOs plus die festen Pads unten.
Die USB-HS-Pins DM/DP (Pads 54/55) und die meisten anderen GPIO liegen auf den kleinen Pads im Feld unter dem Modul (Raster 0,8 mm, nur 0,4 mm Pad-Breite); sie werden mit Durchkontaktierungen nach innen geführt. **Das ist eine Eigenheit des WROOM-1**, die bei Handlötung auffiele, bei PCBA unkritisch ist.

Vermieden: Strapping IO36 (intern auf dem Modul mit 10 k nach 3V3 hochgezogen; SD-DAT1 liegt dort, **R57 wird nicht bestückt**, weil `SD_VDD` beim Reset aus ist und R57 den Pegel sonst undefiniert gezogen hätte, Review B2), IO37 (JTAG-Auswahl, SD-DAT2 hat einen Pull-up an `SD_VDD`: unkritisch, solange keine eFuses gebrannt werden, N5), IO60/IO61 (Boot-Modus; IO61 = BOOT, Taster SW2), IO33/IO34 (USB-Serial/JTAG), TX0/RX0 (Testpunkte). Wecksignale (Power-Latch, Taster, Klickrad-CHANGE) liegen auf LP-GPIO IO0...IO7.

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
| CHG_STAT2 | IO16 | 50 | MCP73871 STAT2 |
| CHG_PG | IO17 | 51 | MCP73871 PG |
| TUSB_INT | IO18 | 52 | TUSB320 INT_N |
| LCD_RST | IO19 | 53 | Display Reset |
| DAC_RESET | IO20 | 15 | CS43131 RESET (Gate von Q20 mit Pull-up an 3V3: Pin offen/high = Reset, low = RESET freigegeben; Q21/Q22 halten RESET ohne 3V3 low) |
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
| BOOT | IO61 | 27 | Download-Modus: Taster SW2 (Rückseite) gedrückt halten, dabei EN antippen (SW3); alternativ TP15 gegen TP17 kurzschliessen |
| ESP_EN | EN | 3 | Reset: RC 10 k / 1 uF, Taster SW3 (Rückseite); alternativ TP14 gegen TP16 kurzschliessen |
| UART_TX0 / UART_RX0 | TX0 / RX0 | 37 / 36 | Testpunkte TP10 / TP11 |
| USBJ_DP / USBJ_DM | IO34 / IO33 | 14 / 13 | USB-Serial/JTAG, Testpunkte TP12 / TP13 |

Alle Zuordnungen sind **ungeprüft** gegen das endgültige Datenblatt (v0.5, vorläufig) und die IDF-6-Dokumentation: Welche Peripherie auf welche GPIOs gelegt werden darf (GPIO-Matrix, LP-IO, SDMMC-Slot 2), vor der Bestellung gegenprüfen.

## Audio: CS43131

- **Taktkonzept** (`docs/AUDIO.md` 5.3): Quarz X1 22,5792 MHz (NDK NX2016SA 22.5792M EXS00A-CS09116, laut Datenblatt Tab. 5-1 geeignet, Register 0x20052 = 0x02) direkt am DAC; der DAC ist I²S-Master (SCLK1, LRCK1 sind Ausgänge), der S31 ist Slave und braucht weder MCLK noch APLL. Die Lastkondensatoren C255/C256 (10 pF C0G) sind ein Startwert für CL = 8 pF und nach Datenblatt Abschnitt 5.3 am Aufbau abzustimmen.
- **Zweiter Quarz** X2 24,576 MHz (NDK NX2016SA 24.576M EXS00A-CS09117) als **DNP**-Option: statt R240/R241 dann R242/R243 (je 0 Ω) bestücken. Das ist die Umschaltung als Lötbrücke; ein 2:1-Taktumschalter-IC wurde nicht eingebaut (weniger Fläche, kein Jitter-Beitrag), auf dem ersten Aufbau werden beide Varianten gemessen.
- **Pegel**: Alle Digitalpins des DAC arbeiten mit VL = 1,8 V (zulässig 1,66...1,94 V, abs. max. 2,33 V). Deshalb: PCA9306 (U30) für I²C (**VREF2 und EN verbunden, gemeinsam über einen 200 k an 3V3, 100 pF nach GND**; ein direkt an 3V3 liegendes VREF2 hätte die 1,8-V-Schiene hochgezogen, Review B1; 4,7 k Pull-ups auf der 1,8-V-Seite), je ein SN74AXC1T45 (U31 BCLK, U32 LRCK: DAC → S31; U33 Daten: S31 → DAC) für I²S. INT liegt in der VP-Domäne (offener Drain, 10 k nach 3V3). RESET liegt ebenfalls in der VP-Domäne (Pegel relativ zu VP bis 5,25 V): Transistor Q20 mit 100 k an VP, Gate-Pull-up 100 k nach 3V3 hält den DAC im Reset, bis der S31 `DAC_RESET` auf low zieht. **Reset-Sicherung (Rev. 3b, Review H1):** Q22 (Gate an 3V3) hält `RST_G` nach GND, solange 3V3 da ist; fehlt 3V3 (Gerät aus, 3V3 fällt), zieht R250 `RST_G` nach VP, Q21 leitet und hält RESET **low**. So steigt RESET nicht ohne VL/VD/VA/VCP; vorher sperrte Q20 ohne 3V3 und RESET ging auf high. Firmware: RESET vor `SYS_PWR_EN = 0` setzen. Ungeprüft: Schwelle von Q22 (2N7002T Vgs(th) 1…2,5 V), RESET-VIH steht im Datenblatt nicht.
- **Versorgung**: VP = SYS_POWER (Batterie bzw. USB-seitig geführter Ausgang des MCP73871, 3,0...5,25 V), 0,1 µF + 4,7 µF. 1,8 V aus U34 (TLV75518P, aus 3V3), VA und VCP über Ferritperle FB1 (BLM15) getrennt von VL/VD. Reihenfolge laut Datenblatt: VP zuerst, dann 1,8 V, dann RESET lösen.
- **Entkopplung** (Fig. 2-1, Zuordnung der Werte aus dem Bild gelesen, vor Bestellung gegen das Datenblatt prüfen): VL, VD, VA je 100 nF; VA, VCP, −VA, VCP_FILT+/−, Flying-Caps je 2,2 µF; FILT+ und FILT− je 15 µF (0603); VP 100 nF + 4,7 µF. Die 15-µF-Typen haben keine verifizierte MPN (Typ nach Verfügbarkeit wählen).
- **Klinke** (SJ-43504: 1 Hülse, 2 Spitze, 3 Ring 1, 4 Ring 2, 5 Spitzenschalter, 6 Ringschalter): HPOUTA → Spitze, HPOUTB → Ring 1, HPREFA → Hülse (1), HPREFB → Ring 2 (4). Ein TRS-Stecker verbindet 1 und 4. HPREFA und HPREFB sind **eigene Netze**, die einzeln bis zur Buchse laufen und dort über je einen Net-Tie (NT1, NT2: Kupferbrücke im Footprint, kein Bauteil) mit der Massefläche (GND) verbunden sind (Datenblatt Abschnitt 8.3: Masse am Buchsenpin). Der Spitzenschalter (5) geht auf HP_DETECT; er ist im Ruhezustand mit der Spitze verbunden, deshalb muss im DAC `HPDETECT_INV` gesetzt werden. ESD: U3 auf HPOUTA/HPOUTB.
- **Erwartete Werte** (Datenblatt, nicht an dieser Platine gemessen): Dynamikumfang 125 dB an 32 Ω, THD+N −110 dB, 30,8 mW an 32 Ω, Ruheleistung ca. 29 mW (statt ca. 100...110 mW bei Tangara). Ausgangsimpedanz: im Datenblatt nicht gefunden, messen.
- **Plan B** (nur beschrieben, nicht verbaut): CS43198 (gleiches QFN-40, Line-Out) + OPA1622 (VSON-10) + TPS65133 mit 2 × 4,7 µH für ±5 V, wie bei Tangara. Würde auf der Rückseite rund 60...80 mm² mehr Fläche brauchen; Pin-Vergleich vor dem Layout nötig. Plan C: Tangara-Kette 1:1 (WM8523 + INA1620), dann wieder MCLK vom S31 oder Oszillator.
- **Bluetooth-Audio**: Der ESP32-Stack liefert für A2DP in der Regel nur SBC; LC3 (LE Audio) nur, wenn Kopfhörer und Firmware LE Audio unterstützen. Für hochauflösenden Klang bleibt der Kabelweg A oder B.
- **USB-Port wird geteilt**: Es gibt nur einen OTG-Port. Entweder ist der Player USB-Speichergerät (MSC) am PC, oder USB-Audio-Host (UAC2) am externen DAC. Beides gleichzeitig geht nicht; die Firmware muss die Rolle (TUSB320 INT/ID) umschalten. Flashen: über USB-Serial/JTAG (Testpunkte TP12/TP13) oder den HS-Port im Download-Modus (Taster **SW2 (BOOT) gedrückt halten und SW3 (EN) antippen**, Taster auf der Rückseite; alternativ TP15 gegen TP17 und TP14 gegen TP16 kurzschließen); beides ungeprüft.

## Display

2,06" AMOLED 410 × 502, CO5300, QSPI + Touch-I²C. Belegung des 30-poligen 0,5-mm-FPC aus dem Waveshare-Schaltplan ESP32-S3-Touch-AMOLED-2.06 V1.0 (Stecker J3), Stecker auf unserer Platine J20 = **Molex 5034803000** (503480-30, Easy-On BackFlip, 0,5 mm, Dual Contact, laut Digi-Key „Height Above Board 1,00 mm“; **ersetzt Rev. 3b den Hirose FH12-30S-0.5SH(55)**, der laut Digi-Key 2,00 mm hoch ist und in der Display-Zone mit ≥ 1,1 mm Luft nicht passte, Review H4), Oberseite, Signalpads (= Kabelmündung des Footprints) bei y = +1,35, Pin 1 links bei x = −7,25, Lage wie beim Hirose-Footprint der Rev. 3; die frühere Angabe „Mundloch nach unten“ passt nicht zu dieser Pad-Lage (die Pads liegen an der Mündung), die Richtung des Panel-FPC (das unter dem Panel zurückgefaltet wird) ist **zu prüfen**:

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

Nicht geprüft: ob der gekaufte Panel-FPC (Kontaktseite oben/unten – der Dual-Contact-Stecker nimmt beide –, Dicke 0,3 mm, Pin-Reihenfolge) zu diesem Stecker passt, Nagelpads des 30-poligen Molex-Footprints (aus der 6-poligen Familie hochgerechnet, **ungeprüft**), genaue Lage und Länge des FPC (Maßzeichnung des Moduls besorgen; DUENNBAU.md nennt 1,7 mm Zusatz an der FPC-Seite). Alternative laut DUENNBAU.md: FPC durch einen Schlitz auf die Rückseite.

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

**Footprint J21 gegen J1 des Klickrads (Review H6/K1) – im Klickrad-Ordner wurde nichts geändert, dort ist zu ändern:** Beide Platinen verwenden denselben Molex 503480-0600, aber verschiedene Landmuster. Hauptplatine J21: Signalpads 0,3 × 0,7 (Pin 1 bei x = +1,25, Mündung bei y_fp = −2,0), Nagelpads 0,8 × 1,0 bei x = ±2,045 (aus dem Zeichnungstext SD-503480-001: Montagefeld 0,79 / 0,5·(N−1) / 0,79, Nagelöffnung 1,0 × 0,3). Klickrad J1 (`klickrad/lib/Klickrad.pretty/Molex_503480-0600_1x06-1MP_P0.50mm_Horizontal`) ist ein Hirose-FH12-Nachbau: Signalpads 0,3 × 1,3 bei y_fp = −1,85, Nagelpads 1,8 × 2,2 bei x = ±3,15, y_fp = +1,4. Die Hirose-Nagelpads liegen außerhalb des Steckerkörpers (Molex-Körper x ±2,35) und treffen die Nägel nicht. **J21 wurde deshalb nicht an J1 angeglichen** (das würde den Fehler auf die Hauptplatine übertragen), sondern J1 muss an J21 angeglichen werden: Footprint von J1 durch das Landmuster von J21 ersetzen, **mit gespiegelter Pin-Reihenfolge** (J1 sitzt auf B.Cu bei 180°; Pin 1 muss von vorn bei x = +1,25 liegen). Dafür liegt `lib/Hauptplatine.pretty/Molex_503480-0600_Pin1links.kicad_mod` bereit (Pin 1 im Footprint links, sonst identisch). Folge in `klickrad.kicad_pcb` (Lage J1 (0; −10,8) bleibt): Signalpads rücken von y = −8,95 auf −8,8 (kürzer, 0,7 statt 1,3 mm), Nagelpads von (±3,15; −12,2) auf (±2,045; −12,0) und werden 0,8 × 1,0 statt 1,8 × 2,2 groß; die Nagelpad-Maße sind in beiden Platinen **Schätzwerte, nicht gesichert**: erst gegen die Molex-Zeichnung (Grafik/3D-Modell) prüfen, dann beide Platinen gemeinsam ändern. Bis dahin gelten **beide Footprints als ungeprüft**; Kabel Pin für Pin durchklingeln (A11).

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
| Display-FPC-Stecker J20 (Vorderseite) | (0; −0,65), Molex 5034803000 (Rev. 3b; vorher Hirose FH12 bei y = −0,5), Signalpads bei y = +1,35, Körper x ±8,35 (vorher ±10,6), y −2,4…+1,7, Nagelpads x ±8,04. **CAD anpassen** (Körper schmaler, Stecker 1,0 mm statt 2,0 mm hoch) | 1,0 mm |
| BOOT-/EN-Taster SW2/SW3 (Rückseite) | SW2 (−18,05; +16,0), SW3 (−18,05; +9,0), B3U-3000P hochkant (Pads untereinander), im linken Randstreifen neben dem Akkufach (x −20,5…−16,0). **CAD: Löcher in der Rückwand (Ø ≥ 2 mm Stößel) über beiden Tastern** | 1,2 mm |
| Display-Zone | x ±18,5, y −6,5…+40,5 (Annahme für das 2,06"-Modul); darunter nur Teile ≤ 1,0 mm (flache 0402/0603, QFN, SOT-523, J20), Luft darunter ≥ 1,1 mm | ≤ 1,0 mm |
| Befestigungslöcher (NPTH Ø 1,8, M1,6) | (−18,2, +46,2), (+18,2, −46,2), (−18,2, −46,2); je r 2,0 bauteilfrei | – |
| Vorderseite oberhalb des Displays | y > 41,0: auch höhere Teile erlaubt (Bauhöhe ≤ 1,5 mm) | – |

**Bauteilhöhen > 3 mm:** nur Klinke (gesamt 5,0 mm, hinten ca. 3,1 mm), USB-C (3,18 mm) und Modul (3,1 mm); nicht vermeidbar (SJ-3506-SMT hätte 6,0 mm). C29 (100 µF) 2,7 mm, alles andere ≤ 1,5 mm. **Passung Plattendicke:** Klinke und USB-C sind Mid-Mount-Teile mit Aussparung für eine bestimmte Plattendicke; der Vorgänger plante 0,8 mm, hier sind es 1,0 mm. Ob SJ-43504 und USB4510-03 1,0 mm vertragen, ist **nicht geprüft**: Das GCT-Datenblatt (USB4510-03-1-A, Rev. A) nennt „Recommended PCB Layout Thickness = 0,80 mm“ (Review H10), für die SJ-43504 nennt es keine Dicke. Rev. 3b ändert die Dicke **nicht** (offen, `KONZEPT.md`); 0,8 mm wäre eine Parameteränderung (`layout.BOARD_T`, Lagenaufbau, PCBWay-Option), ohne neues Routing, aber mit Folgen für CAD (Klinke, Stapel) und die Impedanz.

**Höhenstapel bei Gerätedicke bis 10 mm (neues Ziel):** Front 0,8 + Display 2,05 (Modul mit Touch; Panel allein 1,0) + Luft 1,1 + Platine 1,0 = 4,95 mm; Rückwand 1,0 → Rückzone **4,05 mm** (5,1 mm mit 1,0-mm-Panel). Die Klinke ragt nach STEP-Versatz ca. 3,1 mm hinter die Platine (passt in 4,05 mm), vorn 0,9 mm (sie sitzt unterhalb des Displays); der Akku hat im Mittelbereich höchstens ca. 3,7 mm (Zelle + 0,3 mm Luft) – **eine 4,0-mm-Zelle passt nur mit dem 1,0-mm-Panel (Rückzone 5,1 mm) oder bei 10,3 mm Gerätedicke**. Akkukapazität bei 32 × 38,5 × 3,7…4,0 mm: grob **ca. 450–550 mAh** (Schätzung aus typischer Energiedichte, keine Datenblattwerte) – **unter dem Ziel von 600 mAh**. Verbesserung nur durch längeren Akku: Das Modul (Antenne rechts) braucht die oberen 18,5 mm, der LRA-Ausschnitt die unteren; ein Wegfall des SD-Slots oder ein Modul über dem Display (Vorderseite, y > 41) gäbe ca. 10 mm mehr Zellenlänge.

Randabstände: Teile ≥ 0,7 mm von der Kante, außer Stecker mit Mündung im Randausschnitt.

## Pin-Tabelle

Siehe „GPIO-Prüfung und Belegung“ (Signale ↔ S31-GPIO ↔ Modulpad) und „Display“ (30-poliger FPC). Klickrad: J21-Pins 1 3V3, 2 GND, 3 SDA, 4 SCL, 5 CHANGE, 6 Reserve.

## Geprüft / nicht geprüft

**Geprüft (automatisch):** ERC 0 (`pruefung/erc.rpt`); DRC mit Abgleich gegen den Schaltplan 0 Verstöße, 0 unverbundene Pads (Bericht `pruefung/drc.rpt`); Schaltplan-Netzliste = Platine; Gerber/Bohrdaten mit `kicad-cli` erzeugt, Vorschau (`vorschau/`) neu erzeugt (angesehen); Datenblattwerte der Pinbelegungen wie unter „Festgelegte Chips“; die Review-Korrekturen am Schaltplan wurden gegen die Datenblattstellen des Reviews (PCA9306 §8.1.2/9.2.2.1, MCP73871 Kennwerte) nachvollzogen, **nicht** gemessen.

**Nicht geprüft:** Funktion der Schaltung (nie aufgebaut), neue Reset-Sicherung Q21/Q22/R250 (Schaltschwelle, Anlaufverhalten), Lader-Einstellung R39 = 2,7 k gegen das Datenblatt der echten Zelle, eigene USB-C-Rollen/Host-Schaltung (U12, U20, U21, Q10, Q11, D10), Power-Latch, Pegelwandler am CS43131, Quarzstart; **Antenne** im Gehäuse; Audioqualität; **USB-HS-Impedanz** (Paar gekoppelt, Breite/Abstand nur aus der IPC-Näherung, Aufbau von PCBWay nicht bestätigt); Rückleitung unter dem Analogblock; Footprint-Genauigkeit (Molex 503480 J20/J21 s. o., WROOM-1 selbst erzeugt, X2QFN nach TI-Beispiel, L20 Näherungs-Footprint); CPL-Drehungen/Polarität bei PCBWay (Vorschau prüfen, besonders Q21/Q22, SW2/SW3, J20); Höhenstapel/Kollisionen im CAD; Lieferbarkeit und Preise; LCSC-Nummern; die 15-µF-Typen ohne MPN.

**Menschlicher bzw. Opus-Review vor der Bestellung ist Pflicht** (Schaltplan gegen Datenblätter, Footprints gegen Zeichnungen, CPL-Vorschau bei PCBWay, Antennenfreiraum, Gehäusestapel).

## PCBWay-Bestellung Schritt für Schritt

1. pcbway.com → „PCB Assembly“ → „Quote Now“ (Leiterplatte plus Bestückung).
2. Gerber: `fertigung/hauptplatine_gerber_bohrdaten.zip`.
3. Leiterplatte: **4 Lagen**, **1,0 mm**, 41 × 97 mm, FR-4 Tg 150, Oberfläche **ENIG**, Kupfer außen 1 oz / **innen 1 oz** (PCBWay-Aufbau für 4 Lagen 1,0 mm, siehe unten), Lötstopp/Siebdruck nach Wunsch, kleinste Bahn/Abstand 0,127/0,127 mm (PCBWay-Standard 4 Lagen ca. 0,1 mm), kleinste Bohrung 0,2 mm (Vias 0,45/0,2), Kupfer–Kante 0,3 mm (Steckerpads 0,2 mm), **Impedanzkontrolle für USB-HS (USB_DP/USB_DN, 90 Ω differenziell, F.Cu über In1) anfragen**, Aufbau und Leiterbreite von PCBWay bestätigen lassen (Abschnitt „USB-HS“). Gefräste Innen-/Randausschnitte (LRA, Klinke, USB-C), NPTH getrennt in der Bohrdatei. **Mehrpreis 6 Lagen wäre nicht nötig; 0,8 mm wird nicht gebraucht.**
4. Bestückung beidseitig: 133 Bauteile in 67 Positionen (+ 1 Kabelzeile ohne Bestückung; CPL: 66 oben, 66 unten (132 Zeilen; TP7 steht nur in der Stückliste), DNP-Teile X2, R242, R243, **R1, R57** ausgenommen); Passermarken auf beiden Seiten.
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

## USB-HS: Paar, Lagenaufbau, Impedanz (Review H5)

- **Verlegung (Rev. 3b):** USB_DP/USB_DN laufen von R102/R103 (Oberseite, unter dem Modul) bis zum USB-C auf einer Strecke von **ca. 72,4 mm gekoppelt auf F.Cu** direkt über der durchgehenden GND-Fläche In1 (Breite 0,20 mm, Abstand Kante–Kante 0,15 mm, Mittellinienabstand 0,35 mm). Die Strecke ist aus **einer** Mittellinie (A*, nur 0/45/90°) per Parallelversatz in zwei Bahnen zerlegt, daher sind beide Leitungen auf dem Paar gleich lang (Differenz < 0,1 mm). Einzeln geroutet sind nur der Fan-out an R102/R103 (ca. 2 mm), die ESD-Abgriffe an U5 (kurze Stichleitungen) und die Verbindung zu den J6-Pads (B.Cu, mit je 1–2 Vias). Gesamtlängen: **USB_DP 91,0 mm, USB_DN 90,5 mm (Versatz 0,5 mm)**, 3 bzw. 2 Vias (vorher 86,5/87,7 mm, 5/3 Vias, nicht gekoppelt, über F.Cu/In2/B.Cu verteilt). Fremde F.Cu-Bahnen, die das Paar kreuzten (3V3-Abschnitte), wurden auf andere Lagen verlegt.
- **Lagenaufbau-Referenz** (PCBWay-Seite „Multi-layer laminated structure“, abgerufen 2026-10-05; **nicht** für diese Bestellung bestätigt): 4 Lagen, 1,0 mm, aussen 1 oz / innen 1 oz, Restkupfer innen > 60 %: Kupfer 0,035 mm, **Prepreg 7628 RC46 % 0,196 mm (nach dem Pressen 0,1855 mm), εr 4,74**, Kern 0,43 mm (εr 4,6), Endstärke 1,01 mm ±10 %. In `hauptplatine.kicad_pcb` hinterlegt (Platinen-Setup, Lagenaufbau). Andere PCBWay-Aufbauten für 1,0 mm: 2116 (0,1195 mm, εr 4,45). Der von der Aufgabe genannte JLCPCB-Aufbau JLC04161H-7628 ist ein **1,6-mm**-Aufbau mit demselben Prepreg-Typ (7628); für 1,0 mm bei JLCPCB gibt es eigene Aufbauten [nicht geprüft].
- **Impedanz (IPC-2141-Näherung, ±10 %, keine Feldrechnung):** Zdiff = 2·Z0·(1 − 0,48·e^(−0,96·s/h)), Z0 = 87/√(εr+1,41)·ln(5,98·h/(0,8·w+t)), t = 0,035 mm. Bei 7628 (h 0,1855, εr 4,74): **w 0,20 / s 0,15 → ca. 95 Ω**, w 0,22 / s 0,15 → ca. 91 Ω. Bei 2116 (h 0,1125, εr 4,45): w 0,20 / s 0,15 → ca. 77 Ω, w 0,15 / s 0,15 → ca. 91 Ω. Die gewählte Breite passt also zum 7628-Aufbau; bei einem dünneren Prepreg müsste die Leiterbreite sinken (und die Platine ist dann nachzuziehen).
- **Bestellung:** bei PCBWay „Impedance control“ für 4 Lagen 1,0 mm wählen, in den Bemerkungen angeben: „USB_DP/USB_DN auf F.Cu, differenziell 90 Ω ±10 %, Referenz In1 (GND), Prepreg/Breite nach Ihrer Rechnung anpassen“, **Aufbau und Breite schriftlich bestätigen lassen**, bevor die Gerber freigegeben werden. PCBWay ändert in der Regel nur die Leiterbreite im Rahmen ihrer Rechnung; die geänderte Breite dann in der Platine nachziehen oder die Abweichung bewusst akzeptieren.
- **Offen / ungeprüft:** Impedanz nicht gemessen; ESD-Abgriffe (Stichleitungen an U5 ca. 5 mm) und die Verbindungen am J6 sind nicht gekoppelt; U5 (PE1605C4A6) Kapazität nicht nachgelesen (M10); In1 ist unter dem Paar durchgehend, aber mit Via-Antipads durchsetzt; kein Test-Coupon bestellt.

## Beschaffung: Modul und CS43131 (Review B4/H9)

Nur Hinweise, **keine** Bestellung vorbereitet und keine Alternative bestellbar gemacht:

| Teil | Stand 2026-10-05 (aus Suchauszügen/`docs/MODUL-ALTERNATIVEN.md`, **ungeprüft** am Händler) | Hinweis |
|---|---|---|
| ESP32-S31-WROOM-1-N16R16V (U15) | Digi-Key: Lager 0, „3.250 erwartet 01-Mar-2027“, Werkslieferzeit 21 Wochen; Mouser: nicht bevorratet, 21 Wochen | vor dem PCBWay-Angebot Lieferbarkeit anfragen oder Module selbst beschaffen und beistellen; bis dahin Firmware auf dem S31-Function-CoreBoard-1 testen |
| Alternativ-SKUs mit gleichem WROOM-1-Landmuster (18,0 × 25,5 × 3,1 mm) | Datenblatt v0.5 Tab. 1-1: -N16R8V (16 MB/8 MB), -N8R16V (8 MB/16 MB), -N32R16V, -N16R32V | Händler/Lieferzeit je Variante nicht gefunden; Footprint/Pins gleich, aber Flash-/PSRAM-Größe der Firmware anpassen; die BOM-Zeile U15 nur nach Prüfung ändern |
| ESP32-S31-WROOM-3 | 22 × 30 × 3,5 mm | **nur falls Platz**: neuer Footprint, Pinbelegung ungeprüft, Antennen-Keepout und Gehäuse ändern sich; nicht in Rev. 3b umgesetzt |
| CS43131-CNZR (U17) | Mouser „Minimum 4000 / Reel“; Digi-Key Cut Tape ca. 18,5 USD; Hersteller ca. 20 Wochen | 2–3 Stück vorab bei Digi-Key sichern oder Plan B (CS43198 + OPA1622, siehe „Audio“) |
| Molex 5034803000 (J20) | Digi-Key (Artikel 15710893): Suchauszug „In stock“, Seite nennt Werkslieferzeit 21 Wochen und Verpackung Tape & Reel; Kategorie dort „Connector Assemblies“ | Bestand, Verpackung und Typ (Stecker, nicht Kabel) vor der Bestellung prüfen |

## Offene Risiken

1. **Beschaffung (B4/H9):** ESP32-S31-WROOM-1-N16R16V bei Digi-Key/Mouser nicht lieferbar (Stand 2026-10-05: Lager 0, 21 Wochen Werkslieferzeit), CS43131 bei Mouser ab 4000 Stück/Rolle, Digi-Key Cut Tape, Hersteller ca. 20 Wochen. Das ist **kein Layoutproblem** und mit Rev. 3b nicht gelöst. Hinweise: (a) vor dem PCBWay-Angebot Lieferbarkeit anfragen oder Module selbst beschaffen und beistellen; (b) Varianten mit demselben WROOM-1-Landmuster (18,0 × 25,5 × 3,1 mm, gleiche Pins) laut Datenblatt v0.5 Tab. 1-1: **-N16R8V** (16 MB Flash/8 MB PSRAM), **-N8R16V** (8 MB/16 MB), -N32R16V, -N16R32V (Zeilen unvollständig); Händler und Lieferzeit je Variante **ungeprüft**; Firmware muss auf die Speichergröße angepasst werden; (c) **WROOM-3** (22 × 30 × 3,5 mm) ist **nicht** umgesetzt: neuer Footprint, Pinbelegung ungeprüft, Platz/Keepout/Gehäuse ändern sich (`docs/MODUL-ALTERNATIVEN.md`); (d) S31-Function-CoreBoard-1 für die Firmware-Tests zuerst; (e) vom CS43131 2–3 Stück vorab sichern oder Plan B (CS43198 + OPA1622).
2. **Opus-Zweitreview der Rev.-3b-Änderungen** (Reset-Sicherung, Lader, PCA9306, USB-Paar, J20, Taster) steht aus; alles ist nur am Schaltplan/Layout nachvollzogen.
3. **H2 – VDDPST_SD:** I²S, `DAC_RESET`, `DAC_INT` und `SD_CD` liegen auf den SDIO-Pads (IO20…IO25); deren Versorgung (VDDPST_2 3,3 V oder 1,8 V) ist im Datenblatt v0.5 als „per Register wählbar“ ohne Reset-Default beschrieben. Vor der Bestellung im TRM/IDF nachlesen; sonst DAC-Leitungen auf andere GPIO legen (Platine ändert sich).
4. **H3-Rest:** Leistungsnetze nur teilweise verbreitert (Rev. 3: durchgehend 0,25 mm, BOOST_SW 0,127 mm). Länge ≥ 0,4 mm / Gesamtlänge: VBAT 115,7/116,5 mm, VBUS 52,0/55,1 mm, **SYS_POWER 86,8/147,9 mm** (davon 52,6 mm auf In2), VBUS_SW 13,4/20,2 mm, V5_HOST 21,9/37,1 mm, 3V3 nur 39/295 mm. Engpässe (Maximin-Breite zwischen den Hauptanschlüssen, `tools/widest.py`): SYS_POWER U10 → U4 0,4 mm, → U20 0,35 mm, → R4 0,27 mm, → U17.26 (DAC, wenig Strom) 0,25 mm; VBUS_SW 0,27 mm; V5_HOST 0,25–0,3 mm; 3V3-Zuleitung U4.1 → U15.2 (57,6 mm) 0,25 mm, zu J20/J21 0,13 mm; **BOOST_SW** (9,2 mm, davon 6,0 mm nur 0,13 mm) ist nicht verbreitert, weil L20 7,7 mm von U20 sitzt (kurze Schleife nur durch Umplatzieren, kein Platz gefunden); kein 47-µF-Bulk am Modul. Strombelastbarkeit nach IPC-2221 (ΔT 10 K, 1 oz): 0,25 mm außen ca. 0,9 A, innen ca. 0,44 A (die Rev.-3-Rechnung nahm 0,5 oz innen = 0,26 A an; laut PCBWay-Aufbau sind die Innenlagen 1 oz); Last ca. 0,5–0,7 A (Laden 0,37 A plus System, Host-Boost bis ca. 1 A aus der Zelle): **knapp, offen**
5. **USB-HS (H5):** Paar gekoppelt, Impedanz unbestätigt; Abgriff U5 und Anschluss J6 unten einzeln.
6. **Molex-Footprints (H6):** J21 und J20 (und Klickrad J1) nicht gegen die Zeichnungsgrafik geprüft.
7. **USB4510 bei 1,0 mm (H10):** Datenblatt nennt 0,80 mm; ungeklärt (Anfrage bei GCT oder Platine 0,8 mm).
8. **Antenne**: Modul innerhalb der Kante, Keepout eingehalten, aber Akku 3 mm unter dem Modul und rechter Display-Rahmen daneben: Reichweite ungemessen.
9. **Akkukapazität** unter dem Ziel (s. o.) und Rückzone nur 4,05 mm bei 10 mm Gerät; Zelle (NTC ja/nein, max. Ladestrom) ist festzulegen (R1, R39).
10. **Analog-Block** vom Router geführt; HPREFA/B einzeln zur Buchse, nicht von Hand optimiert.
11. **Eigene USB-C-Rollenlogik** (U12, U20, U21, Q10, Q11, D10) ungebaut; Q1 bleibt im Host-Betrieb ggf. leitend; Boost-Start bei leerem Akku (M1).
12. **ESP32-S31-WROOM-1**: Datenblatt v0.5 vorläufig; Footprint selbst erzeugt; USB und viele GPIO auf den kleinen Pads im Feld (0,8 mm Raster).
13. **3V3-Regler** TLV75733 (1 A, WSON) statt Tangaras TLV75533 (500 mA) bewusst beibehalten (WLAN-Spitzen).
14. **Display**: Panel-FPC (Kontaktseite, Reihenfolge, Mündungsrichtung) ungeprüft; Display-Zone mit Teilen unter dem Panel verlangt ≥ 1,1 mm Luft (CAD-Stand 0,25 mm muss angepasst werden).
15. **Taster SW1, SW2, SW3** auf der Rückseite: Stößel/Löcher in der Rückwand im CAD klären.
16. **Takt**: Quarz-Lastkondensatoren und Register 0x20052 abstimmen.

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

**Rev. 3b (Review-Korrekturen):** auf den fertigen Stand Rev. 3 (`tools/routing/stand_vor_review_fixes.kicad_pcb`) angewendet, **ohne** Freerouting: `tools/rev3b_make.sh` (ca. 30–40 min): `rev3b_stage1.py` (Netzänderungen B1/B3, Reset-Sicherung H1, J20-Tausch H4, DNP R1/R57), `rev3b_stage4.py` (USB-Paar H5), `rev3b_stage2.py` (Taster H8), `rev3b_stage3b.py` (Leistungsnetze segmentweise verbreitern, H3), `rev3b_stage3c.py` (schmale Abschnitte neu verlegen, Netze per `NETS=...`; eine erste Fassung hatte einen Restore-Fehler und wurde verworfen, die Netze wurden mit der korrigierten Fassung bearbeitet), danach `rev3b_finish.py` (Zonen füllen, `stackup.py` Lagenaufbau, `placement.json`), `export.py`, `gen_readme.py`. `rev3b_stage3.py` ist ein verworfener Versuch (alle In2-Stücke von SYS_POWER/VBAT/VBUS/3V3 auf Außenlagen holen: 6 Cluster nicht verbindbar) und nicht Teil des Ablaufs. Hilfsbibliotheken: `rt.py` (Raster-A*-Router mit beliebiger Breite, exakter Abstandsprüfung, Platzsuche, Cluster), `rtedit.py` (Pads umnetzen, Bauteile setzen), `widest.py` (Engpassbreite je Anschlusspaar). Schaltplan und Stückliste kommen weiter aus `tools/netlist.py`.

`tools/make.sh` ist veraltet (Freerouting 2.1.0, ein Lauf) und wird nicht mehr benutzt. Die Zwischenstände dieser Platine (SES, Platine vor dem Routing) liegen in `tools/routing/`; die Handschritte nach dem Router waren: `maze.py` für CHG_PROG3 (R35.1→U10.12), CHG_PROG1 (R39.1→U10.13), GND (J20.26→J20.24, J20.28→J20.26) und 3V3 (J20.29→J20.30, J20.25→J20.29, J20.23→J20.25, C131.1→J20.29 und → Bahnende bei (5,85; 4,48)), nach `rip.py` im Bereich um J20; `fixup.py`; `cleanup.py`; `polish.py`.

## Herkunft und Lizenz

- Dieses Design ist ein abgeleitetes Werk der **Tangara-Hardware** (cool tech zone, jacqueline, <https://cooltech.zone/tangara/>, Quelle <https://codeberg.org/cool-tech-zone/tangara-hw>), lizenziert unter **CERN-OHL-S-2.0**; es steht daher ebenfalls unter CERN-OHL-S-2.0 (Datei `LICENSE`). Die Namensnennung steht im Titelblatt des Schaltplans. Aus Tangara kommen Ladeschaltung, USB-C-Beschaltung, SD-Versorgung, Klinkenfootprint und ESD-Schutz.
- Audio-Schaltung des CS43131 nach dem Cirrus-Datenblatt DS1155F2; Klinken-Footprint von Same Sky/CUI Devices (über die Tangara-Bibliothek).
- Standardfootprints und -symbole: KiCad-Bibliotheken (CC-BY-SA 4.0 mit Ausnahme für Designs).
- Die Platzierungs- und Erzeugungsskripte in `tools/` sind neu geschrieben.
