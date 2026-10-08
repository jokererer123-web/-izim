# -*- coding: utf-8 -*-
"""
YÜK CETVELİ / HESAP RAPORU ÜRETİCİSİ
Elektrik İç Tesisleri Proje Hazırlama esaslarına göre:
  - Daire (mesken) yük cetveli
  - Daire dağıtım tablosu linye cetveli
  - Kat ve kolon (bina ana dağıtım) yük hesabı + eş zamanlılık
  - Ana besleme: akım, sigorta, kablo kesiti, trafo önerisi
Çıktılar: elektrik/hesap/YUK_CETVELI.xlsx, *.csv, HESAP_RAPORU.md
"""
import os, csv, math
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "elektrik", "hesap")
os.makedirs(BASE, exist_ok=True)

GUC = {
    "priz":300,"priz_ip44":300,"priz_cm":2000,"priz_bm":2200,"priz_firin":3300,
    "priz_sofben":1800,"priz_klima":1800,"priz_asp":150,"tv":20,"data":20,
    "lamba":100,"lamba_fl":120,"acil":60,"yon":10,"zil":30,
}

# Daire içi yükler: (mahal, yük tipi, adet, linye)
DAIRE_YUK = [
    ("SALON+MUTFAK","priz",4,"P1"),
    ("SALON+MUTFAK","tv",1,"P1"),
    ("SALON+MUTFAK","lamba",2,"A1"),
    ("SALON+MUTFAK","priz",2,"P3"),        # tezgah
    ("SALON+MUTFAK","priz_firin",1,"PF"),
    ("SALON+MUTFAK","priz_asp",1,"P3"),
    ("SALON+MUTFAK","priz_klima",1,"PK"),
    ("YATAK ODASI","priz",3,"P2"),
    ("YATAK ODASI","tv",1,"P2"),
    ("YATAK ODASI","lamba",1,"A1"),
    ("BANYO+WC","priz_cm",1,"PM"),
    ("BANYO+WC","priz_sofben",1,"PS"),
    ("BANYO+WC","priz_ip44",1,"A2"),
    ("BANYO+WC","lamba_fl",1,"A2"),
    ("BALKON","priz_ip44",1,"A2"),
    ("BALKON","lamba_fl",1,"A2"),
    ("ANTRE","lamba",1,"A1"),
    ("ANTRE","priz",1,"P1"),
    ("ANTRE","zil",1,"A1"),
]

LINYE = {
    "A1":("Aydinlatma linyesi","1.5 mm2 NV-B","B10"),
    "A2":("Islak mahal+balkon aydinlatma/priz","2.5 mm2 NV-B","B16"),
    "P1":("Priz linyesi (salon+antre)","2.5 mm2 NV-B","B16"),
    "P2":("Priz linyesi (yatak)","2.5 mm2 NV-B","B16"),
    "P3":("Mutfak tezgah+aspirator","2.5 mm2 NV-B","B16"),
    "PM":("Camasir makinesi","2.5 mm2 NV-B","B16"),
    "PF":("Firin/ocak","4 mm2 NV-B","C20"),
    "PS":("Sofben/termosifon","2.5 mm2 NV-B","B16"),
    "PK":("Klima","2.5 mm2 NV-B","B16"),
}

def talep_katsayisi(n):
    for lim,k in [(4,.90),(9,.75),(14,.65),(19,.58),(24,.52),(29,.48),(34,.45),(39,.42)]:
        if n<=lim: return k
    return .40

U_MONO, U_TRIF, COSFI = 220.0, 380.0, 0.92
TOPLAM_DAIRE = 34
ORTAK = [("Merdiven/ortak aydinlatma",800),("Asansor",7500),("Hidrofor",3000),
         ("Otopark aydinlatma+havalandirma",1500),("Siginak+yangin sistemleri",1200)]

def daire_hesap():
    """Daire yükleri ve linye toplamları."""
    mahal_rows=[]; linye_top={k:0 for k in LINYE}
    for mahal,tip,adet,lin in DAIRE_YUK:
        w=GUC[tip]; tot=w*adet
        mahal_rows.append((mahal,tip,adet,w,tot,lin))
        linye_top[lin]+=tot
    P_daire=sum(r[4] for r in mahal_rows)
    return mahal_rows, linye_top, P_daire

def stil(ws, row, ncols, header=False):
    thin=Side(style='thin', color='999999')
    for c in range(1,ncols+1):
        cell=ws.cell(row=row,column=c)
        cell.border=Border(left=thin,right=thin,top=thin,bottom=thin)
        cell.alignment=Alignment(vertical='center', wrap_text=True)
        if header:
            cell.font=Font(bold=True); cell.fill=PatternFill('solid', fgColor='DDEEFF')

def main():
    mahal_rows, linye_top, P_daire = daire_hesap()

    wb=openpyxl.Workbook()

    # ---------------- Sheet 1: DAIRE YUK CETVELI ----------------
    ws=wb.active; ws.title="DAIRE_YUK_CETVELI"
    hdr=["MAHAL","YÜK CİNSİ","ADET","BİRİM GÜÇ (W)","TOPLAM GÜÇ (W)","LİNYE"]
    ws.append(["KONUT (DAİRE) YÜK CETVELİ"])
    ws['A1'].font=Font(bold=True,size=13)
    ws.append(hdr); stil(ws,2,len(hdr),True)
    for r in mahal_rows:
        ws.append(list(r)); stil(ws,ws.max_row,len(hdr))
    ws.append(["TOPLAM BAĞLI GÜÇ (DAİRE)","","","","",P_daire])
    stil(ws,ws.max_row,len(hdr)); ws.cell(row=ws.max_row,column=6).font=Font(bold=True)
    for col,w in zip("ABCDEF",[20,26,8,16,16,8]): ws.column_dimensions[col].width=w

    # ---------------- Sheet 2: DAIRE TABLO CETVELI ----------------
    ws=wb.create_sheet("DAIRE_TABLO")
    ws.append(["DAİRE DAĞITIM TABLOSU (DT) LİNYE CETVELİ"])
    ws['A1'].font=Font(bold=True,size=13)
    hdr=["LİNYE","AÇIKLAMA","HESAP YÜKÜ (W)","SİGORTA","KABLO"]
    ws.append(hdr); stil(ws,2,len(hdr),True)
    for lin,(acik,kablo,sig) in LINYE.items():
        ws.append([lin,acik,linye_top.get(lin,0),sig,kablo]); stil(ws,ws.max_row,len(hdr))
    ws.append(["DAİRE GİRİŞİ","","", "40A + 30mA KAÇAK AKIM", "3x10 mm2 NV-B"])
    stil(ws,ws.max_row,len(hdr))
    for col,w in zip("ABCDE",[10,40,16,26,20]): ws.column_dimensions[col].width=w

    # ---------------- Sheet 3: KOLON / BINA ----------------
    ws=wb.create_sheet("KOLON_BINA")
    ws.append(["BİNA ANA DAĞITIM (KOLON) YÜK HESABI"])
    ws['A1'].font=Font(bold=True,size=13)
    ws.append(["Açıklama","Değer"])
    stil(ws,2,2,True)
    g=lambda a,b: (ws.append([a,b]), stil(ws,ws.max_row,2))
    P_ortak=sum(v for _,v in ORTAK)
    P_konut=TOPLAM_DAIRE*P_daire
    k=talep_katsayisi(TOPLAM_DAIRE)
    P_konut_hesap=P_konut*k
    P_toplam=P_konut_hesap+P_ortak
    I=P_toplam/(math.sqrt(3)*U_TRIF*COSFI)
    # kablo seçimi (Cu N2XH, ~0.4 A/mm2 yoğunluk)
    kesit = next((s for s in [35,50,70,95,120,150,185,240,300] if s*1.0>= I/1.6), 300)
    g("Daire sayısı", TOPLAM_DAIRE)
    g("Daire bağlı gücü (W)", round(P_daire,0))
    g("Konut toplam bağlı gücü (W)", round(P_konut,0))
    g("Eş zamanlılık katsayısı (n=%d)"%TOPLAM_DAIRE, k)
    g("Konut hesap gücü (W)", round(P_konut_hesap,0))
    g("Ortak mahal gücü (W)", P_ortak)
    g("TOPLAM HESAP GÜCÜ (W)", round(P_toplam,0))
    g("TOPLAM HESAP GÜCÜ (kW)", round(P_toplam/1000,1))
    g("Hesap akımı (A, 380V)", round(I,1))
    g("Ana şalter / sigorta", "%d A TMŞ + 300mA yangın koruma"%( (int(I/0.8)//50+1)*50 ))
    g("Ana besleme kablosu (Cu N2XH)", "4x(1x%d mm2)"%kesit)
    g("Önerilen trafo gücü (kVA)", 250 if P_toplam/1000/0.7<250 else 400)

    # ortak mahal alt listesi
    ws.append([]); ws.append(["ORTAK MAHAL LİSTESİ"]); 
    for a,b in ORTAK: ws.append([a,b])

    # ---------------- Sheet 4: LEJANT ----------------
    ws=wb.create_sheet("LEJANT")
    ws.append(["SEMBOL","AÇIKLAMA"])
    stil(ws,1,2,True)
    for s,a in [("2P+T priz","Topraklı priz 300W"),("IP44 priz","Sıçr.su korumalı"),
                ("ÇM","Çamaşır mak. prizi"),("F","Fırın prizi"),("TS","Termosifon"),
                ("TV","Televizyon prizi"),("X lamba","Aydınlatma noktası"),
                ("anahtar","Adi anahtar"),("komütatör","Komütatör"),("DT","Daire tablosu"),
                ("zil","Kapı zili"),("ACİL","Acil aydınlatma")]:
        ws.append([s,a])

    xlsx=os.path.join(BASE,"YUK_CETVELI.xlsx"); wb.save(xlsx)

    # CSV
    with open(os.path.join(BASE,"daire_yuk_cetveli.csv"),"w",newline="",encoding="utf-8-sig") as f:
        wcsv=csv.writer(f); wcsv.writerow(hdr)
        for r in mahal_rows: wcsv.writerow(r)
        wcsv.writerow(["TOPLAM","","","","",P_daire])
    with open(os.path.join(BASE,"kolon_bina.csv"),"w",newline="",encoding="utf-8-sig") as f:
        wcsv=csv.writer(f)
        wcsv.writerow(["Açıklama","Değer"])
        wcsv.writerow(["Daire sayısı",TOPLAM_DAIRE])
        wcsv.writerow(["Konut toplam bağlı gücü (W)",P_konut])
        wcsv.writerow(["Eş zamanlılık katsayısı",k])
        wcsv.writerow(["Konut hesap gücü (W)",round(P_konut_hesap)])
        wcsv.writerow(["Ortak mahal gücü (W)",P_ortak])
        wcsv.writerow(["TOPLAM HESAP GÜCÜ (kW)",round(P_toplam/1000,1)])
        wcsv.writerow(["Hesap akımı (A)",round(I,1)])

    # MD rapor
    md=f"""# ELEKTRİK İÇ TESİSATI – YÜK HESAP RAPORU

Standartlar: Elektrik İç Tesisleri Yönetmeliği, EMO Proje Hazırlama Yönetmeliği,
TS EN 60617, TS IEC 60364, Elektrik Tesislerinde Topraklamalar Yönetmeliği.

## Özet
| Büyüklük | Değer |
|---|---|
| Daire sayısı | {TOPLAM_DAIRE} |
| Daire bağlı gücü | {P_daire:.0f} W |
| Konut bağlı gücü | {P_konut:.0f} W |
| Eş zamanlılık katsayısı | {k} |
| Konut hesap gücü | {P_konut_hesap:.0f} W |
| Ortak mahal | {P_ortak} W |
| **Toplam hesap gücü** | **{P_toplam/1000:.1f} kW** |
| Hesap akımı (380 V) | {I:.1f} A |
| Ana şalter | {(int(I/0.8)//50+1)*50} A TMŞ + 300 mA |
| Ana kablo | 4x(1x{kesit} mm2) Cu N2XH |
| Trafo önerisi | {250 if P_toplam/1000/0.7<250 else 400} kVA |

Detaylar `YUK_CETVELI.xlsx` ve CSV dosyalarındadır.
"""
    open(os.path.join(BASE,"HESAP_RAPORU.md"),"w",encoding="utf-8").write(md)
    print("P_daire=",P_daire,"P_toplam_kW=",round(P_toplam/1000,1),"I=",round(I,1),"kesit=",kesit)

if __name__=="__main__":
    main()
