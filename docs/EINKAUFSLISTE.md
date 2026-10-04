# Einkaufsliste Phase 1 (inkl. Klickrad-Modul)

Budget: **100–150 €** ohne Filament. Preise sind **Richtwerte aus dem Gedächtnis, nicht verifiziert** (Stand Okt 2026, inkl. grob geschätztem Versand/MwSt.). Suchbegriffe sind Suchtexte für AliExpress/Banggood, keine Produktlinks. Hintergrund zum Board: `RECHERCHE.md`.

## Liste

Spalte „€“ = Gesamtpreis der Zeile (Menge schon eingerechnet).

| Nr | Teil | Zweck | Menge | Suchbegriff | € | Prio |
|---|---|---|---|---|---|---|
| 1 | Waveshare ESP32-S3-Touch-AMOLED-1.8 | Hauptboard | 1 | `Waveshare ESP32-S3-Touch-AMOLED-1.8` (Waveshare-Shop oder AliExpress „Waveshare Official Store“); Variante SKU 29957 | 35 | muss |
| 2 | Klickrad-Platine, Fertigung | Ø 32 mm, 2 Lagen, 1,0 mm, rund | 5 Stück | JLCPCB: „PCB prototype, 5 pcs, 1.0 mm, HASL lead-free“, Gerber-ZIP aus `hardware/pcb/`; ca. 2 € Platine + Versand nach DE | 12 | muss |
| 3 | MPR121 (QFN-20) | Touch-Controller | 3 | `MPR121QR2` (LCSC/Mouser sicherer als AliExpress, dort Fälschungen möglich) | 5 | muss |
| 4 | DRV2605L (VSSOP-10) | Haptiktreiber | 3 | `DRV2605LDGSR` | 6 | muss |
| 5 | SMD-Taster, flach | Mitteltaste, max. 4 × 4 × 1,5 mm | 10 | `SMD tact switch ultra thin 1.5mm`, Höhe im Datenblatt prüfen | 2 | muss |
| 6 | JST-SH-Buchse 1,0 mm, 6-polig, SMD | Stecker am Modul | 10 | `SH1.0 6P SMD connector socket 1.0mm` (Ausrichtung passend zum Footprint wählen) | 2 | muss |
| 7 | JST-SH-Kabel, 6-polig, einseitig offen | Modul zu Waveshare-Pads (an 1,27-mm-Pads löten) | 5 | `JST SH 1.0mm 6 pin cable single end 100mm 28AWG` | 3 | muss |
| 8 | SMD-Widerstände und -Kondensatoren | 0402/0603-Kleinteile (100 nF, 1 µF, 10 µF, 10 k, 1 k, 0 Ω) | Sortiment | `0603 resistor kit 1% assortment`, `0603 capacitor kit`, bei Bedarf `0402 capacitor kit` | 8 | muss |
| 9 | X-Achsen-LRA, 3 Typen | Haptik vergleichen, siehe unten | 3 × 1–2 | `X axis linear vibration motor` mit Maßen (siehe Tabelle LRA) | 9 | muss |
| 10 | LiPo 1S 3,7 V mit Schutzschaltung, MX1.25 2P | Stromversorgung | 1 | `3.7V 400mAh lipo battery MX1.25 2pin` (Waveshare empfiehlt 3,85 × 24 × 28 mm; Polung am Board prüfen) | 8 | muss |
| 11 | M2-Schrauben-Sortiment | Gehäuse, Klickrad | 1 Set | `M2 screw assortment kit pan head 4 6 8 10mm` | 4 | muss |
| 12 | M2-Gewindeeinsätze (Einschmelz) | Gehäuse | 50–100 | `M2 brass heat set insert knurled M2x3 OD3.2` | 4 | muss |
| 13 | Logic Analyzer 8 Kanäle | Latenz und I²C messen (sigrok/PulseView) | 1 | `USB logic analyzer 24MHz 8 channel` | 9 | soll |
| 14 | Flussmittel (no-clean, Spritze) | SMD löten | 1 | `no clean flux paste syringe` | 5 | soll |
| 15 | Lötpaste, niedrig schmelzend | QFN/VSSOP | 1 | `Sn42Bi58 solder paste 138C syringe` | 8 | soll |
| 16 | Mini-Heizplatte | Reflow für das Klickrad; entfällt, wenn Heißluft vorhanden | 1 | `mini hot plate SMD preheater` | 15 | soll |
| 17 | Pinzette, Entlötlitze, Kapton-Band | Löthilfe | 1 Set | `ESD tweezers set`, `desoldering wick 2mm`, `kapton tape` | 6 | soll |
| 18 | Silikonlitze 28–30 AWG | LRA-Anschluss, Bastelverbindungen | 1 | `silicone wire 30AWG` | 4 | soll |
| 19 | Lötschablone (Stencil) | Pastendruck, nur mit der PCB-Bestellung sinnvoll | 1 | JLCPCB „SMT stencil“, Rahmenlos | 8 | kann |
| 20 | Taptic-Engine-Ersatzteil (iPhone) | Referenz-Haptik (laut `PLAN.md`) | 1 | `iPhone 7 taptic engine replacement` | 10 | kann |

## Summen

| Stufe | Summe |
|---|---|
| Muss (Nr. 1–12) | 98 € |
| Muss + Soll (Nr. 1–18) | 145 € |
| Alles inkl. Kann (Nr. 1–20) | 163 € |

Zeilen: Muss 35+12+5+6+2+2+3+8+9+8+4+4 = 98. Soll 9+5+8+15+6+4 = 47. Kann 8+10 = 18.

**Budget:** Muss + Soll = 145 € liegt im Rahmen von 100–150 €, aber nur mit 5 € Reserve. Die Kann-Zeilen sprengen es (163 €) und werden nicht bestellt. Preisabweichung beim Board (Waveshare kostet oft 40 € und mehr) frisst die Reserve.

**Weglassen, wenn es knapp wird** (Reihenfolge):
1. Nr. 20 und 19 (Kann),
2. Nr. 16 Heizplatte, falls Heißluftstation vorhanden (-15 €), sonst Nr. 15/16 mit der Heißluft lösen,
3. Nr. 18 und 17 (Litze und Kleinwerkzeug aus Bestand),
4. Nr. 13 Logic Analyzer nur, wenn das Latenz-Ziel (< 10 ms) erst später gemessen wird,
5. Nr. 9 auf 2 LRA-Typen reduzieren (-3 €), Nr. 3 und 4 auf je 2 Stück (-3 €).
Mit allen Streichungen (Nr. 13, 16, 17, 18, 3 und 4, 9) sinkt Muss + Soll von 145 € auf etwa 105 €.

Nicht eingerechnet: Filament, Lötkolben/Multimeter (vorhanden angenommen), USB-C-Kabel, Mikro-SD-Karte (für Phase 1 nicht nötig), Versandkosten über das Eingerechnete hinaus.

## LRA-Kandidaten (X-Achse, rechteckig)

Die AliExpress-Teile sind meist ohne Datenblatt. Typische Bauformen und Resonanzfrequenzen am Beispiel der Datenblattangaben eines Herstellers (NFP Motor, Quelle: nfpmotor.com/products-linear-resonant-actuators-lras.html); die Maße sind brauchbare Suchwerte, die Teile auf AliExpress können abweichen:

| Typ | Maße B × L × H | Resonanz | Spannung | Suchbegriff |
|---|---|---|---|---|
| A: klein | 4,5 × 12 × 3,0 mm | 235 Hz | 1,8 Vrms | `X axis linear vibration motor 4.5x12` |
| B: quadratisch | 9,5 × 9,5 × 3,5 mm oder 8 × 9 × 3,5 mm | 170 Hz | 0,9 Vrms | `X axis LRA 9.5x9.5` / `linear resonant actuator 8x9` |
| C: Handy-Typ | 8 × 15 × 3,0 mm | 170 Hz | 0,9 Vrms | `X axis linear vibration motor 8x15` |

- Frequenz und Spannung ungeprüft für die tatsächlich gelieferten Teile. DRV2605L: Auto-Kalibrierung ausführen, Nennspannung und Resonanz in die Register eintragen.
- Zum Einbau auf der Rückseite des Ø-32-mm-Moduls (Bauteile max. 1,5 mm plus LRA): Höhe 3,0–3,5 mm einplanen; Fläche aller drei Typen passt in Ø 32.
- Vorsicht bei „Z-Achse“ / runden Münz-LRA (z. B. Ø 10 × 4 mm): schwingen senkrecht zur Platine und wirken anders.

## Hinweise zu Verbrauchsmaterial

- **Filament (nur Hinweis, nicht im Budget):** PETG für den Prototyp (steif, einfach, SV06 Ace); ASA für spätere Gehäuse auf dem Voron (Maßhaltigkeit, Wärmebeständigkeit). Steifigkeit ist für die Haptik wichtiger als Optik. Auf PLA verzichten (weich, Kriechen).
- **Gewindeeinsätze:** Einschmelzen mit Lötkolben (Spitze mit Einsatz-Aufsatz oder normale Spitze); Bohrung laut Datenblatt der Einsätze im CAD hinterlegen.
- **JST-SH-Kabel:** „Same side“-Kontakte verwenden (beide Enden gleiche Reihenfolge). Pin 1 = 3V3 muss auf beiden Seiten stimmen, sonst Kurzschluss/Falschpolung: Durchgang messen, bevor Strom anliegt.
- **Lötpaste:** Niedrig schmelzende SnBi-Paste (138 °C) schont die Platine und das Display-Board; Heizplatte nur mit dem Klickrad-Modul verwenden, nicht mit dem Waveshare-Board.
- **MPR121 und DRV2605L:** wenn möglich bei LCSC/Mouser kaufen (zusammen mit den Platinen bei JLCPCB, Versand pro Bestellung beachten), weil auf AliExpress Fälschungen kursieren. Unverifiziert, was günstiger ausfällt.
