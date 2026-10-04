# Platzierung der Rückseitenbauteile (x, y, Drehung); Koordinaten Frontansicht, Mitte = (0, 0)
# U1 um 90 Grad gedreht: Tasten-Pins (KG, KB, K2) zeigen nach oben (Norden), K1/K0 nach Osten, Bus (SDA, RESET, SCL, CHANGE) nach unten zu J1.
POS = {
 'U1': (0.0, -1.5, 90), 'U2': (8.2, -4.0, 180), 'J1': (0, -11.4, 0),
 'R5': (-2.4, 1.3, 0), 'R4': (0.45, 1.75, 270), 'R3': (2.7, 1.3, 180),
 'R2': (3.9, -0.2, 180), 'R1': (3.9, -1.4, 180),
 'C1': (3.1, -3.0, 90), 'C2': (4.4, -3.0, 90), 'R6': (0.45, -4.6, 270),
 'C3': (10.8, -6.9, 90), 'C4': (4.9, -6.3, 90), 'C5': (7.6, -8.2, 0), 'R7': (6.0, -1.5, 90),
 'R8': (3.6, -6.6, 90), 'R9': (2.4, -6.6, 90),
 'TP1': (-12.3, -3.0, 90), 'TP2': (-12.3, -0.4, 90),
}

PRE_TRACKS = []
PRE_VIAS = []
