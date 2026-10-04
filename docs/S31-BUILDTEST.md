# ESP32-S31: Machbarkeits-Build

Stand 2026-10-04. Frage: Gibt es Toolchain und Komponenten für den ESP32-S31, bevor Platinen bestellt werden? Testprojekte liegen in `firmware-s31-test/` (je ein Ordner pro Test, `build/` und `managed_components/` wurden danach gelöscht, `dependencies.lock` bleibt als Versionsnachweis).

**Nur Build-Tests.** Es gibt keine S31-Hardware, nichts wurde ausgeführt, geflasht oder emuliert. „Baut“ heißt: Konfiguration, Kompilieren, Linken und Image-Erzeugung laufen fehlerfrei durch. Das sagt nichts über Laufzeitverhalten, Pin-Belegung, Timing oder Stabilität aus. Die Pins in den Testprojekten sind willkürlich.

## Umgebung

- ESP-IDF **v6.1** (Tag `v6.1`, Commit `fff9895c82d744c7237be8847347bdd1b07c6643`), installiert nach `/root/esp-idf-v6` (`git clone --depth 1 --branch v6.1 --recursive --shallow-submodules`, `./install.sh esp32s31`). Die bestehende Installation `/root/esp-idf` (v5.4.2) blieb unverändert.
- Neuere Tags auf GitHub: v6.1 ist der neueste Release (zusätzlich v6.1-rc1/beta1, v6.0.x). `master` wurde nicht getestet.
- Toolchain: `riscv32-esp-elf` esp-15.2.0_20251204 (S31 ist RISC-V, **zwei Kerne**, 240 oder 320 MHz wählbar), esptool 5.4.0, Component Manager 3.1.2.
- Der S31 ist in `idf.py` weiterhin **Preview-Target**: `idf.py --preview set-target esp32s31` ist nötig. Ohne `--preview` bricht die Konfiguration mit „compiler not found“ ab (irreführende Meldung, Ursache ist das fehlende Flag). `./install.sh esp32s31` genügt für die Toolchain, `--preview` gehört nur an `idf.py`.
- Host: Python 3.11, 4 Kerne.

## Ergebnis

| Test | Baut? | Details, Fehler, Workaround |
|---|---|---|
| a) Hello World | **ja** | Binär 0x26510 Byte. Nur `--preview` nötig. |
| b) Bluetooth Classic A2DP Source (`examples/bluetooth/bluedroid/classic_bt/a2dp_source`, unverändert) | **ja** | Binär 0xff0f0 Byte. Die `sdkconfig.defaults` des Beispiels reichen (`BT_ENABLED`, `BT_BLUEDROID_ENABLED`, `BT_CLASSIC_ENABLED`, `BT_A2DP_ENABLE`, `BTDM_CTRL_MODE_BR_EDR_ONLY`, `BT_BLE_ENABLED=n`, `PARTITION_TABLE_SINGLE_APP_LARGE`). Es gibt eine leere `sdkconfig.defaults.esp32s31`. Im Link sind `esp_a2d_source_init` und `esp_bt_controller_init` enthalten, der Controller liegt als Binärbibliothek vor (`components/bt/controller/lib_esp32s31/esp32s31-bt-lib`, `libbredr_app.a`). Die Soc-Caps nennen `SOC_BT_CLASSIC_SUPPORTED`. |
| c) QSPI-LCD `esp_lcd_co5300` + LVGL 9 über `esp_lvgl_port` | **ja** | Aufgelöst vom Component Manager: `esp_lcd_co5300` 2.2.0, `esp_lvgl_port` 2.9.0, `lvgl/lvgl` **9.6.0~1**. Binär 0x91e60 Byte. Es gab keine Anpassung am Code gegenüber `firmware/main/display.c`. Das SPI-Hostmodell (`spi_bus_initialize`, `CO5300_PANEL_BUS_QSPI_CONFIG`) kompiliert unverändert. Auch `esp_lcd_sh8601` 2.x ist in der Registry. |
| d) I²S std, Slave, 32 Bit (24 Bit im Config-Feld umschaltbar) | **ja** | `esp_driver_i2s` vorhanden, `i2s_std.c`, `I2S_ROLE_SLAVE`. Soc-Caps: I²S HW-Version 2, TDM, PDM, APLL, externer Takt. Binär 0x37f50 Byte. Ungeprüft: Slave-Timing (BCLK/WS vom DAC bzw. Codec), Verhalten bei 24 Bit im 32-Bit-Slot. |
| e) USB Host + UAC + TinyUSB Device | **ja** | `SOC_USB_OTG_SUPPORTED`, ein OTG-Port, `esp_hal_usb/esp32s31` vorhanden. Aufgelöst: `espressif/usb` 1.5.0 (der USB-Host-Stack ist seit IDF 6 eine verwaltete Komponente, nicht mehr in `components/`), `espressif/usb_host_uac` 1.5.0, `espressif/esp_tinyusb` 2.3.0, `espressif/tinyusb` 0.21.0~2. Im Link: `usb_host_install`, `uac_host_install`, `tinyusb_driver_install`, `dcd_init`. Binär 0x42530 Byte. **Nur Linken getestet**: Host und Device laufen am S31 nicht gleichzeitig (ein Port), im Test wurden beide Treiber nur in ein Image gelinkt. |
| f) Bestehende `firmware/` (Kopie) mit `set-target esp32s31` | **ja, ohne Quelländerung** | 1913 Ninja-Schritte, 0 Warnungen, Binär 0x9c740 Byte (39 % der 1-MB-Partition frei, Standardtabelle). Geändert wurde nur die Kopie: die Zeile `CONFIG_IDF_TARGET="esp32s3"` in `sdkconfig.defaults` wurde entfernt. Die Abhängigkeit `lvgl ~9.3.0` löste den Stand 9.3.0 auf. Der Build nutzt weiter `CONFIG_SPIRAM_MODE_OCT` (S31 hat OPI-Support in den Soc-Caps) und erzeugte S31-Standardwerte für PSRAM-Takt (200 MHz). Diese Werte wurden nicht auf Plausibilität geprüft. Fehlerkategorien: keine. |

## Beobachtungen

- Alle Komponenten, die wir brauchen, sind für den S31 vorhanden: Controller-Bibliothek für BR/EDR, Bluedroid-A2DP, `esp_lcd`/SPI, `esp_driver_i2s`, USB-OTG-HAL, SDMMC (`SOC_SDMMC_HOST_SUPPORTED`, 2 Slots, 4 Bit), PSRAM, WLAN, dazu BLE.
- IDF 6.x entfernt Altlasten. Unsere Phase-1-Firmware baut trotzdem unverändert, weil sie schon die neuen I²C- und SPI-Treiber nutzt. Für die Tangara-Portierung (siehe `FIRMWARE-PORTIERUNG.md`) bleibt das IDF-5.5-auf-6.x-Thema real, wurde hier aber nicht untersucht.
- Die S31-Kconfig enthält „Bringup“-Schalter (`ESP_BRINGUP_BYPASS_*`), sie sind für diesen Chip aber aus (Clock-Tree und RNG unterstützt).
- Preview-Hinweise im Build: Kconfig-Meldungen zu `BT_NIMBLE_MESH_PROVISIONER` und `FATFS_PRINT_*` (`default 0` bei bool). Das sind harmlose Hinweise aus IDF selbst, kein S31-Problem.
- Component-Manager-Versionen: keine der genannten Komponenten sperrt den S31 über ein `targets`-Feld. Das ist aus dem erfolgreichen Auflösen und Bauen abgeleitet, nicht aus den Herstellerdokumenten.

## Risikoeinschätzung

| Bereich | Risiko | Begründung |
|---|---|---|
| Toolchain / IDF | niedrig bis mittel | IDF 6.1 baut alles ohne Eingriff. Der S31 bleibt „Preview“, Bugs und Änderungen zwischen Patch-Releases sind möglich. IDF-Version im Projekt fest pinnen. |
| Bluetooth-Kopfhörer (A2DP Source) | **mittel bis hoch** | Bauen ist erledigt, aber das ist die schwächste Stelle: Controller ist eine Binärbibliothek im Preview-Zustand, Interoperabilität mit echten Kopfhörern, Audioaussetzer und Koexistenz mit WLAN/USB sind nur mit Hardware prüfbar. Kein Build-Test kann das ersetzen. Mit dem Waveshare-S3 geht A2DP-Test **nicht** (kein Classic). |
| Display (CO5300, QSPI, LVGL 9) | niedrig | Treiber und Port bauen unverändert. Der QSPI-Pfad ist derselbe wie bei Phase 1; Prototyp mit S3 prüft Treiber und LVGL-Teil, der S31-SPI-Host bleibt ungeprüft. |
| USB-Audio (UAC Host) | mittel | Komponenten bauen. Als Fallstrick: nur **ein** USB-OTG-Port, Host (UAC) und Device (MSC) schließen sich aus; ein Betriebsmodus-Wechsel ist nötig. Reife des S31-USB-Hosts unbekannt (Preview). |
| I²S zum DAC | niedrig | Treiber vollständig. Ungeprüft sind Slave-Timing und 24/32-Bit-Format am echten Codec. Wir betreiben den S31 normalerweise als Master, Slave nur falls nötig. |
| Gesamt | mittel | Kein Ausschlusskriterium gefunden. |

## Empfehlung

1. **Platinenbestellung für den S31 ist aus Software-Sicht nicht blockiert.** Alle geprüften Komponenten bauen auf IDF 6.1.
2. Vor der Bestellung der Endplatine mit S31 ein **S31-Entwicklungsboard** kaufen (falls erhältlich), um Bluetooth (A2DP zu realen Kopfhörern), USB-UAC und PSRAM zu testen. Das ist die einzige Möglichkeit, die offenen Hauptrisiken zu klären.
3. Die Prototypenplatine (Waveshare ESP32-S3) bleibt für Display, Klickrad und Haptik die richtige Wahl. Bluetooth-Kopfhörer gibt es dort nur über BLE-Audio-Ansätze, nicht über A2DP.
4. Fallback für Bluetooth einplanen (offener Punkt in `KONZEPT.md`): externes Bluetooth-Audio-Modul oder ein zusätzlicher Chip mit Classic-BT, falls der S31-Controller instabil ist. Das ist nur ein Hinweis; die Entscheidung liegt beim Projektinhaber.
5. IDF auf **v6.1** pinnen (`Commit fff9895c`), Abhängigkeiten per `dependencies.lock` festhalten. Bei jedem IDF-Patch den Buildtest wiederholen: `idf.py --preview set-target esp32s31 build` in den Ordnern unter `firmware-s31-test/`.

## Reproduktion

```
git clone --depth 1 --branch v6.1 --recursive --shallow-submodules https://github.com/espressif/esp-idf /root/esp-idf-v6
cd /root/esp-idf-v6 && ./install.sh esp32s31 && . ./export.sh
cd /home/user/tangara/firmware-s31-test/<test> && idf.py --preview set-target esp32s31 && idf.py build
```
