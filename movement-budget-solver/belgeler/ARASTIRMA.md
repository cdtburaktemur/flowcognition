# Araştırma ve kanıt özeti

**© 2026 FlowCognition by suvilab.com**

Bu belge, Movement Budget Solver kurallarının hangi kanıt sınıflarıyla ilişkilendirildiğini açıklar. Literatür heterojendir; tabloda bulunan eşikler klinik protokol yerine başlangıç mühendislik parametreleri olarak değerlendirilmelidir.

## İncelenen güncel kaynaklar

| Kod | Kaynak | Solver'a etkisi |
|---|---|---|
| M01 | [Almeida ve ark., 2025, rotasyon sistematik derlemesi](https://doi.org/10.3390/dj13100440) | Rotasyon doğruluğunun geniş aralıkta değiştiğini, kanin ve premolarlarda öngörülebilirliğin daha düşük olabildiğini gösterir. |
| M02 | [Zhang ve ark., 2025, kuvvet odaklı otomatik staging](https://doi.org/10.3390/bioengineering12020111) | 0,25 mm adımlı iteratif staging yaklaşımının araştırma yönünü destekler; klinik doğrulama gerektirir. |
| M03 | [Altıntaş ve ark., 2025, alt keser intrusion derlemesi](https://doi.org/10.3390/jcm14176339) | Intrusion için tek bir başarı oranı yerine belirsizlik ve düşük öngörülebilirlik gösterimi gerektirir. |
| M04 | [Kravitz ve ark., attachment tasarımı RCT](https://pubmed.ncbi.nlm.nih.gov/37610383/) | Attachment etkisinin hareket tipine ve tasarıma bağlı olduğunu destekler. |
| M05 | [Houle ve ark., 2021, wear protokolü RCT](https://pubmed.ncbi.nlm.nih.gov/33296455/) | 7/10/14 günlük kullanım etkisinin hareket ve protokole göre değiştiğini gösterir. |
| M06 | [Papadimitriou ve ark., 2024, wear protokolü sistematik derlemesi](https://doi.org/10.1093/ejo/cjae020) | Kullanım süresini sabit katsayıya çevirmeden vaka girdisi olarak saklama gereğini destekler. |
| M07 | [Molar distalizasyon sistematik derlemesi, 2026](https://doi.org/10.3390/jcm15145568) | Distalizasyonun ankraj ve hareket sıralamasıyla birlikte ele alınmasını destekler. |
| M08 | [Refinement sistematik derlemesi, 2026](https://pubmed.ncbi.nlm.nih.gov/42442043/) | İlk plan ile gerçekleşen hareket arasındaki geri beslemenin ayrı bir katman olmasını destekler. |

## Uygulama ilkeleri

1. `preferred`, `warning` ve `maximum` eşikleri birbirinden ayrılır.
2. Hareket yükü ile öngörülebilirlik ayrı alanlardır; düşük yük güvenilirlik garantisi değildir.
3. Birleşik hareketler ağırlık ve coupling katsayılarıyla değerlendirilir; katsayılar `EXPERT_RULE` olarak işaretlenir ve kurum içi verilerle kalibre edilmelidir.
4. Çarpışma, temas, ankraj ve geometri denetimi başarısızsa stage otomatik olarak klinik onaylanmış sayılmaz.
5. Literatürde desteklenmeyen hasta özelinde kesin sonuçlar üretilmez.

## Kaynak kataloğu

Makale kimlikleri ve kanıt güven düzeyleri `hareket_butcesi/veri/kaynaklar.json` içindedir. Yeni bir kural eklenirken en azından kaynak, yıl, çalışma tipi ve güven düzeyi girilmelidir.

© 2026 FlowCognition by suvilab.com
