#!/usr/bin/env python3
"""Schreibt tools/projekt_vorlage.kicad_pro und ../hauptplatine.kicad_pro (PCBWay-Standard 4 Lagen, 1,0 mm)."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def netclass(name, clr, tw, prio, **kw):
    d = {"name": name, "clearance": clr, "track_width": tw, "via_diameter": 0.45, "via_drill": 0.2, "microvia_diameter": 0.3,
         "microvia_drill": 0.1, "diff_pair_width": 0.2, "diff_pair_gap": 0.25, "diff_pair_via_gap": 0.25,
         "pcb_color": "rgba(0, 0, 0, 0.000)", "schematic_color": "rgba(0, 0, 0, 0.000)", "wire_width": 6, "bus_width": 12,
         "line_style": 0, "priority": prio}
    d.update(kw); return d
pro = {
 "meta": {"filename": "hauptplatine.kicad_pro", "version": 3},
 "board": {"design_settings": {
   "defaults": {"board_outline_line_width": 0.1, "copper_line_width": 0.2, "copper_text_size_h": 1.0, "copper_text_size_v": 1.0,
                "silk_line_width": 0.15, "silk_text_size_h": 0.9, "silk_text_size_v": 0.9, "silk_text_thickness": 0.15},
   "rules": {"min_clearance": 0.09, "min_copper_edge_clearance": 0.2, "min_hole_clearance": 0.25, "min_hole_to_hole": 0.5,
             "min_through_hole_diameter": 0.2, "min_via_annular_width": 0.125, "min_via_diameter": 0.4, "min_track_width": 0.09,
             "min_text_height": 0.8, "min_text_thickness": 0.12, "min_microvia_diameter": 0.2, "min_microvia_drill": 0.1,
             "min_silk_clearance": 0.0, "min_connection": 0.0, "min_resolved_spokes": 2, "solder_mask_to_copper_clearance": 0.0,
             "min_groove_width": 0.0, "min_copper_edge_clearance": 0.2},
   "rule_severities": {"silk_over_copper": "ignore", "silk_overlap": "ignore", "courtyards_overlap": "warning",
                       "lib_footprint_issues": "ignore", "lib_footprint_mismatch": "ignore"},
   "track_widths": [0.0, 0.127, 0.2, 0.3, 0.4], "via_dimensions": [{"diameter": 0.0, "drill": 0.0}, {"diameter": 0.45, "drill": 0.2}]}},
 "net_settings": {"classes": [netclass("Default", 0.127, 0.127, 2147483647), netclass("Power", 0.127, 0.25, 1), netclass("USB_HS", 0.127, 0.2, 0, diff_pair_width=0.2, diff_pair_gap=0.15)], "meta": {"version": 4},
   "net_colors": None, "netclass_assignments": None,
   "netclass_patterns": [{"netclass": "USB_HS", "pattern": p} for p in ("USB_HS_DP", "USB_HS_DM", "USB_DP", "USB_DN")] + [{"netclass": "Power", "pattern": p} for p in ("3V3", "SYS_POWER", "VBAT", "VBUS", "VBUS_SW", "V5_HOST", "V5A", "VN5A", "SD_VDD")]},
 "schematic": {"drawing": {"default_line_thickness": 6.0}},
 "sheets": [], "text_variables": {}}
for p in (os.path.join(ROOT, 'tools', 'projekt_vorlage.kicad_pro'), os.path.join(ROOT, 'hauptplatine.kicad_pro')):
    json.dump(pro, open(p, 'w'), indent=2)

# Bibliothekstabellen
SYM = ["Device", "power", "Switch", "Connector", "Connector_Generic", "Mechanical"]
FP = ["Resistor_SMD", "Capacitor_SMD", "Package_TO_SOT_SMD", "Package_DFN_QFN", "Package_SO", "Package_SON", "Connector_JST", "Connector_Audio", "Connector_Card",
      "Button_Switch_SMD", "TestPoint", "Connector_Wire", "MountingHole", "Oscillator", "Inductor_SMD", "Crystal", "Connector_FFC-FPC"]
t = '(sym_lib_table\n  (version 7)\n  (lib (name "Hauptplatine") (type "KiCad") (uri "${KIPRJMOD}/lib/Hauptplatine.kicad_sym") (options "") (descr "Eigene Symbole Hauptplatine"))\n'
t += ''.join('  (lib (name "%s") (type "KiCad") (uri "${KICAD9_SYMBOL_DIR}/%s.kicad_sym") (options "") (descr ""))\n' % (n, n) for n in SYM) + ')\n'
open(os.path.join(ROOT, 'sym-lib-table'), 'w').write(t)
t = '(fp_lib_table\n  (version 7)\n  (lib (name "Hauptplatine") (type "KiCad") (uri "${KIPRJMOD}/lib/Hauptplatine.pretty") (options "") (descr "Eigene Footprints Hauptplatine"))\n'
t += ''.join('  (lib (name "%s") (type "KiCad") (uri "${KICAD9_FOOTPRINT_DIR}/%s.pretty") (options "") (descr ""))\n' % (n, n) for n in FP) + ')\n'
open(os.path.join(ROOT, 'fp-lib-table'), 'w').write(t)
