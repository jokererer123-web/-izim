# -*- coding: utf-8 -*-
"""
TİPİK KAT ELEKTRİK TESİSAT PLANI ÜRETİCİSİ
Mimari altlık (DXF) üzerine EMO / TS EN 60617 sembolleriyle
elektrik iç tesisat planı çizer; lejant, notlar ve antet ekler.
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ezdxf
from ezdxf.enums import TextEntityAlignment

SRC = os.path.join(os.path.dirname(__file__), "..", "elektrik", "dwg", "MIMARI_PROJE.dxf")
OUT = os.path.join(os.path.dirname(__file__), "..", "elektrik", "cizim", "ELEKTRIK_TESISAT_PLANI_TIP_KAT.dxf")

AXC = 49210.0   # simetri aksı (sol/sağ daire arası)

LAYERS = {
    "E-PRIZ":     (3,  "prizler"),
    "E-PRIZ-OZEL":(3,  "özel prizler"),
    "E-AYD":      (5,  "aydınlatma"),
    "E-ANAHTAR":  (5,  "anahtarlar"),
    "E-TABLO":    (1,  "tablolar"),
    "E-ZAYIF":    (6,  "zayıf akım"),
    "E-ACIL":     (1,  "acil aydınlatma"),
    "E-HATT":     (40, "linyeli hatlar"),
    "E-YAZI":     (7,  "elektrik yazıları"),
    "E-LEJANT":   (7,  "lejant+antet"),
}

def make_layers(doc):
    for name, (col, desc) in LAYERS.items():
        if name not in doc.layers:
            doc.layers.add(name, color=col)

# ----------------------------- SEMBOLLER ----------------------------------
def priz(msp, x, y, layer="E-PRIZ", ang=90):
    a = math.radians(ang)
    msp.add_circle((x, y), 7, dxfattribs={"layer": layer})
    x2, y2 = x + 9*math.cos(a), y + 9*math.sin(a)
    msp.add_line((x, y), (x2, y2), dxfattribs={"layer": layer})
    # toprak hattı çizgisi
    tx, ty = x2 + 4*math.cos(a+math.pi/2), y2 + 4*math.sin(a+math.pi/2)
    msp.add_line((x2 - 4*math.cos(a+math.pi/2), y2 - 4*math.sin(a+math.pi/2)),
                 (tx, ty), dxfattribs={"layer": layer})

def priz_etiket(msp, x, y, etiket, layer="E-PRIZ-OZEL", ang=90):
    priz(msp, x, y, layer, ang)
    t = msp.add_text(etiket, height=10, dxfattribs={"layer": layer})
    t.set_placement((x + 10, y - 4))

def lamba(msp, x, y, layer="E-AYD"):
    msp.add_circle((x, y), 7, dxfattribs={"layer": layer})
    d = 7/math.sqrt(2)
    msp.add_line((x-d, y-d), (x+d, y+d), dxfattribs={"layer": layer})
    msp.add_line((x-d, y+d), (x+d, y-d), dxfattribs={"layer": layer})

def anahtar(msp, x, y, kom=0, layer="E-ANAHTAR"):
    msp.add_circle((x, y), 2, dxfattribs={"layer": layer})
    a = math.radians(45)
    x2, y2 = x + 12*math.cos(a), y + 12*math.sin(a)
    msp.add_line((x, y), (x2, y2), dxfattribs={"layer": layer})
    n = 1 + (1 if kom else 0)
    for i in range(n):
        off = (i - (n-1)/2) * 4
        bx, by = x2 + off*math.cos(a), y2 + off*math.sin(a)
        msp.add_line((bx - 3*math.cos(a+math.pi/2), by - 3*math.sin(a+math.pi/2)),
                     (bx + 3*math.cos(a+math.pi/2), by + 3*math.sin(a+math.pi/2)),
                     dxfattribs={"layer": layer})

def tablo(msp, x, y, ad, layer="E-TABLO"):
    w, h = 26, 36
    p = [(x, y), (x+w, y), (x+w, y+h), (x, y+h), (x, y)]
    msp.add_lwpolyline(p, dxfattribs={"layer": layer})
    msp.add_line((x, y), (x+w, y+h), dxfattribs={"layer": layer})
    t = msp.add_text(ad, height=12, dxfattribs={"layer": layer})
    t.set_placement((x - 4, y - 18))

def zil(msp, x, y, layer="E-ZAYIF"):
    msp.add_arc((x, y+4), 8, 180, 360, dxfattribs={"layer": layer})
    msp.add_line((x-8, y+4), (x+8, y+4), dxfattribs={"layer": layer})

def buton(msp, x, y, layer="E-ZAYIF"):
    msp.add_circle((x, y), 3, dxfattribs={"layer": layer})

def zayif(msp, x, y, etiket, layer="E-ZAYIF"):
    msp.add_circle((x, y), 7, dxfattribs={"layer": layer})
    t = msp.add_text(etiket, height=8, dxfattribs={"layer": layer})
    t.set_placement((x + 9, y - 3))

def acil(msp, x, y, layer="E-ACIL"):
    lamba(msp, x, y, layer)
    t = msp.add_text("ACİL", height=8, dxfattribs={"layer": layer})
    t.set_placement((x + 9, y - 3))

def yaz(msp, x, y, s, h=12, layer="E-YAZI"):
    t = msp.add_text(s, height=h, dxfattribs={"layer": layer})
    t.set_placement((x, y))
    return t

def hatt(msp, pts, etiket=None, layer="E-HATT"):
    msp.add_lwpolyline(pts, dxfattribs={"layer": layer})
    if etiket:
        yaz(msp, pts[0][0]+6, pts[0][1]+6, etiket, 10, layer)

# --------------------------- DAİRE YERLEŞİMİ -------------------------------
def daire_symbols(msp, rooms, dt_xy, flip=False):
    """rooms: dict tip->(x,y). flip: sag daire icin yatay ofset ters."""
    sgn = -1 if flip else 1
    def O(cx, cy, dx, dy): return (cx + sgn*dx, cy + dy)

    sal = rooms["SALON"]; yat = rooms["YATAK"]; ban = rooms["BANYO"]; bal = rooms["BALKON"]
    sx, sy = sal; yx, yy = yat; bx, by = ban; kx, ky = bal

    # --- Salon+Mutfak ---
    priz(msp, *O(sx,sy,-80,-40)); priz(msp, *O(sx,sy,-80,40))
    priz(msp, *O(sx,sy,50,55)); priz(msp, *O(sx,sy,50,-55))
    zayif(msp, *O(sx,sy,-50,-60), "TV")
    lamba(msp, *O(sx,sy,-35,10)); lamba(msp, *O(sx,sy,35,10))
    priz_etiket(msp, *O(sx,sy,70,15), "")
    priz_etiket(msp, *O(sx,sy,70,-15), "")
    priz_etiket(msp, *O(sx,sy,85,45), "F")
    priz_etiket(msp, *O(sx,sy,85,-45), "ASP")
    anahtar(msp, *O(sx,sy,-95,75), kom=1)

    # --- Yatak ---
    priz(msp, *O(yx,yy,-55,-30)); priz(msp, *O(yx,yy,-55,30)); priz(msp, *O(yx,yy,55,-30))
    zayif(msp, *O(yx,yy,45,40), "TV")
    lamba(msp, yx, yy)
    anahtar(msp, *O(yx,yy,75,-55))

    # --- Banyo ---
    priz_etiket(msp, *O(bx,by,-30,-35), "CM")
    priz_etiket(msp, *O(bx,by,-30,35), "TS")
    priz_etiket(msp, *O(bx,by,40,30), "IP44")
    lamba(msp, bx, by)
    anahtar(msp, *O(bx,by,60,-55))

    # --- Balkon ---
    priz_etiket(msp, *O(kx,ky,-25,0), "IP44")
    lamba(msp, *O(kx,ky,25,0))
    anahtar(msp, *O(kx,ky,55,-30))

    # --- Antre / tablo / zil ---
    dx, dy = dt_xy
    tablo(msp, dx, dy, "DT")
    zil(msp, dx+40*sgn, dy+10)
    buton(msp, dx+52*sgn, dy+10)
    lamba(msp, dx+25*sgn, dy+30)
    anahtar(msp, dx+10*sgn, dy+45, kom=1)
    hatt(msp, [(dx+13*sgn, dy+18), (sx-20*sgn, sy-20)], "L1..L9")

ROOM_SETS = [
    (dict(SALON=(48994, -44900), YATAK=(48578, -44863),
          BANYO=(48804, -44877), BALKON=(48351, -44855)),
     (49120, -44500), False),
    (dict(SALON=(49363, -44527), YATAK=(49665, -44316),
          BANYO=(49257, -44313), BALKON=(49767, -44519)),
     (49300, -44750), True),
    (dict(SALON=(49082, -43350), YATAK=(48499, -43452),
          BANYO=(48764, -43404), BALKON=(48352, -43389)),
     (49150, -43700), False),
    (dict(SALON=(49360, -43717), YATAK=(49665, -43965),
          BANYO=(49278, -44026), BALKON=(49767, -43762)),
     (49300, -43600), True),
]

LEJANT = [
    ("priz", "2P+T TOPRAKLI PRIZ (300W)"),
    ("priz_ip44", "SPLASH KORUMALI PRIZ IP44"),
    ("priz_cm", "ÇAMAŞIR MAK. PRIZI (2000W)"),
    ("priz_firin", "FIRIN/OCAK PRIZI (3300W)"),
    ("priz_sofben", "TERMOSIFON/ŞOFBEN PRIZI"),
    ("tv", "TELEVIZYON PRIZI"),
    ("lamba", "ADI AYDINLATMA NOKTASI"),
    ("anahtar", "ADI ANAHTAR"),
    ("anahtar_k", "KOMÜTATÖR ANAHTAR"),
    ("tablo", "DAIRE DAGITIM TABLOSU (DT)"),
    ("zil", "KAPI ZILI / BUTON"),
    ("acil", "ACIL AYDINLATMA ARMATÜRÜ"),
]

def ciz_lejant(msp, x0, y0):
    yaz(msp, x0, y0+40, "ELEKTRİK SEMBOL LEJANTI (TS EN 60617)", 16, "E-LEJANT")
    y = y0
    for key, acik in LEJANT:
        if key == "priz": priz(msp, x0+10, y, "E-LEJANT")
        elif key == "priz_ip44": priz_etiket(msp, x0+10, y, "IP44", "E-LEJANT")
        elif key == "priz_cm": priz_etiket(msp, x0+10, y, "ÇM", "E-LEJANT")
        elif key == "priz_firin": priz_etiket(msp, x0+10, y, "F", "E-LEJANT")
        elif key == "priz_sofben": priz_etiket(msp, x0+10, y, "TS", "E-LEJANT")
        elif key == "tv": zayif(msp, x0+10, y, "TV", "E-LEJANT")
        elif key == "lamba": lamba(msp, x0+10, y, "E-LEJANT")
        elif key == "anahtar": anahtar(msp, x0+10, y, 0, "E-LEJANT")
        elif key == "anahtar_k": anahtar(msp, x0+10, y, 1, "E-LEJANT")
        elif key == "tablo": tablo(msp, x0+2, y-15, "", "E-LEJANT")
        elif key == "zil": zil(msp, x0+10, y, "E-LEJANT")
        elif key == "acil": acil(msp, x0+10, y, "E-LEJANT")
        yaz(msp, x0+35, y-5, acik, 11, "E-LEJANT")
        y -= 45

NOTLAR = [
    "1- Tesisat, Elektrik İç Tesisleri Yön. ve EMO Proje",
    "   Hazırlama Yön.'ne uygun yapılacaktır.",
    "2- Tüm prizler topraklı, 2P+T, çocuk korumalıdır.",
    "3- Banyo/balkon prizleri IP44, 30 mA kaçak akım",
    "   rölesi korumalıdır.",
    "4- Daire girişinde 30 mA hayat koruma rölesi",
    "   kullanılacaktır.",
    "5- Linye kesitleri: aydınlatma 1.5, priz 2.5 mm2.",
    "6- Kolon hesabı için yük cetveline bakınız.",
    "7- Banyo+mutfakta ek potansiyel dengeleme",
    "   yapılacaktır (Topraklamalar Yön.).",
    "8- Simetrik dairelerde tesisat aynen tekrarlanır.",
]

def ciz_antet(msp, x0, y0):
    p = [(x0, y0), (x0+700, y0), (x0+700, y0+180), (x0, y0+180), (x0, y0)]
    msp.add_lwpolyline(p, dxfattribs={"layer": "E-LEJANT"})
    yaz(msp, x0+15, y0+140, "PROJE: KONUT BINASI - ELEKTRIK İÇ TESİSATI", 16, "E-LEJANT")
    yaz(msp, x0+15, y0+105, "PAFTA: TIPİK KAT ELEKTRİK TESİSAT PLANI", 14, "E-LEJANT")
    yaz(msp, x0+15, y0+75, "ÖLÇEK: 1/50", 12, "E-LEJANT")
    yaz(msp, x0+15, y0+48, "STANDART: TS EN 60617 / TS IEC 60364 / EMO", 12, "E-LEJANT")
    yaz(msp, x0+15, y0+20, "TARİH: 2026 - ÇİZEN: ARENA AI", 12, "E-LEJANT")

def build():
    doc = ezdxf.readfile(SRC)
    msp = doc.modelspace()
    make_layers(doc)
    for rooms, dt, mir in ROOM_SETS:
        daire_symbols(msp, rooms, dt, flip=mir)
    ciz_lejant(msp, 62900, -43600)
    y = -44260
    for satir in NOTLAR:
        yaz(msp, 62900, y, satir, 11, "E-LEJANT")
        y -= 34
    ciz_antet(msp, 62900, -45350)
    doc.saveas(OUT)
    print("saved", OUT)

if __name__ == "__main__":
    build()
