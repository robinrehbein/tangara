# Dünnbau-Studie und Display-Auswahl

Stand: 2026-10-04. Vorgabe: so dünn wie möglich, hochauflösendes Display, Top-Hi-Fi-Audio (Klinke, USB-C-Audio, Bluetooth). Gehäuse FDM (Voron/ASA, SV06 Ace/PETG), Platinen bei PCBWay mit Bestückung. Maße in mm. Skizze: `docs/duennbau/stackup.svg`.

Kennzeichnung: **[geprüft]** = aus Datenblatt, Herstellerseite oder STEP-Datei gemessen. **[abgeleitet]** = aus geprüften Werten gerechnet. **[ungeprüft]** = Annahme, Schätzung oder Gedächtnis, vor dem Layout klären.

## 1. Ergebnis in Kürze

- Das aktuelle Endgerät (12,2 mm) ist ein **Klinken-getriebener Entwurf**: Die Bauteilzone hinter der Platine ist 6,2 mm hoch, weil die Klinke SJ-3506-SMT laut STEP **6,0 mm dick** ist. Danach folgen Wände (2,4), Display mit Touch (2,3) und die 1,0-mm-Platine.
- **Erreichbar: 8,2 mm nominal, 8,5 mm mit Toleranzreserve (Variante A).** Rückfall 9,0 mm (Variante B), wenn die Klinken-Montage nicht wie angenommen klappt. Stretch 7,8 bis 8,0 mm (Variante C).
- Wichtigste Maßnahmen: Klinke **SJ-43504-SMT-TR (5,0 mm statt 6,0)** von der Rückseite in einen Platinenausschnitt; **ESP32-S31-WROOM-1 (3,1 mm) statt -WROOM-3 (3,5 mm)**; alle hohen Teile auf **einer** Seite (Rückseite); Platine 0,8 mm; Akku 3,0-mm-Pouch (303040 oder 303450); Front als 0,8-mm-Acrylplatte; Rückwand 1,0 mm; LRA ≤ 2,0 mm.
- **Display: 2,06" 410 × 502 (CO5300), ca. 315 ppi**, Außenmaße des Moduls passen in 40 mm Gehäusebreite. Ein Panel ohne Touch bringt **keine** Dicke (die Dicke bestimmt der Klickrad-Stapel mit Klinke, nicht das Display). Nur Kosten und Optik.
- Gehäuse neu: **40 × 90 × 8,5** (Variante A, 2,06") statt 42 × 95 × 12,2. Zum Vergleich iPod nano 5G: 38,7 × 90,7 × 6,2.
- Preis der Dünnheit: Akku nur ca. 350 bis 600 mAh, **grob 3 bis 5 h** Wiedergabe (Schätzung). Jeder Millimeter mehr Akkudicke bringt etwa +40 bis 70 %.

## 2. Ist-Stapel des aktuellen Entwurfs (12,2 mm)

Quellen: `hardware/cad/params.py` (`E_*`), `TEILE.md`, `hardware/render/explosionsmodell.html`. Z von hinten nach vorn, Rückseite außen = 0.

| Lage | z von … bis | Dicke | Was sitzt dort |
|---|---|---|---|
| Rückschale Boden | 0 … 1,2 | 1,2 | `E_FRAME_Z0`, Boden 1,2 |
| Bauteilzone unten (Innenrahmen) | 1,2 … 7,4 | **6,2** | alle Bauteile der Hauptplatine, Akku 4,6 (Platzhalter), Klinke, USB-C, LRA-Sockel |
| Hauptplatine | 7,4 … 8,4 | 1,0 | 38 × 89 × 1,0, Bauteile nur unten |
| Luft unter dem Display | 8,4 … 8,7 | 0,3 | abgeleitet |
| Display-Modul mit Touch | 8,7 … 11,0 | 2,3 | Fensterhöhe `E_DISP_WIN` |
| Front (Oberschale Platte) | 11,0 … 12,2 | 1,2 | `E_PLATE` |
| **Summe** | | **12,2** | |

Klickrad im alten Entwurf: Abdeckung 1,95 (z 10,25 … 12,2), Klickrad-Platine 1,0 (9,2 … 10,2), Distanzring 0,8 auf der Hauptplatine, LRA 3,6 hängt durch den Ausschnitt Ø 26 der Hauptplatine nach unten (Render).

**Was die Dicke treibt** (Anteil an 12,2):

| Treiber | Anteil | Begründung |
|---|---|---|
| Bauteilzone unten 6,2 | 51 % | Mindesthöhe = Klinke SJ-3506-SMT mit **6,0 mm Dicke** [geprüft, STEP aus `tangara-ref`: Y-Ausdehnung −3,0 … +3,0]. Akku (4,6), WROVER (3,65 [geprüft, STEP]) und USB4510 (3,18 [geprüft, STEP]) liegen alle darunter. |
| Wände 1,2 + 1,2 | 20 % | Druck mit 3 Perimetern |
| Display mit Touch 2,3 + Luft 0,3 | 21 % | Deckglas 1,5 + OCA + Zelle (Datenblatt DO0180FMST08: 2,52 gesamt) |
| Platine 1,0 | 8 % | |

Nebenbefund [abgeleitet]: Klinke (x −12, bis 14 bis 15 mm tief) und der Ausschnitt Ø 26 für den LRA überlappen sich im Entwurf. Der Konflikt gehört in den Floorplan der Hauptplatine (siehe Abschnitt 8).

## 3. Gemessene und recherchierte Teile

### 3.1 Klinke

| Teil | Dicke (Höhe) | Breite × Tiefe | Anschlüsse | Status |
|---|---|---|---|---|
| CUI/Same Sky **SJ-3506-SMT-TR** (Tangara) | **6,0** (STEP) | 12,8 × 15,4 (STEP), Gehäuse 12,8 | 6 Pins, 2 Schalter, Hülse, Fuß-Pads in der Platinenebene | [geprüft] Datenblatt: „mid mount for low profile“, Bushing Ø 6,0 |
| Same Sky **SJ-43504-SMT-TR** | **5,0** (STEP: +1,9 / −3,1 um den Pad-Ursprung) | 9,1 × 14,0 | 6 SMD-Pads (alle auf F.Cu, laut Footprint der Tangara-Bibliothek), 2 Schalter, geschirmt | [geprüft] Datenblatt: „mid mount for low profile applications“, Φ 3,6 Bohrung. **Lage des STEP-Ursprungs zur Platine ungeprüft.** |
| Same Sky SJ-3502-SMT-TR | Höhe ohne Maß im extrahierten Datenblatt | ca. 12,5 lang | ohne Schalter | [ungeprüft] Maße nicht eindeutig lesbar |

Untergrenze: Eine 3,5-mm-Buchse braucht mindestens Ø 3,5 plus Wandstärken, also etwa 4,5 bis 5 mm [abgeleitet]. Eine nennenswert dünnere Standardbuchse gibt es nicht; ich habe keine gefunden. Wer weniger als 5 mm will, braucht eine Sonderbauform (nicht recherchiert).

**Folge:** Die Buchse bleibt der zweite harte Block neben dem Modul. Mid-Mount heißt hier: Buchse sitzt in einer Randaussparung der Platine, die Platine teilt die Bauhöhe auf.

Montage-Idee (Variante A) [abgeleitet, ungeprüft]: SJ-43504 **mit Pads auf der Rückseite (B.Cu)** von hinten in die Aussparung setzen. Wenn der STEP-Ursprung die Pad-Ebene ist, ragen dann 1,9 − 0,8 = **1,1 mm** über die Platinenvorderseite und 3,1 mm unter die Rückseite. Bei Pads auf der Vorderseite (Normalfall im Footprint) ragen 1,9 mm nach vorn und 2,3 nach hinten (Rückfall, Variante B).

### 3.2 USB-C

| Teil | Dicke | Breite × Tiefe | Hinweis | Status |
|---|---|---|---|---|
| GCT **USB4510-03-1-A** (Tangara, Top-Mount, 16 Pin) | **3,18** (STEP; USB-C-Norm ca. 3,26) | 11,54 × 7,2 | USB 2.0 mit Daten, Tangara-Footprint vorhanden | [geprüft] |
| GCT USB4720-03-A (Horizontal Mid-Mount SMT, 16 Pin, 1,13 mm Offset, IP67) | ca. 3,26 | – | Mid-Mount mit Datenpins | [ungeprüft]: nur Mouser-Listing, Datenblatt nicht gelesen |
| GCT USB4715-GF-A (Mid-Mount, 6 Pin) | – | – | **Nur Power, keine Datenleitungen. Für USB-Audio unbrauchbar.** | [geprüft] (DigiKey-Titel „Power Only“) |

**Empfehlung:** Mid-Mount bringt hier **nichts**. USB4510 (3,18) auf der Rückseite liegt unter der Akku- und Modulhöhe (3,3 bzw. 3,1). Mid-Mount erst bei Variante C prüfen, wenn die Rückzone unter 3,2 soll.

### 3.3 ESP32-S31-Modul

| Modul | L × B × H | Status |
|---|---|---|
| **ESP32-S31-WROOM-1** | 18,0 × 25,5 × **3,1** | [geprüft] Espressif Produktseite und Datenblatt |
| ESP32-S31-WROOM-1U | 18,0 × 20,5 × 3,2 (U.FL) | [geprüft] |
| ESP32-S31-WROOM-3 (aktuell festgelegt) | 22,0 × 30,0 × **3,5** | [geprüft] |
| ESP32-S31-WROOM-3U | 22,0 × 24,0 × 3,5 | [geprüft] |
| MINI-Typ | **existiert für S31 nicht** (Espressif-Seite listet nur WROOM-1/-1U/-3/-3U) | [geprüft], Stand der Seite 2026-08 |

Das WROOM-1 ist 0,4 mm flacher und deutlich kleiner. Beide Datenblatt-Auszüge nennen 54 GPIOs, USB-HS-OTG, SDMMC, I²S. **Offen:** Ob alle Pins, die der Entwurf nutzt, am WROOM-1 herausgeführt sind, ist nicht belegt [ungeprüft]. Pinbelegungstabelle beider Datenblätter vergleichen, bevor die Festlegung `-WROOM-3` in `TEILE.md` geändert wird. Antenne: bei beiden an der Schmalseite, der Bereich um die Antenne muss frei von Kupfer, Akku und Metall bleiben (Gehäuse aus ASA/PETG ist unkritisch).

Der nackte SoC (QFN 8 × 8) würde den Stapel weiter senken (ca. 1 mm statt 3,1), verlangt aber ein eigenes HF-Layout mit Zulassungsrisiko. Für ein Hobbyprojekt nicht empfohlen.

### 3.4 Akku (Pouch)

Nenndicke 3,0 mm; reale Zellen sind oft 3,2 bis 3,5 mm dick (mit Quellreserve) [ungeprüft, Herstellerangabe je Zelle nötig]. Rechnung mit 3,3.

| Zelle | Maße (D × B × L) | Kapazität | Quelle/Status |
|---|---|---|---|
| **303450** | 3,0 × 34 × 50 | 500 bis 600 mAh | eBay-Listing 500 mAh, kriscables 600 mAh [geprüft als Händlerangabe] |
| **303040** | 3,0 × 30 × 40 | ca. 350 bis 400 mAh | [ungeprüft], aus Gedächtnis; Händlerangabe einholen |
| 302535 / 303035 | 3,0 × 25 × 35 / 30 × 35 | ca. 250 / 300 mAh | [ungeprüft] |
| 503450 (Vergleich) | 5,0 × 34 × 50 | 1000 mAh | Amazon/fpbattery-Datenblatt [geprüft] |

Aktuell geplante Zelle (Platzhalter in `params.py`): 34 × 40 × 4,6. Eine 4,6-mm-Zelle passt in keine der Zielvarianten.

Laufzeit, grobe Schätzung [ungeprüft, nicht gemessen]: Mittlere Leistungsaufnahme bei lokaler Wiedergabe mit Display meist aus: MCU ca. 40 mA, DAC/Verstärker/±5-V-Wandler ca. 20 bis 30 mA, Display kurz an im Mittel ca. 10 bis 20 mA, Verluste: **ca. 80 bis 120 mA** am Akku. 303450 (550 mAh, 90 % nutzbar): **ca. 4 bis 6 h**. 303040 (370 mAh): **ca. 3 bis 4 h**. Bluetooth-Streaming und WLAN kosten mehr. Der Verbrauch gehört in den ersten Messungen auf dem Prototyp erfasst. Für lange Laufzeit wäre ein stromsparender Wandler/DAC mit integriertem Kopfhörerverstärker (statt DAC + INA1620 + ±5 V) der größere Hebel; das ist ein eigenes Paket und hier nicht untersucht.

### 3.5 LRA (X-Achse, flach)

Alle Werte Vybronics-Herstellerseite [geprüft], Lieferbarkeit/Preis [ungeprüft]. „Rechteck-LRA“ schwingt in der Ebene der größten Fläche, also X-Achse.

| Typ | L × B × D | Resonanz | Kraft (Grms) | Bemerkung |
|---|---|---|---|---|
| **VLV101040J-TG3** | 10 × 10 × **1,0** | 190 Hz | 2,50 bei 1,0 Vac | passt ohne Ausschnitt in den Spalt 1,1 (Variante A); Kraft ausprobieren |
| **VL120628H** | 12 × 6 × **2,0** | 200 Hz | 1,80 | braucht Ausschnitt in der Hauptplatine |
| VLV101040A | 10 × 10 × 2,5 | 170 Hz | 2,75 | stärker, aber 2,5; nur mit Ausschnitt und höherem Stapel |
| VLV200634A | 20 × 6 × 1,5 | 160 Hz | 2,40 | schlank, länger |
| VLV041235L | 12 × 4 × 1,8 | 240 Hz | 1,60 | zu schwach? ausprobieren |

Die in `TEILE.md` genannten Kandidaten (3,0 bis 3,5 mm dick) entfallen. AliExpress-Äquivalente (NFP/Jinlong, z. B. `NFP-ELV0832B` 8 × 3 mm, Rund) gibt es, mit unklaren Daten: per DRV2605L-Autokalibrierung vermessen.

## 4. Display-Vergleich

Vergleichswert iPod nano 5G: 2,2", 240 × 376, ca. 204 ppi (Vorgabe).

| | A: 1,8" / 1,78" | B: **2,06"** | C: 1,91" (LilyGo) | D: 2,16" |
|---|---|---|---|---|
| Auflösung | 368 × 448 | **410 × 502** | 240 × 536 | 480 × 480 |
| Treiber | CO5300 (V2) oder SH8601 (V1), je nach Los | CO5300 / CO5300AF-51 | RM67162 | CO5300 |
| Interface | QSPI (SPI, MIPI je nach Strap) | QSPI (Waveshare-Board), Panel-Datenblatt LX: MIPI 24 Pin | QSPI | QSPI |
| Aktive Fläche | 28,7 × 34,94 | **33,09 × 40,51** | 19,8 × 44,2 | ca. 38,8 × 38,8 (gerechnet) |
| ppi | **ca. 326** | **ca. 315** | ca. 308 | ca. 315 |
| Pixel | 165 k | **206 k (+25 %)** | 129 k | 230 k |
| Modul-Außenmaß | 33,57 × 41,2 (mit Cover, FMST08) / 32,94 × 40,64 (GL178AMC12C) | **34,79 × 43,14** (LCM); Modul-Fläche 37,26 × 44,86 | schmal | breiter als 42 |
| Dicke mit Cover + Touch | 2,52 (FMST08) / 2,25 (GL178AMC12C) | **2,05** (LX) | – | – |
| Dicke nacktes Zellenpaket | **0,85** (Zelle) + 0,175 OCA + 1,5 Cover = 2,52 (FMST08) | nicht ausgewiesen [ungeprüft] | – | – |
| Touch-IC | FT3168 (V1) / CST820 (V2, GL178: CST820) | CST9217 | – | CST9220 |
| FPC | 34 Pin (FMST08) / 24 Pin (GL178) | 24 Pin (LX) | – | – |
| Spannungen | VCI 2,7 bis 3,6; VDDIO 1,65 bis 3,4; ELVDD 4,55 bis 4,65 und ELVSS −2,25 bis −2,15 vom Treiber erzeugt [FMST08-Datenblatt, geprüft] | CO5300-Panel analog [ungeprüft] | – | – |
| Bezug | AliExpress: `DO0180FMST03` (ca. 6,89 US$), `DO0180PFST05`, „368*448 QSPI CO5300 + Touch“ (ca. 10 US$); Waveshare Board V2 | AliExpress „2.06-inch AMOLED CO5300AF-51“ (Listing nennt widersprüchlich 320×240: vor dem Kauf prüfen), lxdisplay.com, Waveshare ESP32-S3-Touch-AMOLED-2.06 | LilyGo | Waveshare ESP32-S3-Touch-AMOLED-2.16 |
| Gehäusebreite | ab ca. 38,7 | ab ca. **40** | ab ca. 30 | ab ca. 46 |

Hinweis zur Lage der FPC: In keinem Datenblatt war die Lage eindeutig lesbar. Üblich ist die FPC an der unteren Schmalseite des Panels, zur Klickrad-Seite hin [ungeprüft]. Aus dem Datenblatt für 2,06" ableitbar: Differenz Modul 44,86 − LCM 43,14 = 1,7 mm Zusatz an der FPC-Seite. Vor dem Layout Maßzeichnung des gekauften Moduls besorgen.

### 4.1 Ohne Touch?

- Das Zellenpaket allein ist **0,85 mm** dick (FMST08-Datenblatt: 2,52 = 1,5 Cover + 0,175 OCA + 0,85 Zelle). Panels „ohne Cover und ohne Touch“ sind Sonderware (OEM-Anfrage bei lxdisplay, lcdscreenmfg u. a.), ich habe **kein** Standardangebot gefunden [ungeprüft]. Die AliExpress-Typen `DO0180PFST05` / `DO0180FMST03` sind in den Listings nicht eindeutig als „touchfrei“ bezeichnet.
- **Aber:** In Variante A bestimmt der Klickrad-Stapel mit Klinke die Höhe über der Platine (2,9), nicht das Display. Das Standardmodul mit Touch (2,05 beim 2,06") passt in diese Höhe (Luft bleibt). Ein Panel ohne Touch spart also **0 mm Gesamtdicke**, solange die Klinke 1,1 mm über die Platine ragt. Es lohnt sich erst, wenn die Klinke komplett hinter die Platine rutscht (Variante C).
- Touch muss nicht beschaltet werden: Touch-IC auf der FPC ignorieren (Reset/INT unbeschaltet, Pads nicht bestücken) [ungeprüft, je nach FPC].

### 4.2 Empfehlung

**2,06" 410 × 502 (CO5300) für das Endgerät.**
- Hochauflösend: ca. 315 ppi (1,5-mal die Dichte des nano 5G), 25 % mehr Pixel als 368 × 448 bei fast gleicher Dichte, dafür 34 % mehr Fläche (1340 mm² gegen 1003 mm²).
- Gleicher Treiber (CO5300, QSPI) wie das Prototyp-Display; der Treiber-Code, `esp_lcd_co5300` (Espressif-Komponente) und das Waveshare-Board 2,06" liefern Referenz.
- Passt in 40 mm Breite: Panel 34,8 + 2 × 0,3 Spiel + 2 × 1,2 Wand = 37,8 → 40 mm lassen 1,1 mm je Seite als Blende. Länge: 3,0 Rand + 43,1 Panel + 2,0 Steg + 32 Rad + ca. 4,5 Rand = 85 → 90 mm bietet 5 mm Reserve für Klinke/USB.
- Prototyp bleibt zunächst auf dem 1,8" Waveshare-Board; die Software ist auf 410 × 502 anpassbar. Optional: Waveshare ESP32-S3-Touch-AMOLED-2.06 (Uhrenboard) als zweites Entwicklungsboard kaufen, um UI und Haptik in der Zielgröße zu testen (Maße des Boards ungeprüft).

Rückfall bei Lieferproblemen: 1,8" 368 × 448 (kleineres Gehäuse 38,7 breit, siehe Abschnitt 6).

## 5. Ziel-Stapel (Variante A, empfohlen)

Annahmen, die gelten müssen [alle abgeleitet oder ungeprüft]: Klinke SJ-43504 von hinten, Pads auf B.Cu, Ursprung = Pad-Ebene (ragt 1,1 über die Platine); LRA 1,0 mm dick ohne Ausschnitt oder 2,0 mit Ausschnitt; alle Bauteile höher als 0,8 mm auf der Rückseite; Akku 3,3 mit Reserve.

Z von hinten nach vorn:

| Lage | Dicke Alt | Dicke Neu A | Dicke Neu B (Rückfall) | Dicke Neu C (Stretch) | Anmerkung |
|---|---|---|---|---|---|
| Rückwand | 1,2 | **1,0** | 1,0 | **0,8** | A/B gedruckt (ASA, 5 Schichten à 0,2); C: 0,8-mm-FR4- oder Alu-Platte, steifer |
| Luft | (0) | 0,2 | 0,2 | 0,1 | |
| Rückzone (Akku/Modul/USB/Klinke unten) | 6,2 | **3,3** | 3,3 | 3,2 | Akku 3,0 + 0,3; WROOM-1 3,1; USB4510 3,18; Klinke unter der Platinenrückseite: 3,1 (A, Pads hinten) bzw. 3,1 − 0,8 = 2,3 (B) |
| Hauptplatine | 1,0 | **0,8** | 0,8 | 0,8 | 4 Lagen, PCBWay Standardstärke |
| Vorderseite: Luft/flache Teile (≤ 0,9) | 0,3 | **1,1** | **1,9** | 1,1 | A: Klinke ragt 1,1; B: Pads vorn, ragt 1,9; wird vom Klickrad-Bereich bestimmt (siehe unten) |
| Display: AMOLED 0,85 + OCA 0,15 (Panel ohne Cover) oder Modul 2,05 mit Touch | 2,3 | **1,0** (0,85 + 0,15) | 1,0 | 1,0 | siehe 4.1: mit Touch-Modul 2,05 passt ebenfalls (Luft schrumpft) |
| Front (Acryl/Glas) | 1,2 | **0,8** | 0,8 | 0,7 | |
| **Summe nominal** | **12,2** | **8,2** | **9,0** | **7,8** | |
| mit Reserve +0,3 | | **8,5** | 9,3 | 8,1 | Druck- und Klebetoleranzen |

Rechnung der Vorderseite Variante A: Front 0,8 + Kleber 0,1 + Klickrad-Platine 0,8 = 1,7; Luft 0,1; Klinke-Überstand 1,1 → Platinenvorderseite bei 1,7 + 0,1 + 1,1 = **2,9**. Die Luft unter dem Display ist dort 2,9 − 1,8 = 1,1. Darin passen flache Bauteile (≤ 0,9) ohne Mehrdicke, das Display-Modul mit Touch (2,05) ebenfalls.

Der LRA liegt hinter der Klickrad-Platine (z 1,8 bis 2,8 bei 1,0 mm Dicke, ohne Ausschnitt) oder reicht mit 2,0 mm durch einen Ausschnitt der Hauptplatine (z 1,8 bis 3,8).

Variante B: Klinke im Normalfall (Pads vorn): Überstand vorn 1,9 → Platine vorn 3,7 → Gesamt 9,0.

Variante C: nur mit Rückwand 0,8 (FR4/Alu), weniger Luft, Front 0,7 und exakter Zelle (≤ 3,2 mm). Erreicht ca. 7,8 mm; darunter blockieren USB4510 (3,18), WROOM-1 (3,1) und die Klinke (5,0 mm Gehäuse) die Rückzone. Weiter nur mit Sonderteilen (nackter SoC, flachere Buchse).

Gegenüberstellung der Dicke (Skizze: `docs/duennbau/stackup.svg`).

### Wandstärken im FDM-Druck

- Rückwand 1,0 mm (5 Schichten à 0,2 mm, ASA) ist druckbar, aber weich; Rippen kosten Höhe. **Rückwand als 0,8-mm-FR4-Platte** (bei PCBWay mitbestellbar) ist steifer und dünner (Variante C).
- Seitenwand 1,2 mm (3 Perimeter à 0,4). Dünner (0,8 bis 0,9 = 2 Perimeter) ist möglich, aber weniger steif; nur in Zonen ohne Last.
- Front: dünne Platte (Acryl/PC 0,8 oder Glas 0,7), laser- oder fräsgeschnitten (PCBWay/Pollen/Online-Zuschnitt), per VHB/OCA in einen Falz des gedruckten Rahmens geklebt. Gedruckte 0,8-mm-Frontplatten sind ungenau (Fenster, Planarität) und ohne Display-Deckglas zu weich.
- Sichtfläche und Lichtstreuung: Klickrad-Bereich nicht durch transparentes Filament, eher mattes Acryl mit Rückdruck.
- Schrauben: M2-Senkkopf braucht ca. 1,2 mm Wand; bei 1,0-mm-Rückwand deshalb **M1,6-Senkkopf** oder Verschraubung in den Rahmen-Seitenwänden (Domen im Rand, nicht über der Platine) [ungeprüft].

## 6. Neue Außenmaße

| | Alt | Neu, 2,06" (empfohlen) | Neu, 1,8" (Rückfall) | iPod nano 5G |
|---|---|---|---|---|
| Breite | 42 | **40,0** | 38,7 | 38,7 |
| Höhe | 95 | **90,0** | 90,7 (oder 88) | 90,7 |
| Dicke | 12,2 | **8,5** (A, mit Reserve) | 8,5 | 6,2 |
| Volumen (grob) | 48,7 cm³ | 30,6 cm³ | 29,9 cm³ | 21,8 cm³ |

Ecken: R7 aus dem alten Entwurf bleibt sinnvoll bei 8,5 mm Dicke nur als Kantenrundung in der Ebene; Rundung der Flächenkanten maximal 0,8.

## 7. Teileliste (Ziel A)

| Funktion | Teil | Höhe/Dicke | Quelle/Status |
|---|---|---|---|
| Display | 2,06" AMOLED 410 × 502, CO5300(AF-51), Modul mit Touch | 2,05 | lxdisplay.com (Datenblatt-Angaben), AliExpress; [geprüft: Maße], Bestellung offen |
| MCU-Modul | ESP32-S31-WROOM-1-N16R8V (oder N16R16V) | 3,1 | Espressif, Mouser; [geprüft] Pins vs. WROOM-3 prüfen |
| Klinke | Same Sky SJ-43504-SMT-TR | 5,0 | Same Sky, Mouser/DigiKey; [geprüft: Maße], Einbaulage ungeprüft |
| USB-C | GCT USB4510-03-1-A (Tangara-Teil) auf der Rückseite | 3,18 | Tangara-STEP [geprüft] |
| Akku | LiPo 3,0 × 34 × 50 (303450) oder 3,0 × 30 × 40 (303040), mit Schutzschaltung | 3,0 (+0,3) | Händlerangaben [ungeprüft], Datenblatt der Zelle holen |
| LRA | Vybronics VLV101040J-TG3 (10 × 10 × 1,0) oder VL120628H (12 × 6 × 2,0) | 1,0 / 2,0 | Vybronics, DigiKey/Mouser; [geprüft: Maße], Haptik auf Prototyp ausprobieren |
| Klickrad-Platine | rund Ø 32, **0,8 mm**, 4 Lagen | 0,8 | PCBWay |
| Klickrad-Abdeckung | entfällt als gedruckter Teil: Front-Platte 0,8 darüber (kapazitiv durch 0,8 Acryl ist üblich [ungeprüft: Empfindlichkeit]) oder 0,6-mm-FR4 wie Tangara | 0,6 bis 0,8 | Tangara-BOM [geprüft] |
| Mitteltaster | Ultraflacher SMD-Taster ≤ 0,6 mm (Typ noch auswählen) | ≤ 0,6 | [ungeprüft] Der 1,5-mm-Taster aus `TEILE.md` ist für 8,5 mm zu hoch, wenn er in der Ebene der Front-Platte arbeiten soll |
| Verbinder Klickrad-Hauptplatine | 6-pol. FFC 0,5 mm, ZIF, ca. 1,0 mm hoch (z. B. Hirose FH12-6S-0.5SH) oder Löt-Pads | ca. 1,0 | [ungeprüft] statt JST-SH 1,0 mm (≈ 4 mm hoch) |
| Display-FPC-Verbinder | Standard-Typ des Panels (24 oder 34 Pin, 0,5 mm), Bauhöhe ≤ 1,0 | ≤ 1,0 | je nach Panel, [ungeprüft] |
| Front | Acryl/PC 0,8 oder Glas 0,7, zugeschnitten | 0,8 | Zuschnitt-Dienst [ungeprüft] |
| Rückwand | gedruckt 1,0 oder FR4 0,8 | 1,0 / 0,8 | PCBWay [ungeprüft] |
| Gehäuserahmen | gedruckt (ASA/PETG), Seitenwand 1,2 | 8,2 | Voron/SV06 |

## 8. Folgen

### 8.1 Hauptplatine

- Dicke **0,8 mm**, 4 Lagen. Außenmaß ca. 37,0 × 84 (statt 38 × 89), an das Gehäuse 40 × 90 anpassen.
- **Bestückung hauptsächlich auf der Rückseite** (B). Vorderseite nur Teile ≤ 0,9 mm (0402, 0603, QFN/DFN), im Bereich unter dem Display 1,1 mm frei. Ein-Seiten-Bestückung bei PCBWay ist günstiger; Zwei-Seiten ist erlaubt, wenn nötig.
- **Rückseite: alle Teile ≤ 3,3 mm** (Modul 3,1, USB-C 3,18, Akku 3,3 mit Reserve).
- **Randaussparung für die Klinke** (SJ-43504: Layout laut Datenblatt, Notch ca. 10,55 × 9,3 mm Bezugsmaß, genaues Maß der Zeichnung folgt dem Footprint; Footprint mit Pads auf **B.Cu** spiegeln). Klinke unten bei x −12, Tiefe ca. 14: **Sperrzone** für Akku und Teile auf der Rückseite und für Teile auf der Klickrad-Rückseite.
- Aussparung für den LRA (nur bei VL120628H 12 × 6 × 2,0: ca. 13 × 7); bei VLV101040J (1,0) entfällt sie. Der alte Ausschnitt Ø 26 entfällt oder schrumpft.
- Modulwechsel auf **WROOM-1** (Footprint 18 × 25,5 statt 22 × 30 spart ca. 280 mm² Platinenfläche); Pin-Check vor Festlegung.
- Floorplan (grob, ungeprüft): oben Modul (Antenne an der Oberkante), mittig Akku auf der Rückseite (34 × 50 oder 30 × 40), unten Klinke (x −12) und USB-C (x +10), Hi-Fi-Teile (WM8523, INA1620, ±5 V) in einer Ecke, weit weg vom Modul und von der Haptik-Versorgung.
- Display-FPC: durch einen Schlitz (ca. 1 × 14) auf die Rückseite führen und dort steckern, oder vorn mit Verbinder ≤ 1,0 (passt gerade in die 1,1 Luft). Entscheidung nach Maßzeichnung des gekauften Moduls.
- Akku: Pads für Litzen statt Stecker (Steckerhöhe) oder Seiteneinschub; Schutzschaltung der Zelle beachten.
- Mid-Mount-USB-C nicht nötig (siehe 3.2).

### 8.2 Klickrad-Platine

- Dicke **0,8 mm** statt 1,0, 4 Lagen. Außen-Ø 32 bleibt, Bohrungen wie in `TEILE.md`.
- Abdeckung: entfällt als Druckteil. Entweder die Front-Platte (0,8) liegt direkt auf, oder 0,6-mm-FR4 (Tangara). Mitteltaste: ≤ 0,6 mm hoch oder auf die Front-Platte ein Taster-Kolben; 1,5-mm-Taster passen nicht.
- Rückseite: Bauteile ≤ 0,8 mm (DRV2605L in WSON, AT42QT2120 in QFN). **Sperrzone** für die Klinke (x −16,5 bis −7,5, y −43 bis −31 relativ zur Gehäusemitte) und für den LRA.
- LRA: 10 × 10 × 1,0 (VLV101040J) direkt auf die Platinenrückseite kleben, oder 12 × 6 × 2,0 mit Ausschnitt in der Hauptplatine. Haptik-Test auf Prototyp zuerst.
- **Schnittstelle:** Anstelle des 6-poligen JST-SH (≈ 4 mm Höhe) ein flacher FFC-Stecker (ca. 1,0 mm) oder Löt-Pads. Pinbelegung und Signale bleiben wie in `TEILE.md`. `TEILE.md` gilt für Prototyp **und** Endgerät: Änderung nur nach Entscheidung des Koordinators; für den Prototyp bleibt JST-SH.
- Befestigung: die 3 Löcher Ø 2,2 bleiben; Köpfe M1,6 oder Verklebung. Ohne Distanzring (Aufbau Distanzring 0,8 entfällt: Platine liegt an der Front-Platte).

### 8.3 CAD (`hardware/cad/params.py`, `endgeraet.py`, Render)

- `E_W, E_L, E_TOP` = 40 / 90 / 8,5 (bzw. 8,2 + Reserve). `E_WALL` = 1,2; `E_PLATE` entfällt (Front-Platte als eigenes Teil 0,8 mit Fenster/Klickrad-Aussparung).
- Gehäuseaufbau ändern: **Rahmen** (Seitenwände, Falz für Front-Platte vorn und Rückwand hinten), **Front-Platte** (Zuschnittzeichnung als DXF/SVG), **Rückwand**. Trennfuge bei z = 6 und Innenrahmen mit Domen entfallen oder schrumpfen.
- `E_FRAME_Z0/Z1`, `E_BATT` (34 × 50 × 3,3), `E_SPACER` (Distanzring entfällt), `E_JACK_*`, `E_USB_*` (Öffnungshöhe 3,4 statt 5; Klinke 5,2 hoch × 9,6 breit), `E_SWITCH_H`, `E_COVER_T` neu setzen.
- Display-Fenster 33,9 × 41,3 (aktive Fläche 33,09 × 40,51 + 0,4), Position nach FPC-Seite; Modul 37,3 × 44,9 als Umriss.
- Klickrad-Öffnung Ø 30,6 bleibt (oder Front-Platte ohne Öffnung, wenn sie die Klickrad-Fläche trägt).
- Ein/Aus-Taste und Tasten: Höhe neu aus der Rückzone ableiten.
- Prototyp-Gehäuse bleibt unberührt (19,1 mm, anderes Ziel).
- Explosionsmodell: Teile neu dimensionieren (Akku 3,3, LRA 1,0, Klinke 5,0 usw.).

### 8.4 Dokumente

- `TEILE.md`: Endgerät-Tabelle und Chipliste ändern (Maße, Modul WROOM-1, Klinke SJ-43504, Akku, Platinen 0,8 mm, Verbinder), mit Begründung. Das ist Aufgabe des Koordinators.
- `KONZEPT.md` „Offene Punkte“: Display jetzt 2,06" 410 × 502; Akku 303450/303040; Laufzeit messen.

## 9. Ungeprüftes und Risiken

1. **Lage des STEP-Ursprungs der Klinke SJ-43504** (Pad-Ebene ↔ Platinenmitte): bestimmt den Überstand 1,1 oder 1,9 mm und damit 8,2 gegen 9,0. Prüfen: 3D-Modell/Footprint von Same Sky herunterladen (`sameskydevices.com/product/resource/3dmodel/sj-43504-smt-tr`) und mit der Platinenebene vergleichen, oder Muster bestellen.
2. Pins des WROOM-1 gegenüber dem WROOM-3 (Datenblatt-Auszüge nannten beide 54 GPIOs): Pinbelegung vergleichen.
3. Akku-Dicke der Zelle (3,0 + Quellung), Kapazitäten 303040/303450: Zellen-Datenblatt, Händler.
4. Mid-Mount-USB-C (USB4720-03-A): nicht gelesen, nur Listing.
5. Lieferbarkeit/Preis des 2,06"-Panels als nacktes Modul; widersprüchliche Listing-Angabe (320 × 240) bei AliExpress. Interface-Strap (QSPI statt MIPI) und FPC-Pinbelegung beim Händler erfragen.
6. Touch-Durchlässigkeit der 0,8-mm-Acrylfront über der Klickrad-Platine.
7. Haptikgefühl mit 1,0-mm-LRA (10 × 10, 2,5 Grms) und steifer Front-Platte; Vergleich mit 2,0 mm.
8. Steifigkeit des 1,0-mm-Gedruckten (Rückwand) und der 0,8-mm-Front. FR4-Rückwand als Alternative.
9. Antenne des Moduls: Freiraum und Abstand zum Akku.
10. Alles in diesem Dokument ist am Rechner entstanden; kein Teil wurde gemessen oder bestellt.

## 10. Quellen

- Tangara-Hardware, lokale Kopie `/home/user/tangara-ref/tangara-hw/` (STEP-Maße per CadQuery, Footprints, BOM)
- Same Sky SJ-3506-SMT-TR: https://www.sameskydevices.com/product/resource/sj-3506-smt-tr.pdf
- Same Sky SJ-43504-SMT-TR: https://www.sameskydevices.com/product/resource/sj-43504-smt-tr.pdf
- Same Sky 3,5-mm-Buchsen (Mid-Mount-Liste): https://www.sameskydevices.com/3.5-mm-audio-jacks
- Espressif ESP32-S31-WROOM-3/-3U Datenblatt: https://documentation.espressif.com/esp32-s31-wroom-3_wroom-3u_datasheet_en.pdf
- Espressif ESP32-S31-WROOM-1/-1U Datenblatt: https://documentation.espressif.com/esp32-s31-wroom-1_wroom-1u_datasheet_en.pdf
- Espressif ESP32-S31 Produktseite (Modulliste): https://www.espressif.com/en/products/socs/esp32-s31
- Display DO0180FMST08 (1,8"): https://www.scribd.com/document/701940696/SPEC-DO-28
- GL178AMC12C (1,78" CST820): https://lcdscreenmfg.com/product/1-78inch-amoled-display-368448-oncell-capacitive-oled-touchscreen-qspi-cover-glass/
- LX Display AMOLED-Liste (2,06" 410 × 502): https://www.lxdisplay.com/Product/AMOLED.html
- Waveshare ESP32-S3-Touch-AMOLED-2.06: https://docs.waveshare.com/ESP32-S3-Touch-AMOLED-2.06
- LilyGo T-Display-S3-AMOLED-Plus (1,91"): https://lilygo.cc/en-us/products/t-display-s3-amoled-plus
- Vybronics Rechteck-LRA: https://www.vybronics.com/products/linear-lra-vibration-motors
- GCT USB Type-C: https://gct.co/usb-connector/usb-type-c; USB4715 (nur Power): https://www.digikey.com/en/products/detail/gct/USB4715-GF-A/16669072
- Akkus: https://www.ebay.com/itm/236923739987 (303450, 500 mAh), https://kriscables.com/product/rechargeable-li-po-battery-37v-600mah-303450/ (600 mAh), https://www.fpbattery.com/wp-content/uploads/2024/06/fpbattery-503450-3.7V-1000mAh-Lithium-Polymer-Battery-Specification.pdf
