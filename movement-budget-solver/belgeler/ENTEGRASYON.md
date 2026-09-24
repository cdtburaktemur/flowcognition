# CAD ve staging entegrasyonu

**© 2026 FlowCognition by suvilab.com**

## Python API

```python
from hareket_butcesi.cozucu import planla

sonuc = planla(istek, geometri_denetçisi=denetçi)
```

`istek` JSON şemasına uygun sözlüktür. `denetçi`, aday stage özeti alıp şu alanları döndürebilir:

```json
{
  "durum": "gecti",
  "penetrasyon_mm": 0.0,
  "temaslar": []
}
```

`gecti`, `bilinmiyor` ve `kaldi` durumları desteklenir. `cad-koprusu/denetci.mjs`, gerçek CAD/BVH çağrısını bu sözleşmeye uyarlamak için örnek adaptördür.

## HTTP API

`python -m hareket_butcesi sun --port 8766` komutuyla:

- `GET /api/v1/bilgi`
- `GET /api/v1/politika`
- `GET /api/v1/ornek`
- `POST /api/v1/planla`
- `POST /api/v1/geri-bildirim`

uçları açılır. İstemci ve sunucu aynı özel veri sözleşmesini kullanır; paket adı ve API adresleri değişmez.

## CAD döngüsü

`planla` aday stage'i üretir, dış denetçiye verir ve yalnızca `gecti` sonucu gelen adımı kabul eder. Çarpışma veya temas sorunu görülürse hareket küçültülür ya da sonraki stage'e aktarılır. Solver otomatik IPR, attachment veya expansion kararı uygulamaz; bunları açıklama ve öneri katmanına bırakır.

© 2026 FlowCognition by suvilab.com
