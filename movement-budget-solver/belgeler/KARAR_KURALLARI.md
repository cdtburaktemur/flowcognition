# Karar kuralları

**© 2026 FlowCognition by suvilab.com**

Solver'ın karar akışı şöyledir:

1. Final setup, diş bazında MD/BL/IE, rotasyon, tip ve tork bileşenlerine ayrılır.
2. Diş grubu ve hareket yönü için temel bütçe seçilir.
3. Attachment, hareket büyüklüğü, temas, periodontal destek ve temas/çarpışma koşulları katsayı olarak uygulanır.
4. Her hareketin yükü `abs(planlanan) / preferred` ile hesaplanır.
5. Ağırlıklı birleşik yük ve hareket çiftlerinin coupling cezası hesaplanır.
6. `warning` veya `maximum` sınırı aşılırsa hareket sonraki stage'e aktarılır.
7. Ankraj bağımlılıkları ve opsiyonel CAD/BVH denetimi uygulanır.
8. Denetim bilinmiyorsa sonuç `geometri_bekleniyor`, hata varsa `denetci_hatasi` durumunda kalır.

## Durumlar

- `hazir`: Geometri denetimi yapılmadan oluşturulmuş taslak.
- `geometri_bekleniyor`: CAD/BVH sonucu gerekli veya denetim sonucu belirsiz.
- `geometri_denetimli_taslak`: Tüm aday stage'ler dış denetçiden geçti; klinik onay yerine geçmez.
- `asama_siniri`: İzin verilen maksimum stage sayısı aşıldı.
- `engellendi`: Ankraj veya zorunlu bağımlılık nedeniyle hareket ilerletilemedi.
- `denetci_hatasi`: CAD/BVH adaptörü hata verdi ya da eski aday gönderildi.
- `veri_yetersiz`: Girdi veya hareket ekseni doğrulanamadı.

`distal_yuzde50` stratejisi, distal ark hareketini iki faza bölerek ankrajı korumaya yönelik başlangıç sıralamasıdır. Bu, klinik protokol önerisi değildir ve kurum içi doğrulama olmadan otomatik seçilmemelidir.

© 2026 FlowCognition by suvilab.com
