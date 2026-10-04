"""Gemeinsame Bauteil- und Netzliste für Schaltplan- und Layout-Generator."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAPFILE = os.path.join(ROOT, 'tools', 'seg_map.json')

def seg_map():
    """Segment k (0..11) -> MPR121-Elektrode n (0..11). Wird vom Layout bestimmt."""
    if os.path.exists(MAPFILE):
        return json.load(open(MAPFILE))
    return list(range(12))

def parts():
    sm = seg_map()
    P = []
    def add(ref, value, sym, fp, pins, **kw):
        d = dict(ref=ref, value=value, sym=sym, fp=fp, pins=pins); d.update(kw); P.append(d)
    # MPR121 UQFN-20: 1 IRQ 2 SCL 3 SDA 4 ADDR 5 VREG 6 VSS 7 REXT 8..19 ELE0..11 20 VDD
    pins = {'1': 'INT', '2': 'SCL', '3': 'SDA', '4': '3V3', '5': 'VREG', '6': 'GND', '7': 'REXT', '20': '3V3'}
    for n in range(12): pins[str(8 + n)] = f'ELE{n}'
    add('U1', 'MPR121QR2', 'Sensor_Touch:MPR121QR2', 'Klickrad:QFN-20_3x3mm_P0.4mm_noEP', pins,
        mpn='MPR121QR2', mfr='NXP', desc='12-Kanal kapazitiver Touch-Controller I2C 0x5B')
    add('U2', 'DRV2605LDGSR', 'Driver_Haptic:DRV2605LDGS', 'Package_SO:MSOP-10_3x3mm_P0.5mm',
        {'1': 'REG', '2': 'SCL', '3': 'SDA', '4': 'GND', '5': '3V3', '6': '3V3', '7': 'LRA_P', '8': 'GND', '9': 'LRA_N', '10': '3V3'},
        mpn='DRV2605LDGSR', mfr='Texas Instruments', desc='Haptik-Treiber LRA/ERM, I2C 0x5A')
    cap = lambda ref, v, nets, fp='Capacitor_SMD:C_0402_1005Metric', mpn='', d='': add(
        ref, v, 'Device:C', fp, {'1': nets[0], '2': nets[1]}, mpn=mpn, desc=d)
    cap('C1', '0.1uF', ('3V3', 'GND'), d='MPR121 VDD Entkopplung')
    cap('C2', '0.1uF', ('VREG', 'GND'), d='MPR121 VREG')
    cap('C3', '1uF', ('3V3', 'GND'), d='MPR121 Puffer')
    cap('C4', '1uF', ('3V3', 'GND'), d='DRV2605L VDD (1 uF laut Datenblatt)')
    cap('C5', '1uF', ('REG', 'GND'), d='DRV2605L REG (1 uF laut Datenblatt)')
    cap('C6', '10uF', ('3V3', 'GND'), fp='Capacitor_SMD:C_0603_1608Metric', d='DRV2605L VDD Puffer (LRA-Strom)')
    res = lambda ref, v, nets, d='', dnp=False: add(ref, v, 'Device:R', 'Resistor_SMD:R_0402_1005Metric',
                                                  {'1': nets[0], '2': nets[1]}, dnp=dnp, desc=d)
    res('R1', '75k', ('REXT', 'GND'), 'MPR121 REXT 1 %')
    res('R2', '4.7k', ('3V3', 'SDA'), 'I2C Pull-up SDA, DNP (Hauptboard hat 2,2k)', True)
    res('R3', '4.7k', ('3V3', 'SCL'), 'I2C Pull-up SCL, DNP', True)
    add('SW1', 'B3U-1000P', 'Switch:SW_Push', 'Button_Switch_SMD:SW_SPST_B3U-1000P', {'1': 'BTN', '2': 'GND'},
        mpn='B3U-1000P', mfr='Omron', desc='Taster 3x2.5x1.2 mm Mitteltaste')
    add('J1', 'SM06B-SRSS-TB', 'Connector_Generic:Conn_01x06', 'Connector_JST:JST_SH_SM06B-SRSS-TB_1x06-1MP_P1.00mm_Horizontal',
        {'1': '3V3', '2': 'GND', '3': 'SDA', '4': 'SCL', '5': 'INT', '6': 'BTN'}, mpn='SM06B-SRSS-TB(LF)(SN)', mfr='JST', desc='JST-SH 6-pol. seitlich')
    add('TP1', 'LRA+', 'Connector:TestPoint', 'Connector_Wire:SolderWirePad_1x01_SMD_1x2mm', {'1': 'LRA_P'}, desc='Lötpad LRA Litze +', nobom=True)
    add('TP2', 'LRA-', 'Connector:TestPoint', 'Connector_Wire:SolderWirePad_1x01_SMD_1x2mm', {'1': 'LRA_N'}, desc='Lötpad LRA Litze -', nobom=True)
    for k in range(12):
        add(f'SEG{k+1}', f'Touch{k+1}', 'Connector:TestPoint', f'Klickrad:SEG{k+1}', {'1': f'ELE{sm[k]}'}, nobom=True)
    return P
