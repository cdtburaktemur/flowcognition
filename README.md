# FlowCognition 
Şeffaf plak dental CAD sistemleri için geliştirilen özel yazılım modülleri.

## Modüller

- [Combined Movement Reasoning · Birleşik hareket değerlendirmesi](combined-movement-reasoning/README.md): öteleme, rotasyon, tip, tork ve intrüzyon için araştırma amaçlı karar desteği; klinik güvenlik onayı vermez.
- [Movement Budget Solver · Hareket bütçesi çözücüsü](movement-budget-solver/README.md): diş ve hareket tipine göre stage bütçesi, birleşik hareket, ankraj sıralaması ve CAD/BVH denetimi.

## Başlangıç

Python 3.11 veya üzeriyle, depo kökünden:

```powershell
cd combined-movement-reasoning
python -m birlesik_hareket sun
```

Arayüz: [Yerel uygulama](http://127.0.0.1:8765/).
Kurulum, test ve CAD bağlantısı için modülün kullanım kılavuzuna bakın.

Movement Budget Solver için:

```powershell
cd movement-budget-solver
python -m unittest discover -s testler -v
python -m hareket_butcesi sun --port 8766
```

**Açık kaynak değildir. Hak sahibinin yazılı izni olmadan kullanılamaz.**
Koşullar [LICENSE](LICENSE) dosyasındadır.

© 2026 FlowCognition by suvilab.com — Tüm hakları saklıdır.
