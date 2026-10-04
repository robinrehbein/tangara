# Teile und Schnittstellen

Gemeinsame Grundlage für Firmware, CAD und Platinen. Maße in mm. Werte mit „(prüfen)“ sind aus dem Gedächtnis und müssen gegen Datenblatt oder Herstellerseite geprüft werden.

## Phase-1-Prototyp

| Teil | Auswahl | Hinweis |
|---|---|---|
| Hauptboard | Waveshare ESP32-S3-Touch-AMOLED-1.8 | 1,8" AMOLED 368 × 448 (QSPI, SH8601), Touch, PMU AXP2101, Audio-Codec ES8311, IMU, RTC, SD (alles prüfen). Außenmaße und herausgeführte Pins prüfen. |
| Klickrad-Modul | eigene Platine, siehe unten | |
| LRA | X-Achsen-LRA, 2–3 Typen zum Vergleichen | Bauform und Resonanzfrequenz je Typ notieren |
| Akku | LiPo 1S mit Schutzschaltung, Stecker passend zum Waveshare-Board (prüfen, vermutlich MX1.25) | Größe nach Gehäuse |
| Gehäuse | Prototyp-Gehäuse v1 (FDM-Druck) | Display oben, Klickrad unten, Hochformat |

## Klickrad-Modul (eigene Platine)

Runde Platine, die Touch-Rad, Mitteltaste und Haptik vereint. Der LRA sitzt direkt auf der Rückseite, damit der Tick genau unter dem Daumen spürbar ist.

**Mechanik**
- Platine rund, **Ø 32 mm**, Dicke 1,0 mm, 2 oder 4 Lagen
- Touch-Segmente vorne: Ring von **r = 6,5 bis r = 12,8 mm**, 8–12 Segmente
- Mitteltaste vorne: SMD-Taster mittig, max. 4 × 4 mm, Höhe ≤ 1,5 mm
- 3 Befestigungslöcher Ø 2,2 mm auf **r = 14,6 mm** bei 90°, 210° und 330° (0° = rechts, gegen den Uhrzeigersinn)
- Rückseite: Bauteile max. 1,5 mm hoch, plus LRA (aufgeklebt, Lötpads für die Litzen)
- Abdeckung vorne (gedruckt): Ø 30 mm, liegt direkt auf der Platine

**Elektrik**
- Touch-Controller: MPR121 (I²C, **Adresse 0x5B**, ADDR an VDD), damit die Rohwerte der Segmente für eine feine Winkelberechnung gelesen werden können. Alternativen erlaubt, wenn sie Rohwerte liefern.
- Haptik-Treiber: DRV2605L (I²C, Adresse 0x5A fest), LRA-Modus
- Mitteltaste: nach GND, Pull-up auf der MCU-Seite

**Stecker: JST-SH 1,0 mm, 6-polig**

| Pin | Signal |
|---|---|
| 1 | 3V3 |
| 2 | GND |
| 3 | SDA |
| 4 | SCL |
| 5 | INT (MPR121 IRQ, open drain, aktiv low) |
| 6 | BTN (Mitteltaste, aktiv low) |

DRV2605L-EN fest auf 3V3; Standby per I²C.

## Endgerät (Konzept, siehe `hardware/render/explosionsmodell.html`)

| Teil | Maße |
|---|---|
| Gehäuse außen | 42 × 95 × 12,2, Ecken r = 7, Wand 1,4, Trennfuge bei z = 6 |
| Display-Fenster | 30,2 × 36,7, Mitte bei y = +21 (Gehäusemitte = 0) |
| Klickrad-Öffnung | Ø 30,6, Mitte bei y = −27 |
| Klickrad-Abdeckung | Ø 30 / Ø 11,6, 1,95 dick |
| Hauptplatine | 38 × 89 × 1,0, Ecken r = 5 |
| Akku | ca. 34 × 40 × 4,6 (Platzhalter) |
| Schrauben | 4 × M2, bei (±15, ±40), Gewindeeinsätze im Innenrahmen |

## Bestellstatus

Noch nichts bestellt.
