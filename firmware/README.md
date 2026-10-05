# Firmware Phase 1 (ESP-IDF)

Prototyp-Firmware für das **Waveshare ESP32-S3-Touch-AMOLED-1.8** mit dem **Klickrad-Modul** (Tangara-Technik: **AT42QT2120** auf I²C 0x1C im Wheel-Modus + DRV2605L; Klickrad v1 mit MPR121 bleibt per Kconfig wählbar; Schnittstelle siehe `../TEILE.md`).

**Lizenz: GPL-3.0-only** (`LICENSE`), weil Code aus der Tangara-Firmware (cool tech zone, GPL-3.0) übernommen wurde. Übernommen bzw. portiert (mit SPDX-/Copyright-Header der Originalautoren): `components/at42qt2120` (aus `src/drivers/touchwheel.cpp`), `components/drv2605l` (Init-Sequenz, LRA/ERM-Einstellungen, Effektliste aus `src/drivers/haptics.cpp` und `haptics.hpp`). Alle anderen Dateien tragen `Copyright 2026 Nano-Player-Projekt` und dieselbe Lizenz. Die Portierungsanalyse der gesamten Tangara-Firmware steht in `../docs/FIRMWARE-PORTIERUNG.md`. Ziel: Scrollen in einer Liste mit 1.000 Einträgen anfühlen und die Latenz Eingabe -> Haptik messen. Bedienlogik und Haptik folgen der Emulator-App (`ScrollWheel.kt`, `PlayerModel.kt`, `Haptics.kt`).

**Stand: kompiliert, aber nicht auf Hardware getestet.** Details siehe unten.

## Aufbau

```
firmware/
  CMakeLists.txt, sdkconfig.defaults, .gitignore
  main/
    board_config.h     zentrale Pins/Adressen, jeweils mit Status [geprüft] / [Vorschlag] / [prüfen]
    Kconfig.projbuild  menuconfig "Nano-Player" (Raster, Rate-Limit, Effekt-IDs, LRA-Daten, Debug)
    board.c            gemeinsamer I2C-Bus, IO-Expander TCA9554 (Display-/Touch-Reset), I2C-Scan
    display.c          esp_lcd QSPI (CO5300 oder SH8601) + LVGL 9 über esp_lvgl_port, 368x448 Hochformat
    input.c            Eingabe-Task (Prio 10, Core 1): QT2120-Position bzw. MPR121-Segmente lesen, Mitteltaste, Haptik direkt auslösen
    haptics.c          Tick / Klick / Anschlag, Rate-Limit, Latenz-Messpunkt
    model.c            Bedienlogik (Seitenstapel, Auswahl, Anschlag), wie PlayerModel.kt, ohne LVGL
    ui.c               Statusleiste, Liste (Auswahl orange #FF8A3D), "Wird gespielt"/Info
  components/
    at42qt2120/        Treiber (Tangara-Port): Init, Wheel-Position 0..255, Mitteltaste (Taste 3), Kalibrierung, Low-Power
    mpr121/            Treiber Klickrad v1: Init, Touch-Status, gefilterte Werte, Baselines (nur bei Kconfig "MPR121")
    drv2605l/          Treiber (Tangara-Abgleich): Init LRA/ERM, Auto-Kalibrierung, Effekt/Sequenz, Standby, Effektliste
    clickwheel/        reine Logik (Winkel, Raster, Tippen) für Segmente und für Wheel-Position, Host-Test in test_host/
```

### Ablauf einer Drehung

1. Input-Task liest alle `NANO_WHEEL_POLL_MS` (5 ms) den Controller in **einer** I2C-Transaktion (QT2120: Register 2..5 = Status, Tasten, Wheel-Position; MPR121: Touch-Status + gefilterte Werte); im Leerlauf schläft er bis zur Flanke von INT (QT2120: CHANGE, Stecker-Pin 5) bzw. BTN.
2. **QT2120 (Standard):** Der Chip liefert die Position 0..255 selbst; `cw_update_position()` rechnet sie in einen Winkel um (Klickrad-v2-Konvention, `cw_config_wheel_v2()`: Position 0 oben = -90 Grad, steigt gegen den Uhrzeigersinn, Stecker unten = Position 128; Einbau-Drehung per `NANO_WHEEL_V2_MOUNT_OFFSET_DEG`, Gegenprobe `NANO_WHEEL_V2_MIRRORED`; Finger im Uhrzeigersinn ergibt positive Schritte = nach unten scrollen). **MPR121 (v1):** Signal pro Segment = Baseline − gefilterter Wert, Winkel = Vektorsumme (gewichteter Schwerpunkt) aus dem stärksten Segment und seinen zwei Nachbarn, Rundlauf wird korrekt behandelt.
3. Winkeldifferenzen werden akkumuliert, jeder volle Rasterschritt (`NANO_WHEEL_DETENT_DEG`, 15 Grad) ergibt einen Schritt. Gedreht wird erst nach `NANO_WHEEL_TAP_SLOP_DEG` Bewegung; vorher zählt Loslassen als Tippen (oben MENU, unten PLAY, rechts NEXT, links PREV, wie `buttonAt` im Emulator).
4. Der Schritt geht in das Modell (`model_step`), danach **sofort** `haptics_tick()` (DRV2605L, Effekt 1) im selben Task. Das UI liest den Zustand später per LVGL-Timer (10 ms) aus dem Modell. Rate-Limit: Ticks innerhalb von 20 ms werden ausgelassen (die Auswahl bewegt sich trotzdem). Am Listenende: Anschlag-Effekt (Default 10 Double Click), eigenes Limit 80 ms.
5. Der DRV2605L hat den Effekt als einzigen Eintrag der Wellenform-Sequenz vorgeladen; wiederholte Ticks schreiben nur das GO-Bit (2 Byte).

Die Mitteltaste ist beim QT2120 Taste 3 des Chips (wie Tangara) und zusätzlich über den BTN-Pin (Stecker-Pin 6, abschaltbar) lesbar; beide laufen durch dieselbe Entprellung.

Bedienung: Mitteltaste öffnet den markierten Eintrag (und löst einen Klick aus), Tippen oben auf den Ring geht zurück (Tipp-Klick). Auf "Wird gespielt" ändert Drehen die Lautstärke (Anzeige, kein Ton in Phase 1).

## Verkabelung Klickrad-Modul <-> Waveshare-Board

An die 1,27-mm-Lötpads des Waveshare-Boards (Quelle: `../docs/RECHERCHE.md`, Schaltplan):

| JST-SH-Pin | Signal | Waveshare | Status |
|---|---|---|---|
| 1 | 3V3 | 3V3-Pad | geprüft |
| 2 | GND | GND-Pad | geprüft |
| 3 | SDA | GPIO15 (geteilter Bus, 2,2 kΩ Pull-ups onboard) | geprüft (Schaltplan) |
| 4 | SCL | GPIO14 | geprüft (Schaltplan) |
| 5 | INT (QT2120: CHANGE; MPR121: IRQ) | GPIO17 (Testpunkt TP11, sonst unbelegt) | Vorschlag |
| 6 | BTN | GPIO18 (Testpunkt TP12) | Vorschlag |

Latenz-Messpunkte für den Logic Analyzer (Vorschlag, Pads laut Recherche frei): **GPIO38** toggelt beim Erkennen eines Rasterschritts, **GPIO39** direkt nach dem I2C-Befehl an den DRV2605L. Die Differenz ist Firmware-Latenz + I2C-Zeit; die mechanische Antwort des LRA lässt sich mit Beschleunigungssensor oder Mikrofon dazumessen. Abschaltbar: `Nano-Player -> Debug -> Latenz-Messpunkte`.

Auf dem Modul **keine** zusätzlichen I2C-Pull-ups bestücken. Adressen: 0x5A (DRV2605L), 0x1C (AT42QT2120) bzw. 0x5B (MPR121, v1); belegt auf dem Board sind 0x15 CST820, 0x18 ES8311, 0x20 TCA9554, 0x34 AXP2101, 0x51 PCF85063, 0x6B QMI8658. Beim Start wird der Bus gescannt und geloggt (abschaltbar).

## Board-Fakten (aus Waveshare-Beispielcode)

- Display QSPI: CS=12, SCLK=11, D0..D3=4..7, 368x448, RGB565. Kein Reset-GPIO; LCD_RST, Display-Versorgung und Touch-Reset hängen am **TCA9554 (0x20)**: Konfig-Register 0x03, Ausgang 0x01, Bits 0 (LCD_RST), 1 (Versorgung), 2 (Touch-RST), 7 (SD-CS). `board.c` setzt sie wie das Waveshare-Beispiel.
- **V2** (seit 30.05.2026 allein lieferbar): CO5300 + CST820, Panel-Versatz x = 0x10. **V1**: SH8601 + FT3168. Auswahl per Kconfig (`Display-Variante`), Default V2. Beide Treiber sind gebaut (`espressif/esp_lcd_co5300`, `espressif/esp_lcd_sh8601`).
- Die Waveshare-Komponente `waveshare/esp32_s3_touch_amoled_1_8` wird bewusst nicht benutzt (verlangt IDF >= 5.5); die Pins stehen direkt in `board_config.h`.

## Bauen und Flashen

```bash
. ~/esp-idf/export.sh          # ESP-IDF v5.4.x oder v5.5
cd firmware
idf.py set-target esp32s3
idf.py build
idf.py -p /dev/ttyACM0 flash monitor
idf.py menuconfig              # Menü "Nano-Player"
```

Beim ersten Build lädt der Component Manager `esp_lvgl_port` 2.9, `lvgl` 9.3, die zwei Display-Treiber (Internet nötig). LVGL ist auf 9.3 festgelegt, weil 9.6 viele API-Namen als veraltet markiert. USB-C des Boards ist der native USB (Log über USB-Serial-JTAG).

## Einstellungen (menuconfig -> Nano-Player)

| Option | Default | Bedeutung |
|---|---|---|
| Display-Variante | V2 CO5300 | oder V1 SH8601 |
| Touch-Controller | AT42QT2120 | oder MPR121 (Klickrad v1) |
| Board-Profil | Prototyp | Prototyp (Waveshare, gebaut) oder Endgeraet (Hauptplatine Rev. 3b, S31, nur vorbereitet, ungebaut), siehe unten |
| Segmente / Winkel Segment 0 / Drehsinn (nur MPR121) | 12 / 105 / im Uhrzeigersinn | an die Platine anpassen |
| `NANO_WHEEL_V2_MOUNT_OFFSET_DEG` / `NANO_WHEEL_V2_MIRRORED` (nur QT2120) | 0 / aus | Einbau-Drehung des Moduls gegenueber Stecker unten; Spiegelung als Gegenprobe |
| `NANO_WHEEL_DETENT_DEG` | 15 | Rasterschritt |
| `NANO_WHEEL_TOUCH_ON/OFF/NOISE_FLOOR` | 40 / 20 / 8 | nur MPR121: Schwellen auf der Signalstärke; mit `NANO_WHEEL_LOG_RAW` am echten Rad einstellen |
| `NANO_WHEEL_TAP_SLOP_DEG` | 20 | Tippen vs. Drehen |
| `NANO_TICK_MIN_INTERVAL_MS` | 20 | Rate-Limit Ticks |
| `NANO_ENDSTOP_MIN_INTERVAL_MS` | 80 | Rate-Limit Anschlag |
| `NANO_EFFECT_TICK` / `CLICK` / `ENDSTOP` | 1 / 4 / 10 | DRV2605L-Effekt-IDs (1 Strong Click 100 %, 4 Sharp Click 100 %, 10 Double Click 100 %, 14 Strong Buzz 100 %) |
| `NANO_LRA_FREQ_HZ` / `RATED_MVRMS` / `OVERDRIVE_MVPEAK` | 235 / 1800 / 2600 | Tangara-Motor (235 Hz, 1,8 V RMS, 2,6 V Spitze); **aus dem Datenblatt des gewählten LRA eintragen** |
| `NANO_HAPTIC_AUTOCAL` | an | Auto-Kalibrierung beim ersten Start (ca. 1 s Brummen), Ergebnis im NVS (wie Tangara), danach gespeicherte Werte |
| `NANO_HAPTIC_ERM` / `IGNORE_NACK` / `INTERRUPT` | aus / aus / an | Tangara-Optionen: ERM-Modus (offener Regelkreis, Bibliothek C), ACK-Prüfung aus, laufenden Effekt vor dem nächsten abbrechen |
| `NANO_LATENCY_PROBE`, `NANO_I2C_SCAN` | an | Debug |

## Was gebaut und getestet wurde

- **Gebaut:** ESP-IDF v5.4.2, Ziel esp32s3, `idf.py build` fehlerfrei (QT2120-Standard: App 0x97200 Bytes, 41 % der 1-MB-Partition frei; zusätzlich Variante `NANO_WHEEL_MPR121` fehlerfrei). Frühere Zusatzvarianten (V1 SH8601, eigener Wheel-Bus, Latenz-Messpunkte aus) wurden nach der Umstellung nicht erneut gebaut. Nicht mit IDF 5.5 gebaut.
- **Auf dem PC getestet:** `components/clickwheel/test_host/test.c` (Winkel-Rekonstruktion aus Segmenten, Drehen im/gegen den Uhrzeigersinn ergibt 5 Schritte für 90 Grad, Tippen oben ergibt MENU; neu: dieselben Tests mit Wheel-Position 0..255 inkl. Rundlauf 255 -> 0). Aufruf: `gcc -I../include test.c ../clickwheel.c -lm && ./a.out`.
- **Nicht getestet (keine Hardware):** alles, was Chips anspricht. Insbesondere
  - Display-Init, Panel-Versatz, Helligkeitsbefehl, Farben/Byte-Reihenfolge (`swap_bytes`), Pufferplatz in internem RAM;
  - AT42QT2120: Init-Sequenz aus Tangara übernommen, am Tangara-Rad bewährt, aber an unserem Modul ungeprüft; ob CHANGE auch bei reiner Positionsänderung auslöst (wir pollen deshalb beim Berühren alle 5 ms); Elektrodenlage/Orientierung (Position 0 oben, gegen den Uhrzeigersinn steigend, Stecker = 128: aus dem Footprint gerechnet, nicht gemessen); Mitteltaste = Taste 3 und Guard = Taste 4 sind Tangara-Belegung und müssen zur Platine passen (TEILE.md beschreibt noch 12 Segmente);
  - MPR121 (nur v1): Konfiguration (Auto-Config, Schwellen, Update-Rate 4 ms), Rauschverhalten des Rings;
  - DRV2605L: Register-Formeln (RATED_VOLTAGE korrigiert: sqrt im Zähler, gegen Tangara-Wert 0x46 geprüft, ergibt 68), DRIVE_TIME, Ergebnis der Auto-Kalibrierung und NVS-Ablage; Effekt-IDs 4 und 10 fühlen sich am LRA evtl. anders an als gedacht;
  - Mitteltasten-Entprellung (15 ms), INT-Aufwachen, Zusammenspiel Display-Task (Core 0) und Input-Task (Core 1) auf demselben I2C-Bus;
  - tatsächliche Latenz (Ziel unter ca. 10 ms laut `../KONZEPT.md`; 5 ms Abtastung + I2C ca. 0,3 bis 0,7 ms je Transaktion sind Schätzungen);
  - Pins GPIO17/18 (INT/BTN) und GPIO38/39 (Messpunkte): Vorschläge, Lage der Pads am echten Board prüfen; Pins für optionalen eigenen Wheel-Bus (GPIO41/42) sind ungeprüft.

## Offene Punkte

- Gegen das Datenblatt des gewählten LRA: Resonanzfrequenz, Nennspannung, Overdrive; danach Kalibrierwerte (`comp`, `bemf`) im Log notieren und fest eintragen (`use_stored_cal`).
- Effektstärke: der DRV2605L spielt Bibliothekseffekte in fester Stärke; für einstellbare Intensität wäre RTP-Modus mit eigenen Kurzimpulsen nötig (nächster Schritt, falls der Library-Effekt nicht reicht).
- Rad-Orientierung am echten Klickrad v2 pruefen (Konvention ist eingebaut, aber nicht gemessen; Gegenprobe `NANO_WHEEL_V2_MIRRORED`).
- Audio, SD, Bluetooth und Wiedergabe sind nicht Teil von Phase 1.

## Board-Profil Endgeraet (vorbereitet, ungebaut, ungetestet)

Kconfig `Nano-Player -> Board-Profil -> Endgeraet` waehlt `main/board_config_endgeraet.h` (Pins der Hauptplatine Rev. 3b aus `../hardware/pcb/hauptplatine/README.md`): I2C IO6/IO7, Klickrad-CHANGE IO0, Display 410 x 502 CO5300 mit QSPI IO48/49/11/10/9/51 und LCD_RST IO19, Power-Latch IO4 wird in `board_init()` gehalten. Kein TCA9554, kein BTN-Pin, keine Latenz-Messpunkte, kein eigener Wheel-Bus. Der ESP32-S31 wird von IDF 5.4.2 nicht unterstuetzt: das Profil ist **nicht fuer den S31 gebaut**; ein Versuch mit dem Ziel esp32s3 bricht erwartungsgemaess bei GPIO49 ab (S3 hat keine GPIO49..51) (siehe Abschnitt "Board-Profil Endgeraet" in `../docs/FIRMWARE-PORTIERUNG.md` fuer Ergebnis und offene Punkte).
