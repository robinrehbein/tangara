# Platzierung der Rückseitenbauteile (x, y, Drehung); Koordinaten Frontansicht, Mitte = (0, 0)
# U1 um 90 Grad gedreht: Tasten-Pins (KG, KB, K2) zeigen nach oben (Norden), K1/K0 nach Osten, Bus (SDA, RESET, SCL, CHANGE) nach unten zu J1.
POS = {
 'U1': (0.0, -1.5, 90), 'U2': (-7.5, -5.0, 0), 'J1': (0, -11.4, 0),
 'R5': (-2.4, 1.3, 0), 'R4': (0.45, 1.75, 270), 'R3': (2.7, 1.3, 180),
 'R2': (3.9, -0.2, 180), 'R1': (3.9, -1.4, 180),
 'C1': (3.1, -3.0, 90), 'C2': (4.4, -3.0, 90), 'R6': (0.45, -4.6, 270),
 'C3': (-6.5, -2.0, 0), 'C4': (-4.3, -2.5, 90), 'C5': (-9.9, -8.8, 0), 'R7': (-6.6, -7.8, 0),
 'R8': (-4.7, -8.0, 180), 'R9': (-3.1, -7.0, 0),
 'TP1': (-12.3, -3.0, 90), 'TP2': (-12.3, -0.4, 90),
}

# Vorverlegte Leiterbahnen (Netz, Lage, Punkte, Breite): sichern die Topologie. Alle drei laufen unter dem Stecker durch
# (Kupfer unter dem Steckerkörper ist erlaubt, Bauteile nicht), so kreuzen sich SDA, SCL und 3V3 nicht mit CHANGE:
#  SCL (y = -10,6) und SDA (y = -11,4) gehen vom Steckerpad nach links zu U2, 3V3 (y = -12,0) vom Steckerpad 1 nach links in den U2-Bereich.
PRE_TRACKS = [
 ('SCL', 'B', [(-0.5, -9.6), (-0.5, -10.6), (-3.6, -10.6), (-3.6, -4.5), (-4.9, -4.5)], 0.15),
 ('SDA', 'B', [(0.5, -9.6), (0.5, -11.4), (-4.2, -11.4), (-4.2, -5.0), (-4.9, -5.0)], 0.15),
 ('3V3', 'B', [(2.5, -9.6), (2.5, -12.0), (-5.4, -12.0)], 0.2),
]
PRE_VIAS = []
