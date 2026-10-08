# -*- coding: utf-8 -*-
"""
ELEKTRİK İÇ TESİSATI - ORTAK TANIMLAR (Türk Standartları)
---------------------------------------------------------
Dayanak:
  * Elektrik İç Tesisleri Yönetmeliği
  * Elektrik İç Tesisleri Proje Hazırlama Yönetmeliği (EMO)
  * Elektrik Kuvvetli Akım Tesisleri Yönetmeliği
  * Elektrik Tesislerinde Topraklamalar Yönetmeliği
  * TS EN 60617 (Grafik semboller) / TS IEC 60364 serisi
  * TEDAĞ / dağıtım şirketi proje şartnameleri

Çizim birimi: mimari altlık santimetre (1 birim = 1 cm) olduğundan
tüm sembol/ölçü değerleri cm olarak verilmiştir.
"""

# ---------------------------------------------------------------------------
# Yük varsayımları (bağlı güç, W) - konut iç tesisatı tipik değerleri
# ---------------------------------------------------------------------------
GUC = {
    "priz":            300,   # 2P+T topraklı priz
    "priz_ip44":       300,   # sıçr su korumalı priz (banyo/traş)
    "priz_cm":        2000,   # çamaşır makinesi prizi
    "priz_bm":        2200,   # bulaşık makinesi prizi
    "priz_firin":     3300,   # fırın/ocak prizi (trifaze kabul, monofaze linye)
    "priz_sofben":    1800,   # şofben / termosifon
    "priz_klima":     1800,   # klima prizi
    "priz_asp":        150,   # aspirator / davlumbaz
    "tv":               20,
    "data":             20,
    "lamba":           100,   # adi aydınlatma noktası
    "lamba_fl":        120,   # banyo/balkon armatür
    "acil":             60,   # acil aydınlatma armatürü
    "yon":              10,   # yön levhası (kaçış)
    "zil":              30,   # kapı zili + buton
}

# Linye (devre) tanımları: ad -> (kablo kesiti mm2, sigorta A, tip)
LINYE = {
    "A1":  ("1.5 mm2 NV-B", 10, "B10", "Aydinlatma linyesi"),
    "A2":  ("1.5 mm2 NV-B", 10, "B10", "Aydinlatma linyesi (islak+balkon)"),
    "P1":  ("2.5 mm2 NV-B", 16, "B16", "Priz linyesi"),
    "P2":  ("2.5 mm2 NV-B", 16, "B16", "Priz linyesi"),
    "P3":  ("2.5 mm2 NV-B", 16, "B16", "Mutfak tezgah priz linyesi"),
    "PM":  ("2.5 mm2 NV-B", 16, "B16", "Beyaz esya prizleri (CM+BM)"),
    "PF":  ("4 mm2 NV-B",   20, "C20", "Firin/ocak linyesi"),
    "PS":  ("2.5 mm2 NV-B", 16, "B16", "Sofben/termosifon linyesi"),
    "PK":  ("2.5 mm2 NV-B", 16, "B16", "Klima linyesi"),
}

# Eş zamanlılık (talep) katsayıları - konut kolon hesabı (daire adedi -> katsayı)
# Elektrik İç Tesisleri Proje Hazırlama esasları / dağıtım şartnamelerinde
# kullanılan tipik değerlerdir.
def talep_katsayisi(n):
    if n <= 4:   return 0.90
    if n <= 9:   return 0.75
    if n <= 14:  return 0.65
    if n <= 19:  return 0.58
    if n <= 24:  return 0.52
    if n <= 29:  return 0.48
    if n <= 34:  return 0.45
    if n <= 39:  return 0.42
    return 0.40

# Gerilim ve güç katsayısı
U_MONO = 220.0     # V (faz-notr)
U_TRIF = 380.0     # V
COSFI  = 0.92

# Bina verisi (mimari projeden okunmuştur)
KAT_ADI   = ["BODRUM", "ZEMIN", "1-7.KAT(x7)", "8.KAT", "9.KAT", "10.KAT"]
DAIRE_KAT = 4
# toplam daire (mimari projedeki alan tablosunda 34-36 daire okunmaktadır)
TOPLAM_DAIRE = 34

# Ortak mahal yükleri (W)
ORTAK = [
    ("Merdiven/ortak aydinlatma", 800),
    ("Asansor",                  7500),
    ("Hidrofor",                 3000),
    ("Otopark aydinlatma+hav.",  1500),
    ("Siginak+yangin sistemleri",1200),
]
