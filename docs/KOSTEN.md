# Kostenübersicht

Grobe Schätzung, Stand 2026-10-04. Preise sind Richtwerte und nicht gegen die Shops geprüft. Versand und Zoll sind nur pauschal enthalten.

## 1. Phase 1: Prototyp (Waveshare-Board, Klickrad, Haptik)

Details: `docs/EINKAUFSLISTE.md`.

| Stufe | Summe |
|---|---|
| Muss | ca. 98 € |
| Muss + Soll | ca. 145 € |

## 2. Endgerät: Platinen und Teile

| Posten | Schätzung | Hinweis |
|---|---|---|
| ESP32-S31-DevKitC-1 (Bluetooth-Test vor der Platinenbestellung) | 20–40 € | empfohlen |
| Hauptplatine, 5 Stück, 4 Lagen, 0,8 mm, ENIG (PCBWay) | 40–60 € | ohne Bestückung |
| Bestückung (PCBA) Hauptplatine: Einrichtung | 30–50 € | einmalig |
| Bauteile Hauptplatine je Gerät | ca. 35–40 € | davon CS43131 allein ca. 17 €, S31-Modul ca. 5–7 € |
| → Hauptplatine mit **2** bestückten Exemplaren | ca. 150–220 € | **Empfehlung** |
| → Hauptplatine mit **5** bestückten Exemplaren | ca. 280–350 € | |
| Klickrad-Platine v2, 5 Stück, plus FR4-Abdeckung | 25–45 € | selbst löten |
| oder Klickrad-Platine mit PCBA | 60–80 € | |
| 2,06"-AMOLED-Panel | 15–25 € | Auflösung vor dem Kauf prüfen |
| Akku 303450 | 5–8 € | |
| FFC-Kabel und Breakout (Molex 503480-0600) | 5–10 € | |
| LRA-Kandidaten für das Endgerät (flach und X-Achse ≤ 3 mm) | 10–15 € | |
| Frontplatte Acryl/Glas, Laserzuschnitt | 10–20 € | |
| Versand und Zoll (pauschal) | 20–40 € | |
| **Summe Endgerät (2 bestückte Hauptplatinen)** | **ca. 260–480 €** | |

## 3. Gesamt

| | Summe |
|---|---|
| Phase 1 | ca. 100–145 € |
| Endgerät | ca. 260–480 € |
| **Gesamt** | **ca. 360–625 €** |

Das ursprüngliche Budget (100–150 €) deckt nur Phase 1. Das Endgerät mit PCBA bei PCBWay liegt deutlich darüber.

**Hebel zum Sparen:** nur 2 Hauptplatinen bestücken lassen; Klickrad-Platine selbst löten; CS43131 durch die Tangara-Kette ersetzen (spart wenig, kostet Klangqualität); Endgerät erst nach erfolgreichem Phase-1-Test bestellen.

**Lieferzeit:** CS43131 bei Digi-Key ca. 20 Wochen, LCSC nur wenige Stück auf Lager → vor der Bestellung Verfügbarkeit prüfen.
