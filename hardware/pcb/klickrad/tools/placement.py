# Platzierung der Rückseitenbauteile (x, y, Drehung); Koordinaten Frontansicht, Mitte = (0, 0)
# U1 um 90 Grad gedreht: Tasten-Pins (KG, KB, K2) zeigen nach oben (Norden), K1/K0 nach Osten, Bus (SDA, RESET, SCL, CHANGE) nach unten zu J1.
POS = {
 'U1': (0.0, -1.5, 90), 'U2': (8.5, -3.6, 180), 'J1': (0, -10.8, 0),
 'R5': (-2.4, 1.3, 0), 'R4': (0.45, 1.75, 270), 'R3': (2.7, 1.3, 180),
 'R2': (3.9, -0.2, 180), 'R1': (3.9, -1.4, 180),
 'C1': (2.6, -5.0, 90), 'C2': (3.9, -3.0, 90), 'R6': (0.45, -4.6, 270),
 'C3': (10.2, -7.6, 180), 'C4': (4.5, -6.2, 90), 'C5': (7.2, -8.6, 0), 'R7': (6.4, -0.8, 90),
 'R8': (-2.6, -6.3, 0), 'R9': (-2.6, -5.2, 0),
 'TP1': (13.1, -2.4, 90), 'TP2': (13.1, -4.8, 90),
}

# J1-Pin 2 (GND) wird vorab unter dem Steckerkörper nach Osten herausgeführt (sonst von den Nachbarsignalen eingeschlossen)
PRE_TRACKS = [
 ('GND', 'B', [(0.75, -8.95), (0.75, -10.3), (5.8, -10.3), (5.8, -8.6)], 0.2),     # J1-Pin 2 (GND) unter dem Steckerkörper nach Osten
 ('GND', 'B', [(1.45, -1.5), (2.95, -1.5)], 0.15),                                 # U1 Pin 8 -> Via
 ('GND', 'B', [(1.45, -2.4), (2.95, -2.4)], 0.15),                                 # U1 Pin 10 (MODE) -> Via
 ('GND', 'F', [(2.95, -1.5), (2.95, -2.4)], 0.2),                                  # Brücke auf F.Cu im Ring zwischen Taste und Rad (Pin 9 = 3V3 liegt dazwischen)
]
PRE_VIAS = [('GND', 2.95, -1.5), ('GND', 2.95, -2.4)]
