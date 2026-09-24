# Doğrulama

**© 2026 FlowCognition by suvilab.com**

Modül klasöründe aşağıdaki kontroller çalıştırılmalıdır:

```powershell
python -m unittest discover -s testler -v
python -m pip wheel . --no-deps --wheel-dir dist
python -m hareket_butcesi planla hareket_butcesi/veri/ornek.json --cikti dist/ornek-sonuc.json
node --check hareket_butcesi/arayuz/uygulama.js
```

Testler; kural doğrulamasını, tek ve birleşik hareket bütçesini, ankraj sıralamasını, geometri ayrıştırmasını, quaternion normalizasyonunu, stale CAD denetçisi reddini ve geri bildirim özetini kapsar.

Paketleme çıktıları `dist/` altında tutulur ve Git'e alınmaz. Örnek planın `geometri_bekleniyor` durumunda kalması beklenen davranıştır; gerçek CAD/BVH denetçisi bağlanmadan plan klinik olarak tamamlanmış sayılmaz.

© 2026 FlowCognition by suvilab.com
