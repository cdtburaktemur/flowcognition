# © 2026 FlowCognition by suvilab.com — Tüm hakları saklıdır.
"""Deterministik, sınırlandırılmış aşama paketleme ve dış geometri geri beslemesi."""

from copy import deepcopy
import math
from typing import Protocol

from .dogrulama import GirdiHatasi, EKSENLER, istek_dogrula, nesne, metin, mantik, secim
from .geometri import hareket_ayristir, poz_hesapla
from .kurallar import kurallari_yukle, politika_dogrula, etkin_butce, asama_yuku, asama_tahmini, ongorulebilirlik, ozet, veri_oku


class GeometriDenetcisi(Protocol):
    """CAD tüm aday yolu, kökleri, komşuları ve karşıt arkı kontrol eder."""

    def __call__(self, aday: dict) -> dict:
        """Aday özeti ve geometri revizyonuna bağlı denetim yanıtı döndürür."""
        ...


def denetim_dogrula(yanit, aday, kimlikler):
    nesne(yanit, ("durum", "aday_ozeti", "geometri_revizyonu", "yol_denetlendi", "sorunlu_disler", "denetci", "aciklama"), ad="geometri yanıtı")
    secim(yanit["durum"], ("uygun", "carpisma", "bilinmiyor"), "geometri durumu")
    metin(yanit["denetci"], "denetçi")
    metin(yanit["aciklama"], "denetim açıklaması")
    mantik(yanit["yol_denetlendi"], "yol denetlendi")
    if yanit["aday_ozeti"] != aday["aday_ozeti"] or yanit["geometri_revizyonu"] != aday["geometri_revizyonu"]:
        raise GirdiHatasi("Eski veya farklı geometri denetim yanıtı reddedildi.")
    if type(yanit["sorunlu_disler"]) is not list or any(type(f) is not int or f not in kimlikler for f in yanit["sorunlu_disler"]):
        raise GirdiHatasi("Geometri yanıtındaki dişler arkta bulunmalı.")
    if yanit["durum"] == "uygun" and (not yanit["yol_denetlendi"] or yanit["sorunlu_disler"]):
        raise GirdiHatasi("Geçerli sonuç için tüm yol denetlenmeli ve sorunlu diş bulunmamalı.")
    return deepcopy(yanit)


def planla(istek, politika=None, geometri_denetçisi: GeometriDenetcisi | None = None):
    """Taslak ya da dış denetimli sayısal plan üretir; klinik onay vermez.

    Her diş sabit başlangıç-hedef yolu üzerinde ilerler. İlerleme azalmaz.
    CAD onayı olmayan aşamalar yalnız taslak sayılır, otomatik uygulanmaz.
    """
    istek_dogrula(istek)
    istek = deepcopy(istek)
    p = kurallari_yukle() if politika is None else politika_dogrula(politika)
    disler = sorted(istek["disler"], key=lambda d: d["fdi"])
    for dis in disler:
        if "donusum" in dis:
            ayrisim = hareket_ayristir(dis["donusum"])
            if any(abs(ayrisim[ad]-dis["hareket"][ad]) > 1e-6 for ad in EKSENLER):
                raise GirdiHatasi(f"{dis['fdi']}: hareket ile başlangıç/hedef dönüşümleri uyuşmuyor.")
        if math.sqrt(sum(dis["hareket"][ad]**2 for ad in EKSENLER[3:])) >= 180:
            raise GirdiHatasi("Toplam dönme vektörü 180 dereceden küçük olmalı; uzun yol ayrı segmentlerle tanımlanmalı.")
    butceler = {d["fdi"]: etkin_butce(d,p) for d in disler}
    tahminler = {d["fdi"]: asama_tahmini(d["hareket"],butceler[d["fdi"]],p) for d in disler}
    aktif_hedef = {d["fdi"] for d in disler if any(v != 0 for v in d["hareket"].values())}
    ilerleme = {d["fdi"]: 0. if d["fdi"] in aktif_hedef else 1. for d in disler}
    sonuc = {"surum":"1.0", "motor_surumu":"0.1.0", "telif":"2026 FlowCognition by suvilab.com",
             "vaka_kimligi":istek["vaka_kimligi"], "durum":"taslak", "klinik_onay":False, "otomatik_uygulama":False,
             "tamamlandi":False, "geometri_dogrulandi":False, "girdi_ozeti":ozet(istek), "politika_ozeti":ozet(p),
             "politika_surumu":p["surum"], "kaynak_tabani_ozeti":ozet(veri_oku("kaynaklar.json")),
             "aciklama":"Mühendislik bütçesi; kuvvet/stres veya biyolojik güvenlik hesabı değildir.",
             "disler":[], "asamalar":[], "olaylar":[], "bulgular":[], "kalan_hareketler":{}}
    for dis in disler:
        fdi = dis["fdi"]
        kayit = {"fdi":fdi, "butceler":butceler[fdi], "tahmin":tahminler[fdi], "ongorulebilirlik":ongorulebilirlik(dis), "atasman_senaryosu":None}
        if dis["atasman"] == "yok" and any(dis["hareket"][ad] != 0 for ad in ("rotasyon_derece", "tork_derece")) or dis["atasman"] == "yok" and dis["hareket"]["ie_mm"] < 0:
            karsilastirma = deepcopy(dis)
            karsilastirma["atasman"] = "planli"
            diger = asama_tahmini(dis["hareket"], etkin_butce(karsilastirma,p), p)
            kayit["atasman_senaryosu"] = {"mevcut_tahmin":tahminler[fdi]["birlesik_yol_tahmini"], "planli_atasman_tahmini":diger["birlesik_yol_tahmini"], "hekim_incelemesi":True, "otomatik_ekleme":False, "aciklama":"Aynı mühendislik politikasında varsayımsal karşılaştırma; klinik kazanç veya ataşman tasarımı önerisi değildir."}
        sonuc["disler"].append(kayit)
    sonuc["ark_alt_siniri"] = max(t["sert_limit_alt_siniri"] for t in tahminler.values())
    sonuc["ark_birlesik_yol_tahmini"] = max(t["birlesik_yol_tahmini"] for t in tahminler.values())

    def bitir(durum):
        sonuc["durum"] = durum
        sonuc["asama_sayisi"] = len(sonuc["asamalar"])
        sonuc["kalan_hareketler"] = {str(d["fdi"]): {ad: d["hareket"][ad]*(1-ilerleme[d["fdi"]]) for ad in EKSENLER} for d in disler if ilerleme[d["fdi"]] < 1-1e-12}
        sonuc["tamamlandi"] = not sonuc["kalan_hareketler"]
        sonuc["geometri_dogrulandi"] = bool(sonuc["asamalar"]) and sonuc["tamamlandi"] and all(a["geometri"]["durum"] == "uygun" for a in sonuc["asamalar"])
        return sonuc

    if not aktif_hedef:
        return bitir("hareket_yok")
    eksik, risk = [], []
    if not istek["tam_ark"]:
        eksik.append("Tam ark ve pasif diş envanteri gerekli.")
    if istek["ankraj"] == "bilinmiyor":
        eksik.append("Ankraj değerlendirmesi eksik.")
    elif istek["ankraj"] == "yetersiz":
        risk.append("Ankraj yetersiz olarak bildirildi.")
    for dis in disler:
        for ad in ("periodontal", "kok", "komsu_temas", "okluzal_temas"):
            if dis[ad] == "bilinmiyor":
                eksik.append(f"{dis['fdi']}: {ad} bilinmiyor.")
            if dis[ad] in ("aktif_hastalik", "riskli"):
                risk.append(f"{dis['fdi']}: {ad} riskli.")
        if dis["fdi"] in aktif_hedef and dis["atasman"] == "bilinmiyor":
            eksik.append(f"{dis['fdi']}: ataşman planı eksik.")
        if dis["fdi"] in aktif_hedef and dis["kilitli"]:
            risk.append(f"{dis['fdi']}: kilitli diş için sıfır olmayan hedef.")
        if dis["periodontal"] == "azalmis":
            sonuc["bulgular"].append(f"{dis['fdi']}: azaltılmış bütçe uzman değerlendirmesinin yerine geçmez.")
    sonuc["bulgular"].extend(risk+eksik)
    if risk or eksik:
        return bitir("engellendi" if risk else "veri_yetersiz")
    onceki = {}
    if istek["strateji"] == "distal_yuzde50":
        for kadran in range(1,5):
            zincir = sorted([d["fdi"] for d in disler if d["fdi"]//10 == kadran and d["hareket"]["md_mm"] < 0], reverse=True)
            onceki.update({son:ilk for ilk,son in zip(zincir,zincir[1:])})

    for numara in range(1,istek["azami_asama"]+1):
        if all(ilerleme[f] >= 1-1e-12 for f in aktif_hedef):
            return bitir("geometri_denetimli_taslak" if geometri_denetçisi else "geometri_bekleniyor")
        secilen, korunacak = {}, set()
        # Az ilerlemiş diş önce seçilir; eşitlikte posterior diş önceliklidir.
        sirali = sorted(disler, key=lambda d:(ilerleme[d["fdi"]], -(d["fdi"]%10), d["fdi"]))
        for dis in sirali:
            fdi = dis["fdi"]
            if fdi not in aktif_hedef or ilerleme[fdi] >= 1-1e-12 or fdi in korunacak:
                continue
            if fdi in onceki and ilerleme[onceki[fdi]] < .5-1e-12:
                continue
            if set(dis["destek_disleri"]) & secilen.keys():
                continue
            secilen[fdi] = min(1-ilerleme[fdi],tahminler[fdi]["azami_ilerleme"])
            korunacak.update(dis["destek_disleri"])
        if len(secilen) == len(disler):
            # Pasif diş olmadan basit dişsel ankraj modeli ilerleyemez.
            secilen.pop(next(reversed(secilen)))
        if not secilen:
            sonuc["bulgular"].append("Sıralama/ankraj kısıtları ilerlemeye izin vermiyor.")
            return bitir("cozum_bulunamadi")
        kabul = None
        for deneme in range(p["en_fazla_yeniden_deneme"]+1):
            if not any(v > 1e-12 for v in secilen.values()):
                break
            aday = {"numara":numara, "geometri_revizyonu":istek["geometri_revizyonu"], "politika_ozeti":sonuc["politika_ozeti"], "disler":[], "ankraj":{"aktif_disler":sorted(secilen), "destek_disleri":[d["fdi"] for d in disler if d["fdi"] not in secilen], "kilitli_disler":[d["fdi"] for d in disler if d["kilitli"]], "ankraj_skoru":None, "aciklama":"Pasiflik ve açık destek bağımlılıkları kontrol edilir; fiziksel ankraj kapasitesi hesaplanmaz."}}
            for dis in disler:
                fdi = dis["fdi"]
                artis = secilen.get(fdi,0.)
                hedef = min(1.,ilerleme[fdi]+artis)
                pay = {ad:dis["hareket"][ad]*(hedef-ilerleme[fdi]) for ad in EKSENLER}
                oge = {"fdi":fdi, "baslangic_ilerleme":ilerleme[fdi], "bitis_ilerleme":hedef, "hareket":pay, "yuk":asama_yuku(pay,butceler[fdi],p), "baslangic_pozu":None, "bitis_pozu":None}
                if "donusum" in dis:
                    oge.update(baslangic_pozu=poz_hesapla(dis["donusum"],ilerleme[fdi]), bitis_pozu=poz_hesapla(dis["donusum"],hedef))
                if oge["yuk"]["durum"] != "butce_icinde":
                    raise GirdiHatasi("İç tutarsızlık: üretilen aday bütçe dışında.")
                aday["disler"].append(oge)
            aday["aday_ozeti"] = ozet(aday)
            if geometri_denetçisi is None:
                denetim = {"durum":"bilinmiyor", "aciklama":"CAD/BVH denetçisi bağlı değil; aday yalnız mühendislik taslağıdır."}
            else:
                try:
                    denetim = denetim_dogrula(geometri_denetçisi(deepcopy(aday)),aday,{d["fdi"] for d in disler})
                except Exception as hata:
                    sonuc["bulgular"].append("Geometri denetçisi başarısız veya geçersiz yanıt verdi; aday ilerletilmedi.")
                    sonuc["olaylar"].append({"asama":numara,"tur":"denetci_hatasi","hata_turu":type(hata).__name__})
                    return bitir("denetci_hatasi")
                if denetim["durum"] == "bilinmiyor":
                    sonuc["bulgular"].append(denetim["aciklama"])
                    return bitir("geometri_bekleniyor")
                if denetim["durum"] == "carpisma":
                    sorunlu = set(denetim["sorunlu_disler"]) & secilen.keys() or set(secilen)
                    sonuc["olaylar"].append({"asama":numara,"tur":"carpisma","deneme":deneme,"aday_ozeti":aday["aday_ozeti"],"disler":sorted(sorunlu),"aciklama":denetim["aciklama"]})
                    if deneme >= p["en_fazla_yeniden_deneme"]//2 and len(secilen)>1:
                        ertelenen = max(sorunlu)
                        secilen.pop(ertelenen)
                        sonuc["olaylar"].append({"asama":numara,"tur":"erteleme","fdi":ertelenen})
                    else:
                        for fdi in sorunlu:
                            secilen[fdi] *= p["kucultme_orani"]
                    continue
            kabul = {**aday,"geometri":denetim}
            break
        if kabul is None:
            sonuc["bulgular"].append("Çarpışma için sınırlı küçültme/erteleme araması tükendi. Alternatif yol veya temas düzenlemesi hekimce incelenmeli; otomatik IPR/ekspansiyon uygulanmadı.")
            return bitir("cozum_bulunamadi")
        sonuc["asamalar"].append(kabul)
        for oge in kabul["disler"]:
            ilerleme[oge["fdi"]] = oge["bitis_ilerleme"]
    if all(ilerleme[f]>=1-1e-12 for f in aktif_hedef):
        return bitir("geometri_denetimli_taslak" if geometri_denetçisi else "geometri_bekleniyor")
    sonuc["bulgular"].append("Azami aşama sınırı aşıldı; kalan hareket ayrı raporlandı.")
    return bitir("asama_siniri")
