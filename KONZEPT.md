# Konzept: Musikplayer (inspiriert von Tangara)

Hobbyprojekt. Vorbild: [Tangara](https://cooltech.zone/tangara/) (Open Hardware, GPL-Firmware).

## Ziele

- Besseres Display als Tangara (dort: 1,8" TFT mit 160×128)
- Hochwertiges haptisches Feedback beim Scrollen, Richtung Apple Taptic Engine
- Lokale Wiedergabe (FLAC/MP3 von SD-Karte), Bluetooth-Kopfhörer, Klinke
- Streaming über WLAN

## Entscheidungen

| Thema | Entscheidung | Begründung |
|---|---|---|
| Plattform | **A: Mikrocontroller**, B (Linux) als Rückfalloption | Akku, sofort an, volle Kontrolle über UI und Haptik |
| SoC | **ESP32-S31** | WLAN 6 + Bluetooth Classic (A2DP) + LE Audio in einem Chip, 320 MHz RISC-V, PSRAM, 2D-Beschleuniger (PPA), Touch-Kanäle für ein Scrollrad |
| Firmware-Basis | Fork der Tangara-Firmware (ESP-IDF, LVGL, Lua) | spart sehr viel Arbeit; GPL ist für ein Hobbyprojekt kein Problem |
| Hauptplatine Endgerät | **ESP32-S31-WROOM-3** | Bluetooth-Kopfhörer sind Pflicht; kein XIAO mit Bluetooth Classic verfügbar. Prototyp bleibt auf dem Waveshare-ESP32-S3. |
| Audio über Kabel | **3,5-mm-Klinke mit Hi-Res-DAC und USB-C-Audio (Host, UAC2)** | beste Qualität über Kabel; Bluetooth auf dem ESP32 nur SBC bzw. LC3 |
| Musikquellen (Prototyp) | gekaufte, DRM-freie Dateien (z. B. Bandcamp, Qobuz) | einfach und legal |
| Gehäuse | 3D-Druck (PETG oder Resin, steif wegen Haptik) | |
| Leitziele Endgerät | **kompakt (ca. 44 × 100 × bis 10 mm, bewusst größer als die Dünnbau-Studie)**, **hochauflösendes Display**, **Top-Hi-Fi über Kabel** | Nutzervorgabe; Umsetzung in `docs/DUENNBAU.md` und `docs/AUDIO.md` |

## Prototyp 1: Haptik und Scrollen

Ziel: herausfinden, ob sich das Scrollen „premium“ anfühlt, bevor eine Platine entsteht.

- ESP32-S3- oder ESP32-S31-Devboard
- AMOLED-Modul, ca. 2", QSPI
- Haptik-Treiber TI DRV2605L (Breakout) mit **X-Achsen-LRA** (seitlich schwingend wie die Taptic Engine)
- Eingabe: Magnet-Encoder oder kapazitiver Touch-Ring
- Software: LVGL-Liste mit 1.000 Einträgen, ein Haptik-Tick pro Eintrag

Worauf es beim Haptik-Gefühl ankommt:

- Latenz unter ca. 10 ms von der Eingabe bis zum Tick
- kurze, harte Impulse mit Overdrive und aktivem Bremsen statt langer Vibration
- schnelles Scrollen: Ticks zusammenfassen oder auslassen, sonst „brummt“ es
- LRA steif mit dem Gehäuse verbinden
- eigene Stromversorgung für den Haptik-Treiber, damit kein Brummen im Audio landet

Ausbaustufen: Cirrus CS40L2x oder Awinic AW862xx für eigene Wellenformen; BLDC-Motor mit Software-Rastung (Projekt „SmartKnob“).

## Werte aus dem Emulator

Mit der App in [`android-emulator/`](android-emulator/README.md) ermitteln und hier eintragen. Der Ablauf steht in [PLAN.md](PLAN.md).

| Parameter | Wert |
|---|---|
| Display | _offen_ |
| Rasterschritt (Grad) | _offen_ |
| Haptik-Typ | Predefined: Click (DRV2605L: Effekt 1 oder 4) |
| Stärke | _offen_ |
| Mindestabstand zwischen Ticks (ms) | _offen_ |
| Anschlag am Listenende | _offen_ |

## Offene Punkte

- **Spotify:** Offline ist nicht möglich (DRM, nur offizielle Apps). Streaming wäre über `cspot` (inoffiziell, Spotify Connect) denkbar. Erst nach dem Prototyp wieder aufgreifen.
- **Weitere Streaming-Quellen:** Subsonic/Navidrome, Jellyfin, Internetradio
- **Display:** genaue Größe und Auflösung
- **Akku:** Größe und Laufzeit, Verbrauch im WLAN-Betrieb messen
- **ESP32-S31:** Wie reif sind ESP-IDF, Bluetooth Classic und die Devboards?
- **Onion Omega2+:** nur als Testgerät nutzbar (kein Bluetooth, schwache CPU)
- **Audio (aus `docs/AUDIO.md`):** Bauhöhe der Klinke am echten Teil messen; PLL-Betrieb des CS43131 gegen zweiten Quarz (24,576 MHz) messen; maximale BCLK des S31 im I²S-Slave-Betrieb prüfen; Ausgangsimpedanz und Rauschen der Ladungspumpe am Aufbau messen; CS43131 hat lange Lieferzeit (Digi-Key ca. 20 Wochen), rechtzeitig bestellen
- **Dünnbau (aus `docs/DUENNBAU.md`):** Überstand der Klinke SJ-43504 nach vorn prüfen (entscheidet 8,5 gegen 9,0 mm); Pins des ESP32-S31-WROOM-1 prüfen; 2,06"-Panel-Auflösung beim Händler prüfen
- **Devialet Phantom Reactor:** Steuerung und Wiedergabe über UPnP/DLNA als Idee für Phase 4 (nicht bestätigt)
- **Entscheidung offen: Dünn gegen Haptikqualität.** Ein 1-mm-LRA würde 8,5 mm Dicke ohne Ausschnitt erlauben, ist aber ein Z-Achsen-Typ mit wenig bewegter Masse und fühlt sich kaum wie eine Taptic Engine an. Vorschlag: Ausschnitt in der Hauptplatine als Standard, damit ein LRA bis 3,0 mm (bevorzugt X-Achse) unter das Klickrad passt. Im Prototyp beide LRA-Arten testen, dann festlegen.
- **Budget:** Gesamt grob 360–625 € (Phase 1 plus Endgerät mit PCBA), siehe `docs/KOSTEN.md`. Das ursprüngliche Budget von 100–150 € deckt nur Phase 1.
- **Hauptplatine nicht bestellbereit (Stand 2026-10-04):** platziert, aber nicht geroutet (DRC 955 Meldungen, 34 von 408 Verbindungen offen). Die Fläche reicht bei 37 × 86 mm nicht (1648 mm² verfügbar gegen 1824 mm² benötigt). Das Layout braucht einen Menschen in KiCad oder eine Abspeckung des Umfangs. Nichts bestellen, bevor das geklärt ist. Details: `hardware/pcb/hauptplatine/README.md`.
- **Hauptplatine: Akkugröße gegen LRA-Ausschnitt:** Mit dem Standard-Ausschnitt für den LRA schrumpft der Akku auf ca. 30 × 35 mm (ca. 300 mAh) oder das Gehäuse wird länger.
- **Entscheidung:** Das Gerät wird größer und dicker (ca. 44 × 100 × bis 10 mm), damit die Hauptplatine mit allen Funktionen Platz hat und routbar ist. Die Dünnbau-Studie bleibt als Referenz (`docs/DUENNBAU.md`).
- **S31-Build-Test (aus `docs/S31-BUILDTEST.md`, nur Build, nichts auf Hardware getestet):** A2DP Source, CO5300 + LVGL, I²S-Slave, USB-UAC/MSC und die Firmware-Kopie bauen mit ESP-IDF v6.1 für `esp32s31` (Preview-Target: `idf.py --preview set-target esp32s31`). IDF auf v6.1 pinnen. Größtes Risiko: Bluetooth-Kopfhörer (Controller als Binärbibliothek im Preview-Stand). Vor der Endplatine ein ESP32-S31-DevKitC-1 beschaffen und A2DP, USB-UAC und PSRAM testen. Fallback bei Problemen: externes Bluetooth-Modul. USB: nur ein OTG-Port, Host (UAC) und Device (MSC) schließen sich aus.
