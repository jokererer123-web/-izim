# ELEKTRİK İÇ TESİSAT PROJESİ

`MIMARI+PROJE_recover.dwg` mimari projesi üzerinden üretilmiştir.
DWG dosyası bu ortamda doğrudan açılamadığı için LibreDWG (WASM) ile
DXF'e dönüştürülmüş (`dwg/MIMARI_PROJE.dxf`), ardından mimari altlık
üzerine elektrik iç tesisat planı çizilmiştir.

## İçerik
| Dosya | Açıklama |
|---|---|
| `dwg/MIMARI_PROJE.dxf` | Mimari projenin DXF dönüşümü |
| `cizim/ELEKTRIK_TESISAT_PLANI_TIP_KAT.dxf` | Tipik kat elektrik tesisat planı (katmanlı) |
| `cizim/output/ELEKTRIK_TESISAT_PLANI_TIP_KAT.png/pdf` | Plan görüntüsü |
| `cizim/output/LEJANT_VE_NOTLAR.png` | Sembol lejantı + teknik notlar + antet |
| `hesap/YUK_CETVELI.xlsx` | Yük cetveli (daire, tablo, kolon/bina) |
| `hesap/daire_yuk_cetveli.csv`, `kolon_bina.csv` | CSV çıktıları |
| `hesap/HESAP_RAPORU.md` | Hesap özeti |
| `index.html` | Tarayıcı önizleme sayfası |

## Dayanak Standartlar
- Elektrik İç Tesisleri Yönetmeliği
- Elektrik İç Tesisleri Proje Hazırlama Yönetmeliği (EMO)
- Elektrik Kuvvetli Akım Tesisleri Yönetmeliği
- Elektrik Tesislerinde Topraklamalar Yönetmeliği
- TS EN 60617 (grafik semboller), TS IEC 60364 serisi

## Katmanlar (elektrik)
`E-PRIZ`, `E-PRIZ-OZEL`, `E-AYD`, `E-ANAHTAR`, `E-TABLO`, `E-ZAYIF`,
`E-ACIL`, `E-HATT`, `E-YAZI`, `E-LEJANT`

## Yeniden üretim
```
python3 ../tools/build_elektrik.py   # DXF planı üretir
python3 ../tools/render_elec.py ...  # PNG/PDF görüntü
python3 ../tools/yuk_cetveli.py      # yük cetveli
python3 ../tools/make_web.py         # önizleme sayfası
```
