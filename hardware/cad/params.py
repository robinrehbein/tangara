"""Zentrale Parameter fuer alle 3D-Druck-Teile (Maße in mm).

Koordinaten: X nach rechts, Y nach oben (Display oben), Z nach vorn (Betrachter).
Gehaeuse-Mitte bei X=0, Y=0; Rueckseite aussen bei Z=0.

Werte mit  # PLATZHALTER  sind nicht verifiziert und nach dem Nachmessen der
echten Teile hier zu aendern. Alles andere stammt aus TEILE.md / Render / Wiki.
"""

# ---------------------------------------------------------------- Allgemein
NOZZLE = 0.4
MIN_WALL = 1.2            # 3 Perimeter
FIT = 0.3                 # Spiel an Passungen (0,2-0,3)
FIT_TIGHT = 0.2
INSERT_HOLE_D = 3.2       # Bohrung fuer M2-Schmelzeinsatz (Ø)
INSERT_HOLE_DEPTH = 4.0   # Tiefe der Bohrung
M2_CLEAR_D = 2.4          # Durchgangsloch M2
M2_CSK_D = 4.4            # Senkung (Ø an der Oberflaeche), 90 Grad -> M2-Senkkopf
SCREW_HEAD_D = 3.5        # Flachkopf-/Linsenkopf M2 (ISO 7380: Ø3,5 x 1,3)
SCREW_HEAD_H = 1.3
BOSS_D = INSERT_HOLE_D + 2 * MIN_WALL   # 5,6 Mindest-Dom-Ø
BOSS_D = 6.4              # Dom-Ø fuer Gehaeuseschrauben (breiter = steifer)

# ------------------------------------------------ Klickrad-Modul (TEILE.md)
WHEEL_PCB_D = 32.0
WHEEL_PCB_T = 1.0
WHEEL_HOLE_D = 2.2
WHEEL_HOLE_R = 14.6
WHEEL_HOLE_ANGLES = (90, 210, 330)
WHEEL_COVER_D = 30.0
WHEEL_COVER_HOLE_D = 11.6
WHEEL_BTN_D = 11.0
WHEEL_BTN_T = 1.15
WHEEL_OPEN_D = 30.6       # Oeffnung in der Frontplatte
SWITCH_SIZE = 4.4         # Tasterkasten 4x4 + Spiel (Pocket in der Mitteltaste)
SWITCH_H = 1.5            # max. Tasterhoehe (TEILE.md: <= 1,5)
LRA_L, LRA_W, LRA_H = 15.0, 9.5, 3.5   # Obergrenze lt. Recherche (bis 9,5x15x3,5)

# ===================================================== PROTOTYP-GEHAEUSE v1
# Entscheidung: Das Waveshare-Board wird MIT seinem schwarzen Originalgehaeuse
# eingesetzt (Maßzeichnung im Wiki: 37,6 x 45,2 x 15,0, Ecken R1,8). Die
# nackte Platine ist nicht verifiziert; sie passt ebenfalls (nur mehr Luft).
BOARD_W = 37.6            # Wiki-Zeichnung (mit Gehaeuse)
BOARD_L = 45.2            # Wiki-Zeichnung (mit Gehaeuse)
BOARD_T = 15.0            # Wiki-Zeichnung (mit Gehaeuse)
BOARD_R = 1.8
DISP_VIS_W = 28.7         # sichtbare Displayflaeche (Wiki)
DISP_VIS_H = 34.94
DISP_WIN_W = DISP_VIS_W + 1.0   # Fenster in der Frontschale
DISP_WIN_H = DISP_VIS_H + 1.0
DISP_WIN_R = 2.0
DISP_CY_FROM_BOARD_TOP = 22.6  # PLATZHALTER: Display-Mitte ab Board-Oberkante (hier: mittig)
DISP_CX_OFFSET = 0.0           # PLATZHALTER
USB_EDGE_TOP = True       # USB-C an der oberen Schmalseite (Gegenseite = Loetpads, nahe Klickrad)
USB_X = 0.0               # PLATZHALTER: X-Versatz ab Boardmitte
USB_Z_FROM_FRONT = 7.5    # PLATZHALTER: Mitte USB-C ab Board-Vorderseite
USB_OPEN_W = 12.0         # Oeffnung fuer Stecker mit Huelle
USB_OPEN_H = 7.0
SIDEBTN_Y_FROM_TOP = 6.0  # PLATZHALTER: Abstand der BOOT/PWR-Taster ab Board-Oberkante
SIDEBTN_Z_FROM_FRONT = 7.5  # PLATZHALTER
SIDEBTN_OPEN = 4.0        # Zugangsloch (rund-eckig) links = BOOT, rechts = PWR
LIPO_W, LIPO_L, LIPO_T = 24.0, 28.0, 3.85   # empfohlener Akku (Wiki); Akku liegt hinter dem Klickrad-Halter
LIPO_GAP = 0.3

# Gehaeusehuelle
SKIN = 1.2                # Aussenhaut an der Trennfuge
LIP_T = 1.2               # Nut-/Feder-Lippe der Rueckschale
SEAM_GAP = 0.2
WALL = SKIN + SEAM_GAP + LIP_T   # 2,6 Gesamtwand
LIP_H = 2.5
FRONT_T = 1.6             # Frontplatte
REAR_T = 2.0              # Boden Rueckschale
R_OUT = 7.0
EDGE_FILLET = 1.0
TOP_ROOM = 7.4            # Platz ueber dem Board (Schraubdome + USB)
BOARD_REAR_GAP = 0.5      # Luft hinter dem Board (Schaumstoff / Andruckrippen)

# Klickrad im Prototyp
WHEEL_GAP = 1.5           # Platine-Vorderseite -> Frontplatte (Schraubenkoepfe)
COVER_T = 2.4             # Prototyp: dicker als Endgeraet (1,95), damit Kopf-Taschen moeglich
HEAD_POCKET_D = SCREW_HEAD_D + 0.5
HEAD_POCKET_H = SCREW_HEAD_H + 0.2
HOLDER_T = 2.0
HOLDER_R = WHEEL_PCB_D / 2 + 0.3
DOME_D = 5.6
DOME_H = LRA_H + 0.5      # Abstand Platinenrueckseite -> Halterbasis
EAR_W = 6.2
CABLE_SLOT = (8.0, 5.0)   # Kabeldurchfuehrung der Litzen (Rechteck) in der Halterbasis
CABLE_SLOT_POS = (-7.8, 4.5)  # relativ zur Radmitte

# abgeleitete Prototyp-Maße
P_IW = BOARD_W + 2 * FIT
P_WHEEL_Y = HOLDER_R + 0.5    # Radmitte ab Innenkante unten (ca. 16.8)
P_WHEEL_ZONE = P_WHEEL_Y + max(HOLDER_R, WHEEL_HOLE_R + DOME_D / 2) + FIT
P_IL = P_WHEEL_ZONE + BOARD_L + TOP_ROOM
P_OW = P_IW + 2 * WALL
P_OL = P_IL + 2 * WALL
P_PI = REAR_T + BOARD_REAR_GAP + BOARD_T      # Z der Frontplatten-Innenseite
P_T = P_PI + FRONT_T                          # Gesamthoehe
P_ZS = P_PI - WHEEL_GAP - WHEEL_PCB_T - DOME_H  # Trennfuge (Z)

# ====================================================== ENDGERAET (Render)
E_W, E_L, E_R = 42.0, 95.0, 7.0
E_WALL = 1.4
E_TOP = 12.2
E_SEAM = 6.0
E_PLATE = 1.2
E_DISP_WIN = (30.2, 36.7, 2.3)
E_DISP_Y = 21.0
E_WHEEL_Y = -27.0
E_COVER_T = 1.95
E_COVER_Z0 = 10.25
E_WHEEL_PCB_Z0 = 9.2
E_SWITCH_H = 1.2          # PLATZHALTER (Taster-Hoehe)
E_FRAME_CLEAR = 0.2
E_FRAME_Z0, E_FRAME_Z1 = 1.2, 7.4
E_FRAME_WALL = 1.7
E_SCREWS = [(-15, 40), (15, 40), (-15, -40), (15, -40)]
E_USB = (11.0, 5.0)       # Oeffnung (B x H), Mitte x=0, z=5.8 (Render)
E_USB_Z = 5.8
E_JACK_D = 7.0            # Oeffnung Klinke, x=-12
E_JACK_X = -12.0
E_SD = (12.6, 2.4)        # microSD rechts, y=-5, z=6.9
E_SD_Y, E_SD_Z = -5.0, 6.9
E_PWR_X, E_PWR_Z = 8.0, 9.2   # Render: z 10,3 -> auf 9,2 gesenkt (Taster der Hauptplatine, Wandstaerke oben)
E_PWR = (8.0, 3.0)
E_LRA_Y = -29.0           # Render: LRA 16 x 6 x 3,6 bei (0,-29)
E_BATT = (30.0, 34.0, 4.6)  # PLATZHALTER
E_BATT_Y = 19.5
E_SPACER = (32.0, 27.0, 0.8)  # Distanzring unter der Klickrad-Platine (Aussen-Ø, Innen-Ø, Hoehe)

PLATZHALTER = [
    "BOARD_W/BOARD_L/BOARD_T: Wiki-Maß MIT Originalgehaeuse, nackte Platine ungeprueft",
    "DISP_CY_FROM_BOARD_TOP, DISP_CX_OFFSET: Displaylage im Board",
    "USB_X, USB_Z_FROM_FRONT, USB_OPEN_*: USB-C-Lage",
    "SIDEBTN_*: Lage BOOT/PWR-Seitentaster",
    "LRA_L/W/H: Obergrenze der LRA-Kandidaten",
    "CABLE_SLOT*: Lage der Litzen/Loetpads",
    "SWITCH_H, WHEEL_PCB/Komponentenhoehen: Mitteltaster",
    "E_BATT*, E_SWITCH_H, E_USB*, E_JACK_D, E_SD*: Endgeraet-Annahmen",
]
