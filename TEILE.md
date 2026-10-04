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
- Platine rund, **Ø 32 mm**, Dicke 1,0 mm, **4 Lagen** (auf 2 Lagen nicht sauber routbar; In1 = GND-Gitter unter dem Ring, In2 = 3V3)
- Touch-Segmente vorne: Ring von **r = 6,5 bis r = 12,8 mm**, 8–12 Segmente
- Mitteltaste vorne: SMD-Taster mittig, max. 4 × 4 mm, Höhe ≤ 1,5 mm
- 3 Befestigungslöcher Ø 2,2 mm auf **r = 14,6 mm** bei 90°, 210° und 330° (0° = rechts, gegen den Uhrzeigersinn)
- Rückseite: Bauteile max. 1,5 mm hoch, plus LRA (aufgeklebt, Lötpads für die Litzen)
- Abdeckung vorne (gedruckt): Ø 30 mm, liegt direkt auf der Platine

- Stecker J1 auf der Rückseite bei 270° (unten): x ±4,9, y −14,7 … −8,1 relativ zur Modulmitte, höher als 1,5 mm (Höhe prüfen)
- LRA-Freifläche auf der Rückseite: x −8 … +8, y +3 … +9; LRA-Lötpads bei x ≈ −12,3
- 12 Segmente à 30°. Zuordnung (Mittenwinkel gegen den Uhrzeigersinn ab rechts, von vorne gesehen): ELE8 15°, ELE7 45°, ELE6 75°, ELE5 105°, ELE4 135°, ELE3 165°, ELE2 195°, ELE1 225°, ELE0 255°, ELE11 285°, ELE10 315°, ELE9 345°. Firmware: Segment 0 bei 105° (Bildschirmkonvention, im Uhrzeigersinn). Am echten Rad prüfen.

**Elektrik**
- Touch-Controller: **v2: AT42QT2120 (I²C 0x1C, Wheel-Modus) nach Tangara-Vorbild**; v1 nutzte MPR121 (0x5B)
- Haptik-Treiber: DRV2605L (I²C, Adresse 0x5A fest), LRA-Modus
- Mitteltaste: nach GND, Pull-up auf der MCU-Seite

**Änderung für das dünne Endgerät (Entscheidung nach `docs/DUENNBAU.md`):** JST-SH ist mit ca. 4 mm zu hoch. Klickrad v2 bekommt einen **flachen 6-poligen FPC/FFC-Stecker (≤ 1,2 mm)** mit derselben Pinbelegung; am Waveshare-Prototyp über eine FFC-Breakout-Platine. Mitteltaste v2 **kapazitiv** (AT42QT2120 Key 3), Pin 6 wird Reserve. Platine 0,8 mm, Rückseitenbauteile ≤ 0,8 mm, flacher LRA (z. B. Vybronics VL120628H, 12 × 6 × 2,0, prüfen), Abdeckung 0,6-mm-FR4.

**Stecker v1: JST-SH 1,0 mm, 6-polig** (v2: FPC/FFC, gleiche Belegung)

| Pin | Signal |
|---|---|
| 1 | 3V3 |
| 2 | GND |
| 3 | SDA |
| 4 | SCL |
| 5 | INT / CHANGE (AT42QT2120 bzw. MPR121, open drain, aktiv low) |
| 6 | BTN (Mitteltaste, aktiv low) |

DRV2605L-EN fest auf 3V3; Standby per I²C.

## Endgerät: Ziel-Stack-up (Entscheidung nach `docs/DUENNBAU.md`, Variante A)

| Punkt | Entscheidung |
|---|---|
| Außenmaße | ca. **40 × 90 × 8,5 mm** (8,2 nominal + 0,3 Reserve; Rückfall 9,0) |
| Display | **2,06" AMOLED 410 × 502, CO5300, QSPI** (ca. 315 ppi). Auflösung beim Händler vor dem Kauf prüfen. |
| MCU-Modul | ESP32-S31-**WROOM-1** (18 × 25,5 × 3,1) statt WROOM-3, sofern alle benötigten Pins herausgeführt sind (prüfen) |
| Hauptplatine | 0,8 mm, hohe Teile nur auf der Rückseite (≤ 3,3 mm), ca. 37 × 84 mm |
| Klinke | SJ-43504-SMT-TR (5,0 mm) in Randausschnitt der Platine (statt SJ-3506, 6,0 mm). Risiko: Überstand nach vorn ungeprüft. |
| Akku | Pouch 3,0 mm (303450, 500–600 mAh), Fach 34 × 50 × 3,3 |
| Front/Rückseite | Front 0,8-mm-Acryl oder Glas, Rückwand 1,0 mm gedruckt oder 0,8-mm-FR4 |

Die Maße darunter beschreiben noch den ersten Entwurf (12,2 mm) und werden mit dem neuen CAD ersetzt.

## Endgerät (erster Entwurf, siehe `hardware/render/explosionsmodell.html`)

| Teil | Maße |
|---|---|
| Gehäuse außen | 42 × 95 × 12,2, Ecken r = 7, Wand 1,4, Trennfuge bei z = 6 |
| Display-Fenster | 30,2 × 36,7, Mitte bei y = +21 (Gehäusemitte = 0) |
| Klickrad-Öffnung | Ø 30,6, Mitte bei y = −27 |
| Klickrad-Abdeckung | Ø 30 / Ø 11,6, 1,95 dick |
| Hauptplatine | 38 × 89 × 1,0, Ecken r = 5 |
| Akku | ca. 34 × 40 × 4,6 (Platzhalter) |
| Schrauben | 4 × M2, bei (±15, ±40), Gewindeeinsätze im Innenrahmen |

**Abweichungen im CAD-Entwurf** (Details: `hardware/cad/README.md`)
- Ein/Aus-Taste auf z = 9,2 statt 10,3 (sonst zu dünne Wand über der Öffnung)
- Oberschale ohne Schraubdome (Display belegt die Stellen), Halt über Innenrahmen und 4 Rastnasen; ungeprüft
- Klickrad-Platine im Endgerät vorerst mit Distanzring und Klebeband. Offen: 3 Aussparungen in der Hauptplatine für eine Verschraubung.

## Hauptplatine Endgerät: festgelegte Chips

Grundsatz: so viel wie möglich vom Vorbild Tangara übernehmen (Hardware CERN-OHL-S-2.0, Firmware GPL-3.0; lokale Kopie für die Arbeit unter `/home/user/tangara-ref/`, nicht im Repo).

| Funktion | Chip | Herkunft |
|---|---|---|
| MCU, WLAN 6, Bluetooth Classic + LE Audio, USB-HS-OTG | ESP32-S31-WROOM-3 | neu (Tangara: ESP32-WROVER-E) |
| DAC (Klinke, bis 24 Bit/192 kHz) | WM8523 | Tangara |
| Kopfhörerverstärker | INA1620, ±5 V aus TPS65133/TPS65135 | Tangara |
| Klinkenbuchse | SJ-3506-SMT | Tangara |
| LiPo-Lader mit Power-Path | MCP73871 | Tangara |
| 3V3 | TLV75533 | Tangara |
| USB-C-Buchse | USB4510-03-1-A | Tangara |
| USB-Audio-Host (Rollenumschaltung, 5 V) | TUSB320LAI, TPS61023, TPS2553 | neu |
| Akkustand | MAX17048 (I²C 0x36) | neu (bei Tangara über den SAMD21) |
| Touch-Rad (Klickrad-Modul v2) | AT42QT2120 (I²C 0x1C) | Tangara |
| Haptik (Klickrad-Modul) | DRV2605L (I²C 0x5A) | Tangara |

Nicht übernommen: SAMD21-Co-Prozessor und SD-Multiplexer (der S31 hat selbst USB), Display ST7735 (wir nutzen das 1,8"-AMOLED).

## Bestellstatus

Noch nichts bestellt.
