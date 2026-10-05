# Design-Review Hauptplatine Rev. 3 und Klickrad v2 (vor der Bestellung)

Stand: 2026-10-05. Review-Gegenstand: `hardware/pcb/hauptplatine/` (Schaltplan, Platine, Fertigungsdaten) und `hardware/pcb/klickrad/` (v2). Es wurden **keine** Platinen- oder CAD-Dateien geändert. Nichts davon wurde auf Hardware gemessen; alle Aussagen sind Abgleich von Schaltplan/Layout gegen Datenblätter oder Rechnung.

**Ergebnis in einem Satz:** Nicht bestellbereit. Es gibt vier Blocker (I²C-Pegelwandler schiebt die 1,8-V-Schiene hoch, Strapping-Pin IO36 wird von der SD-Beschaltung undefiniert gezogen, Lader läuft im AC-Modus mit 1 A in einen ca. 500-mAh-Akku, das S31-Modul ist derzeit nicht lieferbar) und zehn Befunde der Stufe „Hoch“.

## Methode

- Netzliste und Stückliste mit `kicad-cli sch export netlist/bom` (KiCad 9.0.9) aus `hauptplatine.kicad_sch` und `klickrad.kicad_sch` exportiert, je Bauteil Pin → Netz ausgewertet.
- Platine mit `pcbnew` (Python) ausgewertet: Pad-Lagen, Bahnbreiten und Lagen je Netz, Vias in Pads, Kontur (Edge.Cuts), Lage der Stecker.
- Datenblätter heruntergeladen und gelesen (Version in Klammern): ESP32-S31-WROOM-1/-1U (v0.5, vorläufig), ESP32-S31 Series (v0.5), Cirrus CS43131 (DS1155F2), Microchip MCP73871 (DS20002090E), TI PCA9306 (SCPS113O), TI TUSB320LAI (SLLSEQ8D), TI TPS2553 (SLVS…, Rev. mit RILIM 15 k), TI TPS61023 (SLVSF14B), TI TLV757P (SBVS322C), TI TPS22948 (SLVSEZ7A), TI SN74AXC1T45 (SCES882E), TI DRV2605L, Analog Devices MAX17048 (Pin-Tabelle, Sleep-Abschnitt), Microchip AT42QT2120 (9634E), Same Sky SJ-43504-SMT-TR (Rev. 1.05), GCT USB4510 (Rev. A, 2021-07-01), Molex SD-503480-001 (Rev. J1, **nur Text der Zeichnung, Grafik nicht auswertbar**), Hirose FH12-30S-0.5SH(55) (nur Digi-Key-Parameter).
- Verfügbarkeit nur aus Suchergebnis-Auszügen vom 2026-10-05 (Digi-Key, Mouser); keine Bestellung, kein Warenkorb.

Kennzeichnung: **[D]** Datenblatt, **[L]** aus Layout/Netzliste ermittelt, **[R]** gerechnet/geschätzt, **[?]** ungeprüft.

---

## 1. Befunde Hauptplatine nach Schweregrad

### Blocker (zerstört Bauteile, verhindert Start/Laden oder Bestellung)

| Nr | Bereich | Befund | Beleg | Fix-Vorschlag |
|---|---|---|---|---|
| B1 | I²C-Pegelwandler U30 (PCA9306) | **VREF2 (Pin 7) liegt direkt an 3V3**, EN (Pin 8) separat über R247 200 k an 3V3. Das ist laut TI der „improper setup“: Der Referenz-FET zwischen VREF2 und VREF1 leitet, sobald VCC2 > VCC1 + Vth, und schiebt die 1,8-V-Schiene (VREF1 = `V1P8`) auf VCC2 − Vth ≈ 2,7 V, weil der LDO U34 keinen Strom aufnehmen kann. An `V1P8` hängen VL/VD und über FB1 VA/VCP des CS43131: Absolutgrenze 2,33 V. | [L] U30.7 = `3V3`, U30.8 = `PCA_EN`, R247 `3V3`–`PCA_EN`. [D] PCA9306 §8.1.2 + Fig. 8-1/8-2, §8.1.7 („VREF1 node voltage is VCC2 − Vth“), §9.2.2.1 („EN must be connected to VREF2 and both pins pulled to VDPU through 200 kΩ“). [D] CS43131 Tab. 3-3: VA, VL, VD, VCP max. 2,33 V. | U30 Pin 7 und Pin 8 verbinden, gemeinsam über **einen** 200 k an 3V3, 100 pF von VREF2 nach GND. Bias-Strom (3,3 − 2,4) V / 200 k ≈ 5 µA fließt dann in `V1P8`; das nimmt die Last (DAC) auf. |
| B2 | Strapping IO36 (VDD_SPI) | IO36 (Modulpad 21) ist `SD_D1` mit R57 10 k nach `SD_VDD`. `SD_VDD` ist beim Reset **aus** (TPS22948 ON hat 500 k Pull-down, IO42 ist beim Reset ein Eingang), also ≈ 0 V über C42/Karte. Im Modul zieht R10 = 10 k IO36 nach 3V3. Ergebnis beim Reset ≈ 1,65 V: **undefinierter Strapping-Pegel**. GPIO36 = 0 wählt VDD_SPI = 1,8 V für den Flash (eFuse-Default). Folge: Modul startet nicht oder nur zufällig. Die README-Aussage „Pull-up passt zum Standard“ stimmt nicht, weil der Pull-up an einer abgeschalteten Schiene hängt. | [L] R57 `SD_VDD`–`SD_D1`, U15.21 = IO36 = `SD_D1`, U16.3 ON = `SD_VDD_EN` (IO42). [D] WROOM-1 v0.5 Tab. 3-1 Fußnote 2 („IO36 is pulled up internally within the module“), Fig. 8-1 (R10 10K an VDD33), Tab. 4-1/4-4 (GPIO36 → VDD_SPI 3,3 V / 1,8 V). [D] TPS22948 „Smart ON pin pull down 500 kΩ“. | R57 **nicht bestücken** (Modul-Pull-up 10 k reicht für DAT1) oder R57 an 3V3 statt `SD_VDD`. Gleiches für R61 (IO37) prüfen, siehe N5. README-Text korrigieren. |
| B3 | Lader U10 (MCP73871): SEL/PROG1 | **SEL hoch = AC-Adapter-Modus**, nicht USB (README und Netzlisten-Beschreibung R43 „SEL hoch = USB“ sind falsch). R43 zieht SEL an 3V3 → bei eingeschaltetem Gerät: Eingangsgrenze 1,5–1,8 A, Ladestrom nach PROG1: R39 = 1 k → **1,0 A** (0,9–1,1 A) in eine Zelle von ca. 450–550 mAh (≈ 2 C). Bei ausgeschaltetem Gerät ist 3V3 weg, SEL und PROG2 werden über R43/R36 auf ≈ 0 V gezogen → USB-Modus 100 mA (ca. 6 h Ladezeit). Beides passt nicht: zu hoher Ladestrom (Sicherheit, Zellalterung) bzw. sehr langsames Laden im Aus-Zustand; an einem 500-mA-USB-Port bricht VBUS im AC-Modus ein (VPCC ist abgeschaltet). | [L] R43 `3V3`–`CHG_SEL`, R36 `3V3`–`CHG_PROG2`, R39 1 k an PROG1, U10.2 VPCC = `VBUS_SW`. [D] MCP73871 Elektrische Kennwerte: „AC-Adapter Fast Charge IREG 900/1000/1100 mA, PROG1 = 1 k, SEL = High“; „ILIMIT_AC 1500/1650/1800 mA, SEL = High“; „USB … PROG2 = Low/High, SEL = Low“; VPCC „can be disabled by connecting the VPCC pin to IN“. | Einfachste sichere Lösung: SEL fest auf **GND** (USB-Modus) und PROG2 fest an `VBUS_SW` (500 mA Eingangsgrenze, auch im Aus-Zustand), **ohne** GPIO-Verbindung; IO14/IO15 dann frei. Soll der S31 umschalten können: SEL mit Pull-down als Default, PROG2-Pull-up nur über Teiler oder Serienwiderstand und GPIO als Open-Drain, damit keine 5 V an IO14/IO15 liegen (gleiches Muster wie M5). PROG1 an die Zelle anpassen: für 500 mAh und 0,5–1 C **R39 = 2,0–2,2 k (≈ 450–500 mA)**. Danach Zellen-Datenblatt (max. Ladestrom) prüfen. |
| B4 | Beschaffung U15 | ESP32-S31-WROOM-1-N16R16V laut Suchergebnis-Auszügen (2026-10-05): Digi-Key „Out of stock, 3.250 erwartet am 01-Mar-2027“, Mouser „Out of stock, Factory Lead Time 21 Weeks“. Eine PCBA-Bestellung mit Beschaffung durch PCBWay ist so nicht planbar. | Suchergebnis-Auszüge digikey.com (Teil 29821762) und mouser.co.il, abgerufen 2026-10-05 [?: nicht auf der Seite selbst bestätigt]. | Vor dem Angebot bei PCBWay Lieferbarkeit anfragen oder Module selbst kaufen und beistellen. Bis dahin Board nicht bestellen; S31-DevKit für die Firmware-Tests (B1/B6 in `PROBLEME.md`) zuerst. |

### Hoch (funktioniert wahrscheinlich nicht wie gedacht oder ist ein Sicherheits-/Zuverlässigkeitsrisiko)

| Nr | Bereich | Befund | Beleg | Fix-Vorschlag |
|---|---|---|---|---|
| H1 | CS43131 RESET (Q20) | Logik kehrt sich beim Abschalten um: R245 zieht `DAC_RESET_N` an VP (= `SYS_POWER`, immer vorhanden), Q20 hält RESET nur low, solange sein Gate über R244 an **3V3** liegt. Ist 3V3 aus (Gerät aus) oder fällt beim Abschalten, sperrt Q20 und **RESET geht high, während VL/VD/VA/VCP fehlen oder abfallen**. Datenblatt: RESET erst lösen, wenn alle Schienen stehen; beim Abschalten erst RESET setzen, dann Schienen entfernen, VP zuletzt. Der Ruhestrom „Off“ ist nur mit RESET = LOW spezifiziert. Teilweise Entschärfung: VD-POR des Chips (Tab. 3-18), aber Pop- und Verbrauchsverhalten bleiben ungeklärt. Eine VIH/VIL-Angabe für RESET (VP-Domäne) steht nicht im Datenblatt (gesucht, nicht gefunden). | [L] Q20 G = `DAC_RESET` (R244 100 k an 3V3), D = `DAC_RESET_N` (R245 100 k an `SYS_POWER`). [D] CS43131 §5.2 Power Sequencing; Tab. 3-19 Fußnote 1 („Off configuration: RESET = LOW … VP = 3,6 V“); Tab. 1-1 RESET in Domäne VP. | Nicht einfach den Gate-Pull-up an `SYS_POWER` legen: Das Gate hängt an IO20, dessen ESD-Diode es bei fehlendem 3V3 auf ca. 0,3–0,6 V klemmt, Q20 wäre trotzdem aus. Stattdessen (a) **Spannungswächter auf `V1P8`** mit Open-Drain-Ausgang (Schwelle ca. 1,6 V, z. B. TPS3839-Klasse [?]) auf `DAC_RESET_N`, verodert mit Q20 für die Firmware; R245 bleibt an VP. Damit ist RESET bei fehlender oder fallender 1,8-V-Schiene immer low (§5.2 beim Ein- und Ausschalten erfüllt). Oder (b) `DAC_RESET_N` mit 100 k nach GND als Default und nur auf Befehl über PMOS (Source VP) + NMOS (Gate IO20) hochziehen. Firmware zusätzlich: RESET vor `SYS_PWR_EN = 0` setzen. Ungeprüft, RESET-VIH steht nicht im Datenblatt. |
| H2 | VDDPST_SD-Domäne (IO20–IO25) | I²S (IO22–24), `DAC_RESET` (IO20), `DAC_INT` (IO21, R246 10 k an 3V3) und `SD_CD` (IO25) liegen auf den dedizierten SDIO-Pads. Deren IO-Spannung VDDPST_SD stammt laut S31-Datenblatt **wahlweise aus VDDPST_2 (3,3 V) oder VDD_LDO_1P8**, „configurable via internal registers“; der Reset-Default ist nicht angegeben. Steht der Default oder eine IDF-Einstellung auf 1,8 V, werden die Pins von R244/R246 und den AXC-Ausgängen (VCCB = 3,3 V) überfahren. | [D] ESP32-S31 Datenblatt v0.5 Tab. 2-1 (Pins 27–33: „VDDPST_SD“) und Fußnote 2 („power source can be VDDPST_2 or VDD_LDO_1P8, configurable via internal registers“). [?] Default nicht gefunden. | Vor der Bestellung im TRM/`esp-idf` (`soc`/`sdmmc`-LDO) den Default nachlesen. Wenn unklar: DAC-Leitungen auf normale 3,3-V-GPIO legen (frei: IO8, IO43–IO47, IO52–IO57). Umgekehrt: Bei sicherer 1,8-V-Domäne könnten U31–U33 und Teile von U30 entfallen. |
| H3 | Kupferquerschnitt Leistungsnetze | `SYS_POWER`, `VBUS`, `VBAT` laufen teilweise auf **In2 (0,5 oz) mit 0,25 mm** (19/9/14 Segmente). Nach IPC-2221 trägt das bei 10 K Erwärmung nur ca. **0,26 A** (außen 1 oz: ca. 0,9 A). Gefordert: Ladestrom + Systemlast (heute bis 1,65 A Eingang, nach B3-Fix ca. 0,5–0,7 A), Boost-Eingang im Host-Betrieb ca. 0,9 A. `BOOST_SW` (Schaltknoten TPS61023, Spulenstrom bis Strombegrenzung 3,7 A) ist **0,127 mm** breit (10 Segmente). Auch die **3V3-Zuleitung** vom LDO U4 (y ≈ +4,5) zum Modul-Pad U15.2 (y ≈ +28,8, ca. 33 mm) besteht aus 0,25-mm-Bahnen auf F.Cu, B.Cu **und In2**; WLAN-Sendespitzen des S31 liegen bei mehreren 100 mA. Der Bulk-C29 (100 µF) sitzt bei y ≈ −29, also ca. 58 mm vom Modul entfernt; am Modul nur C101 22 µF. | [L] `pcbnew`-Auswertung: z. B. SYS_POWER {F.Cu 0,25: 15, B.Cu 0,25: 34, In2 0,25: 19, 7 Vias}, BOOST_SW {F.Cu 0,127: 10}. [R] IPC-2221-Näherung, Werte in Abschnitt 4. [D] TPS61023: Schalterstrom 3,7 A. | Leistungsnetze auf Außenlagen mit ≥ 0,5 mm (besser Flächen) und je Lagenwechsel ≥ 2 Vias; `BOOST_SW` als kurze, breite Kupferfläche (U20–L20 ≤ 2 mm); 3V3 zum Modul ≥ 0,5 mm außen oder als Fläche, zusätzlicher Bulk (≥ 47 µF) direkt am Modul. Danach DRC neu. |
| H4 | Display-Stecker J20 Höhe | **Hirose FH12-30S-0.5SH(55) ist 2,0 mm hoch** (Bottom Contact). README/TEILE gehen von 1,0 mm aus; J20 sitzt bei (0; −0,5) **in der Display-Zone** (y −6,5…+40,5), in der nur Teile ≤ 1,0 mm bei ≥ 1,1 mm Luft vorgesehen sind. Kollision mit dem Panel. | [D] Digi-Key FH12-30S-0.5SH(55): „Height Above Board 2.00 mm“, „Contacts, Bottom“, FFC 0,30 mm. [L] J20 bei (100; 100,5) abs., README Tab. „Mechanik“ J20 „1,0 mm“. | 1,0-mm-Typ wählen (z. B. Molex 503480-3000, gleiche Familie wie J21, Dual Contact; Footprint dann neu und **gegen Zeichnung**), oder J20 aus der Display-Zone legen. Kontaktseite/Faltung des Panel-FPC dabei festlegen. |
| H5 | USB-HS-Paar (480 Mbit/s) | Bestätigt A15: `USB_DP` 86,5 mm / 5 Vias, `USB_DN` 87,7 mm / 3 Vias, 0,2 mm Bahn, über F.Cu/In2/B.Cu verteilt, nicht gekoppelt. B.Cu-Abschnitte haben als Referenz In2 (Signal- **und** GND-Lage, also lückenhaft). Im Projekt ist **kein Lagenaufbau** hinterlegt (`stackup` fehlt in der `.kicad_pcb`), die Impedanz ist damit unbestimmt. | [L] `pcbnew`: USB_DP {F 6, B 7, In2 8 Segmente, 0,2 mm}, USB_DN {F 4, B 12, In2 17}. [R] Schätzung Abschnitt 4: bei 0,2 mm Prepreg ergibt 0,2/0,127 mm ca. 98 Ω differenziell, bei 0,1 mm Prepreg 0,15/0,2 mm ca. 91 Ω. | PCBWay-Lagenaufbau für 4 Lagen/1,0 mm anfragen, daraus Breite/Abstand für 90 Ω rechnen, Paar gekoppelt auf **F.Cu über In1 (GND)** führen, max. 2 Vias je Leitung, Längenunterschied ≤ 1 mm, Impedanzkontrolle bestellen. Kurz halten: USB-C bei x = +9 und Modul-Pads 54/55 liegen 80 mm auseinander; ggf. Modul oder Buchse umplatzieren. |
| H6 | Klickrad-Stecker: zwei verschiedene Footprints für dasselbe Teil | J21 (Hauptplatine) und J1 (Klickrad) sind beide Molex 503480-0600, haben aber **verschiedene Landmuster**: J21 Signalpads 0,3 × 0,7, Nagelpads 0,8 × 1,0 bei x ±2,045; J1 Signalpads 0,3 × 1,3, Nagelpads **1,8 × 2,2 bei x ±3,15** (Hirose-FH12-Maße). Der Molex-Zeichnungstext nennt ein Montagefeld „0,79 / 0,5(N−1) / 0,79“ (Summe 4,08 = Maß C für 6 Pole) und eine Nagel-Schablonenöffnung 1,0 × 0,3. Je nach Lesart liegt die Nagel-**Mitte** oder die Nagel-**Außenkante** bei ±2,04 mm (Interpretation, Grafik nicht gelesen). In beiden Fällen liegen die Klickrad-Nagelpads (Innenkante bei 2,25 mm, Mitte 3,15 mm) **neben** den Nägeln, der Stecker hält dort nur an den Signalpins. Die Y-Lage der Nägel ist in beiden Footprints ungeprüft (A7/A13). | [L] Footprints `Hauptplatine.pretty/Molex_503480-0600` und `Klickrad.pretty/Molex_503480-0600_1x06-1MP_P0.50mm_Horizontal`. [D] Molex SD-503480-001 Rev. J1, Text: „P.W.BOARD PATTERN … 0.79 / 0.5(N−1) / 0.79“, „OPENING AREA: TERM.(0.7X0.3) NAIL(1.0X0.3)“, Tabelle 6-pol.: A 4,7 / B 2,5 / C 4,08 / D 3,5 [Grafik nicht ausgewertet]. | Ein gemeinsamer, gegen die Molex-Zeichnung (PDF-Grafik bzw. Molex-CAD-Download) vermessener Footprint für beide Platinen. Bis dahin beide als **ungeprüft** behandeln. |
| H7 | Thermistor | R1 (10 k NTC→GND, aus Tangara) liegt **parallel** zum NTC-Pad BT1.1. Mit einer Zelle mit 10-k-NTC ergibt das 5 k × 50 µA = 0,25 V = **Hot-Schwelle VT2** schon bei Raumtemperatur → Laden setzt aus/pendelt. Mit einer Zelle ohne NTC ist R1 richtig. | [L] R1 `NTC`–`GND`, BT1.1 = `NTC`, U10.5 THERM = `NTC`. [D] MCP73871: ITHERM 47/50/53 µA, VT2 0,23/0,25/0,27 V, VT1 1,24 V. Tangara-Netzliste hat ebenfalls R1 10 k. | Entweder NTC der Zelle **oder** R1, nicht beides: R1 als DNP-Option dokumentieren und abhängig von der gekauften Zelle bestücken. Zellentyp (2- oder 3-adrig) jetzt festlegen (A16). |
| H8 | Kabelweg/Flashen | USB-Serial/JTAG (IO33/IO34) geht nur auf Testpunkte TP12/TP13. Der USB-C-Port hängt am HS-OTG-PHY. Laut Datenblatt kann der Joint-Download-Modus auch über **USB 2.0 HS OTG** flashen (gut), aber nur mit BOOT (IO61) = 0 beim Reset; BOOT/EN liegen nur auf Testpunkten TP14–TP17, die im geschlossenen Gehäuse nicht erreichbar sind. Ohne JTAG/Konsole am USB-C ist Fehlersuche im Gehäuse kaum möglich. | [L] TP12–TP17. [D] WROOM-1 v0.5 Tab. 4-3 Fußnote 2 (USB-OTG Download Boot), §4.1. | BOOT auf einen von außen erreichbaren Taster legen (z. B. SW1-Kombination ist nicht möglich, also kleiner zweiter Taster oder Pogo-Pin-Feld an der Gehäusekante); Firmware-Weg „Reboot in Download-Modus“ per Software vorsehen. Optional analoger USB-Schalter USB-C ↔ USB-Serial/JTAG. |
| H9 | Bauteil-Lieferbarkeit CS43131 | Mouser listet CS43131-CNZR mit „Minimum 4000 / Reel“; Digi-Key ca. 18,5 USD als Cut Tape, Bestand nicht bestätigt; Hersteller-Lieferzeit laut `AUDIO.md` ca. 20 Wochen. | Suchergebnis-Auszüge 2026-10-05 [?]; `PROBLEME.md` A6. | Vor der Bestellung 2–3 Stück sichern (Digi-Key CT) oder Plan B (CS43198 + OPA1622) entscheiden. |
| H10 | Mechanik USB-C | GCT USB4510-03-1-A: „Recommended PCB Layout **Thickness = 0.80 mm**“ (Mid-Mount, 1,6 mm Offset). Die Platine ist 1,0 mm. Klärt A14 für die USB-Buchse mit „nicht freigegeben“; Folge: Buchse sitzt 0,2 mm anders als im Gehäuse-CAD, THT-Laschen ragen weniger heraus, Steckerführung nicht geprüft. | [D] USB4510 Rev. A Blatt 1, Text „Recommended PCB Layout Thickness=0.80mm“. [L] Platinendicke 1,0 mm (`GetBoardThickness`). | Bei GCT nachfragen oder 3D-Modell bei 1,0 mm prüfen; sonst 0,8 mm Platine (TEILE.md „0,8 mm nur, wenn nötig“) oder andere Buchse für 1,0 mm. Für die SJ-43504 nennt das Datenblatt **keine** Plattendicke [?]. |

### Mittel (sollte vor der Bestellung behoben oder bewusst akzeptiert werden)

| Nr | Bereich | Befund | Beleg | Fix-Vorschlag |
|---|---|---|---|---|
| M1 | USB-Rollenlogik Q1/Q10/D10 | Bei eingeschaltetem Gerät und angestecktem Ladegerät fließt Strom von VBUS über R113 und D10 in `TUSB_ID`: rechnerisch `TUSB_ID` ≈ 4,0 V (3,3 V + 0,7 V), über der Grenze VDD + 0,3 V von TUSB320-ID und IO3. Im Aus-Zustand (3V3 = 0) hängt das Durchschalten von Q1 (Laden!) an Q10 mit Gate ≈ 2,6 V, also knapp über Vgs(th) max. des 2N7002T (aus dem Gedächtnis 2,5 V [?]). | [L] R113 100 k `VBUS`–`Q1_GN`, D10 A1 = `Q1_GN`, K = `TUSB_ID`, R112 100 k an 3V3. [R] Knotengleichung. [D] TUSB320LAI Abs.-Max. ID ≤ VDD + 0,3 V. | Rollen-Pfad neu: Q1 standardmäßig EIN (Gate-Pull-down), im Host-Betrieb über `HOST_EN` aktiv AUS; oder fertigen Power-Mux/Lastschalter mit Rückstromsperre. Simulation oder Aufbau-Test einplanen. |
| M2 | CS43131 VP | VP = `SYS_POWER` = VBUS minus Durchlass bei USB-Betrieb. Betriebsbereich VP 3,0–5,25 V, Abs.-Max. 6,3 V. Ladegeräte mit 5,3–5,5 V liegen über dem Betriebsbereich. | [D] CS43131 Tab. 3-2/3-3. [L] U17.26 = `SYS_POWER`. | Akzeptabel, aber notieren; alternativ VP aus `VBAT` oder über Schottky/LDO auf ≤ 5,0 V begrenzen. |
| M3 | Ausgangskondensatoren Boost | C112 ist laut Beschreibung „25 V X5R“, die MPN GRM188R60J226MEA0 ist aber **6,3 V**; an 5,1 V bleiben von 22 µF + 10 µF (0603) effektiv grob 6–8 µF [R]. Datenblatt: effektiv 4–1000 µF, typ. 10 µF. Funktioniert vermutlich, Reserve gering. L20 (DFE201610E-1R0M, Isat ca. 3 A [?]) liegt unter der Schalterstrombegrenzung 3,7 A; TI empfiehlt Spulen mit 7–9,6 A Isat. Footprint L20 = `L_0805` als Näherung für 2016-Gehäuse. | [L] C112/C113/L20 in BOM. [D] TPS61023 Tab. „COUT effective 4/10/1000 µF“, Tab. 8-2. | C112 als 10-V- oder 16-V-Typ (z. B. 0805 wenn Höhe erlaubt), L20-Footprint nach Murata-Landmuster, Spule mit Isat ≥ 3,7 A wählen oder Strombegrenzung akzeptieren. |
| M4 | Vias in Signal-Pads | Vias liegen **in** den Pads von U10 Pin 13 (PROG1, QFN 0,5 mm), R39.1 und R121.2 (aus `maze.py`). Nicht gefüllte Vias ziehen Lot ab → offene Lötstellen am QFN. | [L] `pcbnew`-Prüfung „Via in SMD-Pad“: U10.13, R39.1, R121.2 (EP-Vias von U10/U17/U34 sind gewollt). | Vias aus den Pads schieben oder „Via in Pad, gefüllt und überkupfert“ bestellen (Mehrpreis). |
| M5 | Taster-Eingang KEY_LOCK_MCU | Bei gedrücktem SW1 liegt `KEY_LOCK` ≈ 0,91 × `SYS_POWER` (bis 4,6 V mit USB) über R201 10 k an IO5 (3,3-V-Pin, nicht 5-V-fest). Bei ausgeschaltetem Gerät speist das über die ESD-Diode in die 3V3-Schiene. Strom ca. 0,1–0,4 mA [R]. | [L] R4/R200/R201, U15.7. | Teiler (z. B. R201 10 k + 18 k nach GND) oder Schottky-Klemme an 3V3. |
| M6 | Stückliste unvollständig | Ohne MPN: R110 (887 k), R116 (390 k), R117 (51 k), R118 (49,9 k, setzt den Strom von U21), R247 (200 k), C245/C246 (15 µF 0603, Typ offen), R1, TP7. Nur sehr wenige LCSC-Nummern; Spalte „Nummer geprüft“ fast überall NEIN. | `fertigung/hauptplatine_BOM_PCBWay.csv`. | Alle Positionen mit MPN (1 %-Typen für Teiler/ILIM), 15 µF prüfen (alternativ 2 × 10 µF oder 22 µF 0603, Datenblatt nennt „15 µF nominal“). |
| M7 | CPL/Pin 1 | CPL enthält KiCad-Rohwerte (Unterseite z. B. U17 180°, U15 90°). PCBWay rechnet Unterseiten-Drehungen je nach Konvention um; nicht geprüft. Kritisch sind QFNs ohne sichtbare Pin-1-Markierung (U10, U17, U12 X2QFN, U4/U21/U34 WSON) und J20/J21. | `fertigung/hauptplatine_CPL_PCBWay.csv`. | Bei PCBWay ausdrücklich die Bestückungsvorschau (DFM-Bilder) anfordern und je Teil gegen Pin 1 im Siebdruck abhaken (README Schritt 6). |
| M8 | Fertigungsregeln Via | Alle 346 Vias 0,45/0,2 mm → Restring 0,125 mm. PCBWay-Standard für Restring ist nach meiner Erinnerung ≥ 0,15 mm [?]; 0,2-mm-Bohrung kann Aufpreis kosten. | [L] Via-Statistik. | Kapazitäten bei PCBWay prüfen; ggf. 0,5/0,25 mm. |
| M9 | 3V3-Versorgung bei leerem Akku | TLV75733 (LDO) aus `SYS_POWER`: unter ca. 3,5–3,6 V Akkuspannung fällt 3V3 bei WLAN-Spitzen unter 3,3 V (Dropout). Im USB-Betrieb Verlust (5 − 3,3) V × I im WSON-6. Wie Tangara, aber S31 + AMOLED + DAC-LDO hängen alle an 3V3. | [D] TLV757P Tab. Dropout, Abs.-Max. VIN 6,0 V. [L] U4 IN = `SYS_POWER`. | Firmware-Abschaltschwelle ≥ 3,4 V; mittelfristig Buck-Boost (z. B. TPS63802) prüfen. |
| M10 | ESD an CC mit DRP | U5 (PE1605C4A6, Klemme mit Rail-Diode an VBUS) sitzt an CC1/CC2. Als DRP legt TUSB320 Rp (Stromquelle bis VDD) auf CC; ohne VBUS kann die Rail-Diode VBUS auf ca. CC − 0,6 V anheben. Wirkung auf die Erkennung ungeprüft. Kapazität von PE1605 für 480 Mbit/s nicht nachgelesen (Hersteller: „ultra low capacitance“). | [L] U5 Pins 4/6 = CC1/CC2, 5 = VBUS. [?] | CC-Leitungen mit eigenem Low-Cap-TVS ohne Rail-Diode schützen (oder Datenblatt PE1605 prüfen und am Aufbau messen). |
| M11 | Akku-Lötpads | BT1: NTC, GND, BAT+ auf 2,0 mm Raster mit 1,5 mm Pads (0,5 mm Spalt), nur „+“ im Siebdruck. Beim Anlöten der Litzen leicht Brücke BAT+–GND; kein Sicherungselement auf der Platine (nur PCM der Zelle). Die Akku-Polarität ist hier kein Stecker-Thema (keine JST/MX-Buchse), sondern Litzen-Lötung. | [L] BT1-Footprint `BATT_PADS_3`, Siebdruck „+“ bei Pad 3. | Pads auf ≥ 2,5 mm Raster, „−“ und „NTC“ beschriften, Zelle **mit** Schutzschaltung kaufen; vor dem Anlöten Polarität mit Multimeter prüfen. |
| M12 | Antennenfreiraum | Keepout auf der Platine eingehalten (README), aber Display-Rahmen überlappt den Keepout (C8) und der Akku liegt 3 mm unter dem Modul. | `PROBLEME.md` C8; README „Offene Risiken“ 1. | Display-Lage aus der Panel-Zeichnung festlegen; ggf. Modul um 90° drehen oder Antenne über die Kante ragen lassen. |

### Niedrig (Hinweise, Dokumentation, Firmware)

| Nr | Bereich | Befund | Beleg | Fix-Vorschlag |
|---|---|---|---|---|
| N1 | U16 TPS22948 Pin 5 | Pin 5 ist **FLT** (Open-Drain-Ausgang), nicht GND; im Schaltplan auf GND gelegt. Elektrisch harmlos (Ausgang zieht nur nach GND), Fehlerinfo geht verloren. | [D] TPS22948 Pin-Tabelle (DCK: 5 = FLT). [L] U16.5 = GND. | Symbol korrigieren, Pin offen lassen oder an GPIO. |
| N2 | SD_CD ohne Pull-up | Kartenerkennung (IO25) hat keinen externen Pull-up; Molex 104031 schaltet nach GND. | [L] Netz `SD_CD` nur J4.9 und U15.20. | Internen Pull-up in der Firmware aktivieren (IO25 liegt in VDDPST_SD, siehe H2) oder 100 k an 3V3. |
| N3 | HOST_EN | Netz wird von Q11 (Open-Drain) und R115 bestimmt; IO2 hängt parallel. Firmware darf IO2 nie push-pull high treiben (Kurzschluss gegen Q11). | [L] Q11 D = `HOST_EN`, U15.4. | Firmware: IO2 nur als Open-Drain/Eingang; im Schaltplan vermerken. |
| N4 | Display-Touch-Reset | TP_RST fest high (R132), der Touch-Controller (FT3168, I²C 0x38) kann nicht per GPIO zurückgesetzt werden. | [L] R132. | Optional an freien GPIO. |
| N5 | IO37 (JTAG-Quelle) | R61 zieht IO37 (SD_D2) an das beim Reset abgeschaltete `SD_VDD`. Mit Default-eFuses wird IO37 ignoriert, also unkritisch; wer `EFUSE_JTAG_SEL_ENABLE` brennt, bekommt Pad-JTAG. | [D] WROOM-1 v0.5 Tab. 4-7. | Keine eFuses brennen; R61 wie R57 an 3V3 legen. |
| N6 | AXC-Eingang I2S_DOUT | U33-Eingang B (`I2S_DOUT`, IO24) floatet bis die Firmware den Pin konfiguriert; Datenblatt: Eingang nicht floaten lassen. | [D] SN74AXC1T45 Pin-Tabelle. | 100 k Pull-down an `I2S_DOUT`. |
| N7 | Doku-Widersprüche | README nennt U34 „gleiche Familie TLV757P“, MPN TLV75518P ist TLV755P (500 mA, gleiche DRV-Belegung – unkritisch). README „J20 1,0 mm“ (siehe H4), „SEL hoch = USB“ (B3), „IO36-Pull-up passt“ (B2), C112 „25 V“ (M3). | Netzliste/BOM/README. | Beim Fix mitkorrigieren. |
| N8 | Fuel Gauge | MAX17048: CTG und QSTRT an GND, VDD = CELL = VBAT, EP an GND: richtig. Sleep über SDA/SCL-low nur bei `EnSleep = 1` – kein Problem bei ausgeschaltetem 3V3. ALRT an LP-GPIO IO1 mit Pull-up: richtig. | [D] MAX17048 Pin-Tabelle, Abschnitt Sleep. | – |
| N9 | Klinke HP_DETECT | Spitzenschalter (Pin 5) ist ruhend mit der Spitze verbunden; CS43131 erwartet „offen ohne Stecker, an Spitze mit Stecker“. Die Umkehr über `HPDETECT_INV` ist im Datenblatt vorhanden. Kein ESD-Schutz auf `HP_DETECT`. | [D] CS43131 §4.5.1.2, Register HPDETECT_INV; SJ-43504 Schaltbild. | Firmware setzt HPDETECT_INV; optional ESD auf HP_DETECT. |

---

## 2. Geprüft ohne Befund

| Prüfpunkt | Ergebnis | Beleg |
|---|---|---|
| ESP32-S31-WROOM-1 Landmuster | Rand-Pads 1–40 (1,5 × 0,9, Raster 1,27, Pin 1 bei 7,49 mm unter der Oberkante), 20 Innen-Pads 0,4 × 0,8 (Raster 0,8; Reihen 42–49, 50–55, 61–56) und 3 × 3 GND-Pads 0,9 × 0,9 stimmen mit Abb. 11-1 überein; Nummerierung der Innen-Pads passt. | [D] WROOM-1 v0.5 Abb. 11-1, Tab. 3-1; [L] Footprint-Pads |
| WROOM-1 Pinbelegung | Pad → GPIO der Netzliste stimmt mit Tab. 3-1 (u. a. 26 = IO60, 27 = IO61, 36/37 = RX0/TX0, 54/55 = USB_DM/DP, 13/14 = IO33/IO34 USB-Serial/JTAG). | [D] Tab. 3-1 |
| Boot/Strapping | IO61 (BOOT) 10 k Pull-up + 100 nF, IO60 offen (interner Pull-up → SPI-Boot), EN 10 k/1 µF (τ 10 ms ≫ BOOT-τ 1 ms, Hold-Zeit 3 ms erfüllt). Download über UART0, USB-Serial/JTAG **und USB-OTG** möglich. | [D] Tab. 4-1, 4-2, 4-3 |
| SDMMC-Slot 2 auf IO35–IO40 (VDDPST_3, 3,3 V) | zulässig laut IO-MUX (SD2_CDATA0…CCMD) | [D] Tab. 3-1, S31 Tab. 2-1 |
| CS43131 Pinbelegung | alle 40 Pins gegen Tab. 1-1 geprüft (Pin 30 = ADR an GND → Adresse …00; HPINA/B 12/15 offen, haben Pull-down; TSO offen) | [D] Tab. 1-1, Tab. 4-12 |
| CS43131 Beschaltung | VL/VD 100 nF, VA 2,2 µF, −VA 2,2 µF, FLY_VA 2,2 µF, FILT± 15 µF, VCP-Filter 3 × 2,2 µF + 2 Fly-Caps, VP 0,1 + 4,7 µF, Quarz-Lastkapazitäten C0G: entspricht Fig. 2-1 (EXT_VCPFILT = 0). Quarz NDK NX2016SA 22.5792M ist in Tab. 5-1 gelistet (Register 0x20052 = 0x02). HPREFA/B einzeln an die Hülse, Net-Tie an der Buchse: wie Fig. 2-1. | [D] Fig. 2-1, Tab. 5-1 |
| I²S-Richtung | DAC als Master: U31/U32 DIR = VCCA (A→B, DAC→S31), U33 DIR = GND (B→A, S31→DAC). Pinbelegung DRL korrekt. | [D] SN74AXC1T45 Tab. 4-1 |
| Power-Up-Reihenfolge DAC | VP liegt immer an (Batterie), 1,8 V kommt nach 3V3: erfüllt „VP zuerst“ (Abschalten siehe H1) | [D] CS43131 §5.2 |
| TUSB320LAI | Pin 3 PORT offen = DRP, Pin 5 ADDR an GND = 0x47, Pin 11 EN_N an GND, VBUS_DET über 887 k (Datenblatt 855–920 k), ohne VDD **Rd auf CC (Dead Battery)** → Ladegerät liefert auch bei ausgeschaltetem Gerät 5 V. Die 5,1-kΩ-Widerstände sind deshalb nicht nötig. | [D] SLLSEQ8D Pin-Tabelle, §7.3.3 |
| TPS2553DRV / TPS61023DRL / TLV757P DRV / TPS22948 DCK | Pinbelegungen stimmen (Ausnahme N1). TPS2553 EN aktiv high, RILIM 49,9 k → 475–565 mA. TPS61023 FB 595 mV → 5,14 V, „true disconnect“ im Aus-Zustand. | [D] jeweilige Pin-Tabellen |
| MCP73871 Pins/Kondensatoren | Pin 9 TE an GND (Timer an), VPCC an IN (abgeschaltet, zulässig), CE über 10 k an SYS_POWER, ≥ 4,7 µF an IN/OUT/VBAT, PROG3 10 k → 100 mA Abschaltstrom. | [D] MCP73871 Pin-Tabelle, Kennwerte |
| Q1-Richtung | PMOS mit S an VBUS: Body-Diode sperrt VBUS→VBUS_SW, im Host-Betrieb fließt kein Boost-Strom in den Lader. | [L] Q1 |
| I²C-Adressen | 0x1C (QT2120), 0x30 (CS43131, hinter PCA9306), 0x36 (MAX17048), 0x38 (FT3168, laut Waveshare-Wiki/GitHub), 0x47 (TUSB320LAI), 0x5A (DRV2605L): keine Kollision. Pull-ups 2,2 k (3V3) bzw. 4,7 k (1,8-V-Seite), nur einmal auf dem Bus. | [D]/[L] |
| SJ-43504 | Pinbelegung 1 Hülse, 2 Spitze, 3 Ring 1, 4 Ring 2, 5 Spitzenschalter, 6 Ring-1-Schalter; Schlitz 6,80 mm, Ø-1,30-Nasen 7,50 mm von der Kante als Kerben in der Kontur vorhanden; Pad-Raster der Spalte 1/3/6 exakt, Spalte 4/2/5 innerhalb ca. 0,2 mm; Pads 1,35 × 2,0 statt 1,7 × 1,5 (schmaler, wegen 0,3 mm Abstand zum Schlitz). | [D] SJ-43504 Rev. 1.05 „Recommended PCB Layout“; [L] Edge.Cuts |
| USB4510 Pads | 16-Pin-Muster (0,6/0,3 mm) wie Datenblatt, D+/D− beider Reihen verbunden, CC1/CC2 getrennt; Plattendicke siehe H10. | [D] USB4510 Rev. A |
| ESD Klinke | D5V0L2B3T bidirektional an HPOUTA/B | [L] U3 |

## 3. Nicht prüfbar (ausdrücklich ungeprüft)

- **Molex 503480-0600 Landmuster:** nur Zeichnungstext lesbar (Signalpads 0,3 × 0,7, Raster 0,5, Nagel-Schablone 1,0 × 0,3, Versatz 0,79). Lage der Nägel in Y und Lage von Pin 1 („CIRCUIT NO.1“) zur Kabelmündung nicht gesichert. Ebenso ob das gerade, ungedrehte FFC Pin 1 auf Pin 1 bringt (A11).
- **VDDPST_SD-Default** (H2) und maximale BCLK im I²S-Slave-Betrieb (B6).
- **PCBWay-Lagenaufbau 4 Lagen/1,0 mm**, Impedanz, Mindest-Restring, CPL-Konvention Unterseite.
- **Panel-FPC des 2,06"-Displays:** Kontaktseite, Pinfolge, Lage; Waveshare-Belegung übernommen, nicht gegen das Panel-Datenblatt geprüft.
- **PE1605C4A6** (Kapazität, Klemmverhalten), **2N7002T** Vgs(th), **DFE201610E-1R0M** Isat: Datenblätter nicht geladen.
- **CS43131 RESET-Schwellen** (VP-Domäne): im Datenblatt nicht gefunden.
- SJ-43504 bei 1,0 mm Platinendicke (Datenblatt nennt keine Dicke), STEP-Ursprung/Höhenversatz (A5).
- Lieferbarkeit aller übrigen Teile, LCSC-Nummern.
- Routing-Qualität im Analogteil (HPOUT/HPREF 0,127 mm, Rückstrompfade) und Antennenleistung im Gehäuse.

## 4. Rechnungen (Schätzungen)

**Strombelastbarkeit Leiterbahn (IPC-2221, ΔT = 10 K / 20 K):** 0,25 mm × 35 µm außen: 0,88 / 1,19 A; 0,25 mm × 17,5 µm innen: 0,26 / 0,36 A; 0,127 mm × 35 µm außen: 0,54 / 0,73 A. Widerstand 0,25 mm × 35 µm: ca. 2 mΩ/mm (100 mm ≈ 0,2 Ω).

**Differenzielle Impedanz Microstrip (IPC-2141-Näherung, εr 4,4, 35 µm):**

| Prepreg h | Breite / Abstand | Z0 einzeln | Zdiff |
|---|---|---|---|
| 0,10 mm | 0,127 / 0,127 mm | 53 Ω | 92 Ω |
| 0,10 mm | 0,15 / 0,20 mm | 49 Ω | 91 Ω |
| 0,20 mm | 0,25 / 0,15 mm | 59 Ω | 90 Ω |
| 0,21 mm | 0,25 / 0,15 mm | 61 Ω | 92 Ω |
| 0,20 mm | 0,20 / 0,127 mm (heute 0,2 mm, ungekoppelt) | 66 Ω | (97 Ω gekoppelt) |

Nur Anhaltswerte; maßgeblich ist der Rechner/Lagenaufbau von PCBWay.

**MCP73871-Thermistor:** 50 µA × (10 k ∥ 10 k) = 0,25 V = VT2 (heiß). 50 µA × 10 k = 0,50 V (Mitte des Fensters 0,25…1,24 V).

**PCA9306 falsch beschaltet:** `V1P8` steigt bis 3,3 V − Vth (≈ 0,6 V) ≈ 2,7 V > 2,33 V (Abs.-Max. CS43131).

**IO36 beim Reset:** 3,3 V × 10 k / (10 k + 10 k) ≈ 1,65 V bei `SD_VDD` = 0 V (Kartenlast nicht eingerechnet, mit Karte eher niedriger).

---

## 5. Klickrad v2 (`hardware/pcb/klickrad/`)

| Nr | Schwere | Befund | Beleg | Fix-Vorschlag |
|---|---|---|---|---|
| K1 | Hoch | Molex-Footprint J1 ist eine Hirose-FH12-Kopie: Nagelpads 1,8 × 2,2 bei x ±3,15 treffen die Nägel des 503480 (bei ca. ±2,04) nicht; Signalpads 1,3 statt 0,7 mm lang. Siehe H6. | [L] `Klickrad.pretty/Molex_503480-0600_…`; [D] Molex SD-503480-001 (Text) | Gemeinsamen geprüften Footprint mit der Hauptplatine verwenden. |
| K2 | Mittel | Kein 10-µF-Puffer am DRV2605L (Abweichung zu Tangara); LRA-Stromspitzen kommen über 6-pol. FFC. | README Klickrad | 10 µF auf der Hauptplatine direkt an J21 (3V3–GND) ergänzen. |
| K3 | Mittel | AT42QT2120 bei LCSC nicht auf Lager (A8); Rad 24,6 mm unter Datenblatt-Empfehlung 30–50 mm, GND-Gitter näher (A9); Rückseitenbauteile 1,1 mm statt 0,8 mm. | `PROBLEME.md` A8/A9 | Bauteile vorab bei Mouser/Digi-Key sichern; Empfindlichkeit am ersten Muster messen; Platine bei Bedarf 1,0 mm. |
| K4 | Niedrig | Exposed Pad des QT2120 an GND (Tangara: offen). Datenblatt verlangt nichts Gegenteiliges (nur Pins 8 VSS, 10 MODE an GND); unkritisch. | [D] AT42QT2120 Tab. 1-2 | – |
| K5 | geprüft | QT2120 VQFN-Pinbelegung (Comms-Modus) stimmt: 3 KEY4 Guard, 4 KEY3 Mitte, 5–7 KEY2–0 Wheel, 10 MODE an GND, 11 SDA, 12 RESET (10 k), 14 SCL, 15 CHANGE (Pull-up 10 k auf der Hauptplatine). DRV2605L DGS: 1 REG, 2 SCL, 3 SDA, 4 IN/TRIG (GND), 5 EN (10 k), 6/10 VDD, 7 OUT+, 8 GND, 9 OUT−: stimmt. | [D] AT42QT2120 Tab. 1-2; DRV2605L DGS-Pinout | – |
| K6 | Mittel | FFC-Kabel: BOM nennt Molex 0150200056 „Beispiel, Typ nicht geprüft“. Raster (0,5 mm), Kontaktseite (gleichseitig, Typ A) und Länge (S-Bogen 3,5 mm frei) vor dem Kauf prüfen; Pin 1 auf Pin 1 vor dem Einschalten durchklingeln (A11). | BOM, README Hauptplatine „Klickrad-Anschluss“ | Kabel nach geprüftem Footprint festlegen. |

---

## 6. Fazit

**Bestellbereit: nein.**

Nötig vor einer Bestellung, in dieser Reihenfolge:

1. **B1** PCA9306 umverdrahten (VREF2 = EN, ein 200 k, 100 pF).
2. **B2** R57 (und R61) nicht an `SD_VDD`; R57 DNP oder an 3V3.
3. **B3** Lader: SEL auf USB-Modus (GND bzw. GPIO mit Pull-down), PROG2-Pull-up an eine immer vorhandene Schiene, R39 auf ca. 2,0–2,2 k für die gewählte Zelle; **H7** R1/NTC entscheiden (Zelle festlegen).
4. **H1** DAC-RESET-Logik so ändern, dass RESET ohne 3V3 low bleibt.
5. **H2** VDDPST_SD-Default klären oder DAC-Leitungen auf 3,3-V-GPIO legen.
6. **H3** Leistungsnetze verbreitern/auf Außenlagen, `BOOST_SW` als Fläche.
7. **H4** J20 durch 1,0-mm-Stecker ersetzen oder versetzen.
8. **H6/K1** Einen gemeinsamen Molex-503480-Footprint gegen die Zeichnung (Grafik/CAD-Download) erstellen, auf beiden Platinen verwenden.
9. **H5** Lagenaufbau bei PCBWay erfragen, USB-HS als gekoppeltes 90-Ω-Paar auf F.Cu neu führen.
10. **H10** Plattendicke 0,8 gegen 1,0 mm für USB4510 (und SJ-43504) entscheiden.
11. **M1, M3, M4, M6** (Rollenlogik, C112/L20, Vias in Pads, fehlende MPNs) beheben.
12. **B4/H9** Beschaffung: S31-Modul und CS43131 vorab sichern; vorher S31-DevKit-Tests (A2DP, USB-UAC, PSRAM) laut `PROBLEME.md` B1.
13. Danach: ERC/DRC neu, Netzliste erneut gegen diese Liste prüfen, PCBWay-Bestückungsvorschau (CPL, Pin 1, Unterseite) abhaken (M7), erst dann bestellen.

Die Klickrad-Platine v2 kann nach Behebung von **K1** (Footprint) separat bestellt werden; sie ist elektrisch unauffällig, ihr Funktionsrisiko (Empfindlichkeit, A9) lässt sich nur am Muster klären.
