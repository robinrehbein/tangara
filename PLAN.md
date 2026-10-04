# Umsetzungsplan

Ziel: ein eigener Musikplayer nach dem Vorbild von [Tangara](https://cooltech.zone/tangara/), mit besserem Display, hochwertiger Haptik beim Scrollen und WLAN-Streaming. Hobbyprojekt, eine Person, 3D-Drucker vorhanden.

Grundsatz: **erst das Gefühl testen, dann Hardware bauen.** Jede Phase endet mit etwas, das man in der Hand halten und bewerten kann.

## Überblick

| Phase | Inhalt | Ergebnis | Aufwand (grob) | Kosten (grob) |
|---|---|---|---|---|
| 0 | Emulator-App fürs Handy | Werte für Raster, Haptik und Display stehen fest | 1–2 Wochenenden | 0 € |
| 1 | Haptik- und UI-Prototyp auf echter Hardware | Scrollen fühlt sich „premium“ an | 2–4 Wochenenden | ca. 70–100 € |
| 2 | Audio: SD-Karte, DAC, Bluetooth | Musik von SD-Karte über Kopfhörer | 3–5 Wochenenden | ca. 40–60 € |
| 3 | Wechsel auf ESP32-S31 und Tangara-Fork | eine Plattform mit allen Funktionen | 4–8 Wochenenden | ca. 30–50 € |
| 4 | Streaming über WLAN | Subsonic/Navidrome und Internetradio | 3–6 Wochenenden | 0 € |
| 5 | Eigene Platine und Gehäuse | erstes echtes Gerät | 6–12 Wochenenden | ca. 100–200 € |
| 6 | Feinschliff | Akkulaufzeit, Themes, Lua-Skripte | offen | – |

Die Aufwände sind grobe Schätzungen für einen Hobbyentwickler. Die Preise sind ungefähre Richtwerte, bitte vor dem Kauf prüfen.

---

## Phase 0: Emulator-App (Android)

Liegt im Ordner [`android-emulator/`](android-emulator/README.md).

Was die App kann:
- emuliert das Gerät: Display oben, Scrollrad unten (wie iPod bzw. Tangara)
- Display-Kandidaten in **echter physischer Größe**: Tangara-Original, IPS 2,4", AMOLED 1,8" und 2,06"
- Scrollrad mit einstellbarem Raster (Grad pro Schritt)
- Haptik über die Android-Primitives (`TICK`, `LOW_TICK`, `CLICK`), die einer Taptic Engine am nächsten kommen, plus Varianten zum Vergleichen
- Stärke, Mindestabstand zwischen Ticks und ein „Anschlag“ am Listenende sind einstellbar
- echte Musik vom Handy (Titel, Alben, Künstler), Wiedergabe, Lautstärke über das Rad
- Scroll-Test mit 1.000 Einträgen

**Was du in dieser Phase herausfinden willst:**
1. Welches Display reicht? Wie viele Zeilen braucht man, welche Schriftgröße ist lesbar?
2. Wie viele Rasterschritte pro Umdrehung fühlen sich gut an?
3. Welcher Haptik-Typ und welche Stärke gefallen dir?
4. Ab welcher Scroll-Geschwindigkeit sollen Ticks ausgelassen werden?

Die Werte trägst du am Ende in `KONZEPT.md` ein. Sie sind die Vorgaben für die Firmware.

**Wichtig:** Die Qualität hängt stark vom Handy ab. Gute Ergebnisse liefern Geräte mit gutem LRA-Motor (z. B. aktuelle Pixel oder Samsung-Galaxy-S-Modelle). Ein günstiges Handy fühlt sich schlechter an als die spätere Hardware.

**So übertragen sich die Werte auf die Hardware (DRV2605L, ungefähre Entsprechung):**

| Emulator | DRV2605L-Effekt aus der ROM-Bibliothek |
|---|---|
| Primitive: Tick | 24 „Sharp Tick 1“ |
| Primitive: Low Tick | 26 „Sharp Tick 3“ |
| Primitive: Click | 4 „Sharp Click“ |
| Anschlag (Thud) | 1 „Strong Click“ |
| Stärke | RTP-Amplitude bzw. Overdrive-Spannung |
| Mindestabstand | gleiche Logik in der Firmware |

`PlayerModel.kt` in der App entspricht der späteren UI-Logik der Firmware: Eingaben verarbeiten, Haptik auslösen, Seiten wechseln.

---

## Phase 1: Haptik- und UI-Prototyp

Ziel: dasselbe Gefühl wie im Emulator, nur mit echter Hardware und dem richtigen Motor.

Aufbau:
- Devboard mit AMOLED (z. B. Waveshare ESP32-S3-Touch-AMOLED-1.8, 368×448)
- DRV2605L-Breakout per I²C, daran ein **X-Achsen-LRA**
- Eingabe: Magnet-Encoder (AS5600 oder MT6701) mit 3D-gedrucktem Rad, alternativ ein Touch-Ring aus Kupferband an den Touch-Pins des ESP32
- Firmware: ESP-IDF und LVGL, eine Liste mit 1.000 Einträgen, ein Tick pro Eintrag

Messen und prüfen:
- Latenz von der Drehung bis zum Tick: **unter 10 ms**. Mit dem Logic Analyzer zwischen Encoder-Signal und I²C-Befehl messen.
- LRA steif mit dem Gehäuse verbinden (verschraubt oder verklebt, nicht lose)
- 2–3 verschiedene LRAs vergleichen. Zum Experimentieren eignet sich auch ein Ersatzteil-Taptic-Engine eines iPhones; dessen Daten sind nicht offiziell, der DRV2605L findet die Resonanz aber per Auto-Kalibrierung.
- Overdrive und Bremsen des DRV2605L einstellen: Der Tick soll kurz und hart sein, ohne Nachschwingen.

**Gehäuse:** Ein erstes Handgehäuse drucken (PETG oder Resin, eher steif). Das Gewicht in der Hand verändert das Haptik-Gefühl deutlich.

Ausbaustufe, falls noch mehr Qualität gewünscht ist: Cirrus CS40L2x oder Awinic AW862xx (eigene Wellenformen wie beim Handy) oder ein BLDC-Motor mit Software-Rastung nach dem Vorbild von „SmartKnob“.

---

## Phase 2: Audio

- microSD-Karte mit FAT32 oder exFAT
- I²S-DAC: zum Start ein PCM5102A-Breakout, später ein besserer DAC wie bei Tangara (WM8523 mit Kopfhörerverstärker)
- Decoder: MP3, FLAC, Opus. Tangara bringt fertige Codecs mit, die du in Phase 3 übernimmst.
- Bibliothek: Tags einlesen und indizieren. Tangara nutzt dafür LevelDB, das ist auf 10.000+ Titel ausgelegt.
- Bluetooth A2DP: Der ESP32-S3 kann das nicht. Bis zum S31 entweder einen klassischen ESP32 nutzen oder Bluetooth bis Phase 3 verschieben.

---

## Phase 3: ESP32-S31 und Tangara-Fork

- Den Quellcode der Tangara-Firmware forken (Codeberg, GPL)
- Auf ESP-IDF v6 und den ESP32-S31 portieren: Display-Treiber (QSPI-AMOLED), Haptik-Treiber, Encoder bzw. Touch-Ring
- Der SAMD21-Co-Prozessor von Tangara (Strom, USB) fällt eventuell weg, weil der S31 selbst USB hat. Dafür braucht es einen eigenen Lade- und Power-Pfad.
- Bluetooth Classic (A2DP) und LE Audio auf dem S31 testen. **Risiko:** Der Chip ist neu, Bluetooth Classic im ESP-IDF für den S31 noch jung.

---

## Phase 4: Streaming über WLAN

Reihenfolge nach Aufwand:
1. **Internetradio:** HTTP-Stream mit MP3 oder AAC, einfach
2. **Subsonic-API** (Navidrome, Jellyfin mit Plugin, Gonic): Bibliothek durchsuchen, streamen, **offline auf SD-Karte synchronisieren**
3. Server: Navidrome auf einem PC oder Raspberry Pi zu Hause
4. **Offener Punkt Spotify:** `cspot` (inoffizielles Spotify Connect für ESP32) ausprobieren. Nur Streaming, kein offline. Verstößt gegen Spotifys Nutzungsbedingungen, für privat ok.

WLAN-Verbrauch messen. Streaming kostet deutlich mehr Akku als die Wiedergabe von der SD-Karte.

---

## Phase 5: Eigene Platine und Gehäuse

- KiCad, mit dem Tangara-Schaltplan als Vorlage (CERN OHL)
- Ein **fertiges, zertifiziertes Funkmodul** nutzen (ESP32-S31-Modul), kein eigenes HF-Layout
- Akku: 1S-LiPo mit Schutzschaltung, Lade-IC mit Power-Path, Fuel Gauge
- Fertigung und Bestückung z. B. bei JLCPCB oder PCBWay
- Gehäuse: 3D-Druck, die FreeCAD-Dateien von Tangara als Ausgangspunkt

---

## Einkaufsliste

### Phase 1 (Haptik und UI)

| Teil | Beispiel | ca. Preis |
|---|---|---|
| ESP32-S3-Devboard mit AMOLED | Waveshare ESP32-S3-Touch-AMOLED-1.8 | 30 € |
| Haptik-Treiber | Adafruit DRV2605L Breakout (#2305) | 8–10 € |
| X-Achsen-LRA, 2–3 Sorten | AliExpress: „X-axis linear vibration motor“; optional Taptic-Engine-Ersatzteil | 5–20 € |
| Magnet-Encoder | AS5600- oder MT6701-Breakout mit Magnet | 3–6 € |
| Breadboard, Jumper-Kabel, Stiftleisten | | 10 € |
| Kupferband (Touch-Ring-Experiment) | | 5 € |

### Phase 2 (Audio)

| Teil | Beispiel | ca. Preis |
|---|---|---|
| I²S-DAC | PCM5102A-Breakout | 5 € |
| microSD-Modul und Karte | | 10 € |
| LiPo-Akku 1S, ca. 2.000 mAh, mit Schutzschaltung | | 10 € |
| Lade-IC | Adafruit bq24074 oder ein ähnliches Board mit Power-Path | 10 € |
| Fuel Gauge | MAX17048-Breakout | 8 € |
| Klinkenbuchse-Breakout | | 2 € |

### Phase 3

| Teil | Beispiel | ca. Preis |
|---|---|---|
| ESP32-S31-Devkit | Espressif-Store, Mouser oder DigiKey (Verfügbarkeit prüfen) | 20–40 € |

### Werkzeug (falls nicht vorhanden)

| Teil | Wofür | ca. Preis |
|---|---|---|
| Logic Analyzer, 8 Kanäle (mit PulseView/sigrok) | Latenz messen, I²C/SPI debuggen | 10–15 € |
| USB-C-Strommessgerät | Verbrauch grob messen | 15 € |
| Lötstation, Multimeter | | |
| optional: Nordic PPK2 | genaue Akkulaufzeit-Messung | ca. 100 € |

### Optional: Haptik-Drehrad mit Software-Rastung

| Teil | ca. Preis |
|---|---|
| BLDC-Gimbal-Motor (z. B. 2204) | 15 € |
| TMC6300-Motortreiber-Breakout | 15 € |
| MT6701-Encoder | 5 € |

---

## Risiken

| Risiko | Gegenmaßnahme |
|---|---|
| ESP32-S31 noch unreif (Treiber, Bluetooth Classic) | Phase 1 und 2 auf dem S3 machen, S31 erst in Phase 3 |
| Haptik fühlt sich billig an | LRA-Typ, Befestigung und Overdrive/Bremsen systematisch testen |
| Akkulaufzeit mit großem Display und WLAN | AMOLED mit dunkler UI, WLAN nur bei Bedarf einschalten |
| LiPo-Sicherheit | nur Zellen mit Schutzschaltung und Lade-IC, keine nackten Zellen |
| Projekt wird zu groß | jede Phase einzeln abschließen, Streaming erst nach funktionierendem Offline-Player |
