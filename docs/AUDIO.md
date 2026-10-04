# Audio-Kette: Auswahl für das Endgerät

Stand: 2026-10-04. Ziel laut Vorgabe: Top-Notch-High-Fidelity über Kabel (3,5-mm-Klinke; USB-C-Host für externe DACs), Gerät ≤ 9 mm dick, LiPo 1S, Akkulaufzeit wichtig, möglichst viel von Tangara übernehmen, Bestückung bei PCBWay.

Kennzeichnung: **[D]** = aus Datenblatt entnommen (Quelle am Ende), **[M]** = Messung von Tangara, **[B]** = von mir gerechnet oder geschätzt, **[?]** = ungeprüft. Es wurde nichts gebaut und nichts gemessen. Alle Messwerte der Empfehlung sind Datenblattwerte, keine Messwerte an unserer Platine.

## 1. Ergebnis in Kürze

**Empfehlung: Cirrus CS43131 (DAC mit integriertem Class-H-Kopfhörerverstärker), QFN-40 5 × 5 mm, mit einem 22,5792-MHz-Quarz am Chip. Der ESP32-S31 ist I²S-Secondary (der DAC taktet), damit hängt die Kette nicht vom fehlenden APLL ab.** Tangaras ±5-V-Wandler (TPS65133), der Verstärker (INA1620) und der WM8523 entfallen.

| Kennzahl | Tangara (WM8523 + INA1620) | CS43131 |
|---|---|---|
| Dynamikumfang (A-bewertet) | 104–106 dB [D][M] | 125 dB an 32 Ω, 128–130 dB an 600 Ω/10 kΩ [D] |
| THD+N | −76,5 dB (0,015 %) bei 0 dBFS, 600 Ω [M]; DAC-Datenblatt THD −86/−89 dB [D] | −110 dB an 32 Ω, −113/−115 dB an 600 Ω, −100 dB an 16 Ω [D] |
| Leistung 16 / 32 / 600 Ω | ca. 150 / 220 / 14 mW [B, siehe 2.3] | 15,6 / 30,8 / 5 mW [D] |
| Leistungsaufnahme Ruhe (Wiedergabe, kein Signal) | ca. 100–110 mW an der Batterie [B] | 26 mW an den Schienen, ca. 29 mW an der Batterie [D][B] |
| Versorgungen | 3,3 V und ±5 V | Batterie (3,0–5,25 V) und 1,8 V |
| IC-Fläche (Gehäuse) | ca. 54 mm² plus 2 Spulen [B] | 25 mm² plus Quarz 3,2 mm² [B] |
| IC-Höhe | max. ca. 1,2 mm (TSSOP-20) [?] | max. 0,8 mm [D] |

Kern der Begründung: Der WM8523 ist der Engpass der Tangara-Kette (der INA1620 liegt mit −113 bis −123 dB THD+N weit darunter). Der CS43131 gewinnt rund 20 dB Dynamikumfang und etwa 25 dB THD+N, braucht keinen ±5-V-Wandler und etwa 60 % weniger Leistung im Leerlauf. Er ist auch das dünnere und kleinere System. Die Grenze ist die Ausgangsleistung (31 mW an 32 Ω gegen ca. 220 mW), die für ein Taschengerät mit IEM und üblichen Kopfhörern reicht. Für schwer treibbare Hörer gibt es den USB-C-Host mit externem Verstärker.

## 2. Bewertung der Tangara-Kette

### 2.1 Was Tangara tatsächlich gebaut hat

Aus dem lokalen Schaltplan (`tangara-hw/tangara-mainboard/audio.kicad_sch`) und der Firmware:

- DAC **WM8523** (Cirrus/Wolfson, TSSOP-20), I²S plus **MCLK von GPIO0**, MCLK kommt aus dem **ESP32-APLL** (`i2s_dac.cpp`: `clock_config_.clk_src = I2S_CLK_SRC_APLL`, MCLK-Vielfaches 256 bzw. 384). Steuerung per I²C, Treiber `wm8523.cpp` (73 Zeilen) plus `i2s_dac.cpp` (270 Zeilen).
- Verstärker **INA1620** (WQFN-24, 4 × 4 mm), +6 dB Verstärkung über die integrierten Widerstände, Ausgabe über **SJ-3506-SMT**, ESD **D5V0L2B3T-7** (2-Kanal-bidirektional, SOT-523 [D]).
- Versorgung ±5 V aus **TPS65133** (laut Schaltplan MPN `TPS65133DPDR`, WSON-12 3 × 3 mm, 250 mA je Schiene, > 90 % Wirkungsgrad bei 50–200 mA [D]); das Symbol im Schaltplan heißt irreführend `TPS65135RTER`. Zwei 4,7-µH-Spulen. Der Ausgang ist gleichspannungsgekoppelt (keine Koppelelkos).
- Steuerleitungen `AMP_EN` und `AMP_MUTE` (über den SAMD21-Port-Expander), `3.5mm_DETECT` aus der Buchse.

### 2.2 Messbericht und Datenblatt

| Größe | Wert | Quelle |
|---|---|---|
| SNR (A-bewertet) | 106 dB | Tangara-Bericht [M]; WM8523 typ. 106 dB, 100 dB min. [D] |
| Dynamikumfang WM8523 | 104 dB typ. (A-bewertet, 10 kΩ) | [D] |
| THD WM8523 | −89 dB bei −1 dBFS, −86 dB bei 0 dBFS (10 kΩ) | [D] |
| THD+N gesamt, 600 Ω | 0,015 % (0 dBFS) bis 0,014 % (−10 dBFS), 0,022 % bei −20 dBFS, 0,066 % bei −30 dBFS, 0,15 % bei −40 dBFS, 0,185 % bei −60 dBFS (0,48 % bei −50 dBFS ist im Bericht ein Ausreißer) | [M], Cosmos-E1DA-ADC, nicht unabhängig |
| Ausgangspegel DAC | 2,1 Vrms bei 0 dBFS (3,3 V Versorgung) | [D] |
| INA1620 THD+N | −113 dB (16 Ω, 10 mW), −116 dB (32 Ω), −123 dB (128 Ω); 2,8 nV/√Hz; 2,6 mA je Kanal; bis ±2 V Versorgung | [D] |

Bewertung:

- **Dynamikumfang:** 104–106 dB ist für „gut“, nicht für „Top-Notch“. Tangaras Autorin sagt selbst, die Kette sei für die Oberseite (Verstärkung für schwere Hörer) und nicht für empfindliche IEMs ausgelegt. Das Rauschen ist an sehr empfindlichen IEMs hörbar, Tangara empfiehlt deshalb einen Teiler (100 Ω) zwischen Filter und Verstärker.
- **Verzerrung:** Die Kette ist DAC-begrenzt. Der Verstärker ist 20–30 dB besser als der DAC. THD+N steigt zu kleinen Pegeln stark an (0,185 % bei −60 dBFS), weil das Rauschen dominiert.
- **Leistung:** Der INA1620 an ±5 V bietet 140 mA und ca. 4 V Spitze (Aussteuerung bis ca. 0,8–1 V an die Schiene [D]). Daraus [B]: 16 Ω ≈ 150 mW (stromgrenze), 32 Ω ≈ 220 mW, 300 Ω ≈ 25 mW (2,8 Vrms), 600 Ω ≈ 14 mW. Der DAC liefert hier mit +6 dB mehr als die Schiene hergibt, Tangara begrenzt per Lautstärke-Grenzwert in der Firmware.
- **Ruhestrom:** WM8523 10,8 mA bei 48 kHz, 14 mA bei 96/192 kHz an 3,3 V [D] = 36–46 mW, bei 3,7 V Batterie über LDO ca. 40–52 mW. INA1620 2 × 2,6 mA (max. 3,3 mA) an ±5 V = 52 mW [D][B], über den TPS65133 (CCM-Betrieb, Wirkungsgrad bei kleiner Last nicht im Datenblatt-Auszug, hier 85 % angenommen) ca. 61 mW. Summe ca. 100–110 mW [B]. Für einen Akku-Player ist das viel.
- **Fläche und Höhe:** Drei ICs (TSSOP-20 6,5 × 4,4; WQFN-24 4 × 4; WSON-12 3 × 3) plus zwei Spulen und ca. 25 Passive. Höhe der ICs unkritisch (0,8–1,2 mm), die Spulen sind das höchste Teil der Kette (Höhe der gewählten Spule [?]).
- **Takt:** Der WM8523 will MCLK synchron zu LRCLK (128 fs bis 1152 fs) und hat „Toleranz gegen Phasenschwankungen“, aber keine Jitterunterdrückung. Tangara löst das mit dem ESP32-APLL. **Das fällt beim S31 weg** (kein APLL in IDF 6). Die Dokumentationsseite für den S31 nennt zwar `I2S_CLK_SRC_APLL` im allgemeinen Text, ich konnte das Verhalten nicht prüfen [?]; der Entwurf ist deshalb so gewählt, dass er keinen APLL braucht.

Fazit: Als Baukasten (alles lötbar, ein Treiber, kein Mikro-Controller-Zwang) ist die Kette hervorragend, für „Top-Notch“ aber der falsche DAC. Alles, was um den DAC herum steht (Buchse, ESD, Entkopplung), ist wiederverwendbar.

## 3. Vergleich der Alternativen

Alle Datenblätter wurden gelesen (Cirrus und TI vollständig, ESS ES9038Q2M/ES9039Q2M/ES9219 vollständig, AKM nur Produktseite, weil das Datenblatt ein Anmeldeformular braucht). Verfügbarkeit am 2026-10-04 von den Shopseiten, ohne Bestellung. Preise Einzelstück.

| | **CS43131** | **CS43198** (+ Verstärker) | **ES9039Q2M / ES9038Q2M** (+ I/U-Stufe) | **AK4493SEQ** (+ Verstärker) | **ES9219Q** (DAC + Verstärker) |
|---|---|---|---|---|---|
| Funktion | DAC + Class-H-Verstärker | DAC, Line-Out 2 Vrms pseudodifferentiell | DAC, Strom- oder Spannungsausgang differentiell | DAC, differentiell 2/2,7 Vrms | DAC + Verstärker |
| Dynamikumfang | 130 dB (10 kΩ), 125 dB (32 Ω) [D] | 130 dB (Line) [D] | 130 dB (9039) / 128 dB (9038) [D] | 123–125 dB [D] | 121 dB (123 mit DRE) [D] |
| THD+N | −115 dB (10 kΩ/600 Ω), −110 dB (32 Ω) [D] | −115 dB [D] | −120 dB (differentiell, Referenzaufbau) [D] | −115 dB (2 Vrms) [D] | −112 dB (2 Vrms an 300 Ω), −106 dB (0,3 V an 32 Ω) [D] |
| Leistung (Chip) | 26 mW Ruhe, 40 mW bei 0,1 mW Ausgang [D] | 26 mW Ruhe (DAC allein) [D] | 54–78 mW Wiedergabe, 15–34 mW Leerlauf (9039) [D]; ca. 40 mW (9038) [D] | nicht erhoben [?] | 45 mW (1-V-Modus), 69 mW (2-V-Modus) [D] |
| Versorgungen | VP = Batterie, 1,8 V | 1,8 V (+ ±5 V für Verstärker) | 3,3 V + 1,2 V intern; I/U-Stufe braucht ±Schiene | 5 V + 3,3 V + 1,8 V; Verstärker ±Schiene | 1,8 V + 3,3 V |
| Gehäuse | QFN-40 5×5, 0,8 mm; WLCSP-42 2,7×3,2 | gleiche Gehäuse | QFN-32 5×5 | LQFP-48 (ca. 7×7, ca. 1,7 mm [?]) | QFN-40 5×5 |
| Takt | PLL 9,6–26 MHz, Quarz 22,5792/24,576 MHz | wie CS43131 | MCLK frei bis 50 MHz (asynchron, ASRC) [D] | Standard-MCLK [?] | MCLK frei bis 50 MHz, PLL intern [D] |
| Verfügbarkeit | Digi-Key 251 Stück, 18,52 USD, Lieferzeit Hersteller 20 Wochen; Mouser „nicht gelagert“; LCSC 44 Stück (QFN) und 21 (WLCSP) | Mouser 1274 Stück, 18,19 USD; LCSC 348 Stück | 9039: Mouser 0 Stück, 18,70 USD; 9038: Mouser 2876 Stück, 21,12 USD | Mouser 3168 Stück, 9,74 USD | Mouser 0 Stück, 13,20 USD; LCSC keine |
| Datenblatt | öffentlich (Cirrus, DS1155F2) | öffentlich (DS1156F2) | ES9039Q2M v0.2.3 öffentlich, vorläufig (Mai 2026); ES9038Q2M v1.4 öffentlich | nur über Formular | v1.2 öffentlich |
| Treiber | Linux `cs43130.c` deckt die Familie ab, CS43131/CS43198 [?] | wie CS43131 | Register ESS-typisch, kein Tangara-Bezug | – | – |
| Urteil | **gewählt** | **Plan B** | ES9039: nicht lieferbar, Datenblatt vorläufig; ES9038: Strom-Ausgang braucht Operationsverstärker und ±Schiene, 40 mW zusätzlich | fällt weg: 5-V-Schiene, drei Versorgungen, hohes Gehäuse, Datenblatt nur mit Formular | fällt weg: nicht lieferbar, THD+N an 32 Ω schwächer |

### 3.1 Verstärker: OPA1622 gegen INA1620

Beide haben denselben Chip: gleiche Daten (2,8 nV/√Hz, −119 dB THD+N bei 142 mW an 32 Ω, 2,6 mA je Kanal, ±2 bis ±18 V, Abschalt-Modus mit unterdrücktem Knacken, Ausgangsstrom +145/−130 mA) [D]. Der INA1620 hat zusätzlich vier angepasste 1-kΩ-Dünnschichtpaare (0,004 %) und EMI-Filter im WQFN-24 (4 × 4 mm). Der OPA1622 sitzt im VSON-10 (3 × 3 mm) und braucht externe Widerstände.

| | INA1620 | OPA1622 |
|---|---|---|
| Gehäuse | WQFN-24 4×4 | VSON-10 (DRC) 3×3 |
| Verfügbarkeit | Mouser RTWR 619 Stück (8,59 USD), RTWT 247 Stück (9,79 USD) | Mouser IDRCR 2617 Stück (7,43 USD), IDRCT 365 Stück (8,76 USD); LCSC 7066 und ca. 28 000 Stück |
| Stückzahl für PCBWay (LCSC-Bestand) | nicht geprüft [?] | sehr gut |

Beim CS43131 wird keiner von beiden gebraucht. Beim Plan B (CS43198) ist der **OPA1622 die erste Wahl wegen LCSC-Bestand**, der INA1620 spart vier Widerstände.

### 3.2 Takt: kann der ESP32-S31 MCLK sauber liefern?

Nein, nicht für diese DACs, und das muss er auch nicht:

- Die PLL des CS43131/CS43198 verlangt am Referenzeingang **≤ 50 ps Jitter** und eine Phasenrauschmaske [D]. Ein Takt aus dem Bruchteiler der I²S-Einheit (Quelle 160 MHz oder mehr, Kantenraster mehrere ns) erfüllt das nicht [B].
- Beim Tangara-Aufbau fällt der Takt aus dem APLL. Den gibt es beim S31 laut Vorgabe nicht.
- Beide Cirrus-Chips haben einen **Quarzoszillator** (22,57–24,58 MHz, Last 5–8 pF, ESR ≤ 100 Ω, Ansprechzeit ≤ 6,5 ms) und können **I²S-Master** sein [D]. Die PLL erzeugt aus dem 22,5792-MHz-Quarz auch 24,576 MHz (Beispiel „Ex. 5-6“ im CS43198-Datenblatt, dasselbe PLL-Prinzip im CS43131) [D].
- Die ESS-Chips (ES9039Q2M, ES9219) sind taktfreundlicher: MCLK beliebig bis 50 MHz, die ASRC trennt von der Eingangstaktung [D]. Das wäre der Grund, bei einem Wechsel auf ESS den ESP-Takt zu nutzen. Beim gewählten Cirrus entfällt das.

## 4. Optional: symmetrischer 4,4-mm-Ausgang

**Einschätzung: nicht bei diesem Gerät.**

- Der CS43131 hat einen Mono-/Differenzmodus [D]. Für einen symmetrischen Ausgang braucht man damit **zwei Chips** (einer pro Kanal), also doppelte Fläche, doppelte Leistung (≈ +26 mW) und doppelte Quarz-/Takt-Verteilung. Mit Verstärker-Variante (CS43198 + 2 × OPA1622) ähnlich viel.
- Die 4,4-mm-Pentaconn-Buchsen sind deutlich größer als 3,5-mm-Buchsen, Bauhöhe typischerweise über 7 mm [?, aus dem Gedächtnis, kein Datenblatt geprüft]. Bei ≤ 9 mm Gerätedicke und Wandstärken von je ca. 1 mm bleibt dafür kaum Platz neben Akku und Platine.
- Der Nutzen (Leistung und Kanaltrennung) ist bei Kopfhörern, die ein Taschengerät üblicherweise treibt, klein. Wer symmetrisch hören will, nimmt den **USB-C-Host** mit einem externen Dongle oder Verstärker (UAC2).

Wenn doch gewünscht: erst Platz in `TEILE.md` reservieren und die Buchse als Hochkant-/Randteil planen, nicht jetzt.

## 5. Empfehlung: konkrete Kette

### 5.1 Blockschaltbild

```
ESP32-S31 ──I²C──────────────► CS43131 (QFN-40, I²C-Adresse 0x30–0x33 [?])
          ◄─BCLK/LRCK── I²S ─── (DAC = Main/I²S-Master, taktet BCLK und FSYNC selbst)
          ──SDOUT─────────────►
          ──RESET/INT─────────►/◄
22,5792-MHz-Quarz ──XTI/XTO──► CS43131 (PLL erzeugt 24,576 MHz für die 48-kHz-Familie)
Batterie (SYS) ─► VP (3,0–5,25 V, HV_EN=1 ab 3,3 V)
1,8 V (Buck, optional LDO) ─► VA, VCP, VD, VL
CS43131 HPOUTA/B + HPREFA/B ──► SJ-3506-SMT (TRS) ── ESD D5V0L2B3T-7
HP_DETECT ◄── Buchsenschalter
```

### 5.2 Teileliste

| Funktion | Teil | Herkunft | Bemerkung |
|---|---|---|---|
| DAC + Kopfhörerverstärker | **CS43131-CNZR** (QFN-40, 5 × 5, 0,4 mm Raster, T&R) | neu | Footprint wie CS43198; Pinbelegung der Ausgänge gleich, die Pins HPINA/HPINB (12/15) gibt es nur beim CS43131 [?, Pintabellen vor dem Layout vergleichen] |
| Takt | Quarz 22,5792 MHz, 2,0 × 1,6 mm (z. B. NDK NX2016SA 22.5792M EXS00A-CS09116, im Datenblatt als geeignet gelistet) | neu | Lastkondensatoren nach Abschnitt „Crystal Tuning“ des Datenblatts, Register 0x20052 passend setzen [D] |
| 1,8-V-Schiene | Abwärtswandler vom SYS-Ausgang (Vorschlag TPS62840 oder TPS62A02 [?]) plus bei Bedarf nachgeschalteter rauscharmer LDO (TLV75518 [?]) | neu | Bedarf ca. 14 mA Ruhe, ca. 22 mA bei 0,1 mW Ausgang (1,8 V) [D], für Spitzen 60 mA ansetzen [B]. Ein LDO direkt von 3,3 V würde ca. 33 mW verheizen [B], deshalb Buck |
| VP | direkt vom Batterie-/SYS-Anschluss (MCP73871-Ausgang) | Tangara | 28 µA Ruhe [D]; VP muss **zuerst** kommen [D] |
| Buchse | **SJ-3506-SMT** (Mid-Mount, 3 Leiter, 2 Schalter) | Tangara | Footprint 1:1 aus `CUI_SJ-3506-SMT.kicad_mod` übernehmbar; Gesamthöhe [?] gegen 9-mm-Gehäuse prüfen (Same Sky nennt Buchsenprofile ab 3 mm; flachere Variante ggf. nötig) |
| ESD | **D5V0L2B3T-7** auf HPOUTA/B (und ggf. HP_DETECT) | Tangara | 2-Kanal bidirektional, 5 V [D]; Pflicht bidirektional, weil das Signal um Masse schwingt |
| Mute/Pop | Popguard des CS43131 (siehe 5.4), kein separates Mute-Bauteil | neu | `AMP_EN`/`AMP_MUTE` entfallen |
| Lader, 3,3 V, USB-C | MCP73871, TLV75533, USB4510-03-1-A (unverändert) | Tangara | nicht Teil dieses Pakets |

### 5.3 Takt-Konzept

1. **Ein Quarz 22,5792 MHz** direkt am DAC. Die 44,1-kHz-Familie läuft nativ, die 48-kHz-Familie über die Fractional-N-PLL (22,5792 → 24,576 MHz) [D].
2. Der **DAC ist I²S-Master**, der ESP32-S31 ist **Slave** und liefert nur Daten. Der ESP braucht dazu weder MCLK noch APLL. Der MCLK-Pin (Tangara: GPIO0) entfällt. Lokale Dateiwiedergabe und Streaming puffern mehrere Sekunden und vertragen den Taktunterschied zum Kern. Für Bluetooth-Ausgabe wird der DAC nicht benutzt.
3. Grenze beim S31-Slave-Betrieb: BCLK = 64 × fs. Bei 192 kHz sind das 12,3 MHz, bei 384 kHz 24,6 MHz. Maximal sicher unterstützte BCLK im Slave-Betrieb des S31 ist nicht geprüft [?]. Wir bleiben bei 192 kHz, wie Tangara.
4. Ungeprüft: Ob die PLL-Betriebsart (48-kHz-Familie) die Datenblattwerte für THD+N und Dynamikumfang erreicht. Die Datenblattzahlen wurden mit direktem 22,5792-MHz-Quarz gemessen [D]. **Auf der ersten Platine einen zweiten Quarz-Platz (24,576 MHz) und einen 2:1-Taktumschalter als unbestückte Option vorsehen** und beide Varianten messen.
5. USB-C-Host-Pfad (externer DAC) ist unabhängig. Die Taktung kommt vom USB-Gerät/Feedback, nicht vom Quarz.

### 5.4 Mute und Pop-Unterdrückung

- **Popguard** im CS43131 [D]: Sprung beim Ein-/Ausschalten der Verstärker ±50 µV typ., ±100 µV max. (A-bewertet), Einschaltzeit 12 ms, 22 ms Latenz nach RESET.
- Reihenfolge: VP zuerst, dann 1,8 V, dann RESET lösen. Beim Abschalten erst `PDN_HP` bzw. RESET, dann Schienen entfernen [D].
- Lautstärke mit weicher Rampe (0,5-dB-Schritte, Soft-Ramp) [D] und automatische Stille-Erkennung. Pausiert der Player, wird der Verstärker per `PDN_HP` abgeschaltet.
- `HPOUT_CLAMP` im Register hält die Ausgänge beim Abstecken auf Masse [D].
- Der DAC misst **DC- und AC-Impedanz** des angeschlossenen Hörers und kann so den Ausgangspegel passend wählen [D]. Das ist eine Funktion, die Tangara nicht hat und für IEM-Rauschen wichtig ist. Einbau in die Firmware als spätere Stufe.

### 5.5 Leiterplatten- und Layouthinweise [D]

- Thermal-Pad auf **GNDA**, mit mehreren Durchkontaktierungen auf Massefläche.
- **HPREFA und HPREFB getrennt** zum Massepin der Buchse führen (Abschnitt 8.3), dort durch Via an die Massefläche anschließen.
- Referenzschaltung Fig. 2-1 des Datenblatts übernehmen: ca. 6 × 2,2 µF (fliegende/Filterkondensatoren), 2 × 15 µF an FILT±, 4,7 µF, ca. 5 × 0,1 µF, insgesamt etwa 15–20 Passive [D][B]. Alle Keramik, X7R/X5R mit geringem ESR.
- Class-H-Ladungspumpe und Schalter erzeugen Störungen (nicht gemessen [?]). Abstand zu AT42QT2120 (Touch) und DRV2605L (Haptik) halten und die Mess-Ergebnisse nach dem ersten Aufbau prüfen.
- WLCSP-Variante (CS43131-CWZR) **nicht verwenden**: 42 Bälle auf 2,7 × 3,2 mm erzwingt HDI/Mikro-Vias.

### 5.6 Erwartete Messwerte (Datenblatt, nicht gemessen)

Bedingungen laut Datenblatt: 1 kHz, 20 Hz–20 kHz Bandbreite, 44,1 kHz, 22,5792-MHz-Quarz, VP = 3,6 V, 1,8 V Schienen, Volume 0 dB. Wir erwarten an der fertigen Platine höchstens diese Werte, im Alltag eher 3–6 dB weniger bei THD+N und Rauschen [B, Erfahrungswert, kein Beleg].

| Last | Dynamikumfang A-bew. | THD+N 0 dBFS | Ausgang | Leistung |
|---|---|---|---|---|
| 10 kΩ (HV_EN=1) | 130 dB | −115 dB | 4,9 Vpp (5,7 Vpp mit +1 dB) | – |
| 600 Ω (HV_EN=1) | 130 dB | −115 dB | 4,9 Vpp | 5 mW (6,8 mW mit +1 dB, THD+N dann −105 dB) |
| 600 Ω (HV_EN=0) | 128 dB | −113 dB | 3,96 Vpp | 3,3 mW |
| 300 Ω | nicht im Datenblatt | nicht im Datenblatt | | ca. 10 mW [B, zwischen 600 und 32 Ω interpoliert] |
| 32 Ω (HV_EN=0) | 125 dB | −110 dB | 2,81 Vpp | 30,8 mW |
| 16 Ω (HV_EN=0) | 119 dB | −100 dB | 1,41 Vpp | 15,6 mW |

Übersprechen 105–120 dB bei 1 kHz, Rauschen 0,55 µV (A-bew.), Ausgangsoffset ±50 µV (typ.), Pegelabweichung ±0,1 dB [D]. Ausgangsimpedanz: **im ausgewerteten Datenblatt nicht gefunden, messen**, wichtig für IEMs mit stark schwankender Impedanz [?]. Betriebstemperatur nur −20 bis +70 °C [D] (Tangara-WM8523: −40 bis +85 °C): für ein Taschengerät ohne Bedeutung, aber nicht im Auto liegen lassen.

Hörbare Folgen: Der Rauschpegel liegt bei empfindlichen IEMs (z. B. 110 dB/V) weit tiefer als bei Tangara, ein Dämpfungs-Mod wird nicht nötig [B].

Akku [B]: Ruhe im Audio-Teil ca. 29 mW statt 100–110 mW, bei einer 600-mAh-Zelle (2,2 Wh) und angenommenen 200 mW für den Rest (MCU, Display, Funk – Annahme, nicht gemessen) etwa 9 h statt 7,4 h Gesamtlaufzeit, also ca. +20 %. Bei Spitzenlast steigt der Verbrauch an VP mit der Ausgangsleistung.

## 6. Plan B und Plan C

**Plan B: CS43198-CNZR (+ OPA1622) statt CS43131.** Gleiches QFN-40-Gehäuse und Quarz-/PLL-Takt, derselbe Treiber im Kern (Registerfamilie, Unterschiede ungeprüft [?]). Bestand ist besser (Mouser 1274, LCSC 348 gegen Digi-Key 251). Preis der Verstärker-Stufe: OPA1622 im VSON-10 (3 × 3, LCSC reichlich), ±-Schiene (**TPS65133 wie bei Tangara**, 1:1 übernehmbar, samt 2 × 4,7-µH-Spulen), Verstärkung über 4 Dünnschichtwiderstände, je ca. 50–60 mW mehr Leerlaufleistung [B]. Gewinn: ca. 150–220 mW Ausgangsleistung [B]. Fläche und Höhe wachsen um die Verstärkerstufe und zwei Spulen. Empfehlung: Footprint so anlegen, dass beide Chips passen (Pin-Vergleich vor dem Layout), die Verstärkerstufe als unbestückbare Option.

**Plan C: Tangara 1:1 (WM8523 + INA1620 + TPS65133).** Bewährte, öffentliche, lieferbare Teile (WM8523GEDT/R: Mouser 6768 Stück, 2,95 USD; INA1620: Mouser 619; TPS65133: Datenblatt geprüft, Bestand nicht geprüft [?]). Treiber (`wm8523.cpp`, `i2s_dac.cpp`) lässt sich fast unverändert übernehmen, **mit einem Unterschied**: Der Takt muss vom ESP32-S31 kommen oder von einem 22,5792/24,576-MHz-Oszillator mit Umschalter. Der WM8523 will MCLK synchron zu LRCLK. Schlechtester Audio-Wert der drei, aber risikoärmster Aufbau.

**Nicht lieferbar:** Ist der CS43131 beim Bestellen nicht zu bekommen (Digi-Key-Hersteller-Lieferzeit 20 Wochen), geht Plan B. Wenn auch der nicht kommt, Plan C. ES9039Q2M und ES9219Q sind aktuell bei Mouser nicht lagernd und kommen nicht als Ersatz in Frage.

## 7. Was kommt von Tangara, was ist neu

| Von Tangara 1:1 | Neu | Entfällt |
|---|---|---|
| Buchse SJ-3506-SMT (Footprint, Detect-Schalter) | CS43131 (Treiber und Init) | WM8523 |
| ESD D5V0L2B3T-7 | Quarz und PLL-Konfiguration | INA1620 |
| `3.5mm_DETECT` (nun an HP_DETECT des DAC) | 1,8-V-Schiene | TPS65133 samt 2 Spulen |
| MCP73871, TLV75533 (unverändert) | I²S-Secondary-Betrieb des S31 | Filter 560 Ω / 2700 pF / 100 pF am DAC-Ausgang |
| I²C-Anbindung (Idee) | Impedanzmessung in der Firmware (später) | `AMP_EN`, `AMP_MUTE`, MCLK-Leitung (GPIO0) |

Treiberaufwand [B]: Der WM8523-Treiber (343 Zeilen insgesamt) ist klein. Beim CS43131 ist die Registerkarte deutlich größer (Quarz-, PLL-, Port- und Verstärker-Setup, Impedanzmessung). Mit dem Linux-Treiber `cs43130.c` (GPL, Cirrus) als Vorlage ist der Aufwand überschaubar, die Abdeckung von CS43131 in dieser Datei ist nicht geprüft [?].

## 8. Folgen für die Hauptplatine (für `TEILE.md`, von mir nicht geändert)

- **Versorgungen:** statt 3,3 V und ±5 V jetzt 3,3 V (ESP, Rest), VP direkt vom SYS-Ausgang und neu **1,8 V** (ca. 14–22 mA, Spitze ≈ 60 mA [B]). Der ±5-V-Wandler fällt weg.
- **Takt:** 1 Quarz 22,5792 MHz (2,0 × 1,6 mm) plus zwei unbestückbare Plätze für Option 24,576 MHz/Umschalter. S31 liefert **keinen** MCLK.
- **Pins am S31:** I²S BCLK, WS (beide Eingänge), DOUT, I²C (geteilt), RESET (GPIO), INT (GPIO, offen). Tangaras MCLK-Pin entfällt. I²C-Adresse DAC liegt vermutlich bei 0x30–0x33 [?], kollidiert nicht mit 0x1C, 0x36, 0x5A.
- **Fläche:** Audio-ICs ca. 54 mm² → ca. 28 mm² plus rund 15–20 Passive [B].
- **Höhe:** ICs max. 0,8 mm, Quarz ca. 0,5 mm, keine Spulen im Audio-Pfad. Höchstes Teil im Audio-Bereich ist die Buchse (Höhe [?]). `TEILE.md` sieht derzeit **12,2 mm** Gehäusehöhe vor, die Vorgabe lautet jetzt ≤ 9 mm: Gehäuse, Akku (derzeit 4,6 mm) und Stapel müssen mit der Buchse zusammen neu bilanziert werden.

## 9. Offene Punkte (für `KONZEPT.md`)

1. Höhe von SJ-3506-SMT messen oder flachere 3,5-mm-Buchse wählen.
2. PLL-Betrieb gegen zweiten Quarz messen (Abschnitt 5.3).
3. CS43131 gegen Bestellverfügbarkeit prüfen (Digi-Key 251, Mouser nicht gelagert, LCSC 44) und rechtzeitig bestellen.
4. I²S-Slave-Betrieb des ESP32-S31: maximale BCLK, Treiberstatus in IDF 6 prüfen.
5. Ausgangsimpedanz und Lastverhalten messen (kein Wert im ausgewerteten Datenblatt gefunden).
6. 1,8-V-Wandler und Rauschverhalten der Ladungspumpe am Aufbau prüfen.
7. Ob die Linux-Treiberdatei CS43131 abdeckt, bevor Firmware geplant wird.

## Quellen

Datenblätter wurden heruntergeladen und gelesen: WM8523 v4.3 (statics.cirrus.com), INA1620 SBOS859B und OPA1622 SBOS727B (ti.com), TPS65133 SLVSC01A und TPS65135 (ti.com), CS43131 DS1155F2 und CS43198 DS1156F2 (statics.cirrus.com, mit Browser-Kennung abrufbar), ES9038Q2M v1.4, ES9219 v1.2, ES9039Q2M v0.2.3 (esstech.com), D5V0L2B3T (diodes.com). Tangaras Messbericht: cooltech.zone/tangara/blog/2024-02-14-audio-quality/. Tangara-Hardware und -Firmware lokal unter `/home/user/tangara-ref/`. AKM AK4493SEQ nur Produktseite (akm.com), Datenblatt nicht frei. Verfügbarkeiten: Mouser-Suchseiten, Digi-Key-Produktseite CS43131-CNZR, LCSC-Suchseiten, jeweils am 2026-10-04 abgerufen; Bestände ändern sich laufend.
