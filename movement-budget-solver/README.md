# Movement Budget Solver

**© 2026 FlowCognition by suvilab.com**

Bu klasör, Suvi Flow otomatik staging motorunun hareket bütçesi ve birleşik hareket karar katmanıdır. Modül; diş tipini, hareket yönünü, attachment durumunu, temas/periodontal koşulları ve aynı stage içindeki hareketlerin birleşik yükünü birlikte değerlendirir.

Bu yazılım **özel mülktür**. Açık kaynak değildir; FlowCognition by suvilab.com tarafından yazılı izin verilmeden kopyalanamaz, dağıtılamaz, değiştirilemez veya ticari/klinik bir üründe kullanılamaz. Lisans koşulları için [LICENSE](LICENSE) dosyasına bakın.

## Kurulum ve kullanım

Python 3.11 veya üzeri gerekir. Modül klasöründe:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m unittest discover -s testler -v
python -m hareket_butcesi planla hareket_butcesi/veri/ornek.json --cikti dist/ornek-sonuc.json
```

Yerel arayüzü başlatmak için:

```powershell
python -m hareket_butcesi sun --host 127.0.0.1 --port 8766
```

CAD entegrasyonu için `cad-koprusu/denetci.mjs` içindeki adaptör, gerçek mesh/BVH denetleyicisinin `durum`, `penetrasyon_mm` ve `temaslar` alanlarını döndürmesiyle çalışır. Solver; geometri denetlenmeden klinik olarak tamamlanmış bir plan üretmez.

## Tasarım sınırları

Politika değerleri başlangıç mühendislik eşikleridir; evrensel biyolojik sabit veya hasta özelinde klinik garanti değildir. Her kuralın kanıt kaydı `hareket_butcesi/veri/kaynaklar.json` içinde tutulur. Kaynak özeti ve uygulama sınırlamaları [belgeler/ARASTIRMA.md](belgeler/ARASTIRMA.md) dosyasındadır.

FEM, kuvvet/moment çözümü, otomatik IPR, attachment tasarımı ve klinik onay bu sürümün dışında bırakılmıştır. Bunlar için solver açıklamasında öneri üretilebilir; otomatik uygulama yapmaz.

## Dosya yapısı

- `hareket_butcesi/`: Python paketi ve HTTP arayüzü
- `hareket_butcesi/veri/`: politika, kaynak kataloğu, örnek istek ve JSON şeması
- `cad-koprusu/`: CAD/BVH denetleyici adaptörü
- `araclar/`: örnek istek ve şema üretim araçları
- `testler/`: birim ve entegrasyon testleri
- `belgeler/`: araştırma, karar kuralları, CAD entegrasyonu ve doğrulama belgeleri

© 2026 FlowCognition by suvilab.com
