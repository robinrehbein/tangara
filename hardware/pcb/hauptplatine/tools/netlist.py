"""Bauteil- und Netzliste der Hauptplatine (einzige Quelle fuer Schaltplan, Platine, Stueckliste).

Koordinaten (Platzierung): Platinenmitte = (0,0), x nach rechts, y nach oben, Blick von der DISPLAY-Seite (Oberseite).
Bauteile auf der Unterseite sind in dieser Ansicht "durch die Platine" gezeichnet (also gespiegelt).
"at": (x, y, Drehung in Grad in dieser Ansicht, Seite 'T' oder 'B')
"near": (Ankerbauteil, Ankerpin, dx, dy, Drehung) -> relativ zum Pad des Ankers, gleiche Seite wie der Anker
"""
import os

# ----------------------------------------------------------------------------- Pin-Zuordnung XIAO
# Pad -> (XIAO-Name, ESP32-S3-GPIO, Netz)
XIAO_PINS = {
    '1':  ('D0', 1, 'PWR_BTN'),
    '2':  ('D1', 2, 'LCD_CS'),
    '3':  ('D2', 3, 'LCD_D0'),
    '4':  ('D3', 4, 'LCD_D2'),
    '5':  ('D4', 5, 'SDA'),
    '6':  ('D5', 6, 'WHEEL_INT'),
    '7':  ('D6', 43, 'LCD_TE_MCU'),
    '8':  ('D7', 44, 'JACK_DET'),
    '9':  ('D8', 7, 'I2S_WS'),
    '10': ('D9', 8, 'SD_D0'),
    '11': ('D10', 9, 'SD_CLK'),
    '12': ('3V3', None, '3V3'),
    '13': ('GND', None, 'GND'),
    '14': ('5V', None, None),
    '15': ('D11', 38, 'LCD_RST'),
    '16': ('D12', 39, 'LCD_SCK'),
    '17': ('D13', 40, 'LCD_D1'),
    '18': ('D14', 41, 'LCD_D3'),
    '19': ('D15', 42, 'SCL'),
    '20': ('D16', 10, 'WHEEL_BTN'),
    '21': ('D19', 11, 'I2S_DOUT'),
    '22': ('D18', 12, 'I2S_BCLK'),
    '23': ('D17', 13, 'SD_CMD'),
    '32': ('BAT+', None, 'VBAT'),
    '33': ('BAT-', None, 'GND'),
}

# ----------------------------------------------------------------------------- Display-FPC (34 Pin, laut Waveshare-Schaltplan U4)
FPC_PINS = {
    '1': 'LCD_RST', '2': 'LCD_TE', '3': 'GND', '4': 'GND', '5': 'LCD_D0', '6': None, '7': 'LCD_D1',
    '8': 'SCL', '9': 'LCD_SCK', '10': 'SDA', '11': 'LCD_CS', '12': 'TP_INT', '13': 'LCD_D2', '14': 'TP_RST',
    '15': 'LCD_D3', '16': '3V3', '17': 'LCD_IM1', '18': '3V3', '19': 'LCD_IM0', '20': '3V3', '21': 'GND',
    '22': 'LCD_PWR_EN', '23': 'GND', '24': '3V3', '25': 'GND', '26': '3V3', '27': 'GND', '28': 'GND',
    '29': 'GND', '30': None, '31': 'GND', '32': None, '33': 'GND', '34': None,
    '35': 'GND', '36': 'GND', '37': 'GND', '38': 'GND',
}

# ----------------------------------------------------------------------------- Symbole (eigene)
# name -> (Pinliste links, Pinliste rechts); Pin = (nummer, name, typ)
SYMBOLS = {
    'XIAO_ESP32S3_Plus': dict(
        left=[('1', 'D0/GPIO1', 'bidirectional'), ('2', 'D1/GPIO2', 'bidirectional'), ('3', 'D2/GPIO3', 'bidirectional'),
              ('4', 'D3/GPIO4', 'bidirectional'), ('5', 'D4/GPIO5', 'bidirectional'), ('6', 'D5/GPIO6', 'bidirectional'),
              ('7', 'D6/GPIO43', 'bidirectional'), ('15', 'D11/GPIO38', 'bidirectional'), ('16', 'D12/GPIO39', 'bidirectional'),
              ('17', 'D13/GPIO40', 'bidirectional'), ('18', 'D14/GPIO41', 'bidirectional'), ('19', 'D15/GPIO42', 'bidirectional'),
              ('20', 'D16/GPIO10', 'bidirectional')],
        right=[('8', 'D7/GPIO44', 'bidirectional'), ('9', 'D8/GPIO7', 'bidirectional'), ('10', 'D9/GPIO8', 'bidirectional'),
               ('11', 'D10/GPIO9', 'bidirectional'), ('23', 'D17/GPIO13', 'bidirectional'), ('22', 'D18/GPIO12', 'bidirectional'),
               ('21', 'D19/GPIO11', 'bidirectional'), ('12', '3V3_OUT', 'power_out'), ('13', 'GND', 'power_in'),
               ('14', '5V_VBUS', 'power_out'), ('32', 'BAT+', 'power_in'), ('33', 'BAT-', 'power_in')],
        w=22.86, ref='U'),
    'TLV320DAC3100': dict(
        left=[('2', 'IOVDD', 'power_in'), ('1', 'IOVSS', 'power_in'), ('3', 'DVDD', 'power_in'), ('18', 'DVSS', 'power_in'),
              ('31', '~{RESET}', 'input'), ('9', 'SDA', 'bidirectional'), ('10', 'SCL', 'input'), ('5', 'DIN', 'input'),
              ('6', 'WCLK', 'bidirectional'), ('7', 'BCLK', 'bidirectional'), ('8', 'MCLK', 'input'),
              ('32', 'GPIO1', 'bidirectional'), ('4', 'NC', 'no_connect')],
        right=[('27', 'HPL', 'output'), ('30', 'HPR', 'output'), ('28', 'HPVDD', 'power_in'), ('29', 'HPVSS', 'power_in'),
               ('17', 'AVDD', 'power_in'), ('16', 'AVSS', 'power_in'), ('21', 'SPKVDD', 'power_in'), ('24', 'SPKVDD', 'power_in'),
               ('20', 'SPKVSS', 'power_in'), ('25', 'SPKVSS', 'power_in'), ('22', 'SPKP', 'output'), ('26', 'SPKP', 'output'),
               ('19', 'SPKM', 'output'), ('23', 'SPKM', 'output'), ('11', 'VOL/MICDET', 'input'), ('12', 'MICBIAS', 'power_out'),
               ('13', 'AIN1', 'input'), ('14', 'AIN2', 'input'), ('15', 'NC', 'no_connect'), ('33', 'EP', 'power_in')],
        w=22.86, ref='U'),
    'MAX17048': dict(
        left=[('2', 'CELL', 'input'), ('3', 'VDD', 'power_in'), ('7', 'SCL', 'input'), ('8', 'SDA', 'bidirectional')],
        right=[('1', 'CTG', 'power_in'), ('4', 'GND', 'power_in'), ('9', 'EP', 'power_in'), ('5', 'ALRT', 'open_collector'),
               ('6', 'QSTRT', 'input')], w=15.24, ref='U'),
    'FPC_34': dict(
        left=[(str(i), f'{i}', 'passive') for i in range(1, 35, 2)],
        right=[(str(i), f'{i}', 'passive') for i in range(2, 35, 2)] ,
        extra_bottom=[('35', 'S1', 'passive'), ('36', 'S2', 'passive'), ('37', 'S3', 'passive'), ('38', 'S4', 'passive')],
        w=15.24, ref='J'),
    'MicroSD': dict(
        left=[('2', 'DAT3/CD', 'bidirectional'), ('3', 'CMD', 'input'), ('4', 'VDD', 'power_in'), ('5', 'CLK', 'input'),
              ('6', 'VSS', 'power_in'), ('7', 'DAT0', 'bidirectional'), ('8', 'DAT1', 'bidirectional'), ('1', 'DAT2', 'bidirectional')],
        right=[('9', 'CD', 'passive'), ('10', 'CD_GND', 'passive'), ('11', 'SHIELD', 'passive')], w=15.24, ref='J'),
    'Jack3_SwitchT': dict(
        left=[('T', 'TIP', 'passive'), ('R', 'RING', 'passive'), ('S', 'SLEEVE', 'passive'), ('TN', 'TIP_SW', 'passive')],
        right=[], w=12.7, ref='J'),
}

PARTS = []
def add(ref, value, kind, fp, pins, at=None, near=None, **kw):
    d = dict(ref=ref, value=value, sym=kind, fp=fp, pins=pins, at=at, near=near)
    d.update(kw)
    PARTS.append(d)
    return d

R402 = 'Resistor_SMD:R_0402_1005Metric'
C402 = 'Capacitor_SMD:C_0402_1005Metric'
C603 = 'Capacitor_SMD:C_0603_1608Metric'
C805 = 'Capacitor_SMD:C_0805_2012Metric'

UNIROYAL = {'0': ('0402WGF0000TCE', 'C17168'), '1k': ('0402WGF1001TCE', 'C11702'), '2.2k': ('0402WGF2201TCE', 'C25879'),
            '4.7k': ('0402WGF4701TCE', 'C25900'), '10k': ('0402WGF1002TCE', 'C25744'), '100k': ('0402WGF1003TCE', 'C25741')}

def res(ref, val, n1, n2, near=None, at=None, desc='', **kw):
    mpn, lcsc = UNIROYAL[val]
    return add(ref, val, 'Device:R', R402, {'1': n1, '2': n2}, near=near, at=at, mpn=mpn, mfr='UNI-ROYAL', lcsc=lcsc,
               desc=desc + (' 1 %' if val != '0' else ''), pkg='0402', **kw)

CAPS = {   # Wert -> (Footprint, Hersteller, MPN, LCSC, Paket, Beschreibung)
    '100nF': (C402, 'Samsung', 'CL05B104KO5NNNC', 'C1525', '0402', '100 nF X7R 16 V'),
    '1uF':   (C402, 'Samsung', 'CL05A105KA5NQNC', 'C52923', '0402', '1 uF X5R 6,3 V'),
    '4.7uF': (C603, 'Samsung', 'CL10A475KO8NNNC', '', '0603', '4,7 uF X5R 16 V'),
    '10uF':  (C603, 'Samsung', 'CL10A106KP8NNNC', 'C19702', '0603', '10 uF X5R 10 V'),
    '22uF':  (C805, 'Samsung', 'CL21A226MAQNNNE', '', '0805', '22 uF X5R 25 V'),
    '100uF': (C805, 'Samsung', 'CL21A107MQYNNNE', '', '0805', '100 uF X5R 6,3 V'),
}
def cap(ref, val, n1, n2, near=None, at=None, desc='', **kw):
    fp, mfr, mpn, lcsc, pkg, d = CAPS[val]
    return add(ref, val, 'Device:C', fp, {'1': n1, '2': n2}, near=near, at=at, mpn=mpn, mfr=mfr, lcsc=lcsc, pkg=pkg,
               desc=(desc + ' ' if desc else '') + d, **kw)

# ============================================================================ Module / ICs
xp = {k: v[2] for k, v in XIAO_PINS.items()}
add('U1', 'XIAO ESP32S3 Plus', 'Tangara:XIAO_ESP32S3_Plus', 'Tangara:XIAO-ESP32-S3-Plus-SMD', xp,
    at=(6.2, 32.65, 270, 'B'), mfr='Seeed Studio', mpn='113991120 (XIAO ESP32S3 Plus)', pkg='Modul 21 x 17,8',
    desc='ESP32-S3R8 16 MB Flash, 8 MB PSRAM, USB-C, LiPo-Lader; SMD-Montage ueber Randpads', lcsc='', dk='1597-113991120-ND (laut Hersteller-Distributorliste, vor Bestellung pruefen)')

add('U2', 'TLV320DAC3100', 'Tangara:TLV320DAC3100', 'Package_DFN_QFN:Texas_RHB0032E_VQFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm',
    {'1': 'GND', '2': '3V3', '3': 'DVDD', '4': None, '5': 'I2S_DOUT', '6': 'I2S_WS', '7': 'I2S_BCLK', '8': 'GND', '9': 'SDA',
     '10': 'SCL', '11': 'DAC_VOL', '12': None, '13': None, '14': None, '15': None, '16': 'AGND', '17': 'AVDD', '18': 'GND',
     '19': None, '20': 'AGND', '21': '3V3', '22': None, '23': None, '24': '3V3', '25': 'AGND', '26': None, '27': 'HPL',
     '28': 'AVDD', '29': 'AGND', '30': 'HPR', '31': 'DAC_RST', '32': None, '33': 'AGND'},
    at=(-12.5, 13.0, 0, 'B'), mfr='Texas Instruments', mpn='TLV320DAC3100IRHBR', lcsc='C179677', dk='296-27216-1-ND', pkg='VQFN-32 5x5',
    desc='Stereo-DAC mit Kopfhoerertreiber, I2S + I2C 0x18, PLL aus BCLK')
add('U3', 'TPS7A2030PDBVR', 'Tangara:LDO_SOT23_5', 'Package_TO_SOT_SMD:SOT-23-5',
    {'1': '3V3', '2': 'AGND', '3': '3V3', '4': None, '5': 'AVDD'}, at=(-7.0, 18.0, 0, 'B'),
    mfr='Texas Instruments', mpn='TPS7A2030PDBVR', lcsc='', dk='', pkg='SOT-23-5', desc='LDO 3,0 V 300 mA, 7 uVrms (Analogversorgung)')
add('U4', 'TLV75518PDBVR', 'Tangara:LDO_SOT23_5', 'Package_TO_SOT_SMD:SOT-23-5',
    {'1': '3V3', '2': 'GND', '3': '3V3', '4': None, '5': 'DVDD'}, at=(-7.0, 8.0, 0, 'B'),
    mfr='Texas Instruments', mpn='TLV75518PDBVR', lcsc='', dk='', pkg='SOT-23-5', desc='LDO 1,8 V 500 mA (DVDD des Codecs)')
add('U5', 'MAX17048G+T10', 'Tangara:MAX17048', 'Package_DFN_QFN:TDFN-8-1EP_2x2mm_P0.5mm_EP0.8x1.2mm',
    {'1': 'GND', '2': 'VBAT', '3': 'VBAT', '4': 'GND', '5': 'FG_ALRT', '6': 'GND', '7': 'SCL', '8': 'SDA', '9': 'GND'},
    at=(-9.0, -15.0, 0, 'B'), mfr='Analog Devices (Maxim)', mpn='MAX17048G+T10', lcsc='C2682616', dk='MAX17048G+T10CT-ND', pkg='TDFN-8 2x2',
    desc='Fuel Gauge 1S LiPo, I2C 0x36')

# ============================================================================ Stecker
add('J1', 'AXE534124', 'Tangara:FPC_34', 'Tangara:FPC-AXE534124', dict(FPC_PINS), at=(0.0, -2.0, 0, 'T'),
    mfr='Panasonic', mpn='AXE534124', lcsc='', dk='', pkg='FPC 34 Pol 0,4 mm', desc='Display-FPC-Buchse (wie Waveshare ESP32-S3-Touch-AMOLED-1.8, Landmuster ungeprueft)')
add('J2', 'SM06B-SRSS-TB', 'Connector_Generic:Conn_01x06', 'Connector_JST:JST_SH_SM06B-SRSS-TB_1x06-1MP_P1.00mm_Horizontal',
    {'1': '3V3', '2': 'GND', '3': 'SDA', '4': 'SCL', '5': 'WHEEL_INT', '6': 'WHEEL_BTN'}, at=(7.2, -10.0, 0, 'B'),
    mfr='JST', mpn='SM06B-SRSS-TB(LF)(SN)', lcsc='C160405', dk='455-1796-1-ND', pkg='JST-SH 6 Pol', desc='Klickrad-Modul (3V3, GND, SDA, SCL, INT, BTN)')
add('J3', 'SM02B-SRSS-TB', 'Connector_Generic:Conn_01x02', 'Connector_JST:JST_SH_SM02B-SRSS-TB_1x02-1MP_P1.00mm_Horizontal',
    {'1': 'VBAT', '2': 'GND'}, at=(15.5, -14.0, 180, 'B'),
    mfr='JST', mpn='SM02B-SRSS-TB(LF)(SN)', lcsc='C160402', dk='455-1794-1-ND', pkg='JST-SH 2 Pol', desc='LiPo-Anschluss (Pin 1 = +, Polung des Akkus pruefen!)')
add('J4', 'SJ-3524-SMT', 'Tangara:Jack3_SwitchT', 'Connector_Audio:Jack_3.5mm_CUI_SJ-3524-SMT_Horizontal',
    {'T': 'HPL_J', 'R': 'HPR_J', 'S': 'AGND', 'TN': 'JACK_SW'}, at=(-12.55, 35.5, 0, 'B'),
    mfr='CUI Devices', mpn='SJ-3524-SMT-TR', lcsc='', dk='CP-3524SJCT-ND', pkg='3,5 mm Klinke SMD', desc='3,5-mm-Stereo-Klinke mit Schliesser an der Spitze (Steckererkennung)')
add('J5', 'microSD', 'Tangara:MicroSD', 'Connector_Card:microSD_HC_Molex_104031-0811',
    {'1': 'SD_D2', '2': 'SD_D3', '3': 'SD_CMD', '4': '3V3', '5': 'SD_CLK', '6': 'GND', '7': 'SD_D0', '8': 'SD_D1', '9': None, '10': None, '11': 'GND'},
    at=(-12.3, -5.0, 270, 'B'), mfr='Molex', mpn='104031-0811', lcsc='', dk='', pkg='microSD Push-Push', desc='microSD-Halter, Push-Push, 1-Bit-SDMMC')
add('SW1', 'B3U-3000P', 'Switch:SW_Push', 'Button_Switch_SMD:SW_SPST_B3U-3000P', {'1': 'PWR_BTN', '2': 'GND'},
    at=(8.0, 42.8, 0, 'T'), mfr='Omron', mpn='B3U-3000P', lcsc='', dk='SW1020CT-ND', pkg='3,0 x 2,5 x 1,2 seitlich', desc='Ein/Aus-Taster, seitlich betaetigt (Weckpin)')

# ============================================================================ Passive: Busse, Pull-ups
res('R1', '2.2k', '3V3', 'SDA', near=('U5', '8', -3.0, -3.0, 0), desc='I2C Pull-up SDA')
res('R2', '2.2k', '3V3', 'SCL', near=('U5', '7', -3.0, -4.5, 0), desc='I2C Pull-up SCL')
res('R3', '10k', '3V3', 'WHEEL_INT', near=('J2', '5', 3.0, 3.0, 90), desc='Pull-up Klickrad INT (open drain)')
res('R4', '10k', '3V3', 'WHEEL_BTN', near=('J2', '6', 4.0, 3.0, 90), desc='Pull-up Klickrad BTN')
res('R5', '10k', '3V3', 'PWR_BTN', near=('SW1', '1', -4.0, 0.0, 0), desc='Pull-up Ein/Aus-Taster')
cap('C1', '100nF', 'PWR_BTN', 'GND', near=('SW1', '1', -4.0, 1.5, 0), desc='Entprellung Ein/Aus')
# Display
res('R6', '10k', '3V3', 'LCD_IM1', near=('J1', '17', 0.0, 4.0, 0), side='B', desc='Display IM1 = 1 (wie Waveshare R27)')
res('R7', '10k', 'LCD_IM0', 'GND', near=('J1', '19', 0.0, 4.0, 0), side='B', desc='Display IM0 = 0 (wie Waveshare R28)')
res('R8', '10k', '3V3', 'TP_RST', near=('J1', '14', 0.0, 4.0, 0), side='B', desc='Touch-Reset hochgelegt')
res('R9', '10k', '3V3', 'TP_INT', near=('J1', '12', 0.0, 4.0, 0), side='B', desc='Touch-INT Pull-up (wie Waveshare R26)')
res('R10', '4.7k', '3V3', 'LCD_PWR_EN', near=('J1', '22', 0.0, 4.0, 0), side='B', desc='FPC-Pin 22 (Waveshare DSI_PWR_EN) fest high')
res('R11', '100k', '3V3', 'LCD_RST', near=('J1', '1', 0.0, 4.0, 0), side='B', desc='Reset-Pull-up Display')
res('R12', '1k', 'LCD_TE_MCU', 'LCD_TE', near=('U1', '7', -2.0, 2.0, 0), desc='Serienwiderstand TE (GPIO43 ist UART0-TX beim Booten)')
cap('C2', '10uF', '3V3', 'GND', near=('J1', '24', 0.0, 6.0, 0), side='B', desc='Display VCI/VDDIO')
cap('C3', '100nF', '3V3', 'GND', near=('J1', '26', 0.0, 6.0, 0), side='B', desc='Display VCI/VDDIO')
cap('C4', '10uF', '3V3', 'GND', near=('J1', '16', 0.0, 6.0, 0), side='B', desc='Display/Touch VDD')
cap('C5', '100nF', '3V3', 'GND', near=('J1', '18', 0.0, 6.0, 0), side='B', desc='Display/Touch VDD')
add('TP1', 'TP_INT', 'Connector:TestPoint', 'TestPoint:TestPoint_Pad_D1.0mm', {'1': 'TP_INT'}, near=('J1', '12', 3.0, 4.0, 0), side='B',
    nobom=True, desc='Touch-INT (kein GPIO uebrig)')
# SD
res('R13', '10k', '3V3', 'SD_CMD', near=('J5', '3', 0, 0, 0), desc='SD CMD Pull-up')
res('R14', '10k', '3V3', 'SD_D0', near=('J5', '7', 0, 0, 0), desc='SD D0 Pull-up')
res('R15', '10k', '3V3', 'SD_D1', near=('J5', '8', 0, 0, 0), desc='SD D1 Pull-up (1-Bit-Modus)')
res('R16', '10k', '3V3', 'SD_D2', near=('J5', '1', 0, 0, 0), desc='SD D2 Pull-up (1-Bit-Modus)')
res('R17', '10k', '3V3', 'SD_D3', near=('J5', '2', 0, 0, 0), desc='SD D3 Pull-up (haelt Karte im SD-Modus)')
cap('C6', '10uF', '3V3', 'GND', near=('J5', '4', 0, 0, 0), desc='SD VDD')
cap('C7', '100nF', '3V3', 'GND', near=('J5', '4', 0, 0, 0), desc='SD VDD')
# 3V3 Puffer am XIAO
cap('C8', '22uF', '3V3', 'GND', near=('U1', '12', 3.0, 0, 0), desc='3V3 Puffer (Display/Klickrad-LRA)')
# Audio
cap('C10', '100nF', '3V3', 'GND', near=('U2', '2', 0, 0, 0), desc='IOVDD')
cap('C11', '1uF', '3V3', 'GND', near=('U2', '2', 0, 0, 0), desc='IOVDD')
cap('C12', '100nF', 'DVDD', 'GND', near=('U2', '3', 0, 0, 0), desc='DVDD')
cap('C13', '4.7uF', 'DVDD', 'GND', near=('U2', '3', 0, 0, 0), desc='DVDD')
cap('C14', '100nF', 'AVDD', 'AGND', near=('U2', '17', 0, 0, 0), desc='AVDD')
cap('C15', '4.7uF', 'AVDD', 'AGND', near=('U2', '17', 0, 0, 0), desc='AVDD')
cap('C16', '100nF', 'AVDD', 'AGND', near=('U2', '28', 0, 0, 0), desc='HPVDD')
cap('C17', '4.7uF', 'AVDD', 'AGND', near=('U2', '28', 0, 0, 0), desc='HPVDD')
cap('C18', '100nF', '3V3', 'AGND', near=('U2', '21', 0, 0, 0), desc='SPKVDD (Verstaerker unbenutzt)')
cap('C19', '100nF', '3V3', 'AGND', near=('U2', '24', 0, 0, 0), desc='SPKVDD')
cap('C20', '4.7uF', '3V3', 'AGND', near=('U2', '24', 0, 0, 0), desc='SPKVDD')
res('R18', '10k', '3V3', 'DAC_RST', near=('U2', '31', 0, 0, 0), desc='Reset-RC: Pull-up')
cap('C21', '1uF', 'DAC_RST', 'GND', near=('U2', '31', 0, 0, 0), desc='Reset-RC (Verzoegerung ca. 10 ms)')
res('R19', '10k', 'DAC_VOL', 'AGND', near=('U2', '11', 0, 0, 0), desc='VOL/MICDET unbenutzt auf AGND')
cap('C22', '100uF', 'HPL', 'HPL_J', near=('U2', '27', 0, 0, 0), desc='DC-Sperre Kopfhoerer links')
cap('C23', '100uF', 'HPR', 'HPR_J', near=('U2', '30', 0, 0, 0), desc='DC-Sperre Kopfhoerer rechts')
res('R20', '10k', 'HPL_J', 'AGND', near=('J4', 'T', 0, 0, 0), desc='Entladewiderstand links')
res('R21', '10k', 'HPR_J', 'AGND', near=('J4', 'R', 0, 0, 0), desc='Entladewiderstand rechts')
res('R22', '0', 'AGND', 'GND', near=('U2', '33', 0, 0, 0), desc='Sternpunkt AGND-GND (nur hier verbinden)')
res('R23', '100k', '3V3', 'JACK_SW', near=('J4', 'TN', 0, 0, 0), desc='Pull-up Steckererkennung')
res('R24', '10k', 'JACK_SW', 'JACK_DET', near=('J4', 'TN', 0, 0, 0), desc='Serienwiderstand Erkennung')
# LDOs
cap('C24', '1uF', '3V3', 'AGND', near=('U3', '1', 0, 0, 0), desc='U3 Eingang')
cap('C25', '1uF', 'AVDD', 'AGND', near=('U3', '5', 0, 0, 0), desc='U3 Ausgang')
cap('C26', '4.7uF', 'AVDD', 'AGND', near=('U3', '5', 0, 0, 0), desc='U3 Ausgang')
cap('C27', '1uF', '3V3', 'GND', near=('U4', '1', 0, 0, 0), desc='U4 Eingang')
cap('C28', '1uF', 'DVDD', 'GND', near=('U4', '5', 0, 0, 0), desc='U4 Ausgang')
cap('C29', '4.7uF', 'DVDD', 'GND', near=('U4', '5', 0, 0, 0), desc='U4 Ausgang')
# Fuel Gauge
cap('C30', '100nF', 'VBAT', 'GND', near=('U5', '3', 0, 0, 0), desc='MAX17048 VDD')
add('TP2', 'ALRT', 'Connector:TestPoint', 'TestPoint:TestPoint_Pad_D1.0mm', {'1': 'FG_ALRT'}, near=('U5', '5', 0, 0, 0), nobom=True,
    desc='MAX17048 ALRT (kein GPIO uebrig)')
# Akku-Loetpads (parallel zu J3)
add('TP3', 'BAT+', 'Connector:TestPoint', 'Connector_Wire:SolderWirePad_1x01_SMD_1x2mm', {'1': 'VBAT'}, near=('J3', '1', 0, 0, 0), nobom=True, desc='Akku + Loetpad')
add('TP4', 'BAT-', 'Connector:TestPoint', 'Connector_Wire:SolderWirePad_1x01_SMD_1x2mm', {'1': 'GND'}, near=('J3', '2', 0, 0, 0), nobom=True, desc='Akku - Loetpad')
# Montagelocher Klickrad (NPTH 2,2 mm auf r = 14,6 um (0,-27))
import math
for i, a in enumerate((90, 210, 330)):
    x = 14.6 * math.cos(math.radians(a)); y = -27.0 + 14.6 * math.sin(math.radians(a))
    add(f'H{i+1}', 'M2-Klickrad', 'Mechanical:MountingHole', 'MountingHole:MountingHole_2.2mm_M2', {}, at=(round(x, 4), round(y, 4), 0, 'T'),
        nobom=True, desc='Montageloch Abstandshalter Klickrad (Detail: README)')

def parts():
    return PARTS

# Netze, die als Leistungssymbol dargestellt werden
POWER_NETS = {'GND': 'power:GND', '3V3': 'power:+3V3', 'VBAT': 'power:VBAT', 'AVDD': 'power:+3V0', 'DVDD': 'power:+1V8',
              'AGND': 'power:GNDA', 'VBUS': 'power:VBUS'}
