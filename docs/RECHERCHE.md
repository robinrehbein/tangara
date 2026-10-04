# Recherche: Waveshare ESP32-S3-Touch-AMOLED-1.8 und Teile-Annahmen

Stand: 2026-10-04. Quellen am Ende. Alles, was nicht aus Waveshare-Wiki, Schaltplan-PDF oder Datenblatt stammt, ist als **ungeprüft** markiert.

## 1. Waveshare ESP32-S3-Touch-AMOLED-1.8

| Punkt | Ergebnis | Status |
|---|---|---|
| Außenmaße | Maßzeichnung im Wiki: **37,6 × 45,2 mm, Tiefe 15,0 mm**, Eckenradius 4 × R1,8, Rückseite 27,6 × 27,6 mm (Schraubenraster). Die Zeichnung zeigt das Board **im schwarzen Gehäuse mit Glas**. Die reine Platine ist kleiner. | Maße geprüft (Zeichnung). **Maße der nackten Platine und Dicke ohne Gehäuse nicht verifiziert**: STEP-Datei (Quelle 4) mit CAD ausmessen. |
| Sichtbare Display-Fläche | 28,7 × 34,94 mm (Diagonale 1,78") | geprüft (Zeichnung) |
| Display | **V1: SH8601, V2: CO5300**, beide QSPI, 368 × 448, 16,7 Mio. Farben. Waveshare liefert **ab 30.05.2026 nur noch V2**. Erkennung über Aufkleber auf der Rückseite. | geprüft (Wiki). Heute (Okt 2026) ist V2 wahrscheinlich. |
| Touch | V1: FT3168 (I²C, 0x38 laut Community-Konfigurationen), V2: CST820 | Typen geprüft; Adressen **ungeprüft** |
| PMU | AXP2101 (Laden, Power-Path, mehrere Spannungen), PWR-Taste | geprüft |
| Weitere Chips | ESP32-S3R8 (8 MB PSRAM), 16 MB NOR-Flash, QMI8658 (IMU), PCF85063 (RTC), ES8311 (Codec), **IO-Expander (TCA9554, im Schaltplan als EXIO0–7)** | geprüft; im TEILE.md fehlte der IO-Expander |
| Audio | ES8311 -> **Class-D-Verstärker NS4150B -> Onboard-Lautsprecher** (Schaltplan: Netze PA_OUTL+/-, PA_CTRL). Analoges Mikrofon onboard. **Kein Kopfhörerausgang, keine Klinkenbuchse.** Kopfhörer erst ab Phase 2 (externer I²S-DAC) | geprüft (Wiki und Schaltplan) |
| SD | TF-Slot onboard. Wiki/Schaltplan: Signale MOSI, MISO, SCK, SDCS (SPI-Modus, CS vermutlich über IO-Expander). Das GitHub-README nennt „SDMMC“. | Slot geprüft; **Busmodus widersprüchlich**, im Schaltplan nachsehen bevor Firmware das festlegt |
| Akkustecker | **MX1.25, 2-polig**, 3,7 V, Laden und Entladen über AXP2101. Empfohlener Akku laut Wiki: 3,85 × 24 × 28 mm, 400 mAh. Zusätzliche Pads für RTC-Stützbatterie. | geprüft. **Polung am Board (+/−) vor dem Anstecken prüfen**, bei Zukaufakkus oft vertauscht. |
| USB-C | ESP32-S3 nativ (Flashen, Log). Lage: an einer Schmalseite (in der Pin-Zeichnung Rückansicht unten, mittig); gegenüber liegen die Lötpads oben links. | geprüft (Zeichnung) |
| Tasten | BOOT und PWR als Seitentasten (Wiki); in der Pin-Zeichnung beidseits neben USB-C, in der Maßzeichnung am Gehäuserand sichtbar. Genaue Lage am Board prüfen. | geprüft (Wiki) |
| Hardware-Version | Maßzeichnung zeigt noch Beschriftung SH8601/FT3168 | V2-Maße evtl. abweichend, ungeprüft |

### Herausgeführte Pins (Lötpads, Raster 1,27 mm)

Eine Reihe auf der Rückseite an einer Kante, in der Pin-Zeichnung links oben (Reihenfolge von oben nach unten). Waveshare: „7 GPIO, 1 I²C, 1 UART, 1 USB-Pad“.

| Pad | Signal |
|---|---|
| 1 | VBUS (5 V von USB) |
| 2 | GND |
| 3 | 3V3 |
| 4 | GND |
| 5 | TXD (UART0) |
| 6 | RXD (UART0) |
| 7 | **SCL = GPIO14** |
| 8 | **SDA = GPIO15** |
| 9 | GPIO17 |
| 10 | GPIO18 |
| 11–15 | GPIO38, 39, 40, 41, 42 |
| separat | USB_N = GPIO19, USB_P = GPIO20 |

Hinweis: Die Pinbeschriftung der Zeichnung ist ein Bild und teilweise klein; Reihenfolge und Lage der Pads vor dem Löten am echten Board prüfen. GPIO17 und GPIO18 sind im Schaltplan als reine Testpunkte (TP11, TP12) ohne weitere Last geführt. Für GPIO38–42 war im Schaltplan keine Fremdbelegung zu erkennen (nicht vollständig durchgesehen).

### Anschluss des Klickrad-Moduls

Das Modul liegt am **bereits vorhandenen, geteilten I²C-Bus** (GPIO14 = SCL, GPIO15 = SDA). Auf dem Board sitzen Pull-ups 2,2 kΩ (R29/R30 im Schaltplan an ESP32_SDA/SCL, Zuordnung zu 3V3 nicht eigens geprüft). **Auf dem Klickrad-Modul keine zusätzlichen Pull-ups bestücken.** Bus ist 3,3 V.

| JST-SH-Pin | Signal | Waveshare-Pad |
|---|---|---|
| 1 | 3V3 | 3V3 (Pad 3) |
| 2 | GND | GND (Pad 2 oder 4) |
| 3 | SDA | GPIO15 (Pad 8) |
| 4 | SCL | GPIO14 (Pad 7) |
| 5 | INT | **GPIO17** (Vorschlag) |
| 6 | BTN | **GPIO18** (Vorschlag) |

- INT ist open drain: interner Pull-up des ESP32 reicht für den Anfang, sonst 10 kΩ nach 3V3 auf der Hauptplatinenseite. BTN ebenso (Pull-up MCU-Seite, wie in TEILE.md).
- Strom: LRA über DRV2605L zieht kurz bis ca. 100 mA (Richtwert, vom LRA abhängig). Ob die 3V3-Schiene des AXP2101-Boards das zusätzlich zu Display, WLAN und Lautsprecher verträgt, ist **ungeprüft**. Kondensator (10 µF) nahe DRV2605L auf dem Modul vorsehen. Alternativ DRV2605L aus VBUS/Akku speisen (Betriebsbereich 2–5,2 V laut Datenblatt) – dann Logikpegel prüfen.
- Kabel: JST-SH-Buchse am Modul, am Waveshare-Ende **einseitig offene Kabel** direkt an die 1,27-mm-Pads löten.

## 2. I²C-Adressen und Kollision

| Gerät | Adresse (7 Bit) | Quelle |
|---|---|---|
| ES8311 | 0x18 | Waveshare-Konfigurationen (Schwesterboard 1.75, ESPHome-Beispiel zum 1.75/1.8) |
| IO-Expander TCA9554 | 0x20 (A2:A0 = 000) | Schwesterboard 1.75 – für das 1.8 **ungeprüft** |
| FT3168 / FT5x06-kompatibel | 0x38 | Community-Konfiguration (ESPHome-Forum) |
| CST820 (V2) | 0x15 (üblich, ungeprüft) | Gedächtnis, nicht belegt |
| AXP2101 | 0x34 | Waveshare 1.75 Hardware Reference |
| PCF85063 | 0x51 | dito |
| QMI8658 | 0x6B (Schaltplan-abhängig, auch 0x6A möglich) | dito |
| **MPR121 (ADDR = VDD)** | **0x5B** | NXP-Datenblatt: GND 0x5A, VDD 0x5B, SDA 0x5C, SCL 0x5D |
| **DRV2605L** | **0x5A** fest | TI-Datenblatt |

Ergebnis: **keine Kollision** von 0x5A und 0x5B mit den Bauteilen auf dem Board (Belegung dort 0x15/0x18/0x20/0x34/0x38/0x51/0x6B). Die Adressen der Waveshare-Bauteile stammen teils vom Schwesterboard und sind für genau dieses Board nicht verifiziert; mit dem Beispiel `08_i2c_tools` (Waveshare-Repo) am echten Board scannen. **Achtung:** MPR121 darf nicht auf ADDR = GND (0x5A) gelegt werden, das kollidiert mit dem DRV2605L. Die Festlegung 0x5B in TEILE.md ist richtig.

## 3. Prüfung der „(prüfen)“-Angaben in TEILE.md

| Angabe | Ergebnis |
|---|---|
| 1,8" AMOLED 368 × 448, QSPI | bestätigt |
| SH8601 | **nur V1**, aktuelle Lieferung ist V2 mit **CO5300** |
| Touch | V1 FT3168, **V2 CST820** (nicht im TEILE.md) |
| PMU AXP2101 | bestätigt |
| Audio-Codec ES8311 | bestätigt, aber nur **Lautsprecher** (NS4150B), kein Kopfhörerausgang |
| IMU, RTC, SD | QMI8658, PCF85063, TF-Slot bestätigt |
| Akkustecker MX1.25 | bestätigt (2-polig), Polung am Board prüfen |
| Außenmaße | 37,6 × 45,2 × 15,0 mm laut Zeichnung (mit Gehäuse); nackte Platine offen |
| Herausgeführte Pins | 15 Pads + USB-Pads, siehe oben |

## 4. Abweichungen und offene Punkte

1. Display/Touch-Treiber hängen von der Hardware-Version ab (V1 SH8601/FT3168, V2 CO5300/CST820). Firmware muss beide unterstützen oder die Version beim Kauf prüfen. Waveshare-Komponente `waveshare/esp32_s3_touch_amoled_1_8` deckt beide ab (laut README).
2. Kein Kopfhörerausgang: Kopfhörertest erst mit externem I²S-DAC (Phase 2). Für Phase 1 (Haptik, UI) ohne Folgen.
3. Maße der Platine ohne Gehäuse und die Höhe der höchsten Bauteile: STEP-Datei ausmessen (nicht erledigt, Parsen der Datei lieferte keine verlässlichen Werte).
4. SD-Busmodus (SPI laut Schaltplan, SDMMC laut README) klären.
5. 3V3-Strombudget bei Klickrad-Betrieb messen.
6. Adressen CST820 und TCA9554 am echten Board scannen.
7. LRA-Daten: siehe `EINKAUFSLISTE.md`; Resonanzfrequenzen gelten für Hersteller-Beispiele, die AliExpress-Teile sind meist unspezifiziert und müssen per DRV2605L-Autokalibrierung vermessen werden.

## Quellen

1. Waveshare Wiki: https://docs.waveshare.com/ESP32-S3-Touch-AMOLED-1.8 (Features, Onboard-Ressourcen, Pinout-Bild, Maßzeichnung, Versionshinweis V1/V2)
2. Waveshare Ressourcen: https://docs.waveshare.com/ESP32-S3-Touch-AMOLED-1.8/Resources-And-Documents
3. Schaltplan (PDF): https://files.waveshare.com/wiki/ESP32-S3-Touch-AMOLED-1.8/ESP32-S3-Touch-AMOLED-1.8.pdf (NS4150B, EXIO, GPIO17/18-Testpunkte, 2,2k-Pull-ups, SD-Signale)
4. 3D-Datei: https://files.waveshare.com/wiki/ESP32-S3-Touch-AMOLED-1.8/ESP32-S3-Touch-AMOLED-1.8-3D.zip
5. Maßzeichnung: https://docs.waveshare.com/assets/images/ESP32-S3-Touch-AMOLED-1.8-size-e91f0804f11a3242736e5cb781229629.webp
6. Pin-Zeichnung: https://docs.waveshare.com/assets/images/ESP32-S3-Touch-AMOLED-1.8-details-15-29e01308259f0cbe05e3a0f866adcb5e.webp
7. Waveshare GitHub: https://github.com/waveshareteam/ESP32-S3-Touch-AMOLED-1.8 (README, Beispiele inkl. `08_i2c_tools`)
8. Hardware Reference Schwesterboard 1.75 (Adressen): https://github.com/waveshareteam/ESP32-S3-Touch-AMOLED-1.75/blob/main/HARDWARE_REFERENCE.md
9. ESPHome-Forum, Konfiguration mit I²C GPIO14/15, FT5x06 0x38, ES8311 0x18: https://community.home-assistant.io/t/esp32-s3-1-8inch-amoled-touch/956270
10. MPR121-Adressen (0x5A–0x5D): NXP-Datenblatt MPR121; Diskussion https://forum.arduino.cc/t/mpr121-works-only-on-0x5a-address/564861
11. DRV2605L: TI-Datenblatt (Adresse 0x5A fest); https://forums.adafruit.com/viewtopic.php?t=116210
12. LRA-Beispieldaten: https://www.nfpmotor.com/products-linear-resonant-actuators-lras.html
