# FlowCognition · Birleşik Hareket Akıl Yürütme

Şeffaf plak CAD sistemlerinde aynı aşamada planlanan öteleme, rotasyon, tip,
tork ve intrüzyonu değerlendiren Türkçe karar destek modülü.

**Özel yazılımdır; açık kaynak değildir. Hak sahibinin yazılı izni olmadan
kullanılamaz.** Koşullar [LICENSE](LICENSE) dosyasındadır.

## Mevcut sürüm

0.1.0 bir araştırma ve entegrasyon başlangıç sürümüdür. Klinik doğrulama yapılmamıştır.
Motor “güvenlidir” onayı vermez. Koşullu aday, uzman incelemesi, ayırmayı değerlendirme,
veri yetersizliği veya engelleme sonucu üretir. Sayısal eşikler biyolojik güvenlik
sınırı değildir. Kaynaklar, kural gerekçeleri ve mühendislik varsayımları ayrıdır.

- Beş hareket türünün on ikili birleşimi ve çoklu hareket denetimi.
- Diş bazında FDI numarası, yön, büyüklük, toplam rotasyon ve klinik bağlam.
- Pasif dişlerin riskleri, anterior/posterior intrüzyon ve ankraj uyarıları.
- Sürümlü JSON sözleşmesi, Python arayüzü, komut satırı ve yerel HTTP servisi.
- Türkçe web arayüzü, kaynak listesi ve sonuç indirme.
- Yinelenen alan, yanlış eksen, belirsiz veri, sonlu olmayan sayı ve birim denetimi.
- Deterministik girdi/bilgi tabanı özetleri ve kaynak kimlikleri.

## Çalıştırma

Python 3.11 veya üzeri yeterlidir. Çekirdeğin çalışma zamanı bağımlılığı yoktur.
Depo kökünden önce modül klasörüne geçin:

```powershell
cd combined-movement-reasoning
```

Aşağıdaki tüm komutları `combined-movement-reasoning/` klasöründe çalıştırın:

```powershell
python -m birlesik_hareket sun
```

Tarayıcıda **http://127.0.0.1:8765/** adresini açın. Durdurmak için Ctrl+C kullanın.
Sentetik örnek tüm mevcut üst dişleri içerir; üçüncü molarlar bu örnekte yoktur.
Örnekteki “uygun” alanlarını gerçek hasta verisi kabul etmeyin.

Komut satırından:

```powershell
python -m birlesik_hareket degerlendir birlesik_hareket/veri/ornek.json --cikti sonuc.json
python -m unittest discover -s testler -v
```

Yetkili geliştirme ortamında paket kurulumu:

```powershell
python -m pip install .
birlesik-hareket sun
```

Hareket girdileri **tek aşamaya** aittir. `toplam_rotasyon_derece` tüm planın
mutlak rotasyon büyüklüğüdür. Ekstrüzyon, süt dişleri ve iki çenenin tek istekte
değerlendirilmesi bu sürümün kapsamı dışındadır.

## Belgeler

- [Araştırma ve kanıt sınırları](belgeler/ARASTIRMA.md)
- [CAD entegrasyonu ve koordinat sözleşmesi](belgeler/ENTEGRASYON.md)
- [Karar kuralları ve eşikler](belgeler/KARAR_KURALLARI.md)
- [Doğrulama ve klinik kullanıma geçiş](belgeler/DOGRULAMA.md)
- [Kaynak kataloğu](birlesik_hareket/veri/kaynaklar.json)
- [Makinece okunabilir girdi şeması](birlesik_hareket/veri/istek.sema.json)

Araştırma tarihi: **25 Eylül 2026**. Seçilmiş birincil klinik, laboratuvar ve
sonlu eleman çalışmaları ile derlemeler incelenmiştir. Bütün makalelerin eksiksiz
incelendiği iddia edilmez; erişim düzeyi her kaynak kaydında belirtilir.

Bu modül STL/CBCT segmentasyonu, gerçek çarpışma testi, kuvvet çözümü, periodontal
stres hesaplaması veya tamamlanmış tedavi aşamaları üretmez. Bunlar CAD ve klinik
doğrulama katmanlarının sorumluluğundadır. Klinik değerlendirme alanları kullanıcı
beyanıdır; yazılım bunları bağımsız ölçmüş sayılmaz.

---

© 2026 FlowCognition by suvilab.com — Özel yazılım. Yazılı izin olmadan kullanılamaz.
