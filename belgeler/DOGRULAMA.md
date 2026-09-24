# Doğrulama ve sınırlar

## Yazılım denetimleri

`python -m unittest discover -s testler -v` ile çekirdek ve gerçek yerel HTTP
soketi üzerinden sözleşme testleri çalıştırılır. Testler; on çiftin kapsamı,
çoklu hareket, yön ve diş bağlamı, eksik veri, risk önceliği, pasif ankraj dişleri,
toplam rotasyon, norm hesabı, bozuk/tekrarlı alanlar, sonlu olmayan sayılar,
FDI, tek çene, HTTP gövde/başlık sınırları ve deterministik çıktıyı kapsar.

Sentetik örnekler gerçek hasta kayıtları değildir. Testlerin geçmesi klinik
etkinlik, biyouyumluluk, hasta güvenliği veya mevzuata uygunluk kanıtı değildir.

25 Eylül 2026 yerel denetim kaydı: Windows üzerinde Python 3.13.1 ile 37 test
başarılı oldu. Paket oluşturuldu ve paket içindeki örnek/veri dosyalarıyla
değerlendirme çalıştırıldı. Tarayıcıda sentetik örneğin koşullu aday sonucu,
rotasyon miktarı artırıldığında ayırma incelemesine geçiş ve girdi değiştiğinde
önceki sonucun indirilmesinin engellenmesi doğrulandı. JavaScript sözdizimi
denetimi geçti. GitHub iş akışı eklendi; uzak iş akışı bu oturumda çalıştırılmadı.

## Klinik kullanımdan önce tamamlanacak işler

1. Kullanım amacı, kullanıcı rolü ve hedef hasta grubunu sorumlu uzmanla belirleyin.
2. Kuralları bağımsız ortodontist ve biyomekanik uzmanlarına körlenmiş vakalarla
   değerlendirtin. Yanlış koşullu aday sonuçlarını ayrıca inceleyin.
3. CAD uyarlayıcısında birim, pivot, anatomik eksen ve dönüş işaretlerini her kadran
   için doğrulayın; gerçek kök/kemik ve tüm yol temas denetimlerini bağlayın.
4. Materyal, kesim hattı, ataşman ve takma protokolüne göre ayrı doğrulama yapın.
5. Eşikleri klinik sonuç verisiyle kalibre edin; aynı hasta veya kliniğin kayıtlarını
   eğitim ve doğrulama gruplarına karıştırmayın. Bağımsız dış doğrulama kullanın.
6. Gerçekleşen hareket, refinman gereksinimi, kök ve periodontal sonuçlar gibi
   ölçütleri önceden tanımlayın. Güvenlik değerlendirmesini yalnız kron doğruluğuna
   indirgemeyin. Prospektif değerlendirme ve gerekli etik süreçleri tamamlayın.
7. Hedef pazara ve kullanım amacına göre ürünün düzenleyici durumunu, kalite
   süreçlerini ve insan denetimini ayrıca değerlendirin.

## Bilinen kapsam boşlukları

Ekstrüzyon, süt/karma dişlenme, çeneler arası kuvvetler, kök rezorpsiyonu ölçümü,
hasta uyumu ölçümü, kök şekli ve kemiğin sayısal geometrisi modellenmez. Tam ark ve
uygun klinik durum işaretleri beyana dayanır. Aygıt varlığı otomatik ankraj yeterliliği
sayılmaz. Tork girdisi gerçek kuvvet momenti değildir. Motor hasta hareketinin
zaman içindeki gerçekleşmesini veya malzemenin gevşemesini simüle etmez.

Kaynak listesi güncellendikçe mevcut kuralların geçerliliği yeniden incelenmelidir.
Bir çalışmanın daha yeni olması, eski klinik bulgulardan daha yüksek kanıt
kesinliğine sahip olduğunu göstermez.

---

© 2026 FlowCognition by suvilab.com — Özel yazılım. Yazılı izin olmadan kullanılamaz.
