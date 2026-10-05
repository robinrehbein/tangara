# Modul-Alternativen: ESP32-S31 nicht lieferbar (Fund B4)

Stand der Recherche: **2026-10-05**. Auslöser: `docs/REVIEW-HAUPTPLATINE.md` Fund B4 (ESP32-S31-WROOM-1-N16R16V bei Digi-Key und Mouser nicht lieferbar).
Kennzeichnung: **[Q]** = Seite am 2026-10-05 abgerufen (Quelle genannt), **[S]** = nur Suchergebnis-Auszug, **[?]** = ungeprüft/nicht belegt. Preise in USD, wenn die Seite USD zeigt; nichts umgerechnet.

## 1. Kurzfassung

1. **WROOM-1 ist (noch) nicht beschaffbar, WROOM-3 schon eher.** Für WROOM-1 gibt es keinen Lagerbestand bei irgendeinem geprüften Händler, das Datenblatt ist „Pre-release v0.5, PRELIMINARY“, Espressif verlinkt auf der S31-Produktseite nur beim WROOM-3 eine Bezugsquelle. Beide Dev-Boards tragen das WROOM-3.
2. **Ein „ESP32-S31-DevKitC-1“ gibt es nicht.** `docs/KOSTEN.md` (Zeile 18) nennt es, die Produktseite von Espressif führt für S31 nur ESP32-S31-Function-CoreBoard-1, ESP32-S31-Korvo-1 und ESP-Mosaico. Ersatz: **Function-CoreBoard-1** (trägt das WROOM-3-N16R16V).
3. **Empfehlung Endgerät: ESP32-S31-WROOM-3-N16R16V** (22,0 × 30,0 × 3,5 mm) statt WROOM-1. Das ändert den Footprint der gerouteten Hauptplatine (siehe Abschnitt 6). WROOM-1-N16R16V bleibt „gewünscht, aber nicht planbar“.
4. **Jetzt kaufen: Function-CoreBoard-1** (A2DP-Test auf genau dem Modul, das wir später verbauen).
5. **Gate:** Besteht A2DP-Source auf dem CoreBoard nicht bis zu einem vom Besitzer gesetzten Datum, ist die Rückfalloption **ESP32-WROVER-E-N16R8** (Tangara-Modul, überall lieferbar).

## 2. ESP32-S31-Module (Tabelle)

Alle Varianten: -40 bis 85 °C Umgebung (einzige Temperaturstufe in den Datenblättern), 3,0–3,6 V, Octal-PSRAM, Quad-SPI-Flash. Es gibt keine 105-°C-Variante im Datenblatt [Q: WROOM-1 v0.5 und WROOM-3-Datenblatt, Serienvergleich].

| Bestellnummer | Flash / PSRAM | Antenne | Maße (mm) | Händlerstand 2026-10-05 |
|---|---|---|---|---|
| **ESP32-S31-WROOM-1-N16R16V** | 16 MB / 16 MB | PCB | 18,0 × 25,5 × 3,1 | Digi-Key (29821762): Lager 0, „3.250 erwartet 01-Mar-2027“, Lieferzeit 21 Wochen, 1 Stk. 8,43 USD, 100 Stk. 6,39 USD [Q]. Mouser (356-32S31WRM1N16R16V): „Non-Stocked“, Werkslieferzeit 21 Wochen, 1 Stk. 8,58 USD [Q, mouser.co.il] |
| ESP32-S31-WROOM-1-N16R8V | 16 MB / 8 MB | PCB | 18,0 × 25,5 × 3,1 | nur im Datenblatt, bei keinem Händler gefunden [Q Datenblatt, Händler: ?] |
| ESP32-S31-WROOM-1-N8R16V | 8 MB / 16 MB | PCB | 18,0 × 25,5 × 3,1 | nur im Datenblatt, Händler: [?] |
| ESP32-S31-WROOM-1-N32R16V, -N16R32V | 32/16 MB, 16/32 MB | PCB | Maße im Datenblatt leer | Datenblatt-Zeilen unvollständig, Händler: [?] |
| ESP32-S31-WROOM-1U-N16R16V | 16 MB / 16 MB | U.FL-Buchse | 18,0 × 20,5 × 3,2 | Händler: [?] (nicht gefunden) |
| **ESP32-S31-WROOM-3-N16R16V** | 16 MB / 16 MB | PCB | 22,0 × 30,0 × 3,5 | Digi-Key (29821761): Lager 0, „2.500 erwartet 01-Mar-2027“, 21 Wochen, 1 Stk. 8,22 USD [Q]. Electromaker: „Out of Stock“, Lieferzeit 70 Tage, 1 Stk. 7,30 USD [Q] (Suchauszug zeigte vorher „In stock 7,99 USD“ [S], widerspricht der Live-Seite). AliExpress Espressif-Store: Titel „PCB Version 1.1, ADC Not Calibrated“, Beispielpreis 6,2 USD laut Espressif-Seite [S] |
| ESP32-S31-WROOM-3-N16R8V, -N8R16V, -N32R16V, -N16R32V | siehe Name | PCB | 22,0 × 30,0 × 3,5 | Datenblatt [Q]. **Soyter (PL), N8R16V:** nicht lieferbar, Preis auf Anfrage [Q] |
| ESP32-S31-WROOM-3U-N16R16V | 16 MB / 16 MB | U.FL | 22,0 × 24,0 × 3,5 | Datenblatt [Q], Händler: [?] |
| JLCPCB-Bestückung WROOM-3 (C9900281993) | – | PCB | – | Lager 0, Typ „Extended“ [Q] |

Quellen: Digi-Key-Seiten 29821762/29821761 (abgerufen 2026-10-05), Mouser-Seite WROOM-1 (mouser.co.il) und Mouser-Microsite (WROOM-1 Veröffentlichung 2026-08-17, aktualisiert 2026-08-26), Espressif S31-Produktseite, Datenblatt WROOM-1 v0.5 (Pre-release), Datenblatt WROOM-3/-3U, electromaker.io, soyter.pl, jlcpcb.com.

Beobachtungen:

- Das Digi-Key-Datum „01-Mar-2027“ steht **identisch** bei WROOM-1, WROOM-3, dem Chip und dem CoreBoard (je 1 Stk. beim CoreBoard). Wir behandeln es als Platzhalter des Systems, nicht als Prognose.
- Digi-Key meldet 21 Wochen für alle S31-Teile, Mouser (Lettland) 13 Wochen für das CoreBoard.
- Nicht gefunden: TME (Suche „ESP32-S31“ ohne Treffer [Q]), Mouser-Suche nach Hersteller Espressif ohne Treffer [Q], LCSC (kein S31-Eintrag in den Suchergebnissen [S]). Farnell, RS, Reichelt, Eckstein, Berrybase, Tindie: nicht abgedeckt, [?].
- Bei AliExpress fand sich nur das **WROOM-3** (Espressif-Store), kein WROOM-1 [S].
- Reddit-Hinweis (Auszug [S], Seite nicht abrufbar): Das WROOM-3 habe **keine Castellated-Pads** (Lötbarkeit von Hand). Ungeprüft; vor Handlöten im Datenblatt-Footprint nachsehen.
- Das AliExpress-Modul trägt „PCB Version 1.1, ADC Not Calibrated“: frühe Modulrevision. Für das Testboard unkritisch, für das Endgerät klären, ob die Seriensorte dieselbe ist [?].

## 3. Dev-Boards (Startlösung für den A2DP-Test)

| Board | Modul | Händlerstand 2026-10-05 | Preis |
|---|---|---|---|
| **ESP32-S31-Function-CoreBoard-1** | WROOM-3 (N16R16V) | **Mouser (Lettland):** Lager 0, Nachbestellung 234 Stk. „11/2/2026“ und 585 Stk. „12/2/2026“, Werkslieferzeit 13 Wochen, Rückstand bestellbar [Q]. Datumsformat der Seite nicht bestätigt (vermutlich Monat/Tag, also 2. Nov. und 2. Dez. 2026) [?]. **Digi-Key** (1965-ESP32-S31-FUNCTION-COREBOARD-1-ND): Lager 0, 21 Wochen [Q]. **AliExpress (Espressif-Store):** Suchauszug „Temporarily out of stock“, Beschreibung „engineering sample“ [S] | Mouser 16,97 € [Q]; Digi-Key 20,33 USD [Q]; AliExpress 19,70 bis 22,89 USD (Presse, Juli 2026) [S] |
| ESP32-S31-Korvo-1 | WROOM-3 | Digi-Key: Lager 0 [Q] | Digi-Key 63,07 USD [Q], Espressif „59 USD“ |
| ESP-Mosaico | S31 (16/16 MB) | 2,16"-AMOLED 480 × 480, Vibrationsmotor; Händler: [?] | [?] |
| „ESP32-S31-DevKitC-1“ | – | **existiert nicht** als Produkt (nur Mouser-Seitenbeschreibung „DevKitC-1 Development Kit“ beim CoreBoard [S]) | – |

Software-Stand für A2DP (Entwicklerportal Espressif, „zuletzt aktualisiert 25. Sept. 2026“ [Q]):

- Bluetooth Classic im Bluedroid-Host: A2DP, AVRCP, HFP, HID, SPP, PBAP unterstützt (Haken).
- Weiterhin offen (Sanduhr): MSPI-Tuning für Flash/PSRAM über 80 MHz (IDF-14653, relevant für Display-Bildrate), DAC, Rücklesen von eSCO über I2S/PCM (nur HFP, für uns unerheblich).
- Die Seite sagt: Preview-Support im master-Branch bis zu einer Vollversion. Die IDF-v6.1-Dokumentation (stable) listet Bluetooth Classic samt A2DP (Source und Sink) für den S31 [S]. Beides stimmt zusammen mit `docs/S31-BUILDTEST.md`: bauen geht, auf Hardware ungetestet.
- Massenproduktion: Espressif-Meldung vom 2026-07-27 [Q], Verkauf zunächst über den Espressif-AliExpress-Store.

**Empfehlung Board:** Function-CoreBoard-1 bei Mouser (EU-Seite, Rückstand 13 Wochen laut Seite) bestellen und parallel bei AliExpress auf Wiederverfügbarkeit achten. Frühester genannter Wareneingang bei Mouser: 2. Nov. 2026, falls Monat/Tag [?].

## 4. Nacktes Chip-Gehäuse (nur Bewertung)

- **ESP32-S31NRV16** (16 MB PSRAM im Gehäuse), 80-VFQFN, 8 × 8 mm, 60 GPIO [Q: Digi-Key 29821763, Espressif-Seite].
- Digi-Key: Lager 0, „2.000 erwartet 01-Mar-2027“, 21 Wochen; 1 Stk. 6,25 USD, 100 Stk. 4,72 USD; Rolle ab 2.000 Stk. [Q]. Espressif-Seite: Beispielpreis 4,4 USD (AliExpress), Mindestmenge Direktbestellung 2.000 [S]. Auch der Chip ist also nicht kurzfristig lieferbar.
- Bewertung: Ein nacktes QFN spart kaum Platz gegen das WROOM-1 (8 × 8 mm plus Flash, Quarz, Antennenanpassung, Antenne, HF-Layout), schafft Zertifizierungsaufwand (kein vorzertifiziertes Modul) und ist **nicht** früher lieferbar. Für dieses Hobbyprojekt: **nicht sinnvoll**. Flash extern nötig (Modul trägt separaten Flash; im Chip nur PSRAM) [?: Chip-Datenblatt nicht abgerufen, Zeitüberschreitung].

## 5. Rückfalloptionen (Bluetooth-Audio ist Muss)

Entscheidendes Kriterium ist Bluetooth Classic mit A2DP-Source. Der ESP32-S3 hat es nicht (nur BLE) [Q: ESP-IDF-Programmierhandbuch, Bluetooth-Überblick ESP32-S3], ebenso der C6 (WLAN 6, 802.15.4, BLE) [Q: Elecrow-Vergleich 2026-08-14].

| Option | A2DP-Source | Pro | Contra |
|---|---|---|---|
| **A: ESP32-S31-WROOM-3-N16R16V** (Empfehlung Endgerät) | ja, im Chip (IDF-Status s. o.) | alles in einem Chip, USB-HS-OTG, PPA, 16 MB PSRAM; Pins prinzipiell wie WROOM-1-Layout geplant; Dev-Board verfügbar | 22 × 30 mm statt 18 × 25,5 mm (Platinenbreite 41 mm reicht, Länge +4,5 mm); Antenne am Platinenrand; noch ohne Lager (21 Wochen); Preview-IDF, Controller binär |
| **B: ESP32-WROVER-E-N16R8** (Tangara-Modul) | ja, bewährt (Tangara, `TEILE.md`) | **sofort lieferbar:** Mouser 37.250 Stk. (Nachschub 33.150 „11/2/2026“) ca. 6,45 USD [S], Digi-Key 1.399 Stk. 6,32 USD [S], TME 5.944 Stk. 5,20 USD [S], LCSC 1.513 Stk. [S]; stabile IDF; Tangara-Firmware direkt nutzbar | kein natives USB: für Gerät-an-PC (MSC) und USB-Audio-Host fehlt der SAMD21-Co-Prozessor (`TEILE.md` „Nicht übernommen“), mehr Fläche und Strom; Xtensa 240 MHz, 8 MB PSRAM, keine PPA; Maße ca. 18 × 31,4 mm laut Datenblatt [?: hier nicht geprüft]; nicht pinkompatibel zum S31-Layout, Platine neu zu routen |
| **C: ESP32-S3-WROOM-1 + BT-Audio-Modul** (z. B. Microchip BM83 / IS2083, Quelle: Datenblatt BM83 DS70005402C: mit AT-Firmware „A2DP source, BM83 ist Sender“ [S]) | über das Zusatzmodul | S3 ist breit verfügbar (Digi-Key S3-WROOM-1-N16R8 6,76 USD [Q]), natives USB; Zusatzmodul bringt ggf. bessere Codecs [?] | zusätzliche Fläche (BM83-Maße [?] nicht geprüft), UART-Steuerung plus I²S-Verdrahtung, Mehrkosten ungeprüft (Einzelmodule ca. 9–12 USD bei Sink-Boards [S], Source-Variante [?]), Firmwareaufwand, BM83-Lebenszyklus [?] |
| D: ESP32-P4 + C6 | **nein** (Classic fehlt im C6) | – | scheidet aus; nur der Vollständigkeit halber |
| E: ESP32 mit Bluetooth-Audio über Smartphone-Brücke o. Ä. | – | – | nicht bewertet |

Gewählte Rangfolge: **A, dann B**; C nur wenn B an USB scheitert und der SAMD21 vermieden werden soll.

## 6. Empfehlung und Kosten

**SKU Endgerät: ESP32-S31-WROOM-3-N16R16V** (Digi-Key 29821761 / Electromaker / AliExpress-Espressif).
Folgen für die Hauptplatine (nur Hinweis, Platinendateien werden hier nicht angefasst, Entscheidung beim PCB-Agenten und in `KONZEPT.md`, „Offene Punkte“):

- Footprint WROOM-1 (18 × 25,5, Rand-Pads 1,27 mm Raster) ist **nicht** der des WROOM-3 (22 × 30). Der DXF-Footprint liegt bei Espressif (S31-WROOM-3 PCB Footprint). Pinzuordnung WROOM-3 gegenüber WROOM-1 ist aus den vorliegenden Quellen nicht belegt [?].
- Platine ist 41 mm breit: 22 mm Modulbreite passt rechnerisch, kostet aber Platz bei den 1648/1824-mm²-Verhältnissen aus `KONZEPT.md`. Antenne darf nicht über die Kante hinausragen (`TEILE.md`).
- Dicke 3,5 mm statt 3,1 mm: im Dickenbudget prüfen.
- `TEILE.md` nennt „WROOM-1, sonst WROOM-3“. Der „sonst“-Fall ist hiermit eingetreten; Änderung der Maße/Schnittstelle nur dort begründen.

**Jetzt kaufen (Vorschlag):**

| Posten | Menge | Preis |
|---|---|---|
| Function-CoreBoard-1 (Mouser EU) | 1 | 16,97 € [Q] |
| zusätzliche WROOM-3-N16R16V-Module für Löttests/Beistellung | 2–3, sobald lieferbar | ca. 7–8 USD je Stück [Q] |
| Reserve: ESP32-WROVER-E-N16R8 nur falls Gate reißt | 0 jetzt | ca. 5–6 USD [S] |

Beistellung statt PCBA-Beschaffung: Bei PCBWay/JLCPCB sind die Module derzeit nicht lieferbar (JLCPCB: Lager 0 [Q]), also Module selbst kaufen und beistellen (wie B4 vorschlägt), oder Modul nach der Bestückung von Hand einlöten.

**Gate (Datum vom Besitzer festzulegen):** A2DP-Source mit SBC an einem Kopfhörer auf dem CoreBoard, dazu USB-UAC und PSRAM-Durchsatz für das Display (`docs/S31-BUILDTEST.md`). Scheitert das, geht das Projekt auf Option B (WROVER-E, SAMD21 wie Tangara).

## 7. Offen / ungeprüft

- WROOM-3-Pinbelegung gegenüber WROOM-1, Castellation, Pad-Raster [?].
- Lieferbarkeit WROOM-1 bei Espressif-Direktvertrieb, Farnell, RS, Reichelt, Tindie [?].
- Mouser-DE-Seiten lieferten 404; EUR-Preis nur vom CoreBoard (Lettland-Seite). Datumsformat der Nachbestellungen [?].
- AliExpress-Seiten lieferten keine Preise/Bestände im Abruf, nur Suchauszüge.
- Chip-Datenblatt (QFN) nicht abgerufen; BM83-Abmessungen und Lieferstatus nicht geprüft; WROVER-E-Maße nicht neu geprüft.
- Alle Händlerstände ändern sich täglich; vor der Bestellung neu prüfen.
