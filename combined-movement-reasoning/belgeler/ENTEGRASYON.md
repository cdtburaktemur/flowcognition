# CAD entegrasyon sözleşmesi

## Bağlantı seçenekleri

Bu belgedeki komutlar ve göreli dosya yolları `combined-movement-reasoning/`
klasörünü temel alır. Depo kökünden `cd combined-movement-reasoning` ile geçin.

Python içinde ağ olmadan:

```python
from pathlib import Path
from birlesik_hareket import degerlendir
from birlesik_hareket.dogrulama import json_oku

istek = json_oku(Path("birlesik_hareket/veri/ornek.json").read_text(encoding="utf-8"))
sonuc = degerlendir(istek)
print(sonuc["durum"])
```

C++, C#, JavaScript veya diğer CAD ortamlarından yerel HTTP:

```powershell
$asamaVerisi = Get-Content -LiteralPath birlesik_hareket/veri/ornek.json -Raw -Encoding UTF8
Invoke-RestMethod -Uri http://127.0.0.1:8765/api/v1/degerlendir -Method Post -ContentType 'application/json; charset=utf-8' -Body ([Text.Encoding]::UTF8.GetBytes($asamaVerisi))
```

| Uç nokta | İşlev |
|---|---|
| `POST /api/v1/degerlendir` | Tek aşamanın karar desteği çıktısı |
| `GET /api/v1/sema` | JSON Schema 2020-12 girdi sözleşmesi |
| `GET /api/v1/bilgi` | Politika, hareket çiftleri ve kaynak kataloğu |
| `GET /api/v1/ornek` | Sentetik üst çene örneği |

HTTP 200 geçerli değerlendirme demektir; klinik uygunluk değildir. 422 geçersiz girdi,
413 fazla büyük gövde, 415 yanlış içerik türü, 403 yanlış köken/adres, 404 bilinmeyen
yol demektir. İstek üst sınırı 256 KiB'dır. Sonuç dosyasında `klinik_onay` ve
`otomatik_uygulama` daima `false` değerindedir. Hata alanı Türkçe açıklama taşır.

## Birimler ve yönler

Sözleşme sürümü `1.0`; koordinat etiketi `dis_yerel_klinik_v1` olmalıdır.
Bu etiket bir global XYZ matrisi veya Euler dönüş sırası tanımlamaz. Hareketler
CAD tarafından dişe özgü anatomik referanslardan çıkarılmış **klinik bileşenlerdir**.

| Alan | Birim | Pozitif / negatif anlamı |
|---|---|---|
| `otelemenin_mesial_bileseni_mm` | mm | Mesial / distal gövdesel hedef öteleme |
| `otelemenin_bukkal_bileseni_mm` | mm | Bukkal / lingual-palatal gövdesel hedef öteleme |
| `rotasyon_derece` | derece | Oklüzalden köke bakıldığında saat yönü / tersi |
| `tip_derece` | derece | Kronun mesial / distal açı değişimi |
| `tork_derece` | derece | Kronun bukkal / lingual açı değişimi; izole kök torku garantisi değil |
| `intruzyon_mm` | mm | Apikal doğrultuda pozitif; negatif değer desteklenmez |

Mesial, bukkal ve apikal anatomik yönleri her kadranda yeniden kurulmalıdır.
Bu klinik işaretler bir sağ elli XYZ dönüş sistemi gibi doğrudan kullanılmamalıdır.
Öteleme, dönme pivotunun hareketiyle ikinci kez sayılmamalıdır. Dönmelerin kron
ve kökteki doğrusal etkilerini hesaplamak CAD geometrisinin görevidir.

Mevcut motor dönüş matrisi ayrıştırmaz veya tekrar birleştirmez. CAD uyarlayıcısı,
kendi pivot, kök ekseni ve dönüş sırası sözleşmesini ayrıca korumalı ve sağ/sol,
üst/alt kadranlarda referans örneklerle test etmelidir. Geçersiz etiketi reddetmek
yanlış birimle doğru etiket gönderilmesini saptamaz; birim doğrulaması üreticide
de yapılmalıdır. İki çene iki ayrı istekle gönderilir; çeneler arası temas kontrolü
ana CAD uygulamasında kalır.

## Klinik ve geometrik bağlam

Her mevcut daimi diş tek FDI kaydıyla gönderilir; pasif hareketler sıfırdır. Eksik
dişler eklenmez. `tam_ark` gönderenin tüm mevcut dişleri kapsadığı beyanıdır;
motor diş envanterini kendi başına bilemez. Aynı FDI iki kez kabul edilmez.

`temas_yolu=uygun` yalnız son konum değil hareket yolu boyunca CAD temas kontrolünün
tamamlandığını ifade eder. `kok_kemik=uygun` kökler, kemik sınırları ve planlanan yolun
klinik/geometrik değerlendirmesini temsil eder. Motor mesh işlemi yapmaz.
`kok_degerlendirmesi` ilgili klinik kök değerlendirmesinin tamamlandığı beyanıdır;
otomatik CBCT çekimi önermez.

`atasman=planli` yalnız bir planın mevcut olduğunu söyler; şekil, konum ve etkinliğini
onaylamaz. `materyal_protokolu` kullanılan plak materyali, üretim, kesim hattı ve
takma protokolünün vaka bağlamında değerlendirildiğini belirtir. Bilinmeyen değerler
`bilinmiyor` olarak gönderilmeli, varsayılan “uygun” değerleriyle doldurulmamalıdır.

## Sonuç tüketimi

Önce aşama düzeyindeki `durum`, ardından `ark_bulgulari` ve tüm dişler okunmalıdır.
Dişe ait koşullu aday sonucu, aşama genelindeki engeli geçersiz kılamaz.
Öncelik: engellendi > veri yetersiz > ayırma değerlendirmesi > uzman incelemesi >
koşullu aday > hareket yok. Daha düşük öncelikli gerekçeler çıktıda korunur.

`girdi_ozeti` ve `bilgi_tabani_ozeti` SHA-256 içerik özetleridir; dijital imza,
kimlik doğrulama veya erişim kontrolü değildir. Girdi sırası ve sayı gösterimindeki
farklar özeti değiştirebilir. Klinik kayda sonuçla birlikte tam girdi, motor sürümü,
uzman değerlendirmesi ve kullanılan geometri revizyonu kaydedilmelidir. Bu servis
bunları otomatik saklamaz.

## Dağıtım

Yerel sunucu geliştirme içindir; yalnız `127.0.0.1` üzerinde çalışır. CORS açmaz,
gövde günlüğü tutmaz, değerlendirmeleri diske yazmaz. Kimlik doğrulaması, çok
kullanıcılı yetki kontrolü ve kalıcı kayıt sağlamaz. Üretim CAD entegrasyonunda
Python çekirdeğini süreç içinden çağırın veya kurumun yetkilendirilmiş servis
altyapısına alın. Yerel HTTP sunucusunu doğrudan internete açmayın.

Paket veri dosyaları tekerlek dağıtımına dahildir. `araclar/sozlesme_uret.py` örnek
ve şemayı yeniden üretir; değiştirilmiş sözleşme için doğrulayıcı, şema ve testler
birlikte güncellenmelidir. Eşik veya kaynak değişikliği politika sürümünü arttırmalı
ve klinik değerlendirmeden geçmelidir.

---

© 2026 FlowCognition by suvilab.com — Özel yazılım. Yazılı izin olmadan kullanılamaz.
