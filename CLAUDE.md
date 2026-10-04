# Projekt: Nano-Player

Hobbyprojekt einer Person: ein Musikplayer im Stil des **iPod nano 5. Gen.** (Hochformat-Display oben, Klickrad unten), inspiriert von [Tangara](https://cooltech.zone/tangara/). Sprache in Doku und Commits: Deutsch.

Erst lesen: `KONZEPT.md` (Entscheidungen), `PLAN.md` (Phasen), `TEILE.md` (Teile und Schnittstellen).

## Rahmenbedingungen

- Keine Teile vorhanden. Alles wird gedruckt oder bei AliExpress/Banggood bestellt.
- **Budget gesamt: 100–150 €** (ohne Filament)
- 3D-Drucker: **Sovol SV06 Ace** (FDM, ca. 220 × 220 mm) und **Voron 2.4 300 mm** (FDM, 300 × 300 mm, kann ABS/ASA). Kein Resin.
- Löten: **auch SMD** (Hot Air oder Heizplatte einplanen)
- Gewählter Haptik-Effekt aus dem Emulator: **Predefined: Click** (entspricht DRV2605L-Effekt 1 „Strong Click 100 %“ bzw. 4 „Sharp Click“)

## Feste Entscheidungen

- Plattform: ESP32. Prototyp auf **Waveshare ESP32-S3-Touch-AMOLED-1.8** (1,8" AMOLED 368 × 448), später ESP32-S31.
- Firmware: ESP-IDF und LVGL, später Fork der Tangara-Firmware
- **Klickrad-Modul** als eigene runde Platine mit Touch, Mitteltaste, Haptik-Treiber und LRA. Schnittstelle in `TEILE.md`, sie gilt für Prototyp und Endgerät.
- CAD: parametrisch als Code (CadQuery), STL-Export
- Platinen: KiCad

## Ordnerstruktur

| Ordner | Inhalt |
|---|---|
| `android-emulator/` | Handy-App zum Testen von Display und Haptik |
| `firmware/` | ESP-IDF-Projekt |
| `hardware/cad/` | CadQuery-Quellen, `stl/`, Vorschaubilder, Druckanleitung |
| `hardware/pcb/` | KiCad-Projekte, Gerber, Stückliste |
| `hardware/render/` | 3D-Explosionsmodell (HTML) |
| `docs/` | Einkaufsliste, Anleitungen |

## Arbeitsregeln

- Maße und Schnittstellen nur in `TEILE.md` ändern und dort begründen
- Was nicht geprüft werden konnte (Hardware-Test, DRC ohne KiCad), ausdrücklich als ungeprüft kennzeichnen
- Offene Entscheidungen in `KONZEPT.md` unter „Offene Punkte“ eintragen statt zu raten
- Agenten: **Sonnet, wo möglich** (Umsetzung, Recherche, CAD, Firmware, Routing); **Opus, wo nötig** (kritische Design-Reviews vor einer Bestellung, schwierige Architektur- oder Fehleranalysen)
