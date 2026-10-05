# Portierung der Tangara-Firmware auf ESP32-S31 (AMOLED 368 × 448, AT42QT2120-Klickrad, ohne SAMD21)

Stand 2026-10-04. Grundlage: lokaler Tangara-Checkout `/home/user/tangara-ref/tangara-fw` (GPL-3.0, ein einziger Git-Commit sichtbar, Stand Merge #481 vom 17.08.2026), unsere Phase-1-Firmware in `firmware/` und Espressif-Dokumentation (Quellen am Ende). Alle Aussagen über Tangara sind am Code geprüft; Aufwände sind Schätzungen für eine Person im Hobby-Tempo (Tage = Arbeitstage, ohne Wartezeiten auf Hardware). Nichts davon wurde auf Hardware ausprobiert.

## Kurzfazit

1. **Bluetooth Classic / A2DP auf dem ESP32-S31 ist laut Espressif unterstützt und damit kein Ausschlusskriterium mehr.** Die Statusseite (Stand 25.09.2026) führt Classic im Bluedroid-Host mit A2DP, AVRCP, HFP, HID, PBAP und SPP als unterstützt, ebenso den Classic-Controller (ACL, SCO, eSCO). Das Hauptrisiko ist nicht der Funktionsumfang, sondern die **Reife**: Espressif nennt den S31 in IDF 6.0.x ausdrücklich „preview support“ und rät, bis zu einer vollen Unterstützung den Stand von `master` zu nutzen. Rest-Risiko also „Preview-IDF, wenig Praxiserfahrung“, nicht „fehlt“. Bluetooth-Testen geht nur auf echter S31-Hardware (siehe Abschnitt 4).
2. **Der SAMD21 lässt sich sauber ersetzen**, weil Tangara ihn hinter einer kleinen Klasse (`drivers::Samd`, I²C 0x45) versteckt: Ladestatus, USB-Status, Power-Down, USB-Massenspeicher. Dahinter liegen nur der MCP73871 (STAT1, STAT2, PG, PROG, SEL), der USB-Port und die Versorgungsschaltung. Mit dem S31 (nativer USB-OTG, USB-Serial-JTAG, SDMMC) entfallen UART-Brücke, SD-Umschalter und Co-Prozessor; zu schreiben sind GPIO-Auswertung, ein Power-Latch und TinyUSB-MSC.
3. **Das größte Stück Arbeit ist die Anpassung an Display und Auflösung** (ST7735R 128 × 160 → AMOLED 368 × 448): neuer Display-Treiber (haben wir aus Phase 1), vor allem aber **Schriften und Icons der Lua-UI**, die für 128 Pixel Breite gebaut sind. Das Lua-Layout nutzt zu großen Teilen `HOR_RES()`/`PCT()`, die Assets nicht.
4. **Zweitgrößtes Stück: Portierung von IDF 5.5 auf IDF 6.x** und von ESP32 (Xtensa) auf S31 (RISC-V): I²S-Takt (APLL gibt es nur beim klassischen ESP32), SPI-/ADC-/Pin-Zuordnung, PicolibC statt Newlib als Standard-C-Bibliothek.
5. **Tangaras „eigener esp-idf-Fork“ ist im Checkout nicht zu finden.** `.gitmodules` zeigt auf das normale `github.com/espressif/esp-idf` (fest gepinnter Commit `8c750b08…`, `dependencies.lock` nennt IDF 5.5.0). Gepatcht sind drei **mitgelieferte Komponentenkopien** in `lib/`, siehe Abschnitt 3.3; sie sind klein und weitgehend verzichtbar.

## 1. Was Tangara ist (am Code geprüft)

| Bereich | Befund | Fundstelle |
|---|---|---|
| Hardware | ESP32-WROVER-E-N16R8 (Xtensa, 16 MB Flash, 8 MB PSRAM), ATSAMD21E18A, PCA8575-GPIO-Expander, WM8523-DAC, MCP73871-Lader, ST7735R-Display 128 × 160 | `hardware/pcb/hauptplatine/quellen/tangara_netlist_rev5.json` (liegt bei uns), `src/drivers/display_init.cpp` |
| Umfang Software | ca. 31 000 Zeilen C++ in `src/` (ohne `lib/`), ca. 4 400 Zeilen Lua in `lua/`, C++23, RTTI/Exceptions aus | `wc`, `tools/cmake/common.cmake` |
| Struktur | `src/drivers` (Hardware), `src/tangara/{audio,database,input,lua,system_fsm,ui,battery,tts,…}`, `src/codecs`, tinyfsm-Zustandsautomaten | Verzeichnisse |
| Bibliotheken | LVGL **9.5.0**, luavgl, Lua (esp-idf-lua), LevelDB, libmad (MP3), tremor (Vorbis), dr_flac, opusfile, wavpack, alac, speexdsp (Resampler), libtags, FatFs mit exFAT, esp_littlefs | `lib/`, `src/codecs/` |
| Partitionen | 2 × 4 MB OTA, 3 MB `collate`, 2 MB `lua` (littlefs), 128 KB `repl`, 16 MB Flash | `partitions.csv` |
| Bluetooth | Bluedroid, nur Classic, **A2DP-Source** (Tangara sendet an Kopfhörer), AVRCP-CT und -TG, GAP mit SSP-Kopplung, eigener Scanner; BLE-Speicher wird freigegeben; Sendeleistung per `esp_bredr_tx_power_set` | `src/drivers/bluetooth.cpp`, `src/tangara/audio/bt_audio_output.cpp` |

## 2. Abhängigkeiten zum SAMD21 (konkret)

**Was der SAMD21 auf der Tangara-Platine tut** (Netlist `U13`): UART-Brücke zum ESP (`UART.ESP.RX/TX`) und Reset des ESP (`ESP_EN`); USB-Anschluss (`USB.DN/DP` hängen am SAMD, nicht am ESP); liest `CHG_STAT1`, `CHG_STAT2`, `~CHG_PWR_OK` des MCP73871 und steuert `CHG_PROG`, `CHG_SEL`; schaltet die Systemversorgung (`SYS_PWR_EN_SAMD`); meldet dem ESP Ereignisse über `~SAMD_INT` (ESP-GPIO 35); kann über den Analogschalter 74CBTLV3257 die SD-Karte übernehmen (USB-Massenspeicher). Seine I²S-Pins am DAC sind parallel zum ESP geführt.

**Was im ESP-Code daran hängt** (`src/drivers/samd.cpp`, I²C-Adresse 0x45, Register: Firmware-Version, Ladestatus mit 3 + 2 Bit, USB-Status, Power-Control, USB-Control):

| Stelle | Nutzung | Ersatz |
|---|---|---|
| `battery/battery.cpp` | Ladestatus (kDischarging, kChargingRegular/Fast, kFullCharge, kNoBattery, kBatteryCritical, kFault) neben der ADC-Spannung | MCP73871 STAT1/STAT2/~PG direkt an 3 S31-GPIOs, Dekodierung nach Datenblatt-Tabelle (nicht geprüft). Prozentwert bleibt wie in Tangara aus der ADC-Spannung (ADC1_CH0 über Teiler) |
| `system_fsm/idle.cpp` | nach Leerlauf: Peripherie abschalten, dann `samd.PowerDown()` in Schleife; bleibt an, solange geladen wird | GPIO „Power-Hold“ freigeben bzw. Deep-Sleep. **Erfordert ein Platinendetail**: ein Lastschalter/Latch für die Hauptversorgung mit Wake über Taste oder USB-Anschluss |
| `system_fsm/running.cpp`, `system_events.hpp` | USB-MSC: SD-Karte aushängen, Mux auf SAMD schalten, SAMD starten; Rückweg mit Wartezeiten und SD-Power-Zyklus | Mux entfällt. ESP exportiert die Karte selbst über TinyUSB-MSC (SDMMC-Host am S31 ✅, USB-OTG-Device ✅). Ablauf „Dateisystem aushängen, MSC an, danach neu einhängen“ bleibt gleich |
| `system_fsm/system_fsm.cpp` | `SamdInterrupt` → Status neu lesen, Ereignisse `SamdUsbStatusChanged`, `ChargeStatusChanged` | Interrupt der Lade-GPIOs (Flankenwechsel) auslösen |
| `ui/ui_fsm.cpp`, `lua/settings.lua` | Einstellung „Fast Charge“ (`SetFastChargeEnabled` → PROG/SEL), Seite „USB Storage“ (verlangt SAMD-Firmware ≥ 3) | GPIO-Ausgänge für PROG/SEL bzw. fest verdrahten; Texte der Seite anpassen |
| `lua/lua_version.cpp`, `app_console.cpp` | SAMD-Version abfragen, SAMD-Update („ResetToFlashSamd“) | streichen |
| `system_fsm/booting.cpp` | `std::make_unique<Samd>`; der Konstruktor ruft `ESP_ERROR_CHECK`, ohne SAMD bricht der Start ab | ersetzen |

**Empfehlung:** Die Klasse `drivers::Samd` durch eine gleich benannte Schnittstelle `drivers::PowerManager` mit denselben Methoden ersetzen (`GetChargeStatus`, `GetUsbStatus`, `SetFastChargeEnabled`, `PowerDown`, `UsbMassStorage`) und nur die Implementierung neu schreiben. Dann bleiben alle Aufrufer unverändert. Aufwand: GPIO-Teil 2 bis 3 Tage, TinyUSB-MSC mit SDMMC 4 bis 6 Tage. Konfliktpunkt aus unserem Konzept: Der einzige USB-OTG-Port soll auch **USB-Audio-Host** (TUSB320 Rollenumschaltung) sein; MSC (Device) und UAC (Host) schließen sich zur Laufzeit aus und brauchen eine Umschaltlogik in der Software.

Zusätzlich hängt Tangara am **PCA8575** (`drivers/gpios.cpp`): SD-Mux, SD-Versorgung, Display-Enable, Kopfhörer-Erkennung (`kPhoneDetect`), Verstärker-Enable/-Mute, SD-Card-Detect, Lautstärke- und Sperrtasten. Der S31 hat ca. 54 bis 60 GPIOs; die Klasse steckt hinter `IGpios`, kann also entweder unverändert mit einem PCA8575 weiterlaufen oder auf direkte GPIOs umgestellt werden (1 bis 2 Tage). Mux-Funktionen entfallen.

## 3. Weitere Prüfbefunde

### 3.1 Display und UI-Auflösung

- Treiber: `src/drivers/display.cpp` ist ein handgeschriebener SPI-Treiber für **ST7735R** (`display_init.cpp`, CASET/RASET 128 × 160, Offset-Varianten Green/Red-Tab), 40 MHz SPI, CS GPIO 22, DR (D/C) GPIO 33, Hintergrundlicht per LEDC (GPIO 32, 50 kHz). LVGL-Puffer: `160 * 128 / 10` Pixel, fest.
- Das passt nicht zu QSPI-AMOLED; **neu**: `display.cpp` durch unseren Phase-1-Code (esp_lcd, CO5300/SH8601, Helligkeit per Befehl statt LEDC) ersetzen. Die LVGL-Anbindung (`lv_display_create`, Flush-Callback, Puffer) ist in Tangara kurz und bleibt in der Struktur. Größere Puffer: 368 × 448 × 2 = 330 KB pro Vollbild, bei 1/10-Teilpuffern ca. 33 KB; DMA-fähig, ggf. in internem RAM.
- UI-Code in C++ (`ui_fsm.cpp`, `screen_*.cpp`) lässt sich anpassen, enthält keine eingebaute Pixelgröße außer der Anzeige-Initialisierung.
- Lua-UI: überwiegend `lvgl.HOR_RES()`, `VER_RES()`, `lvgl.PCT(100)` und Flex-Layouts, aber ca. 160 feste Zahlenwerte (Abstände, Höhen, Radien; viele nur 1-Pixel-Abstandhalter). **Schriften** sind vorgerenderte Bitmapschriften `fusion10`/`fusion12` (je ca. 440 KB, werden beim Start ins PSRAM kopiert, `ui_fsm.cpp`), **Icons** sind ca. 60 kleine PNGs in Pixelgröße. Bei 368 × 448 (Faktor ca. 2,9 in beide Richtungen) wirkt alles winzig. Nötig: Schriften neu erzeugen (Werkzeug liegt in `tools/fonts`), Icons skalieren oder neu zeichnen, feste Maße prüfen. Aufwand 5 bis 10 Tage bis zu einer ansehnlichen Oberfläche.
- Zusätzliche Chance: PPA des S31 für Skalierung/Mischung, das AMOLED-Hochformat entspricht dem Tangara-Hochformat.
- LVGL: Tangara nutzt 9.5.0 (`lib/lvgl/lv_version.h`), wir 9.3 (Phase 1). Bei einem Fork gilt 9.5.0; unsere Display-Anbindung muss darauf geprüft werden (Phase 1 hatte 9.6 wegen veralteter API-Namen gemieden).

### 3.2 Eingabe und Haptik (hier passen die Teile schon)

- `src/tangara/input/input_touch_wheel.cpp` arbeitet mit exakt den Daten, die unser `at42qt2120`-Treiber liefert (`wheel_position` 0..255, `is_wheel_touched`, `is_button_touched`). Konvention in Tangara: **Position 0 = oben, 64 = links, 128 = unten, 192 = rechts** (steigt gegen den Uhrzeigersinn); Tick-Schwelle 5 bis 35 Positionseinheiten je nach Einstellung „Scroll-Empfindlichkeit“; Tasten oben/unten/links/rechts über `isAngleWithin(pos, 0|128|64|192, 32)`.
- `input/feedback_haptics.cpp` ruft `drivers::Haptics::PlayWaveformEffect` mit Effekten wie Strong Click 30 %, Medium Click 1, Sharp Click 30 %. Bei einem Fork: unser `components/drv2605l` als Backend einhängen (gleiche Effektnummern, Aufzählung in `drv2605l_effects.h`) oder deren `haptics.cpp` nahezu unverändert behalten (sie nutzt dieselbe I²C-API wie wir). Unsere Vorgabe „Tick = Effekt 1“ lässt sich über die Feedback-Zuordnung setzen.
- Unterschied zu unserer Logik: Tangara löst Ticks aus der Winkeldifferenz zum letzten Tick aus (schwellenbasiert), wir akkumulieren in festen 15°-Schritten mit Tipp-/Dreh-Unterscheidung. Für das „iPod-Gefühl“ ist unsere Logik die bessere Grundlage; Tangaras `TouchWheel::read` müsste dann durch `cw_update_position()` gespeist werden (kleiner Eingriff).

### 3.3 ESP-IDF-Version und „Fork“

- Gepinnt: IDF-Submodul `8c750b088c7cd857d079c0eeb495da199b359461` von **upstream** (`.gitmodules`), `dependencies.lock`: IDF 5.5.0. Das Verzeichnis `lib/esp-idf` ist im Checkout leer (nicht initialisiert), die Git-Historie besteht aus einem Commit; **warum** etwas vendort wurde, lässt sich daher nicht belegen.
- Was in `lib/` an Espressif-Komponenten liegt und **tatsächlich abweicht** (Vergleich Datei für Datei gegen den gepinnten IDF-Commit, geholt von raw.githubusercontent.com):
  - `lib/bt`: von ca. 620 verglichenen Dateien (host/bluedroid, common, include, controller esp32/esp32s3, Kconfig, CMake; die NimBLE-Unterverzeichnisse sind Submodule und wurden nicht verglichen) ist **genau eine** anders: `host/bluedroid/btc/profile/std/a2dp/btc_a2dp_source.c`, dort ist die fest eingestellte PCM-Rate des A2DP-Source von 44 100 auf **48 000 Hz** geändert. Dazu passt `BluetoothAudioOutput::PrepareFormat` (feste 48 kHz, 16 Bit, Stereo). Alles andere in `lib/bt` ist unverändert vom gepinnten IDF.
  - `lib/fatfs`: nur `src/ffconf.h` anders: `FF_FS_EXFAT 1`, `FF_LBA64 1`, `FF_USE_FORWARD 1`, `FF_USE_LABEL 0`. Also **exFAT** für große SD-Karten.
  - `lib/console`: ältere Kopie der Konsolenkomponente (Stand ca. IDF 5.1, kein `esp_console_repl_internal.c`), vermutlich für die Konsolen-API des Entwicklerzugangs; keine funktionale Tangara-Änderung erkennbar.
  - weitere Komponenten (`esp_littlefs`, `esp-idf-lua`, …) sind normale externe Bibliotheken.
- **Folgerung für den S31:** Es gibt keinen echten IDF-Fork zu portieren. (a) In IDF v6.0/v6.1/master leitet `btc_a2dp_source_setup_codec` die PCM-Rate aus der ausgehandelten SBC-Konfiguration ab (48/44,1/32/16 kHz; geprüft in v6.1 und master). Die 48-kHz-Änderung ist dort nicht mehr nötig, dafür muss Tangaras Ausgabeformat der **ausgehandelten** Rate folgen (Ereignis `ESP_A2D_AUDIO_CFG_EVT`, wird in `bluetooth.cpp` bisher nicht ausgewertet) oder man erzwingt 44,1/48 kHz über die SBC-Fähigkeiten. (b) exFAT: eine lokale Kopie von `fatfs` mit geänderter `ffconf.h` weiterführen (IDF 6 prüfen, ob die Komponente noch dort liegt) oder auf die FATFS-Optionen des IDF-Kconfig schauen. (c) Konsole: aktuelle IDF-Konsole verwenden, die `app_console` entsprechend anpassen.
- **IDF 5.5 → 6.x** (nötig, weil der S31 erst ab 6.0 als Ziel existiert): `driver/i2c.h` ist in 6.0 „End-of-Life“ (Entfernung erst in 7.0), Tangara nutzt die neue `i2c_master`-API, bindet aber noch den alten Header ein, läuft also; Standard-C-Bibliothek PicolibC statt Newlib (relevant für `std::format`, `iostream`, `printf`-Formate, Locale/Collation-Code in `src/locale`); Mbed TLS 4.0 (Tangara nutzt kaum TLS); weitere Komponentenänderungen laut Migrationsleitfaden. Aufwand 4 bis 8 Tage, überwiegend Compilerfehler abarbeiten.

### 3.4 Bluetooth-API-Nutzung

- Benutzt (aus `bluedroid`): `esp_bt_controller_*`, `esp_bluedroid_*`, GAP (`esp_bt_gap_set_security_param`, SSP-Bestätigung, Discovery), A2DP-Source (`esp_a2d_source_init`, `register_data_callback`, `esp_a2d_media_ctrl`, `esp_a2d_source_disconnect`), AVRCP-CT und -TG (Statusabfragen, Notifications, Lautstärke), `esp_bredr_tx_power_set`, `esp_bt_controller_mem_release(ESP_BT_MODE_BLE)`. Kein HFP, kein BLE, kein A2DP-Sink. Es ist SBC (die vom Stack eingebaute Kodierung); Tangara bindet den Stack mit `CONFIG_BT_BLUEDROID_PINNED_TO_CORE_1`, `CONFIG_BT_ALLOCATION_FROM_SPIRAM_FIRST`, `CONFIG_BTDM_CTRL_MODE_BR_EDR_ONLY` (`sdkconfig.common`).
- Auf dem S31 existieren dieselben Bluedroid-Klassik-APIs (Seite „Bluetooth Classic – ESP32-S31“ der IDF-v6.1-Doku nennt GAP, L2CAP, SDP, SPP, A2DP „source and sink“, AVRCP, HFP, HID). Die Controller-Kconfig-Symbole unterscheiden sich pro Chip (`CONFIG_BTDM_*` ist ESP32-spezifisch), deshalb: **Kconfig und Controller-Init neu aufsetzen, API-Aufrufe voraussichtlich unverändert**. Ungeprüft: ob `esp_bredr_tx_power_set` und `mem_release` auf dem S31 unverändert verfügbar sind.
- Der klassische ESP32-S3 (Waveshare-Prototyp) hat **kein** Bluetooth Classic. Auf dem Prototypen läuft deshalb Wiedergabe nur lokal; Bluetooth lässt sich erst auf S31-Hardware (oder dem klassischen ESP32) erproben.

### 3.5 Speicher (PSRAM) und Flash

- Tangara-Messpunkte im Code: statischer Readahead-Puffer **1 MB + 1 Byte** im PSRAM (`readahead_source.cpp`), Schriften ca. **1 MB** PSRAM plus `LV_MEM_SIZE` (`ui_fsm.cpp`), Dateipuffer 32 KB im PSRAM, Decoder-Puffer, PCM-Puffer, Lua-Heap, Task-Stacks, Bluetooth und LevelDB-Wurzeln (`SPIRAM_MALLOC_ALWAYSINTERNAL=512`, `BT_ALLOCATION_FROM_SPIRAM_FIRST`, BSS im PSRAM). Läuft auf 8 MB PSRAM; der Code bemüht sich ausdrücklich um niedrigen Spitzenverbrauch beim Start.
- Zusatzbedarf bei 368 × 448: größere Schriften (grob 2 bis 3 MB statt 1 MB, Schätzung), höher aufgelöste Bilddaten/Cover, ggf. Vollbildpuffer 330 KB. **Empfehlung: 16 MB PSRAM** (Modulvarianten `ESP32-S31-WROOM-3-N16R16V` bzw. `N8R16V`), 8 MB (`N16R8V`) sollten reichen, wenn die Schriftgröße begrenzt bleibt (Schätzung, nicht gemessen). Flash: 16 MB wie Tangara (Partitionstabelle übernehmen).
- S31 intern 512 KB SRAM (ESP32: 520 KB), PSRAM Octal-DDR bis 250 MHz laut Chipbeschreibung; „MSPI-Tuning über 80 MHz“ ist laut Statusseite noch offen (IDF-14653), die Anfangsgeschwindigkeit liegt also eventuell unter dem Datenblattwert.

### 3.6 Audio

- `i2s_dac.cpp`: Standardmodus, MCLK GPIO 0, BCLK 26, WS 27, DOUT 5, **`I2S_CLK_SRC_APLL`** (Audio-PLL gibt es beim klassischen ESP32, nicht bei S3; beim S31 prüfen). WM8523 über I²C-Adresse 0x1A (`wm8523.cpp`), Lautstärke über Register. Unser Konzept nennt zusätzlich INA1620 (Kopfhörerverstärker): Tangaras Verstärker-Enable/-Mute laufen über den PCA8575, das bleibt gleich.
- Decoder (`src/codecs`: libmad, tremor, dr_flac, opus, wav, wavpack, alac, `native`) sind reiner C-Code ohne Xtensa-Assembler, nur `tremor/asm_arm.h` (nicht benutzt) und libmad-FPM-Auswahl prüfen; auf RISC-V mit 320 MHz sollte die Rechenleistung höher sein als beim ESP32 mit 240 MHz. Resampler: speexdsp.
- Lokale Ausgabe ist also übernehmbar bis auf Takt/Pins; Bluetooth-Ausgabe: siehe 3.3/3.4 (feste 48-kHz-Annahme).

### 3.7 Speicherkarte, Bibliothek, Datenbank

- SD: Tangara nutzt **SPI-Modus** (`sdspi_host`, VSPI, CS 21, gemeinsamer Bus mit dem Display, Analogschalter zum SAMD). Mit dem S31 wäre **SDMMC (4 Bit)** schneller und frei von Bus-Teilung mit dem Display; Umschreiben von `storage.cpp` ca. 2 bis 3 Tage (inkl. exFAT, Karten-Erkennung, Hot-Plug).
- Datenbank: LevelDB auf der SD-Karte, eigene `env_esp.cpp` (PSRAM für Puffer), Tag-Parser (libtags), Indizes, Sortierung mit Collation-Partition. Reiner C++-Code ohne Hardwarebezug, nur PicolibC/IDF-6-Anpassungen nötig.

## 4. Bluetooth Classic auf dem ESP32-S31: Stand und Einordnung

| Aspekt | Befund (Quelle) |
|---|---|
| Chip | Dual-Core RISC-V 320 MHz, Wi-Fi 6, **Bluetooth 5.4 mit LE und Classic (BR/EDR)**, 802.15.4, USB-OTG High-Speed, SDMMC (UHS-I), 2 × I²S, 512 KB SRAM, PSRAM bis 250 MHz DDR (Espressif-Pressemitteilung 26.03.2026) |
| Controller | Statusseite Developer Portal (Stand 25.09.2026): BR/EDR ACL, SCO, eSCO, APB ✅; Auto-Light-Sleep und Modem-Sleep für Classic ✅; offen: CPB (IDF-15191) und „BR/EDR-Synchrondaten an I²S/PCM routen“ (IDF-15190) |
| Host | „Support of Bluetooth Classic in ESP-Bluedroid Host“ ✅ mit **A2DP**, AVRCP, HFP, HID, PBAP, SPP. Koexistenz Wi-Fi + Bluetooth ✅ |
| Dokumentation | IDF-v6.1-Doku hat die Zielauswahl „ESP32-S31“ mit Seiten zu Classic-Bluetooth und A2DP; das Beispiel `examples/bluetooth/bluedroid/classic_bt/a2dp_source` nennt ausdrücklich ESP32 **und** ESP32-S31 |
| IDF-Version | S31-Unterstützung steht seit IDF **v6.0** als „preview“ in den Release Notes (v6.0.x), die Statusseite rät, bis zu einer vollen Unterstützung `master` zu verwenden. v6.1 ist die aktuelle Stable-Dokumentation |
| Module | `ESP32-S31-WROOM-3` in Varianten N16R8V, N8R16V, N16R16V, N32R16V (Flash/PSRAM in MB) ist bei Espressif gelistet, Muster über AliExpress/DigiKey angeboten |

**Bewertung:** Bluetooth Classic mit A2DP **ist unterstützt**; die Befürchtung „fehlt auf dem S31“ ist damit entkräftet. Bleibende Risiken, in dieser Reihenfolge:
1. **Preview-Status der IDF-Unterstützung**: unbekannte Fehler in Controller und Koexistenz, schnelle Änderungen auf `master` (Wartung des Forks).
2. **Keine Praxiserfahrung mit Tangaras Nutzungsmuster**: Source-Rolle mit AVRCP-TG, Wechsel zwischen Kopfhörern, Dauerbetrieb mit Sleep; auf dem klassischen ESP32 ist das erprobt, auf dem S31 nicht.
3. Ungeklärt: Kopfhörer-Kompatibilität/Latenz des S31-Controllers (nur durch Test), Verhalten von `esp_bredr_tx_power_set`.
4. Am Prototyp (ESP32-S3) kann das Bluetooth nicht erprobt werden; es braucht ein S31-Devkit oder -Modul.

Ob das „Hauptrisiko“ bleibt: **Nein, herabgestuft** auf „mittleres, beherrschbares Risiko“. Neues Hauptrisiko ist der **Gesamtaufwand der Anpassung** (Display/UI-Assets plus IDF-6-Portierung plus Power-Hardware ohne SAMD).

## 5. Einteilung: direkt übernehmbar / anzupassen / neu zu schreiben

Aufwand in Arbeitstagen (grobe Schätzung, ein Entwickler).

### Direkt übernehmbar (Aufwand: Übersetzen und Testen, 0 bis 2 Tage je Block)

| Teil | Bemerkung |
|---|---|
| Codecs (`src/codecs`, libmad, tremor, dr_flac, opus, wavpack, alac) | reiner C/C++-Code |
| Bibliothek/Datenbank (`database`, LevelDB, libtags, collation) | hardwareunabhängig; PicolibC-/IDF-6-Warnungen |
| Wiedergabe-Pipeline (`audio`: Decoder, Prozessor, Warteschlange, Readahead, Resampler) | hardwareunabhängig bis auf Ausgänge |
| Zustandsautomaten (tinyfsm), Ereigniswarteschlangen, Task-Verwaltung (`tasks`) | Core-Zuordnung (Core 0/1) bleibt, S31 ist ebenfalls Dual-Core |
| Lua-Laufzeit, luavgl, Lua-Bindings (`src/tangara/lua`) | hardwareunabhängig; `lua_version`, `lua_gpio`, `lua_i2c` einzeln prüfen |
| NVS-Einstellungen, Themen, TTS-Gerüst | |
| Klickrad: `at42qt2120` (**von uns bereits portiert**), `drv2605l` + `drv2605l_effects.h` (**abgeglichen**) | in `firmware/components/`, Eingabe-Logik `clickwheel` |
| Lizenz | Tangara ist GPL-3.0-only; unsere `firmware/LICENSE` ist gesetzt |

### Anzupassen (Aufwand je Posten)

| Teil | Arbeit | Tage |
|---|---|---|
| IDF 5.5 → 6.x, RISC-V-Ziel, `sdkconfig.common` neu (SPIRAM-Modus, BT-Kconfig, Taktquellen) | Compilerfehler, Kconfig-Symbole, PicolibC | 4 bis 8 |
| Display-Anbindung an LVGL 9.5 | unseren esp_lcd-Treiber (Phase 1) statt `display.cpp`; Helligkeit; Vollbild/Teilpuffer | 2 bis 4 |
| Lua-UI: Schriften, Icons, feste Maße | neue Bitmapschriften, Icons ×3, Layout durchsehen, Themes | 5 bis 10 |
| Eingabe | `input_touch_wheel.cpp` an `cw_update_position()` anbinden oder Schwellenlogik behalten; Orientierung | 1 bis 2 |
| Feedback/Haptik | Backend auf unser `drv2605l` (ERM/LRA, NVS-Kalibrierung ist dort schon) umstellen | 1 |
| I²S/WM8523 | Takt ohne APLL, Pins, Lautstärke-Tabelle; INA1620-Steuerung | 2 bis 4 |
| SD-Karte | SPI → SDMMC, exFAT beibehalten, Karte erkennen | 2 bis 3 |
| GPIO-Expander `Gpios` | auf direkte GPIOs (S31) oder PCA8575 belassen, Mux-Funktionen streichen | 1 bis 2 |
| Bluetooth | Kconfig/Controller-Init für S31, ausgehandelte SBC-Rate statt fester 48 kHz auswerten, Wiederverbindung testen | 3 bis 6 (plus Testzeit) |
| Batterie | ADC-Kalibrierung auf S31 laut Statusseite noch ⏳ (IDF-14742): Spannungswert evtl. selbst kalibrieren oder MAX17048 (steht noch in `TEILE.md`) verwenden | 1 bis 2 |
| Konsole/Entwicklerzugang | aktuelle IDF-Konsole, USB-Serial-JTAG statt SAMD-UART | 1 |
| Partitionstabelle, OTA | übernehmen, anpassen | 0,5 |

### Neu zu schreiben

| Teil | Bemerkung | Tage |
|---|---|---|
| `PowerManager` (Ersatz für `Samd`): Ladestatus aus MCP73871-STAT/PG, Fast-Charge-Pins, Power-Hold/Abschalten, Aufwachen | Platinenentwurf mit Lastschalter/Latch zwingend vorher klären | 2 bis 3 |
| USB-Massenspeicher über TinyUSB (MSC) auf SDMMC, Umschaltung zu USB-Audio-Host | Zusammenspiel mit TUSB320-Rollenwahl | 4 bis 6 |
| Display-Treiber für CO5300/SH8601 im Tangara-Gerüst | existiert in Phase 1 | (siehe oben) |
| Hardware-Tests und Abgleich | Klickrad (Position 0, Drehsinn, Mitteltaste), LRA-Kalibrierung, Bluetooth gegen echte Kopfhörer | laufend |

Gesamtschätzung: 30 bis 55 Arbeitstage bis zu einem Gerät, das Tangara im Funktionsumfang entspricht; Streuung vor allem durch UI-Assets und Bluetooth-Tests.

## 6. Empfohlene Reihenfolge

1. **Tangara unverändert bauen** (IDF 5.5, Ziel esp32) und die Abhängigkeiten lokal klonen (Submodule), damit ein Referenzstand mit `idf.py build` und die Größenangaben vorliegen. Nicht auf Hardware nötig.
2. **IDF auf 6.1 heben**, Ziel zunächst `esp32s3` (Waveshare-Prototyp) mit ausgeschaltetem Bluetooth: Compiler- und Kconfig-Fehler früh beseitigen, ohne S31-Hardware. SAMD, PCA8575 und SD-Mux durch Stubs ersetzen.
3. **Display + Eingabe** auf dem Prototyp: AMOLED-Treiber (Phase 1), `at42qt2120`-Klickrad, Haptik → Menü und Liste laufen mit Lua-UI (zunächst mit alten Schriften, Layout provisorisch).
4. **Wiedergabe lokal** (SD, Datenbank, Codecs, ES8311/Lautsprecher am Prototyp) – damit ist der Kern „Musik hören und blättern“ ohne Bluetooth erreicht.
5. **UI-Assets** (Schriften/Icons) auf 368 × 448 bringen.
6. **S31-Hardware beschaffen** (WROOM-3-Modul, ideal als kleine Adapterplatine mit Klinke/WM8523): Ziel `esp32s31` bauen, Bluetooth-Classic/A2DP zuerst isoliert mit dem IDF-Beispiel `a2dp_source` gegen die vorgesehenen Kopfhörer testen, **dann** Tangaras Bluetooth-Ausgabe aktivieren.
7. **Endgeräte-Platine**: WM8523 + INA1620, MCP73871, Power-Hold, USB (OTG) mit TUSB320; `PowerManager` und MSC.
8. Optionale Feinarbeit: SDMMC, PPA-Beschleunigung, USB-Audio-Host.

## 7. Offene Punkte und nicht Geprüftes

- Reifegrad der S31-Unterstützung in IDF 6.1/master konnte nur über Dokumentation und Statusseite beurteilt werden, nicht durch Bauen (unser Rechner hat nur IDF 5.4.2 mit Ziel esp32s3).
- Warum Tangara die Komponenten `bt`, `fatfs`, `console` vendort hat, ist aus dem Checkout nicht ersichtlich (Einzel-Commit). Die Abweichungen sind nur gegen den gepinnten IDF-Commit verglichen; `lib/console` ist eine ältere Fassung.
- MCP73871-Statuskodierung, Lastschalter-Auslegung und Wake-Quellen sind noch nicht entworfen (Platinenthema, siehe `TEILE.md` mit BQ24074/MAX17048 im bisherigen Stand: diese Teile ändern sich durch die neue Vorgabe).
- `TEILE.md` und `KONZEPT.md` (Klickrad: MPR121/12 Segmente, Endgerät: CS43131/BQ24074) spiegeln die neue Tangara-Technik noch nicht; das ist nicht Teil dieser Änderung.
- AT42QT2120 im Wheel-Modus: Orientierung und Mitteltaste/Guard-Belegung sind Tangara-Annahmen; unser Modul muss Tasten 0 bis 2 als Wheel, Taste 3 als Mitte und Taste 4 als Guard verdrahten oder die Treiber-Init anpassen. Ungeprüft: ob CHANGE bei reinen Positionsänderungen auslöst (Treiber pollt deshalb beim Berühren).
- Speicherbedarfe der vergrößerten UI sind Schätzungen.

## 8. Klickrad-v2-Konvention und Board-Profil Endgerät (Stand 2026-10-05, Firmware vorbereitet, alles ungetestet)

Keine Hardware vorhanden: nichts davon wurde an einem Klickrad, einer Hauptplatine oder einem ESP32-S31 geprüft.

### 8.1 Klickrad-Konvention (umgesetzt in `firmware/components/clickwheel`, `firmware/main/input.c`)

- Konvention laut `TEILE.md` („Klickrad v2“, aus dem Tangara-Footprint gerechnet, **nicht gemessen**): Wheel-Position 0 oben, steigend gegen den Uhrzeigersinn (64 links, 128 unten, 192 rechts); Stecker bei 270° (unten) = Position 128.
- Umsetzung: `cw_config_wheel_v2(cfg, mount_offset_deg, mirrored)` setzt den Bildschirm-Winkel von Position 0 auf −90° + Offset und den Drehsinn auf „gegen den Uhrzeigersinn“. Die Kconfig-Optionen `NANO_WHEEL_FIRST_SEGMENT_DEG`/`NANO_WHEEL_CLOCKWISE` gelten jetzt nur noch für den MPR121 (v1); für den AT42QT2120 gibt es `NANO_WHEEL_V2_MOUNT_OFFSET_DEG` (Default 0 = Stecker unten) und als Gegenprobe `NANO_WHEEL_V2_MIRRORED` (Default aus).
- Drehrichtung im UI: Finger im Uhrzeigersinn → Bildschirmwinkel steigt → positive Rasterschritte → `model_step(+1)` → Auswahl **nach unten**; Finger gegen den Uhrzeigersinn → nach oben. Tippen: Position 0 = MENU (oben), 128 = PLAY (unten), 64 = PREV (links), 192 = NEXT (rechts).
- Befund: Der bisherige Default (−90°, gegen den Uhrzeigersinn) stimmte bereits mit dieser Konvention überein; der alte Host-Test (Test 5) prüfte aber ein im Uhrzeigersinn steigendes Rad und damit nicht die tatsächlich gebaute Konfiguration. Der Test ist neu geschrieben (Positionen 0/64/128/192, Drehen in beide Richtungen mit Rundlauf über 0, Tippen in vier Richtungen, Einbau-Offset, Spiegelung) und läuft grün (`gcc -Wall -I../include test.c ../clickwheel.c -lm && ./a.out`).
- **Ungeprüft:** ob die Elektrodenlage und Verdrahtung des gebauten Klickrads v2 wirklich so liegen. Nach dem Aufbau mit `NANO_WHEEL_LOG_RAW` Position 0/64/128/192 anfahren; läuft das UI falsch herum, zuerst `NANO_WHEEL_V2_MIRRORED`, sonst `NANO_WHEEL_V2_MOUNT_OFFSET_DEG` anpassen. Orientierung in der Hauptplatine: Stecker J21 bei (0; −46,2) unten, passt zu „Stecker unten“.

### 8.2 Vergleich Pin-Tabelle Hauptplatine Rev. 3b ↔ `firmware/main/board_config.h` (Prototyp)

| Thema | Prototyp (Waveshare) | Endgerät Rev. 3b | Folge in der Firmware |
|---|---|---|---|
| I²C | SDA IO15 / SCL IO14, Pull-ups auf dem Board | SDA IO6 / SCL IO7, Pull-ups R120/R121 auf der Hauptplatine | Profil. Auf dem Prototyp sind IO14/IO15 der I²C-Bus, am Endgerät frei (kein Konflikt, Pins nicht belegt) |
| Klickrad CHANGE / BTN | IO17 / IO18 (Testpunkte) | WHEEL_INT = IO0 (LP-GPIO, Weckquelle); **kein BTN** (Stecker-Pin 6 Reserve) | `WHEEL_BTN_USED = 0`, Mitteltaste nur kapazitiv (QT2120-Taste 3) |
| IO-Expander | TCA9554 0x20 (LCD_RST, Display-Versorgung, Touch-Reset, SD-CS) | entfällt; LCD_RST = IO19, DSI_PWR_EN/TP_RESET fest verdrahtet | `BOARD_HAS_TCA9554 = 0` |
| Display | 368 × 448 (1,8"), QSPI CS12/SCK11/D0..3 = 4..7, Gap x 0x10 | 410 × 502 (2,06"), CO5300, SCK IO48, CS IO49, D0 IO11, D1 IO10, D2 IO9, D3 IO51, TE IO12, TP_INT IO50 | Auflösung als Makros (Init-Befehle 0x2A/0x2B und `ui.c` folgen `BOARD_LCD_*_RES`); Gap [offen] |
| Lader-Steuerung | – (AXP2101 0x34) | MCP73871 SEL/PROG2 fest verdrahtet, **keine GPIO**; STAT1 IO13, STAT2 IO16, PG IO17; IO14/IO15 frei | in der Firmware nichts zu steuern; Pins nur als Makros dokumentiert (kein `PowerManager`-Code in Phase 1) |
| DAC-Reset | – (ES8311) | DAC_RESET = IO20 mit Reset-Sicherung: offen/high = DAC im Reset, low = freigegeben; Q21/Q22 halten Reset ohne 3V3 | Phase 1 lässt IO20 unberührt (DAC bleibt im Reset). Audio-Code später: erst Versorgung stabil, dann IO20 auf low. Reset-Logik ungeprüft (Schaltschwelle, Anlauf) |
| Power-Latch | – | SYS_PWR_EN = IO4 (LP-GPIO), KEY_LOCK_MCU = IO5 (Taster lesen) | `board_init()` setzt IO4 sofort auf `BOARD_PWR_HOLD_LEVEL` (1, **Aktivpegel [offen]**); IO5 nicht ausgewertet |
| BOOT / EN | USB-Serial-JTAG des Waveshare-Boards | BOOT = IO61 (SW2), EN (SW3), Rückseite; IO60/IO61 Boot-Modus, IO33/34 USB-Serial/JTAG, IO36/IO37 Strapping | keine Firmware nötig; diese Pins werden nicht belegt |
| I²C-Adressen | 0x15 CST820, 0x18 ES8311, 0x20 TCA9554, 0x34 AXP2101, 0x51 PCF85063, 0x6B QMI8658 | 0x1C QT2120, 0x5A DRV2605L, 0x36 MAX17048, 0x47 TUSB320LAI, CS43131 0x30..0x33 [?] hinter PCA9306; Display-Touch [offen] | Adressen als Makros; keine Kollision bekannt |
| PCA_EN | – | Kein GPIO: gemeinsamer Knoten VREF2/EN des PCA9306 (U30), 200 k nach 3V3 + 100 pF | nichts zu tun; Hinweis: solange 1,8 V (U34) fehlt, ist der DAC-Bus getrennt, der I²C-Scan sieht den CS43131 ggf. nicht |
| I²S / SD | – | I²S BCLK/LRCK/DOUT IO22/23/24 (S31 = Slave, DAC liefert Takt), SDMMC Slot 2 IO35..IO40, SD_CD IO25, SD_VDD_EN IO42 | nur als Makros bzw. Kommentar; Phase 1 hat keinen Ton und keine SD |
| Latenz-Messpunkte | IO38/IO39 | keine vergeben | Kconfig `NANO_LATENCY_PROBE` nur beim Prototyp |

### 8.3 Board-Profil „Endgerät“ (Kconfig `Board-Profil`)

- Auswahl: `idf.py menuconfig` → Nano-Player → Board-Profil → „Endgeraet“. Datei `firmware/main/board_config_endgeraet.h`; `board_config.h` schaltet per `CONFIG_NANO_BOARD_ENDGERAET` um. Beim Endgerät sind SH8601, eigener Wheel-Bus, BTN-Pin und Latenz-Messpunkte in Kconfig ausgeblendet.
- **Nicht für den S31 gebaut:** IDF 5.4.2 kennt das Ziel nicht (S31 ab IDF 6.x, „preview“). Als Syntaxprüfung wurde das Profil höchstens mit dem Ziel esp32s3 und eigener Build-Umgebung übersetzt (Ergebnis: Übersetzung bricht erwartungsgemäß bei `GPIO_NUM_49` ab, weil der ESP32-S3 keine GPIO49..51 hat; weitere Fehler wurden nicht untersucht, der Lauf war nur ein Versuch); das sagt nichts über Pinzulässigkeit oder Verhalten auf dem S31 aus (IO42, IO48..IO51 existieren beim S3 anders belegt).
- Gewählt wurde bewusst nur, was die README eindeutig festlegt; Unklares steht in 8.4.

### 8.4 Offen / TODO für das Profil

1. **Panel-Versatz (Gap x/y) und Init-Sequenz des 2,06"-CO5300** sind nicht ausgewertet (Waveshare-2.06-Beispiel); Gap steht auf 0, Init-Befehle sind die des 1,8"-Moduls mit angepasster Fenstergröße.
2. **Display-Touch** (Controller, Adresse, Reset/INT-Nutzung) ist nicht geklärt und in Phase 1 nicht im Einsatz (`board_touch_is_v2()` ist beim Endgerät nur ein Platzhalter).
3. **Aktivpegel Power-Latch SYS_PWR_EN** (IO4) aus dem Schaltplan prüfen; falsche Annahme = Gerät schaltet nach dem Loslassen von SW1 ab oder lässt sich nicht ausschalten. KEY_LOCK_MCU (IO5) und Abschalten fehlen (`PowerManager`, Abschnitt 2).
4. **Zulässigkeit der Zuordnungen auf dem S31** (SPI-Host-Wahl für QSPI-Display, I²C-Port, GPIO-Matrix, LP-GPIO für IO0/IO4/IO5, SDMMC-Slot 2) ist laut Platinen-README selbst ungeprüft (Datenblatt v0.5); in IDF 6.x gegenprüfen.
5. **CS43131-Adresse** (0x30..0x33 [?]), Verhalten des PCA9306 ohne 1,8 V und Takt/Quarz-Start: Audio-Phase.
6. **DAC-Reset-Sicherung** (Q20/Q21/Q22/R250) ungeprüft; Polarität im Code erst beim Audio-Treiber festlegen.
7. **USB/TUSB320, Host-VBUS (IO2), Lader-STAT/PG, MAX17048:** nur Pin-Makros, keine Treiber.
8. **Mitteltaste:** beim Endgerät nur kapazitiv (QT2120 Taste 3), Guard Taste 4; Pin 6 am Stecker ist Reserve.
9. **Klickrad-Stecker/Footprints** (J1 ↔ J21, siehe Platinen-README Review H6/K1) sind ungeprüft; Kabel durchklingeln, bevor die Firmware gegen das Rad läuft.
10. Schwelle für „Tippen“ (`NANO_WHEEL_TAP_SLOP_DEG`) und Raster (15°) sind für 256 Positionen/360° aus dem Prototyp übernommen, am echten Rad prüfen.

## Quellen

- Espressif Developer Portal, „ESP32-S31 status“ (Stand 25.09.2026): https://developer.espressif.com/hardware/esp32s31/
- ESP-IDF v6.1 Programming Guide, „Bluetooth Classic – ESP32-S31“: https://docs.espressif.com/projects/esp-idf/en/stable/esp32s31/api-reference/bluetooth/classic_bt.html
- Beispiel `a2dp_source` (ESP32 und ESP32-S31): https://github.com/espressif/esp-idf/blob/master/examples/bluetooth/bluedroid/classic_bt/a2dp_source/README.md
- ESP-IDF Releases (v6.0.x: „preview support for ESP32-S31“): https://github.com/espressif/esp-idf/releases
- Espressif, Vorstellung ESP32-S31 (26.03.2026): https://www.espressif.com/en/news/ESP32_S31_Release
- Datenblatt ESP32-S31-WROOM-3: https://documentation.espressif.com/esp32-s31-wroom-3_wroom-3u_datasheet_en.pdf
- IDF-6.0-Migrationsleitfaden Peripherals (legacy I²C EOL): https://docs.espressif.com/projects/esp-idf/en/stable/esp32/migration-guides/release-6.x/6.0/peripherals.html
- `btc_a2dp_source.c` in IDF v6.1/master (PCM-Rate aus SBC-Konfiguration): https://github.com/espressif/esp-idf/blob/v6.1/components/bt/host/bluedroid/btc/profile/std/a2dp/btc_a2dp_source.c
- Tangara-Firmware (lokal): `/home/user/tangara-ref/tangara-fw`
