# 3D-Explosionsmodell (Endgerät v3)

`explosionsmodell.html` ist eine einzelne, eigenständige HTML-Datei (three.js r128 von cdnjs, Schrift von Google Fonts, sonst alles inline). Im Browser öffnen, Schieberegler „Zerlegen“, Ziehen = Drehen, Scrollen/Pinch = Zoomen, Teil anklicken für Maße und Hinweise, Gehäusefarbe wählbar.

## Stand

**Endgerät v3, 44 × 100 × 10 mm**, Maße aus `hardware/cad/params.py` (`V3_*`), Stand 2026-10-04. Das alte 12,2-mm-Konzept (Ober-/Rückschale, Innenrahmen, M2) ist ersetzt.

| Teil | Quelle im Modell |
|---|---|
| Rahmen, Rückwand, Frontplatte, Klickrad-Abdeckung | **echte CAD-STL** (`cad/stl/endgeraet_v3/`), als Base64 eingebettet (0,01 mm gerundet) |
| Hauptplatine 41 × 97 × 1,0 mit Ausschnitten (Klinke, USB-C, LRA) und 3 Löchern | aus Parametern gebaut |
| Display 2,06", Klickrad-Platine Ø 32, LRA 12 × 6 × 3, WROOM-1, microSD, SW1, USB-C, Klinke, Akku, 3 Schrauben | **Platzhalter-Blöcke** aus den Parametern |
| Antennen-Keepout | nur Markierung, standardmäßig ausgeblendet |

## Platzhalter und ungeprüft

- Alle Maße stammen aus dem Rechner-CAD, **nichts ist an echter Hardware geprüft**. Offene Annahmen stehen in `params.py` (`V3_UNGEPRUEFT`) und im CAD-README.
- Display-Modul 34,8 × 43,1 (Maße aus v2, nicht an der Zeichnung geprüft), Lage y = 19,45 ist Annahme.
- microSD-Hüllkörper, Klinkenversatz, USB-C-Aufteilung vorn/hinten, SW1-Maße: Annahmen.
- Bauteile auf der Rückseite der Klickrad-Platine (Treiber, Controller, Mitteltaste): Lage unbekannt, nur Beispielblöcke. Akku: Typ offen, nur Fachgröße 32 × 38,5 × 3,65.
- Bauteile auf der Hauptplatinen-Vorderseite, FFC/FPC und Akku-Litzen sind nicht modelliert; von der Hauptplatine nur C29.
- Darstellung des Displayinhalts und der Rad-Beschriftung ist nur Optik. Frontplatte wird durchscheinend gezeigt, die schwarze Druckmaske ist ein dünnes Blatt.
- Normalen der STL sind flach berechnet, Rundungen wirken daher leicht facettiert.
- Die Datei enthält eine eigene kleine Orbit-Steuerung, weil cdnjs `OrbitControls` für r128 nicht anbietet. RoomEnvironment entfällt, Beleuchtung über Hemisphere- und Richtungslichter.

## STL neu einbetten

Nach einem neuen CAD-Lauf (`cad/build_v3.py`):

```
hardware/cad/.venv/bin/python hardware/render/stl_einbetten.py
```

ersetzt den Block zwischen `// STL-DATEN-BEGIN` und `// STL-DATEN-ENDE` in `explosionsmodell.html`. Ändern sich Maße in `params.py`, müssen die Konstanten am Anfang des Skripts in der HTML (Block „Grundmaße“) und die Teile-Texte von Hand nachgezogen werden.

## Vorschau

`vorschau/*.png`: Screenshots (Playwright/Chromium, Software-GL) zusammengebaut und zerlegt aus mehreren Ansichten, Teilauswahl, Farbvariante.
