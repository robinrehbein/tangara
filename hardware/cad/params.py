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

# ============================================ ENDGERAET v2 (Duennbau, Variante A)
# VORLAEUFIG, aus docs/DUENNBAU.md (Stand 2026-10-04). Genaue Maße und Lagen
# sind NICHT final; alles mit  # VORLAEUFIG  vor dem Layout/Bestellen pruefen.
# Z von hinten (0) nach vorn. Quelle der Werte: DUENNBAU.md Abschnitt 3, 5, 7, 8.
E2_W, E2_L, E2_R = 40.0, 90.0, 4.5          # Aussenmaß; R4,5 statt 6: Klinken-Oeffnung bei x=-12 braucht Wandmaterial vor der Ecke
E2_T = 8.5                                  # Gesamtdicke Variante A mit Reserve
E2_WALL = 1.2                               # Seitenwand (3 Perimeter)
E2_RIM = 0.8                                # sichtbarer Randsteg an Front/Rueck-Falz (2 Perimeter)
E2_FIT = 0.1                                # Spiel Platte <-> Falz je Seite
E2_FIT_PCB = 0.3                            # Spiel Platine/Akku <-> Wand je Seite

# --- Schichten (Z-Lage) -------------------------------------------------------
E2_BACK_T = 1.0                             # Rueckwand gedruckt (Alternative FR4 0,8: E2_BACK_FR4_T)
E2_BACK_FR4_T = 0.8
E2_AIR_BACK = 0.2                           # Luft Rueckwand -> Rueckzone
E2_REAR_ZONE = 3.3                          # Rueckzone: Akku 3,0 + 0,3; ESP 3,1; USB 3,18
E2_PCB_T = 0.8                              # Hauptplatine
E2_FRONT_T = 0.8                            # Frontplatte Acryl/Glas
E2_GLUE = 0.1                               # Klebefilm (VHB/OCA) je Schicht
E2_DISP_T = 2.05                            # Display-Modul mit Touch (2,06" LX)
E2_PCB_Z0 = E2_BACK_T + E2_AIR_BACK + E2_REAR_ZONE      # 4,5 Platine Rueckseite
E2_PCB_Z1 = E2_PCB_Z0 + E2_PCB_T                        # 5,3 Platine Vorderseite
E2_FRONT_Z0 = E2_T - E2_FRONT_T                         # 7,7 Frontplatte Unterseite
E2_DISP_Z1 = E2_FRONT_Z0 - E2_GLUE                      # 7,6 Display Oberseite
E2_DISP_Z0 = E2_DISP_Z1 - E2_DISP_T                     # 5,55 Display Unterseite
E2_LIP_H = 0.8                              # Auflagesteg der Frontplatte (Gesamthoehe: 0,4 Schraege + 0,4 senkrecht), druckbar ohne Stuetzen
E2_LIP_INSET = 1.6                          # Auflagesteg: Abstand Innenkante von Aussen (Randsteg 0,8 + 0,8 Auflage)
E2_LIP_CHAMFER = 0.4                        # 45-Grad-Schraege unter dem Steg (Wand 1,2 -> 1,6), darueber 0,4 senkrechte Kante

# --- Hauptplatine (VORLAEUFIG, DUENNBAU 8.1) -----------------------------------
E2_PCB = (37.0, 84.0, 4.0)                  # B x L, Eckenradius  # VORLAEUFIG
E2_JACK = (9.1, 14.0, 5.0)                  # SJ-43504: B x Tiefe x Hoehe  (STEP, DUENNBAU 3.1)
E2_JACK_X = -12.0                           # VORLAEUFIG (Floorplan)
E2_JACK_Z0, E2_JACK_Z1 = E2_PCB_Z0 - 3.1, E2_PCB_Z0 + 1.9   # Pads auf B.Cu: 3,1 hinten / 1,9 vorn  # UNGEPRUEFT
E2_JACK_NOTCH_PAD = 0.45                    # Platinenausschnitt = Footprint + Spiel
E2_JACK_OPEN_W = 9.6                        # Wandoeffnung Breite (DUENNBAU 8.3: 9,6 x 5,2); Hoehe: von Rueckwand-Oberkante bis Klinke oben + 0,1
E2_USB = (11.54, 7.2, 3.18)                 # GCT USB4510 B x T x H (STEP)
E2_USB_X = 10.0                             # VORLAEUFIG
E2_USB_OPEN_W = 9.4                         # Wandoeffnung Breite; Hoehe: von Rueckwand-Oberkante bis Platine + 0,15 (DUENNBAU: 3,4)
E2_ESP = (25.5, 18.0, 3.1)                  # WROOM-1, um 90 Grad gedreht (X lang)  # VORLAEUFIG
E2_ESP_X = 0.0
E2_PCB_SLOT = (14.0, 1.2, 0.0, -3.2)        # FPC-Schlitz B, H, x, y  # PLATZHALTER

# --- Akku-Fach 303450 ----------------------------------------------------------
E2_BATT = (34.0, 50.0, 3.3)                 # Pouch inkl. Quellreserve
E2_BATT_Y = -3.5                            # so, dass 0,5 Luft zur Klinke bleiben  # VORLAEUFIG
E2_BATT_RIB_T = 0.8                         # Haltestege auf der Rueckwand
E2_BATT_RIB_H = 2.0

# --- Display (2,06" CO5300) -----------------------------------------------------
E2_DISP_MOD = (34.8, 43.1)                  # Modul (LCM)
E2_DISP_ACTIVE = (33.1, 40.5)               # aktive Flaeche
E2_DISP_Y = 20.43                           # Modulmitte; Oberkante 42,0  # VORLAEUFIG
E2_DISP_ACTIVE_DY = 0.0                     # Versatz aktive Flaeche zur Modulmitte  # PLATZHALTER (FPC-Seite)
E2_WIN_MARGIN = 0.4                         # Fenster = aktive Flaeche + 2 x 0,4
E2_WIN_R = 1.5                              # Fensterradius  # PLATZHALTER

# --- Klickrad (Platine + 0,6-mm-FR4-Abdeckung) -----------------------------------
E2_WHEEL_Y = -22.0                          # VORLAEUFIG
E2_WHEEL_PCB_T = 0.8
E2_WHEEL_COVER_T = 0.6                      # FR4 wie Tangara
E2_WHEEL_COVER_D = 30.0
E2_WHEEL_OPEN_D = 30.6                      # Ausschnitt in der Frontplatte
E2_WHEEL_PCB_Z1 = E2_FRONT_Z0 - E2_GLUE     # 7,6 Platine Oberseite (liegt per Klebefilm unter der Front)
E2_WHEEL_PCB_Z0 = E2_WHEEL_PCB_Z1 - E2_WHEEL_PCB_T     # 6,8
E2_LRA = (10.0, 10.0, 1.0)                  # VLV101040J, auf die Platinenrueckseite geklebt
E2_LRA_DY = 6.0                             # Versatz zur Radmitte  # VORLAEUFIG
E2_WHEEL_REAR_PART_H = 0.8                  # Rueckseitenbauteile (DRV2605L, AT42QT2120)

# --- Schrauben (M1,6 Senkkopf, in Rahmendome) -----------------------------------
E2_SCREW_CLEAR_D = 1.8                      # Durchgang in der Rueckwand
E2_SCREW_CSK_D = 3.2                        # Senkung Ø an der Aussenseite (Kopf ca. 3,0)
E2_SCREW_PILOT_D = 1.4                      # Kernloch im Dom (selbstschneidend in ASA)  # UNGEPRUEFT
E2_BOSS_D = 3.6
E2_SCREWS = [(-16.0, 42.0), (16.0, 42.0), (-1.5, -42.5), (-17.8, 24.5), (17.8, -33.0)]  # VORLAEUFIG

# --- Auflager der Platine (Pads an den Seitenwaenden) ---------------------------
E2_PAD = (1.0, 8.0, 0.8)                    # Ueberstand nach innen, Laenge, Hoehe (unter der Platine)
E2_PAD_POS = [(-1, 8.0), (1, 8.0), (-1, -8.0), (1, -8.0)]   # (Seite, y)

# --- Ein/Aus-Taste (rechte Seitenwand) -------------------------------------------
E2_PWR_Y, E2_PWR_Z = 22.5, 3.0              # VORLAEUFIG (Taster auf Platinenrueckseite)
E2_PWR_OPEN = (5.0, 2.0)                    # Wandoeffnung (Y x Z)
E2_PWR_SWITCH = (2.1, 2.0, 1.5)             # Seitentaster-Attrappe  X x Y x Z  # PLATZHALTER

PLATZHALTER_V2 = [
    "E2_PCB (37 x 84, R4), E2_JACK_X, E2_USB_X, E2_ESP*: Floorplan vorlaeufig (DUENNBAU 8.1)",
    "E2_JACK_Z0/Z1: Einbaulage der Klinke (STEP-Ursprung = Pad-Ebene) UNGEPRUEFT; Variante B 9,0 mm",
    "E2_PCB_SLOT: Display-FPC-Schlitz, Lage von der Maßzeichnung des gekauften Moduls abhaengig",
    "E2_DISP_Y, E2_DISP_ACTIVE_DY: Lage der aktiven Flaeche im Modul (FPC-Seite) PLATZHALTER",
    "E2_BATT (3,3 inkl. Quellung) und E2_BATT_Y: Zellendatenblatt fehlt",
    "E2_WHEEL_Y, E2_LRA*: Lage Klickrad und LRA",
    "E2_PWR_*: Ein/Aus-Taster (Typ offen, Attrappe 2,1 x 2,0 x 1,5)",
    "E2_SCREWS, E2_SCREW_PILOT_D: Schraubenlage und Kernloch fuer M1,6 UNGEPRUEFT",
]
