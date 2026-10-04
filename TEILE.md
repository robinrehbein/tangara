# Teile und Schnittstellen

Gemeinsame Grundlage für Firmware, CAD und Platinen. Maße in mm. Werte mit „(prüfen)“ sind aus dem Gedächtnis und müssen gegen Datenblatt oder Herstellerseite geprüft werden.

## Phase-1-Prototyp

| Teil | Auswahl | Hinweis |
|---|---|---|
| Hauptboard | Waveshare ESP32-S3-Touch-AMOLED-1.8 | 1,8" AMOLED 368 × 448 (QSPI), geprüft: V1 SH8601 + FT3168, **V2 (seit 30.05.2026 lieferbar) CO5300 + CST820**; PMU AXP2101, Codec ES8311 mit NS4150B -> **nur Onboard-Lautsprecher, kein Kopfhörerausgang**, IMU QMI8658, RTC PCF85063, IO-Expander TCA9554, TF-Slot. Maße laut Wiki-Zeichnung **37,6 × 45,2 × 15,0** (mit Gehäuse; nackte Platine ungeprüft). Pads 1,27 mm: VBUS, GND, 3V3, GND, TXD, RXD, **SCL = GPIO14, SDA = GPIO15** (geteilter Bus, 2,2 kΩ Pull-ups onboard), GPIO17, 18, 38–42, USB D−/D+ = GPIO19/20. Klickrad-Vorschlag: INT = GPIO17, BTN = GPIO18. Keine Adresskollision mit 0x5A/0x5B. Details und Quellen: `docs/RECHERCHE.md`. |
| Klickrad-Modul | eigene Platine, siehe unten | Anschluss an die Waveshare-Pads: 3V3, GND, SDA = GPIO15, SCL = GPIO14, INT = GPIO17, BTN = GPIO18; I²C-Pull-ups liegen schon auf dem Board, auf dem Modul nicht bestücken |
| LRA | X-Achsen-LRA, 2–3 Typen zum Vergleichen | Bauform und Resonanzfrequenz je Typ notieren. Kandidaten: 4,5 × 12 × 3,0 (235 Hz), 9,5 × 9,5 × 3,5 (170 Hz), 8 × 15 × 3,0 (170 Hz), Herstellerangaben, siehe `docs/EINKAUFSLISTE.md` |
| Akku | LiPo 1S mit Schutzschaltung, Stecker passend zum Waveshare-Board (geprüft: MX1.25, 2-polig; Polung am Board prüfen) | Größe nach Gehäuse; Waveshare empfiehlt 3,85 × 24 × 28 mm, 400 mAh |
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
