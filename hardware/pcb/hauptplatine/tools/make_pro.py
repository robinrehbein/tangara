#!/usr/bin/env python3
"""Schreibt tools/projekt_vorlage.kicad_pro und ../hauptplatine.kicad_pro (PCBWay-Standard 4 Lagen, 1,0 mm)."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def netclass(name, clr, tw, prio, **kw):
    d = {"name": name, "clearance": clr, "track_width": tw, "via_diameter": 0.6, "via_drill": 0.3, "microvia_diameter": 0.3,
         "microvia_drill": 0.1, "diff_pair_width": 0.2, "diff_pair_gap": 0.25, "diff_pair_via_gap": 0.25,
         "pcb_color": "rgba(0, 0, 0, 0.000)", "schematic_color": "rgba(0, 0, 0, 0.000)", "wire_width": 6, "bus_width": 12,
         "line_style": 0, "priority": prio}
    d.update(kw); return d
pro = {
 "meta": {"filename": "hauptplatine.kicad_pro", "version": 3},
 "board": {"design_settings": {
   "defaults": {"board_outline_line_width": 0.1, "copper_line_width": 0.2, "copper_text_size_h": 1.0, "copper_text_size_v": 1.0,
                "silk_line_width": 0.15, "silk_text_size_h": 0.9, "silk_text_size_v": 0.9, "silk_text_thickness": 0.15},
   "rules": {"min_clearance": 0.1, "min_copper_edge_clearance": 0.3, "min_hole_clearance": 0.25, "min_hole_to_hole": 0.5,
             "min_through_hole_diameter": 0.3, "min_via_annular_width": 0.13, "min_via_diameter": 0.5, "min_track_width": 0.1,
             "min_text_height": 0.8, "min_text_thickness": 0.12, "min_microvia_diameter": 0.2, "min_microvia_drill": 0.1,
             "min_silk_clearance": 0.0, "min_connection": 0.0, "min_resolved_spokes": 2, "solder_mask_to_copper_clearance": 0.0,
             "min_groove_width": 0.0, "min_copper_edge_clearance": 0.3},
   "rule_severities": {"silk_over_copper": "ignore", "silk_overlap": "ignore", "courtyards_overlap": "warning",
                       "lib_footprint_issues": "ignore", "lib_footprint_mismatch": "ignore"},
   "track_widths": [0.0, 0.15, 0.2, 0.3, 0.4], "via_dimensions": [{"diameter": 0.0, "drill": 0.0}, {"diameter": 0.6, "drill": 0.3}]}},
 "net_settings": {"classes": [netclass("Default", 0.15, 0.15, 2147483647), netclass("Power", 0.15, 0.35, 1)], "meta": {"version": 4},
   "net_colors": None, "netclass_assignments": None,
   "netclass_patterns": [{"netclass": "Power", "pattern": p} for p in ("3V3", "VBAT", "AVDD", "DVDD", "VBUS")]},
 "schematic": {"drawing": {"default_line_thickness": 6.0}},
 "sheets": [], "text_variables": {}}
for p in (os.path.join(ROOT, 'tools', 'projekt_vorlage.kicad_pro'), os.path.join(ROOT, 'hauptplatine.kicad_pro')):
    json.dump(pro, open(p, 'w'), indent=2)
