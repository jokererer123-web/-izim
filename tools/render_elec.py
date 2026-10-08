# -*- coding: utf-8 -*-
"""Elektrik planını PNG/PDF olarak görüntüler."""
import sys, math, re
import ezdxf
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Arc as MArc, Circle as MCirc

ARCH = {'DUVAR','sıva','KAPI','pencere','mahal','KOLON','balkon','M','DOGRAMA'}
ECOL = {'E-PRIZ':'#00a651','E-PRIZ-OZEL':'#00722e','E-AYD':'#0072bc',
        'E-ANAHTAR':'#0072bc','E-TABLO':'#ed1c24','E-ZAYIF':'#a349a4',
        'E-ACIL':'#ed1c24','E-HATT':'#f7941d','E-YAZI':'#333333','E-LEJANT':'#111111'}

def clean(t):
    t = re.sub(r'\\U\+([0-9A-Fa-f]{4})', lambda m: chr(int(m.group(1),16)), t)
    t = re.sub(r'\\x([0-9A-Fa-f]{2})', lambda m: bytes([int(m.group(1),16)]).decode('cp1254', 'replace'), t)
    t = re.sub(r'\\[fFHWAaCcTQ][^;]*;', '', t)
    t = t.replace('{','').replace('}','')
    t = re.sub(r'\\P',' ', t)
    t = re.sub(r'\\[\\{}]','',t)
    return t

def main(src, out, x0,y0,x1,y1, dpi=170, K=None):
    if K is None: K = 1.0 if out.lower().endswith('.pdf') else 2.5
    # metin boyutu: çizim birimi -> punto (1 birim=1cm=0.001in -> *0.072 pt),
    # K = önizleme okunabilirlik çarpanı
    def fs(h): return max(2.0, h*0.072*K)
    doc = ezdxf.readfile(src)
    msp = doc.modelspace()
    blocks = doc.blocks
    fig = plt.figure(figsize=((x1-x0)/1000,(y1-y0)/1000), dpi=dpi)
    ax = fig.add_axes([0,0,1,1]); ax.set_axis_off()
    ax.set_xlim(x0,x1); ax.set_ylim(y0,y1); ax.set_aspect('equal', adjustable='box')

    def col(lay):
        return ECOL.get(lay, '#999999')
    def lw(lay):
        return 0.9 if lay.startswith('E-') else 0.45

    def prim(e, M, lay):
        t = e.dxftype()
        def pt(p): return (M[0]*p[0]+M[2]*p[1]+M[4], M[1]*p[0]+M[3]*p[1]+M[5])
        c = col(lay)
        if t=='LINE':
            a,b = pt(e.dxf.start), pt(e.dxf.end)
            ax.plot([a[0],b[0]],[a[1],b[1]], lw=lw(lay), color=c)
        elif t=='LWPOLYLINE':
            pts=[pt(p) for p in e.get_points('xy')]
            if e.closed: pts.append(pts[0])
            ax.plot([p[0] for p in pts],[p[1] for p in pts], lw=lw(lay), color=c)
        elif t=='CIRCLE':
            ax.add_patch(MCirc(pt(e.dxf.center), e.dxf.radius, fill=False, lw=lw(lay), color=c))
        elif t=='ARC':
            rot = math.degrees(math.atan2(M[1],M[0]))
            ax.add_patch(MArc(pt(e.dxf.center), 2*e.dxf.radius,2*e.dxf.radius, angle=rot,
                              theta1=e.dxf.start_angle, theta2=e.dxf.end_angle, fill=False, lw=lw(lay), color=c))

    def block(name, M, lay):
        try: blk = blocks.get(name)
        except Exception: return
        for e in blk:
            if e.dxftype()=='INSERT':
                ins=e.dxf.insert
                ang=math.radians(getattr(e.dxf,'rotation',0))
                ca,sa=math.cos(ang),math.sin(ang)
                M2=[M[0]*ca+M[2]*sa, M[1]*ca+M[3]*sa, -M[0]*sa+M[2]*ca, -M[1]*sa+M[3]*ca,
                    M[0]*ins[0]+M[2]*ins[1]+M[4], M[1]*ins[0]+M[3]*ins[1]+M[5]]
                block(e.dxf.name, M2, lay)
            else:
                prim(e, M, lay)

    for e in msp:
        lay = e.dxf.layer
        if not (lay in ARCH or lay in ECOL): continue
        t = e.dxftype()
        if t=='INSERT':
            ins=e.dxf.insert
            if not (x0-600<ins[0]<x1+600 and y0-600<ins[1]<y1+600): continue
            ang=math.radians(getattr(e.dxf,'rotation',0))
            ca,sa=math.cos(ang),math.sin(ang)
            block(e.dxf.name,[ca,sa,-sa,ca,ins[0],ins[1]], lay)
        elif t in ('LINE','LWPOLYLINE','CIRCLE','ARC'):
            prim(e,[1,0,0,1,0,0], lay)
        elif t in ('TEXT',):
            if lay not in ECOL and lay!='mahal': continue
            ax.text(e.dxf.insert[0], e.dxf.insert[1], clean(e.dxf.text),
                    fontsize=fs(getattr(e.dxf,'height',12)), color=col(lay))
        elif t in ('MTEXT',):
            if lay!='mahal': continue
            ax.text(e.dxf.insert[0], e.dxf.insert[1], clean(e.text),
                    fontsize=fs(getattr(e.dxf,'char_height',getattr(e.dxf,'height',12)) or 12), color='#555555')
    if out.endswith('.pdf'):
        fig.savefig(out)
    else:
        fig.savefig(out, facecolor='white')
    print('saved', out)

if __name__=='__main__':
    main(sys.argv[1], sys.argv[2], *map(float, sys.argv[3:7]),
         float(sys.argv[7]) if len(sys.argv)>7 else 170)
