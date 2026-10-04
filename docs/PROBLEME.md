# Problemliste

Alle bekannten Probleme und Lücken, damit am Ende geprüft werden kann, ob sie behoben sind. Stand: 2026-10-04. Status: **offen**, **in Arbeit**, **erledigt**. Beim Beheben Status und Beleg (Datei, Commit, Messung) eintragen.

## A. Blocker vor einer Bestellung

| Nr | Problem | Status | Prüfung am Ende |
|---|---|---|---|
| A1 | Hauptplatine nicht geroutet (DRC 955 Meldungen, 34 von 408 Verbindungen offen); `NICHT_BESTELLEN_ungeroutet_gerber.zip` liegt im Repo | in Arbeit (Agent, neues Layout ca. 41 × 97 mm) | DRC 0 Fehler, 0 offene Verbindungen, Zip umbenannt/ersetzt |
| A2 | Kein Opus-Design-Review der Hauptplatine (Schaltplan gegen Datenblatt-Pins, Einschaltreihenfolge, ungetestete S31-Teile) | offen | Review-Bericht in `docs/`, Befunde abgearbeitet |
| A3 | Klickrad-Platine v2 (AT42QT2120, 0,8 mm, Molex-FFC) unfertig; v1-Dateien werden überschrieben | in Arbeit (Agent) | ERC/DRC 0 Fehler, Gerber und BOM vorhanden, README aktuell |
| A4 | Nichts davon wurde je auf Hardware getestet (Firmware, Platinen, Haptik) | offen | Messprotokoll nach Phase 1 |
| A5 | Unbelegte Teile: LCSC-Nummern, Jack-Höhe/STEP-Ursprung, WROOM-1-Pinbelegung, Auflösung des 2,06"-Displays (Listing widersprüchlich) | offen | Je Teil Datenblatt oder Händlerseite verlinkt |
| A6 | CS43131: Lieferzeit ca. 20 Wochen bei Digi-Key, Verfügbarkeit unklar | offen | Bestellbar bestätigt oder Plan B (CS43198 + OPA1622) gewählt |

## B. Technische Risiken

| Nr | Problem | Status | Prüfung am Ende |
|---|---|---|---|
| B1 | ESP32-S31: Bluetooth Classic nur „Preview“, Controller ist Binärbibliothek; Kopfhörer-Kompatibilität unbekannt | offen | A2DP-Test mit S31-DevKit und mindestens 2 Kopfhörern |
| B2 | Bluetooth-Fallback (externes Modul) nicht geplant | offen | Entscheidung in `KONZEPT.md` |
| B3 | Prototyp Waveshare-S3 kann kein Classic-A2DP, nur BLE | bekannt | Prototyp-Tests nur Display/Haptik/Rad, BT erst auf S31 |
| B4 | Ein USB-OTG-Port: USB-Audio-Host und USB-Speicher (MSC) schließen sich aus | offen | Moduswechsel implementiert und getestet |
| B5 | IDF-Version: S31 braucht v6.1 mit `--preview`, Hauptfirmware nur mit v5.4.2 auf S3 gebaut | offen | Version gepinnt, beide Targets bauen |
| B6 | I²S-Slave-Timing und 24 Bit am Codec, maximale BCLK des S31 ungeprüft | offen | Messung am Aufbau |
| B7 | CS43131: PLL gegen zweiten Quarz, Ausgangsimpedanz, Rauschen der Ladungspumpe ungemessen | offen | Messung nach Aufbau |
| B8 | Haptik: DRV2605L-Tuning, Latenz < 10 ms, Verträglichkeit LRA-Brummen mit Audio ungeprüft | offen | Logic-Analyzer-Messung, Hörtest |
| B9 | Klickrad: Segment-Zuordnung und Winkel-Offset (105°) nur berechnet, nicht am echten Rad geprüft | offen | Test am Aufbau, Wert in Kconfig angepasst |
| B10 | 4 Lagen beim Klickrad statt geplanter 2 (nicht routbar); höhere Kosten | bekannt | Kosten in `docs/KOSTEN.md` stimmen |

## C. Mechanik und CAD

| Nr | Problem | Status | Prüfung am Ende |
|---|---|---|---|
| C1 | CAD-Gehäuse noch für 8,5 mm (v2) bzw. 12,2 mm; Ziel ist jetzt ca. 44 × 100 × bis 11 mm | offen (wartet auf Platinenmaße) | Neues Gehäuse, STL kollisionsfrei, Maße = `TEILE.md` |
| C2 | Oberschale ohne Schraubdome, Halt über Rastnasen: ungeprüft | offen | Probedruck |
| C3 | Klickrad-Platine nur mit Distanzring und Klebeband befestigt, Verschraubung offen | offen | Entscheidung in `TEILE.md` |
| C4 | Ein/Aus-Taste auf z = 9,2 statt 10,3 (Abweichung) | bekannt | Neu bewerten bei neuer Dicke |
| C5 | Akku gegen LRA-Ausschnitt: Platz knapp (Ziel ≥ 600 mAh) | offen | Akkumaße im CAD, Kapazität bestätigt |
| C6 | 3D-Explosionsmodell zeigt noch das alte 12,2-mm-Design (JST, MPR121, Ø26-Ausschnitt) | offen | Modell zeigt aktuelles Design |
| C7 | Passung von Druckteilen (Toleranzen SV06 Ace / Voron) ungeprüft | offen | Probedruck |

## D. Dokumentation und Konsistenz

| Nr | Problem | Status | Prüfung am Ende |
|---|---|---|---|
| D1 | `TEILE.md` und `KONZEPT.md` führen Altes und Neues nebeneinander (8,5 / 12,2 / 44 × 100 × 11 mm; Hauptplatine „WROOM-3→-1“; „Hauptplatine nicht bestellbereit“) | offen | Nach Abschluss bereinigt |
| D2 | `docs/DUENNBAU.md` und `docs/duennbau/stackup.svg` sind überholt | offen | Als „Referenz“ markiert oder aktualisiert |
| D3 | Preise in `docs/EINKAUFSLISTE.md` und `docs/KOSTEN.md` aus dem Gedächtnis, nicht verifiziert; Muss+Soll hat nur 5 € Reserve; Waveshare-Board oft teurer | offen | Preise gegen Händler geprüft |
| D4 | Einkaufsliste noch auf JST-SH und MPR121 (v1), Klickrad ist jetzt v2 (Molex-FFC, QT2120) | offen | Liste auf v2 angepasst |
| D5 | Budget 100–150 € deckt nur Phase 1; gesamt 360–625 € | bekannt | Nutzer hat Gesamtbudget bestätigt |
| D6 | Emulator-Werte (Rasterschritt, Stärke, Mindestabstand, Anschlag) in `KONZEPT.md` noch „offen“ | offen | Werte eingetragen |
| D7 | Querprüfung fehlt: Gehäuse gegen Platinenmaße, Firmware gegen Pinbelegung und Segment-Zuordnung | offen | Prüfliste abgehakt |
| D8 | Repo hat keinen Standardbranch (`main`), kein PR | offen | Entscheidung des Nutzers |
| D9 | `.git` ca. 69 MB durch versehentlich eingecheckte Build-Ordner in der Historie | bekannt, unkritisch | Optional bereinigen |
| D10 | Lizenzen: Tangara-Ableitungen CERN-OHL-S-2.0 / GPL-3.0; Header und LICENSE-Dateien in allen neuen Ordnern prüfen | offen | Stichprobe je Ordner |

## E. Software

| Nr | Problem | Status | Prüfung am Ende |
|---|---|---|---|
| E1 | Firmware nur gebaut, nie geflasht; Klickrad-Komponenten mit Hosttest, Rest ungetestet | offen | Lauf auf Waveshare-Board |
| E2 | Firmware-Fork der Tangara-Firmware noch nicht gemacht (aktuell eigenes Gerüst) | offen | Portierungsplan `docs/FIRMWARE-PORTIERUNG.md` umgesetzt |
| E3 | Spotify (cspot) nur offener Punkt; DRM verhindert Offline | offen | Entscheidung nach Prototyp |
| E4 | Devialet-Steuerung per UPnP nur Idee, nicht als Ziel festgelegt | offen | Als Phase-4-Ziel entscheiden |
| E5 | Android-Emulator: Haptik-Qualität hängt vom Handy; Ergebnisse des Nutzers fehlen | offen | Werte aus Test in `KONZEPT.md` |

## F. Prozess

| Nr | Problem | Status | Prüfung am Ende |
|---|---|---|---|
| F1 | Freerouting unzuverlässig (ignoriert Zeitlimits, kein Ergebnis bei SIGTERM) | bekannt | Alternativer Router oder manuelle Nacharbeit dokumentiert |
| F2 | Router-/Agentenläufe können Dateien überschreiben (Klickrad v1 → v2) | bekannt | v1 per Git-Historie auffindbar |
