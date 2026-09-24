# Karar kuralları

Kurallar koşullu tarama yapar. Hiçbir kural klinik güvenliği kanıtlamaz. `Kxx`
kimlikleri kaynak kataloğuna gider; doğrudan kaynak taşımayan kurallar yazılımın
veri sözleşmesi veya mühendislik ihtiyatıdır.

## Beş hareketin on çifti

| Birleşim | Varsayılan sonuç | Yorum |
|---|---|---|
| Öteleme + rotasyon | Uzman incelemesi | Sınırlı üst molar distalizasyon istisnası koşullu aday |
| Öteleme + tip | Uzman incelemesi | Kron hareketi gövdesel hareket sayılmaz |
| Öteleme + tork | Uzman incelemesi | Kök kontrolü ve dönme merkezi gerekli |
| Öteleme + intrüzyon | Uzman incelemesi | Yön, oran ve vaka düzeni önemli |
| Rotasyon + tip | Uzman incelemesi | İstenmeyen devrilme ayrılmalı |
| Rotasyon + tork | Ayırmayı değerlendir | Doğrulanmamış ihtiyat politikası |
| Rotasyon + intrüzyon | Uzman incelemesi | Yan etki yararlı sinerji sayılmaz |
| Tip + tork | Uzman incelemesi | İki açısal hedef kök kontrolünü kanıtlamaz |
| Tip + intrüzyon | Uzman incelemesi | Görünür ve gerçek intrüzyon ayrılmalı |
| Tork + intrüzyon | Uzman incelemesi | Dikey ve kök kontrolü birlikte incelenmeli |

Üç veya daha fazla hareket ayırmayı değerlendirme üretir. Sırayı otomatik seçmez;
bazı telafi mekaniklerini birbirinden ayırmak da sakıncalı olabileceği için bir
“önce rotasyon, sonra tork” reçetesi üretmez. Aşama sayısı veya tedavi süresi hesaplamaz.

## Sayısal tarama

| Ölçüt | Varsayılan eşik | Köken |
|---|---:|---|
| Yatay ötelemenin iki bileşenli normu | 0.20 mm | Mühendislik ihtiyatı |
| Rotasyon | 1.0° | Mühendislik ihtiyatı |
| Tip | 1.0° | Bildirilen protokol değerinden tarama eşiği; doğrulanmış güvenlik sınırı değil |
| Tork hedef açısı | 1.0° | Bildirilen protokol değerinden tarama eşiği; doğrulanmış güvenlik sınırı değil |
| İntrüzyon | 0.15 mm | Mühendislik ihtiyatı |
| Doğrusal bileşke | 0.25 mm | Literatürdeki aşama değerine dayalı tarama |
| Normalize kareler toplamı | 1.0 | Tamamen mühendislik sezgiseli |

`q = (öteleme/0.20)^2 + (rotasyon/1.0)^2 + (tip/1.0)^2 + (tork/1.0)^2 + (intrüzyon/0.15)^2`

`q` bir kuvvet/stres modeli, enerji hesabı, biyolojik risk olasılığı veya başarı
yüzdesi değildir. Birden fazla hareketin kendi eşiklerinin altında olmasına
rağmen toplam talebin incelemeye yönlendirilmesini sağlar. Eşik aşılması
`ayirma_degerlendirilmeli` üretir; eşik altında kalmak klinik onay vermez.

Öteleme ve intrüzyonun normu, açı değişimlerinden kaynaklanan yüzey hareketlerini
içermez. Doğrusal miktar ile açısal miktar doğrudan toplanmaz. Girdideki sayısal
üst sınırlar sözleşme sınırıdır; tedavi dozu önerisi değildir.

## Kural izleri

| Kod | Denetim |
|---|---|
| A01 | Eksik ark bildirimi |
| A02 | Ankraj, plak oturması, kök değerlendirmesi veya materyal protokolü |
| A03 | Ön ve arka segmentte birlikte intrüzyon |
| A04 | Tüm gönderilen dişlerin aktif olması |
| A05 | Çekimli vaka bağlamı |
| A06 | Posterior distalizasyon ve anterior tork birlikteliği |
| D01–D03 | Eksik klinik veri, bildirilen risk veya azalmış destek |
| D04–D05 | Ataşman planı belirsizliği / yardımcı mekanik incelemesi |
| D06–D08 | Tekil eşik, doğrusal bileşke ve normalize talep |
| D09 | Üç ve üzeri aktif hareket |
| D10–D11 | Kanin/premolar rotasyonu ve toplam rotasyon büyüklüğü |
| D12 | Kök veya dikey kontrol gerektiren hareket |

Hareket varlığı sıfırdan farklı değerle belirlenir; küçük hareketler sessizce
yok sayılmaz. Eşik karşılaştırmasındaki `1e-12` toleransı yalnız kayan nokta
yuvarlaması içindir. Pasif dişler de sağlık/temas/kök bulguları bakımından değerlendirilir.

---

© 2026 FlowCognition by suvilab.com — Özel yazılım. Yazılı izin olmadan kullanılamaz.
