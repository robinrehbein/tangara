#!/usr/bin/env python3
"""Bearbeitungshelfer fuer die Review-Korrekturen (Rev. 3b): Bauteile ersetzen/neu setzen, Pads umnetzen, Verbindungen ziehen (baut auf rt.py auf)."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rt, netlist
import pcbnew
from pcbnew import ToMM
from rt import V, P
HERE = os.path.dirname(os.path.abspath(__file__))
FPDIR = '/usr/share/kicad/footprints/'


class Edit:
    def __init__(self, path):
        self.b = rt.load(path)
        self.parts = {p['ref']: p for p in netlist.parts()}
        self.R = rt.Router(self.b)
        self.FPS = {f.GetReference(): f for f in self.b.GetFootprints()}
        self.PADS = {}
        for f in list(self.FPS.values()): self._cache(f)

    def _cache(self, fp):
        for p in fp.Pads(): self.PADS[(fp.GetReference(), p.GetNumber())] = p

    def pad(self, ref, num): return self.PADS[(ref, str(num))]

    def net(self, name):
        n = self.b.FindNet(name)
        if n is None:
            n = pcbnew.NETINFO_ITEM(self.b, name); self.b.Add(n)
        return n

    def detach_pad(self, ref, num):
        """Entfernt alle Bahnen/Vias desselben Netzes, die das Pad beruehren (Stummel spaeter per prune_dangling)."""
        pad = self.pad(ref, num); net = pad.GetNetname(); g = rt.pad_geom(pad)
        lays = [rt.LIDX[l] for l in rt.LAYS if pad.IsOnLayer(l)]
        n = 0
        for t in list(self.b.GetTracks()):
            if t.GetNetname() != net: continue
            if t.Type() == pcbnew.PCB_VIA_T:
                if rt.Point(*P(t.GetPosition())).buffer(ToMM(t.GetWidth(pcbnew.F_Cu)) / 2).intersects(g): rt.remove_item(self.b, t); n += 1
            else:
                if t.GetLayer() not in rt.LIDX or rt.LIDX[t.GetLayer()] not in lays: continue
                if rt.LineString([P(t.GetStart()), P(t.GetEnd())]).intersects(g): rt.remove_item(self.b, t); n += 1
        return net, n

    def renet(self, ref, num, new):
        old, n = self.detach_pad(ref, num)
        self.pad(ref, num).SetNet(self.net(new))
        print('  %s.%s: %s -> %s (%d Objekte entfernt)' % (ref, num, old, new, n))
        return old

    def new_fp(self, ref, x, y, theta, side):
        part = self.parts[ref]
        lib, name = part['fp'].split(':')
        fp = pcbnew.FootprintLoad(os.path.join(os.path.dirname(HERE), 'lib', 'Hauptplatine.pretty') if lib == 'Hauptplatine' else FPDIR + lib + '.pretty', name)
        fp.SetFPID(pcbnew.LIB_ID(lib, name)); fp.SetReference(ref); fp.SetValue(part['value'])
        for g in list(fp.GraphicalItems()):
            if g.GetLayer() == pcbnew.Edge_Cuts: fp.Remove(g)
        self.b.Add(fp); self.FPS[ref] = fp
        fp.SetPosition(V(0, 0))
        if side == 'B': fp.Flip(V(0, 0), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        fp.SetOrientationDegrees(theta)
        fp.SetPosition(V(x, y))
        for pad in fp.Pads():
            nm = part['pins'].get(pad.GetNumber())
            if nm: pad.SetNet(self.net(nm))
        self._cache(fp)
        fp.Value().SetVisible(False); fp.Reference().SetVisible(False)
        for fld in fp.GetFields(): fld.SetVisible(False)
        if part.get('dnp'): fp.SetDNP(True)
        return fp

    def drop_fp(self, ref):
        fp = self.FPS.pop(ref); rt.GRAVE.append(fp); self.b.Remove(fp)
        for k in [k for k in self.PADS if k[0] == ref]: del self.PADS[k]

    def place_near(self, ref, near, search=14, side='B', theta=0, extra_block=(), margin=0.3, pick=0):
        """Legt das Bauteil auf den naechsten freien Platz (Pads + Rand) in der Naehe von 'near'."""
        fp = self.new_fp(ref, 0, 0, theta, side)
        bx = [rt.pad_geom(p).bounds for p in fp.Pads()]
        w = max(a[2] for a in bx) - min(a[0] for a in bx) + 0.2; h = max(a[3] for a in bx) - min(a[1] for a in bx) + 0.2
        self.drop_fp(ref); self.R.refresh()
        sp = rt.find_spot(self.b, side, w, h, near, items=self.R.items, search=search, nbest=pick + 1, extra_block=extra_block, margin=margin)[pick]
        print('  %s Platz (%.2f, %.2f)' % (ref, sp[0], sp[1]))
        self.new_fp(ref, round(sp[0], 2), round(sp[1], 2), theta, side)
        self.R.refresh()
        return sp

    def conn_pad(self, net, ref, num, widths=(0.127,), **kw):
        R = self.R; R.refresh(); got = None
        for w in widths:
            if len(R.clusters(net)) < 2 or R.connect_pad_to_net(net, ref, num, w=w, quiet=True, **kw) is not None: got = w; break
        print('  verbinde %-12s %s.%s -> Breite %s' % (net, ref, num, got))
        R.refresh()
        return got

    def apply_nc(self):
        NC = json.load(open(os.path.join(HERE, 'nc_nets.json')))
        for (ref, num), pad in self.PADS.items():
            if pad.GetNetname() == '' and ref + '/' + num in NC: pad.SetNet(self.net(NC[ref + '/' + num]))

    def save(self, path):
        pcbnew.SaveBoard(path, self.b)
