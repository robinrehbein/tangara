# Hauptplatine Endgerät (Nano-Player), Rev. 2

> **STATUS: NICHT BESTELLBEREIT. Menschliche Prüfung und Entscheidung vor jeder Bestellung zwingend.**
> - Die Platine ist **nicht fertig geroutet** (Freerouting: 34 von 408 Verbindungen offen, Ergebnis nicht verwertbar). `fertigung/NICHT_BESTELLEN_ungeroutet_gerber.zip` ist nur eine Ansicht der Platzierung. DRC: 274 unverbundene Verbindungen, dazu Silkscreen-Hinweise, 62 Abstandsfehler und 21 Randabstandsfehler (Regel 0,5 mm in der Projektdatei statt 0,2 mm, ungeklärt). ERC: 0 Meldungen.
> - **Nach der Platzierung kamen zwei verbindliche Festlegungen**, die **nicht umgesetzt** sind: (1) Klickrad-Stecker Molex 503480-0600 statt Hirose FH12-6S (Platine hat noch FH12-6S auf der Rückseite, Footprint/LCSC-Nummer nicht verifiziert); (2) Standard-Ausschnitt für den LRA (ca. 14 × 10 mm um (0, −16), darunter keine Bauteile und kein Akku).
> - **Rechnerische Folge von (2)** (Schätzung, nicht per CAD geprüft): Von der Unterkante (y = −43) belegen Klinke 14 mm (bis −29), der LRA-Ausschnitt −21...−11. Ein Akku 34 × 50 beginnt dann bei etwa −10,5 und endet bei +39,5; das WROOM-1 (auch gedreht 18 mm) braucht danach +39,5...+57,5. Die Platine müsste ca. **37 × 100 mm** (Gehäuse ca. 104 mm) werden, oder der Akku auf etwa 30 × 35 mm (z. B. 302535, ca. 300 mAh) schrumpfen, wenn 86 mm bleiben. Das ist eine Entscheidung (Offene Punkte in `KONZEPT.md`), keine Rateaufgabe.
> - **Kabeltyp Klickrad:** Stecker Rückseite der Klickrad-Platine (zeigt nach unten) und Gegenstecker Vorderseite der Hauptplatine (zeigt nach oben), beide mit Kontakten unten: gerades Kabel berührt dann entgegengesetzte Kabelseiten, es braucht **Typ B** (Kontakte an den Enden auf gegenüberliegenden Seiten), Typ A nur bei Schlaufe um die Kante wie im jetzigen Entwurf. In die Stückliste aufnehmen, wenn so gebaut wird.
> - Der Abstand zwischen den Platinen ist nur 1,5 mm (5,3 bis 6,8), beide Stecker ca. 1,0 mm: sie dürfen sich in der Draufsicht nicht überdecken.

4-Lagen-Leiterplatte **37 × 86 × 0,8 mm** (Ecken r = 4), Bestückung beidseitig, bestellfertig für PCBWay (Leiterplatte plus PCBA). KiCad 9, Schaltplan und Platine werden aus Python-Skripten erzeugt (`tools/`).
Grundlage: `docs/DUENNBAU.md` (Dünnbau, Display), `docs/AUDIO.md` (Audio-Kette), `TEILE.md` (Chipliste, Ziel-Stack-up). Rev. 1 (WROOM-3, WM8523-Kette, 38 × 89 × 1,0) ist durch diese Revision ersetzt.

> **Status: nicht in Hardware getestet. Vor der Bestellung muss ein Mensch Schaltplan, Footprints, Bestückungsdrehungen und Gehäuseänderungen prüfen.**
> ERC und DRC laufen (Ergebnis unten), das heißt nur: keine formalen Regelverletzungen. Ob die Schaltung funktioniert, ob die Antenne funkt, ob der Klang gut ist und ob jeder Footprint zum echten Bauteil passt, ist **nicht geprüft**. Siehe „Geprüft / nicht geprüft“.

## Inhalt des Ordners

| Pfad | Inhalt |
|---|---|
| `hauptplatine.kicad_pro`, `.kicad_sch`, `.kicad_pcb` | KiCad-Projekt (Schaltplan A1, eine Seite) |
| `lib/` | eigene Symbole (`Hauptplatine.kicad_sym`) und Footprints (`Hauptplatine.pretty`: ESP32-S31-WROOM-1 selbst erzeugt, Klinke und USB-C aus Tangara, X2QFN, Akkupads, Befestigungsloch) |
| `fertigung/hauptplatine_gerber_bohrdaten.zip` | Gerber (4 Lagen, Maske, Paste, Silkscreen, Kontur) und Bohrdaten (Excellon, PTH/NPTH getrennt) |
| `fertigung/hauptplatine_BOM_PCBWay.csv` | Stückliste im PCBWay-Format (Designator, Menge, Hersteller, MPN, Beschreibung, Gehäuseform, LCSC/Digi-Key nur wo geprüft; DNP markiert) |
| `fertigung/hauptplatine_CPL_PCBWay.csv` | Bestückungsdatei Oberseite und Unterseite (Designator, Mid X/Y, Layer, Rotation), ohne DNP-Teile |
| `fertigung/hauptplatine_schaltplan.pdf` | Schaltplan als PDF |
| `vorschau/` | SVG/PNG der Ober- und Unterseite |
| `pruefung/erc.rpt`, `pruefung/drc.rpt` | Berichte von `kicad-cli` |
| `quellen/` | Quellen: Tangara-Netzliste (Rev. 5), Tangara-Footprints, Lizenztexte |
| `tools/` | Generatoren (siehe „Neuaufbau“) |
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
 AMOLED 2,06" (J20)   Pegelwandler U31-U33  microSD (J4)        Klickrad (J21, FFC 6)     |
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

Quelle: Tangara-Hardware Rev. 5 (cool tech zone, CERN-OHL-S-2.0, <https://codeberg.org/cool-tech-zone/tangara-hw>), Netzliste in `quellen/tangara_netlist_rev5.json`. Anzahl = Bauteile der Stückliste (ohne Testpunkte und Bohrungen); gesamt 133 Bauteile in 68 Positionen.

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
| SYS_PWR_EN | IO1 | 9 | Power-Latch: haelt die Versorgung (LP-GPIO) |
| KEY_LOCK_MCU | IO6 | 10 | Ein/Aus-Taster lesen (LP-GPIO, Weckquelle) |
| WHEEL_INT | IO7 | 11 | Klickrad CHANGE, Weckquelle (LP-GPIO) |
| LCD_SCK | IO8 | 42 | Display QSPI SCK |
| LCD_D3 | IO9 | 43 | Display QSPI D3 |
| I2S_BCLK | IO10 | 44 | I2S Bitclock vom DAC (S31 = Slave) ueber Pegelwandler U31 |
| I2S_DOUT | IO17 | 51 | I2S Daten S31 -> DAC ueber Pegelwandler U33 |
| LCD_TE | IO18 | 52 | Display Tearing-Effect |
| I2S_LRCK | IO19 | 53 | I2S Wordclock vom DAC ueber Pegelwandler U32 |
| TUSB_INT | IO20 | 15 | TUSB320 INT_N |
| TUSB_ID | IO21 | 16 | TUSB320 ID (low = wir sind Quelle) |
| DAC_RESET | IO22 | 17 | CS43131 RESET (1 = Betrieb, ueber Q20) |
| LCD_RST | IO23 | 18 | Display Reset |
| HOST_EN | IO24 | 19 | Host-VBUS an/aus (Boost + Schalter) |
| SCL | IO25 | 20 | I2C SCL |
| SDA | IO42 | 28 | I2C SDA (Display-Touch, Klickrad, MAX17048, TUSB320, CS43131 ueber PCA9306) |
| FG_ALRT | IO43 | 29 | MAX17048 ALRT |
| CHG_PG | IO44 | 30 | MCP73871 PG |
| CHG_STAT1 | IO45 | 31 | MCP73871 STAT1 |
| CHG_PROG2 | IO46 | 32 | MCP73871 PROG2 (USB-Strom), Pull-up 100 k |
| CHG_STAT2 | IO47 | 33 | MCP73871 STAT2 |
| DAC_INT | IO48 | 56 | CS43131 INT (aktiv low, 10 k Pull-up) |
| LCD_D0 | IO49 | 57 | Display QSPI D0 |
| LCD_D1 | IO50 | 58 | Display QSPI D1 |
| LCD_D2 | IO51 | 59 | Display QSPI D2 |
| TP_INT | IO52 | 60 | Touch-Interrupt Display |
| LCD_CS | IO53 | 61 | Display QSPI CS |
| SD_VDD_EN | IO54 | 34 | microSD Versorgung (TPS22948 ON) |
| CHG_SEL | IO55 | 35 | MCP73871 SEL (hoch = USB), Pull-up 10 k |
| SD_CD | IO56 | 38 | microSD Karte erkannt |

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

## Klickrad-Anschluss

Flacher **FFC-Stecker 6-polig, 0,5 mm, Flip-Lock, 1,0 mm hoch** (Hirose FH12-6S-0.5SH(55)): derselbe Typ wie auf dem Klickrad-Modul (`hardware/pcb/klickrad`, J1). Belegung 1 3V3, 2 GND, 3 SDA, 4 SCL, 5 CHANGE, 6 Reserve (offen). I²C-Pull-ups 2,2 k (R120/R121) und CHANGE-Pull-up 10 k (R136) auf der Hauptplatine. Der Stecker J21 sitzt auf der **Rückseite** bei (-2.1, -38.8) mit dem Mundloch zur Plattenunterkante: Das Flachkabel läuft vom Modulstecker nach unten, um die Kante und von hinten in J21 (Biegeradius mindestens 1 mm, Kabellänge ca. 40...50 mm). Die alte Ø-26-Aussparung entfällt (flacher LRA, `docs/DUENNBAU.md`), die drei Löcher Ø 2,2 für das Klickrad sind nicht mehr in der Hauptplatine (Modul wird nach DUENNBAU.md 8.2 geklebt oder mit M1,6 an der Front gehalten).

## Mechanik und Änderungen an Gehäuse/CAD

Koordinaten: Ursprung = Plattenmitte, x nach rechts, y nach oben, Blick auf die Display-Seite (Oberseite). **Plattenmaß 37,0 × 86,0 × 0,8 mm** (DUENNBAU: ca. 37 × 84; 2 mm länger, weil Modul, Klinke, USB-C und Akku sonst nicht auf die Rückseite passen). Gehäuse nach DUENNBAU 40 × 90 × 8,5: Innenmaß 37,6 × 87,6, die Platine liegt mit 0,3 mm Spiel seitlich und 0,8 mm an den Enden.

1. **Randausschnitt Klinke** (SJ-43504): Schlitz 6,8 mm breit, Achse bei x = −12,0, von der Unterkante (y = −43,0) bis y = −30,3, Entlastungsbohrungen Ø 1,3 für die Zapfen; Footprint auf der **Rückseite** (Pads auf B.Cu), Bauteilkörper 5,0 mm; er ragt laut DUENNBAU bei dieser Einbaulage 1,1 mm über die Platinenvorderseite. Sperrzone Oberseite: Schlitz + 1,0 mm; Sperrzone für die Rückseite des Klickrad-Moduls: x −16,5...−7,5, y −43...−31 (DUENNBAU 8.2). Die Einbaulage (Pad-Ebene ↔ Körper) ist ungeprüft.
2. **USB-C** (GCT USB4510, Pads und Laschen auf der Rückseite) bei x = +9,0, Mundloch an der Unterkante; die Kontur aus dem Tangara-Footprint (Randausschnitt 9,24 × 6,0 mm) ist übernommen. Öffnung in der Unterkante des Gehäuses bei x = +9,0.
3. **Akkufach auf der Rückseite** x −17,0...+17,0, y −29,4...+20,6 (34 × 50, Pouch 303450, 3,0 + 0,3 mm). Dort sind auf der Rückseite **keine** Bauteile. Anschluss: Lötpads BT1 (NTC, GND, BAT+) bei (-14.6, +22.5) am oberen Akkuende, Akkuleitungen mit Schutzschaltung.
4. **Modul ESP32-S31-WROOM-1** auf der Rückseite, Mitte (+6.0, +33.8), x −3,0...+15,0, y +21,0...+46,5. Die Antenne (obere 6 mm, kupferfrei auf allen Lagen) liegt bei y = +40,5...+46,5; die Platinenkante liegt bei y = +43,0, also ragt das Modul 3,5 mm über die Platine. **Das Gehäuse muss oben 3,0 mm länger werden** (Innenkante heute y = +43,8, nötig y ≥ +46,8): Gehäuselänge **90 → 93 mm**, nur oben verlängert. Akku, Metall und Display-Rahmen dürfen in der Antennenzone nicht liegen. Alternative: Platine 3,5 mm länger statt Überstand (dann ist das Gehäuse trotzdem länger).
5. **microSD** (Molex 104031-0811) auf der Rückseite bei (-12.1, +35.2), links neben dem Modul; die Karte wird von der linken Plattenkante (x = −18,5) eingeschoben, Öffnung in der linken Gehäusewand bei y = +31,5 (Mündung ragt ca. 0,8 mm über die Platinenkante).
6. **Ein/Aus-Taster SW1** (Omron B3U-3000P, **von oben zu drücken**, 1,2 mm hoch) auf der Rückseite bei (+12.8, -32.8). Er muss von der Gehäuserückseite oder über einen Stößel erreicht werden (CAD sah einen Seitentaster bei x = 8 vor). Ungeprüft; ein rechtwinkliger Seitentaster ist die Alternative.
7. **Display**: Oberseite nur flache Teile (≤ 1,0 mm Bauhöhe, das sind Passive, QFN/WSON, SOT-523, FPC-Stecker 1,0 mm). Die Displayunterseite muss mindestens **1,1 mm** über der Platinenoberseite liegen (DUENNBAU 5). Display-FPC-Stecker J20 bei (+0.0, +3.0) unter dem Display, 1,0 mm hoch (passt in die 1,1 mm). Klickrad-Kreis: Oberseite ist im Kreis r = 16,3 um (0, −25) bauteilfrei (Luft zwischen den Platinen nur 1,2 mm, LRA und Modulbauteile).
8. **Befestigung M1,6**: Die Platine selbst wird nach DUENNBAU 5 nicht verschraubt (Verschraubung in den Rahmen-Seitenwänden). Drei Befestigungslöcher Ø 1,8 (NPTH) sind als **Vorschlag** vorgesehen bei (+17,4, +41,0), (+17,4, +22,0), (+16,2, −41,0), je mit 2,1 mm bauteilfreiem Radius; Positionen mit dem CAD (Rahmen-Domen) abstimmen. Die alten Schraubdome (±15, ±40) mit M2 entfallen.
9. **Kupferfreie Plattenränder:** Teile halten ≥ 0,7 mm Abstand zur Kante; Stecker (Klinke, USB-C, microSD) ragen mit der Mündung bis zur Kante.

Stapel (DUENNBAU 5, Variante A): Rückwand 1,0, Luft 0,2, Rückzone 3,3, Platine 0,8, Vorderseite 1,1 (flache Teile + Klinke), Display 1,0 (Panel) bis 2,05 (Modul mit Touch, Luft schrumpft), Front 0,8 = 8,2 mm nominal, 8,5 mm mit Toleranz. Zusätzlich gilt hier: Bauteile auf der Rückseite höchstens 3,3 mm (Modul 3,1, USB-C 3,18, Klinke unter der Platine 3,1), SW1 1,2, microSD 1,9, Bulk-C29 2,7.

## Abgleich mit CAD v2 (params.py, Block E2_*)

Stand: Die Platine wurde mit den Werten aus DUENNBAU/Gesamtvorgabe gebaut (37 × 86). Die CAD-v2-Randbedingungen wurden danach geliefert und **nicht alle sind erfüllbar**. Hier der Vergleich, damit die Koordination die E2_*-Werte angleichen oder die Randbedingungen lockern kann.

| Nr. | Vorgabe CAD v2 | Stand Hauptplatine | Bewertung |
|---|---|---|---|
| 1 | Nur 0,25 mm Luft unter dem Display, also keine Bauteile auf der Vorderseite im Displaybereich (34,8 × 43,1, Mitte y = +20,43) | Flache Teile (≤ 1,0 mm) stehen auf der Vorderseite, auch unter dem Display, Luft dort 1,1 mm nötig | **nicht erfüllt.** Flächenbilanz: Vorderseite außerhalb Display und Klickrad-Kreis nur ca. 521 mm², Rückseite außerhalb Akkufach 1127 mm², zusammen 1648 mm²; Platzbedarf der Bauteile (Courtyards) flach 781 + hoch 1043 = 1824 mm². Bei 37 × 86 ist die Platine rechnerisch zu klein, wenn die Vorderseite unter dem Display leer bleiben muss. Lösungen: (a) Luft unter dem Display mindestens 1,1 mm (Panel ohne Deckglas 1,0 mm statt Modul 2,05 mm, Gesamtdicke bleibt 8,5), (b) Platine deutlich größer (ca. +6 mm Länge, Gehäuse über 96 mm), (c) kleinerer Akku. Empfehlung (a). |
| 2 | Rückzone ≤ 3,3 mm | Höchstes Rückseitenteil 3,18 mm (USB-C), WROOM-1 3,1 mm, Klinke 3,1 mm | erfüllt |
| 3 | Akku 34 × 50 neben der Klinke, WROOM-1 um 90° gedreht (25,5 × 18) | Modul **nicht gedreht** (18 × 25,5, Antenne zur Oberkante, ragt 3,5 mm über die Platine, Gehäuse +3 mm). Akkufach x −17...+17, y −29,4...+20,6 | abweichend; mit gedrehtem Modul läge die Antenne an der Seitenkante, das wäre ein Neu-Layout |
| 4 | Klinkenausschnitt = Gesamtkörper 9,1 × 14 + 0,45 je Seite; Klinke x = −12, USB-C x = +10 | Klinke x = −12 mit **Schlitz 6,8 mm** (Entlastungsbohrungen Ø 1,3); USB-C **x = +9,0** (Mundloch 9,24) | Klinke: Ausschnitt kleiner als im CAD, Körper liegt auf der Rückseite. USB-C: bitte E2_USB_X = 9,0 setzen |
| 5 | 5 Domkeepouts M1,6 bei (−16, 42), (16, 42), (−1,5, −42,5), (−17,8, 24,5), (17,8, −33) | 3 Löcher Ø 1,8 bei (+17,4, +41,0), (+17,4, +22,0), (+16,2, −41,0) | Konflikte der CAD-Positionen: (−16, 42) mit microSD J4 und Modul; (−17,8, 24,5) mit BT1 (−14,6, +22,5); (−1,5, −42,5) mit J21 (−2,1, −38,8) und Klinke; (17,8, −33) mit SW1 (12,8, −32,8) grenzwertig. Vorschlag: CAD übernimmt meine 3 Positionen |
| 6 | Klickrad-Mitte y = −22 (vorläufig), LRA-Aussparung optional | Kreis r = 16,3 um (0, −25) freigehalten, Aussparung für LRA **nicht** vorgesehen | Mitte y = −25 bitte eintragen. Ist der LRA höher als 1,0 mm, ist eine Aussparung ca. 13 × 7 mm mit Fräskontur nötig, **nicht** umgesetzt |
| 7 | FPC-Schlitz Platzhalter 14 × 1,2 bei (0, −3,2) | Kein Schlitz, flacher FFC-Stecker J20 (30 Pin) bei (+0.0, +3.0) | E2_PCB_SLOT bitte entfernen; Schlitz wäre Neu-Layout |
| 8 | Platine 37 × 84, Ecken R4, 4 Auflagepads 1 × 8 mm | **37 × 86**, Ecken R4,0; Auflagepads nicht vorgesehen | E2_PCB bitte auf 86; Plattenränder sind kupferfrei ≥ 0,2 mm |

Endgültige Werte der Hauptplatine für die Übernahme ins CAD (Mitte = Plattenmitte):
- E2_PCB = (37,0, 86,0, 4,0); Klinke x = −12,0, Schlitz 6,8 mm breit bis y = −30,3; USB-C x = +9,0
- Akkufach (−17,0, −29,4) bis (+17,0, +20,6), Pouch 34 × 50
- WROOM-1 bei (+6.0, +33.8), Antenne an der Oberkante, Überstand 3,5 mm (Gehäuse oben +3 mm)
- microSD J4 bei (-12.1, +35.2), SW1 bei (+12.8, -32.8), J21 bei (-2.1, -38.8), J20 bei (+0.0, +3.0), BT1 bei (-14.6, +22.5)
- Befestigungslöcher: (+17,4, +41,0), (+17,4, +22,0), (+16,2, −41,0); Klickrad-Mitte y = −25,0

Alle Aussagen sind Flächenrechnungen aus dem Platzierungsprogramm, **nicht** durch eine CAD-Kollisionsprüfung belegt. **Vor der Bestellung muss die Koordination entscheiden**, ob Punkt 1 gelockert wird.

## Geprüft / nicht geprüft

**Geprüft (automatisch, Berichte in `pruefung/`):**
- ERC (kicad-cli): keine. Das Schaltplansymbole der ICs sind automatisch erzeugt und haben nur passive Pins; die elektrische Typprüfung (Ausgang gegen Ausgang usw.) ist dort deshalb wirkungslos.
- DRC (kicad-cli, mit Abgleich gegen den Schaltplan): 62 x clearance, 21 x copper_edge_clearance, 1 x courtyards_overlap, 6 x extra_footprint, 4 x footprint_symbol_mismatch, 1 x lib_footprint_mismatch, 32 x net_conflict, 37 x nonmirrored_text_on_back_layer, 81 x silk_edge_clearance, 199 x silk_over_copper, 199 x silk_overlap, 6 x starved_thermal, 32 x text_height, 274 x unconnected_items. Regeln: Bahn/Abstand 0,127 mm, Via 0,45/0,2 mm, Randabstand 0,2 mm, Bohrung ≥ 0,2 mm.
- Routing: NICHT GEROUTET. Freerouting 2.1.0 erreichte nach 40 Durchgaengen nur 34 offene Verbindungen (von 408), 52 nach 27 Durchgaengen im zweiten Lauf; kein gueltiges Ergebnis (SES) wurde geschrieben, weil der Router nicht vorzeitig beendbar ist. Die Gerber-ZIP ist deshalb mit NICHT_BESTELLEN_ungeroutet_gerber.zip bezeichnet.
- Netzliste des Schaltplans = Netzliste der Platine (Parität).
- Datenblattwerte für Pinbelegungen von CS43131 (DS1155F2), ESP32-S31-WROOM-1 (v0.5), TUSB320LAI, TLV757P, TPS2553, SN74AXC1T45, PCA9306 und SJ-43504 wurden den Datenblättern entnommen (Text und Zeichnungen gelesen).

**Nicht geprüft:**
- Funktion der Schaltung (nie aufgebaut, keine Simulation). Besonders: eigene USB-C-Rollen-/Host-Schaltung (U12, U20, U21, Q10, Q11, D10), Power-Latch, Reset-Transistor Q20, die Pegelwandler an der CS43131-Schnittstelle, Takt (Quarzstart, Lastkondensatoren).
- Antenne: Modul mit Antenne über der Plattenkante, Keepout aus dem selbst erzeugten Footprint. Verhalten im Gehäuse, Abstand zum Akku (3,3 mm Pouch direkt daneben), Verstimmung: ungemessen.
- Audioqualität: Layout nach Platzierungsoptimierung und Autorouter, nicht nach Cirrus-Layoutregeln von Hand. Rauschen, Übersprechen, Ladungspumpenstörungen ungemessen. Masseführung: eine durchgehende Massefläche (In1), keine getrennte Analogmasse.
- USB-HS-Leitung: 90 Ω differenziell wurde nicht berechnet; Lagenaufbau (Prepreg-Dicke bei 0,8 mm Platine) bei PCBWay erfragen.
- **Footprint-Genauigkeit**: ESP32-S31-WROOM-1 selbst erzeugt (Maße aus den Zeichnungen des Datenblatts gelesen, nicht aus einer Herstellerdatei); X2QFN-12 für TUSB320 nach TI-Beispiel; FH12-Stecker, VSSOP-8, WSON-6, QFN-40 aus KiCad-Standardbibliotheken (Maße nicht einzeln gegen die Hersteller geprüft); Induktivität L20 mit Näherungs-Footprint; SJ-43504 aus der Tangara-Bibliothek, Pads für 0,2 mm Randabstand auf 1,35 mm verschmälert (Datenblatt: 1,75 mm); microSD-Molex nahe, nicht identisch geprüft.
- Bestückungsdrehungen: Die CPL-Datei nutzt die KiCad-Drehung; PCBWay braucht bei manchen Bauteilen (ICs, Stecker, Dioden) eine andere Nullstellung: Vorschau bei PCBWay prüfen.
- Höhenstapel im Gehäuse, Bauhöhen der Teile (aus Gedächtnis/Datenblattauszug), Lieferbarkeit, Preise.
- Die 15-µF-, 2,2-µF- und 10-µF-Kondensatortypen (MPN teils nicht verifiziert), Induktivität L20 (Sättigungsstrom ≥ 3 A prüfen).

**Menschliche Prüfung vor der Bestellung ist Pflicht.** Mindestens: Schaltplan gegen Datenblätter lesen, alle Footprints gegen Zeichnungen, CPL-Vorschau bei PCBWay, Gehäusestapel und Antennenfreiraum.

## PCBWay-Bestellung Schritt für Schritt

1. Auf pcbway.com „PCB Assembly“ → „Quote Now“ wählen (Leiterplatte plus Bestückung).
2. Gerber hochladen: `fertigung/hauptplatine_gerber_bohrdaten.zip`.
3. Leiterplatte: Lagen **4**, Dicke **0,8 mm**, Maße 37 × 86 mm, FR-4 (Tg 150), Lötstopplack nach Wunsch, Silkscreen weiß, Oberfläche **ENIG**, Kupfer außen 1 oz / innen 0,5 oz, kleinste Leiterbahn/Abstand 0,127/0,127 mm (liegt im Standard 4 Lagen von PCBWay von ca. 0,1 mm, Rückfrage ob 0,8-mm-Aufbau betroffen), kleinste Bohrung 0,2 mm (Vias 0,45/0,2), Impedanzkontrolle: für USB-HS 90 Ω differenziell anfragen (Lagenaufbau von PCBWay bestätigen lassen). Konturausschnitte (Klinke, USB-C) sind gefräst, NPTH-Löcher sind in der Bohrdatei getrennt.
4. Bestückung: **beidseitig** (Top und Bottom), 133 Bauteile in 68 Positionen (118 oben, 12 unten), Passermarken sind auf beiden Seiten vorhanden. Bleifreies Löten.
5. Stückliste `fertigung/hauptplatine_BOM_PCBWay.csv` und Bestückungsdatei `fertigung/hauptplatine_CPL_PCBWay.csv` hochladen. Teile ohne Lieferantennummer (S31-Modul, mehrere Tangara-Teile, CS43131) von PCBWay beschaffen lassen oder selbst liefern (Consigned). Nicht bestückt werden: X2, R242, R243 (DNP, in der Stückliste markiert). Das S31-Modul und die Steckerlaschen der USB-Buchse (THT) brauchen im Angebot Bestätigung; der Akku wird **nicht** bestückt, die Litzen werden von Hand an BT1 gelötet.
6. Vorschau der Bestückung bei PCBWay prüfen: Polarität/Drehung von U3, U4, U5, U10, U12, U15, U17, U20, U21, U22, U30...U34, D4, D10, Q1, Q10, Q11, Q20, X1 und aller Stecker. Fehler per Rückfrage melden, nicht stillschweigend bestätigen.
7. Gerber-Vorschau (Kontur mit den Randausschnitten, NPTH-Bohrungen) prüfen, dann bestellen. Für den ersten Aufbau 5 Platinen, davon 2 bestückt.

## Kosten (grobe Schätzung, nicht geprüft)

Alle Zahlen sind Schätzungen aus dem Gedächtnis (Stand 2026, keine Preisabfrage).

| Posten | Schätzung |
|---|---|
| Bauteile je Platine (S31-Modul ca. 12...18 €, CS43131 ca. 17 €, übrige ICs ca. 14 €, Stecker ca. 8 €, Passive/Quarze ca. 8 €) | ca. 60...65 € |
| Leiterplatte 4 Lagen, 37 × 86 mm, ENIG, 5 Stück | ca. 50...80 € |
| Bestückung beidseitig: Rüstkosten, Schablone, Bestückung, THT-Teile (USB-C-Laschen) | ca. 100...180 € für die Serie, unabhängig von der Stückzahl |
| Versand und Zoll | ca. 30...50 € |
| **Summe für 5 Platinen, davon 2 bestückt** | **ca. 380...520 €, also ca. 100...130 € je bestückter Platine** |

Das ist mehr als das im Projekt genannte Gesamtbudget von 100...150 €. Der CS43131 (Digi-Key: 251 Stück, 18,52 USD, Lieferzeit des Herstellers 20 Wochen, Stand `docs/AUDIO.md`) ist Preis- und Lieferrisiko.

## Offene Risiken

1. **Rückseite ist voll.** Akku 34 × 50 mm, Modul, Klinke, USB-C, microSD und Taster teilen sich eine 37 × 86-mm-Rückseite; deshalb ist die Platine 2 mm länger als in DUENNBAU.md. Wird der kleinere Akku 303040 (30 × 40) gewählt, gewinnt man 10 mm Länge zurück.
2. **Antennenüberstand** (3,5 mm) macht das Gehäuse 3,0 mm länger; Akku-Abstand zur Antenne ungemessen.
3. **Autorouter-Ergebnis.** Das Routing stammt von Freerouting, nicht von Hand: Rückleitungsströme, Ladungspumpe des CS43131 nahe am Analogausgang und die Masseführung sind nicht optimiert. NICHT GEROUTET. Freerouting 2.1.0 erreichte nach 40 Durchgaengen nur 34 offene Verbindungen (von 408), 52 nach 27 Durchgaengen im zweiten Lauf; kein gueltiges Ergebnis (SES) wurde geschrieben, weil der Router nicht vorzeitig beendbar ist. Die Gerber-ZIP ist deshalb mit NICHT_BESTELLEN_ungeroutet_gerber.zip bezeichnet.
4. **HPREF-Führung**: Die Net-Ties NT1/NT2 und die getrennte Leitungsführung der beiden Referenzleitungen sind im Layout nur vom Autorouter erzeugt; ob HPREFA/B wirklich kurz und getrennt am Buchsenpin ankommen, ist im Review zu prüfen.
5. **Eigene USB-C-Rollenlogik** (U12, U20, U21, Q10, Q11, D10): nie gebaut. Mögliche Fehler: Eingangsschalter Q1 bleibt im Host-Betrieb leitend und speist 5 V zurück; Boost startet bei leerem Akku nicht; TUSB320LAI-Konfiguration (PORT offen = DRP, I²C 0x47) braucht Firmware.
6. **ESP32-S31-WROOM-1**: Datenblatt v0.5 vorläufig, Verfügbarkeit (Mouser/Digi-Key) nicht bestätigt, Footprint selbst erzeugt, USB und viele GPIO auf den kleinen Pads im Feld (Raster 0,8 mm).
7. **PCBWay-Prozess**: Sehr kleine Strukturen (QFN-40 mit 0,4 mm Raster, X2QFN-12, FPC 0,5 mm, Bahn 0,127 mm, Via 0,45/0,2) und Randausschnitte mit Kupfer 0,2 mm von der Kante; bei Rückfrage 0,15 mm Bahn und Via 0,6/0,3 verlangen und neu routen.
8. **Display**: Panel-FPC (Kontaktseite, Pin-Reihenfolge, Dicke) und die Lage des FPC ungeprüft; 2,06"-Panel als nacktes Modul schwer beschaffbar (widersprüchliches Listing).
9. **Taster SW1** ist von oben zu drücken (Rückseite), Stößelkonstruktion offen.
10. **Takt**: Quarz-Lastkondensatoren und Register 0x20052 müssen am Aufbau abgestimmt werden; Verhalten der PLL für die 48-kHz-Familie ungemessen.

## Neuaufbau

Voraussetzungen: KiCad 9 (Python `pcbnew`, `kicad-cli`), Python-Pakete `shapely`, `numpy`, `scipy`; Java und `freerouting-2.1.0.jar` für das Routing; `rsvg-convert` für PNG.

```
tools/make.sh                 # nutzt gespeicherte Platzierung und GPIO-Zuordnung
PLACE=1 tools/make.sh         # Platzierung (Simulated Annealing, ca. 10 min) und GPIO-Zuordnung neu
SKIPROUTE=1 tools/make.sh     # vorhandenes Routing (tools/routed_freerouting.kicad_pcb) verwenden
```

Reihenfolge: `netlist.py` (alle Bauteile und Netze, einzige Quelle) → `make_lib.py` (Footprints) → `place_sa.py` (Platzierung, `placement.json`) → `gpio_assign.py` (`gpio_map.json`) → `build_pcb.py` (Platine) → Freerouting → `finish.py` (Zonen, Passermarken, Beschriftung) → `gen_sch.py` (Schaltplan) → `export.py` (Gerber, Stückliste, Bestückung, Berichte) → `gen_readme.py`.

## Herkunft und Lizenz

- Dieses Design ist ein abgeleitetes Werk der **Tangara-Hardware** (cool tech zone, jacqueline, <https://cooltech.zone/tangara/>, Quelle <https://codeberg.org/cool-tech-zone/tangara-hw>), lizenziert unter **CERN-OHL-S-2.0**; es steht daher ebenfalls unter CERN-OHL-S-2.0 (Datei `LICENSE`). Die Namensnennung steht im Titelblatt des Schaltplans. Aus Tangara kommen Ladeschaltung, USB-C-Beschaltung, SD-Versorgung, Klinkenfootprint und ESD-Schutz.
- Audio-Schaltung des CS43131 nach dem Cirrus-Datenblatt DS1155F2; Klinken-Footprint von Same Sky/CUI Devices (über die Tangara-Bibliothek).
- Standardfootprints und -symbole: KiCad-Bibliotheken (CC-BY-SA 4.0 mit Ausnahme für Designs).
- Die Platzierungs- und Erzeugungsskripte in `tools/` sind neu geschrieben.
