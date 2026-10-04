import re
def parse(s):
    tok=re.findall(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()"]+',s)
    i=0
    def rd():
        nonlocal i
        t=tok[i]; i+=1
        if t=='(':
            l=[]
            while tok[i]!=')': l.append(rd())
            i+=1; return l
        if t.startswith('"'): return ('S',t[1:-1])
        return t
    return rd()
def sym(lib,name):
    t=open('/usr/share/kicad/symbols/%s.kicad_sym'%lib).read()
    d=parse(t)
    for x in d:
        if isinstance(x,list) and x[0]=='symbol' and x[1]==('S',name): return x
def pins(x):
    out=[]
    def walk(n):
        if isinstance(n,list):
            if n and n[0]=='pin':
                at=[c for c in n if isinstance(c,list) and c[0]=='at'][0]
                nm=[c for c in n if isinstance(c,list) and c[0]=='name'][0][1][1]
                nu=[c for c in n if isinstance(c,list) and c[0]=='number'][0][1][1]
                out.append((nu,nm,float(at[1]),float(at[2]),at[3],n[1]))
            else:
                for c in n: walk(c)
    walk(x); return out
if __name__=='__main__':
    import sys
    for p in pins(sym(sys.argv[1],sys.argv[2])): print(p)
