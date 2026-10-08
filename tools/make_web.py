# -*- coding: utf-8 -*-
"""elektrik/web/index.html önizleme sayfasını üretir."""
import os, csv

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "elektrik")

def read_csv(p):
    with open(p, encoding="utf-8-sig") as f:
        return list(csv.reader(f))

daire = read_csv(os.path.join(BASE, "hesap", "daire_yuk_cetveli.csv"))
kolon = read_csv(os.path.join(BASE, "hesap", "kolon_bina.csv"))

def table(rows):
    h = "<table><tr>" + "".join(f"<th>{c}</th>" for c in rows[0]) + "</tr>"
    for r in rows[1:]:
        h += "<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>"
    return h + "</table>"

html = f"""<!doctype html>
<html lang="tr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Konut Binası - Elektrik İç Tesisatı</title>
<style>
body{{font-family:Segoe UI,Arial,sans-serif;margin:0;background:#f4f6f8;color:#222}}
header{{background:#0b3d66;color:#fff;padding:18px 28px}}
header h1{{margin:0;font-size:22px}} header p{{margin:4px 0 0;opacity:.85}}
main{{max-width:1200px;margin:0 auto;padding:20px}}
.card{{background:#fff;border-radius:10px;box-shadow:0 1px 4px rgba(0,0,0,.15);padding:18px;margin:18px 0}}
img{{max-width:100%;border:1px solid #ddd;border-radius:6px;background:#fff}}
table{{border-collapse:collapse;width:100%;font-size:14px}}
th,td{{border:1px solid #cfd8e3;padding:6px 10px;text-align:left}}
th{{background:#e8f0fa}}
h2{{color:#0b3d66;font-size:18px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}
@media(max-width:900px){{.grid{{grid-template-columns:1fr}}}}
</style></head><body>
<header><h1>KONUT BİNASI – ELEKTRİK İÇ TESİSAT PROJESİ</h1>
<p>TİPİK KAT TESİSAT PLANI (1/50) • YÜK CETVELİ • TS EN 60617 / TS IEC 60364 / EMO</p></header>
<main>
<div class="card"><h2>1. Tipik Kat Elektrik Tesisat Planı</h2>
<img src="cizim/output/ELEKTRIK_TESISAT_PLANI_TIP_KAT.png" alt="Elektrik tesisat planı"></div>
<div class="card"><h2>2. Sembol Lejantı ve Teknik Notlar</h2>
<img src="cizim/output/LEJANT_VE_NOTLAR.png" alt="Lejant ve notlar"></div>
<div class="card"><h2>3. Yük Cetveli</h2>
<div class="grid">
<div><h2 style="font-size:15px">Daire Yük Cetveli</h2>{table(daire)}</div>
<div><h2 style="font-size:15px">Bina / Kolon Hesabı</h2>{table(kolon)}</div>
</div></div>
<div class="card"><h2>Dosyalar</h2>
<ul>
<li><code>cizim/ELEKTRIK_TESISAT_PLANI_TIP_KAT.dxf</code> – elektrik planı (AutoCAD)</li>
<li><code>dwg/MIMARI_PROJE.dxf</code> – mimari altlık (DWG'den dönüştürülmüş)</li>
<li><code>hesap/YUK_CETVELI.xlsx</code> – yük cetveli (Excel)</li>
<li><code>hesap/HESAP_RAPORU.md</code> – hesap raporu</li>
</ul></div>
</main></body></html>"""

out = os.path.join(BASE, "index.html")
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, "w", encoding="utf-8").write(html)
print("saved", out)
