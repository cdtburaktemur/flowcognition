# © 2026 FlowCognition by suvilab.com — Tüm hakları saklıdır.
"""Refinman ölçümlerinin betimsel özeti; otomatik öğrenme veya kural güncellemez."""

from .dogrulama import GirdiHatasi, EKSENLER, nesne, metin, hareket_dogrula, fdi_dogrula


def geri_bildirim_ozeti(kayit):
    nesne(kayit, ("anonim_vaka", "fdi", "politika_surumu", "olcum_yontemi", "planlanan", "gerceklesen"))
    for ad in ("anonim_vaka", "politika_surumu", "olcum_yontemi"):
        metin(kayit[ad],ad)
    fdi_dogrula(kayit["fdi"])
    hareket_dogrula(kayit["planlanan"])
    hareket_dogrula(kayit["gerceklesen"])
    sonuc = {}
    for ad in EKSENLER:
        plan, gercek = kayit["planlanan"][ad],kayit["gerceklesen"][ad]
        sonuc[ad] = {"isaretli_gerceklesme_orani":None if plan == 0 else gercek/plan,
                     "mutlak_hata":abs(gercek-plan), "ters_yon":plan*gercek<0}
    return {"fdi":kayit["fdi"],"olcumler":sonuc,"otomatik_kalibrasyon":False,
            "aciklama":"Oranlar kırpılmadı; sıfır hedefte oran tanımsızdır. Ölçüm yöntemi ve kayıt hizalaması ayrıca doğrulanmalı."}
