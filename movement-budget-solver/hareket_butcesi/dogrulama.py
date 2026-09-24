# © 2026 FlowCognition by suvilab.com — Tüm hakları saklıdır.
"""Birim, kapsam ve tür doğrulaması; bilinmeyen alanlar reddedilir."""

import json
import math

EKSENLER = ("md_mm", "bl_mm", "ie_mm", "rotasyon_derece", "tip_derece", "tork_derece")


class GirdiHatasi(ValueError):
    """Sözleşmeye uymayan veri."""


def nesne(deger, zorunlu, istege_bagli=(), ad="girdi"):
    if type(deger) is not dict:
        raise GirdiHatasi(f"{ad}: nesne bekleniyor.")
    eksik = set(zorunlu) - deger.keys()
    fazla = deger.keys() - set(zorunlu) - set(istege_bagli)
    if eksik or fazla:
        raise GirdiHatasi(f"{ad}: eksik {sorted(eksik)}, bilinmeyen {sorted(fazla)}.")


def sayi(deger, alt, ust, ad):
    if type(deger) not in (int, float) or not alt <= deger <= ust or not math.isfinite(deger):
        raise GirdiHatasi(f"{ad}: {alt}–{ust} aralığında sonlu sayı bekleniyor.")


def tam_sayi(deger, alt, ust, ad):
    if type(deger) is not int or not alt <= deger <= ust:
        raise GirdiHatasi(f"{ad}: {alt}–{ust} aralığında tam sayı bekleniyor.")


def metin(deger, ad):
    if not isinstance(deger, str) or not deger.strip() or len(deger) > 200:
        raise GirdiHatasi(f"{ad}: boş olmayan, en fazla 200 karakterli metin bekleniyor.")


def secim(deger, degerler, ad):
    if not isinstance(deger, str) or deger not in degerler:
        raise GirdiHatasi(f"{ad}: {degerler} değerlerinden biri bekleniyor.")


def mantik(deger, ad):
    if type(deger) is not bool:
        raise GirdiHatasi(f"{ad}: true veya false bekleniyor.")


def fdi_dogrula(fdi):
    if type(fdi) is not int or fdi // 10 not in (1, 2, 3, 4) or fdi % 10 not in range(1, 9):
        raise GirdiHatasi("FDI daimi diş numarası olmalı.")


def dis_grubu(fdi):
    fdi_dogrula(fdi)
    return "keser" if fdi % 10 <= 2 else "kanin" if fdi % 10 == 3 else "premolar" if fdi % 10 <= 5 else "molar"


def hareket_dogrula(hareket):
    nesne(hareket, EKSENLER, ad="hareket")
    for ad in EKSENLER:
        sayi(hareket[ad], -30 if ad.endswith("mm") else -179, 30 if ad.endswith("mm") else 179, ad)


def dis_dogrula(dis):
    nesne(dis, ("fdi", "hareket", "atasman", "periodontal", "kok", "komsu_temas", "okluzal_temas", "destek_disleri", "kilitli"), ("donusum",), "diş")
    fdi_dogrula(dis["fdi"])
    hareket_dogrula(dis["hareket"])
    secim(dis["atasman"], ("yok", "planli", "bilinmiyor"), "ataşman")
    secim(dis["periodontal"], ("normal", "azalmis", "aktif_hastalik", "bilinmiyor"), "periodontal")
    for ad in ("kok", "okluzal_temas"):
        secim(dis[ad], ("uygun", "riskli", "bilinmiyor"), ad)
    secim(dis["komsu_temas"], ("uygun", "dar", "riskli", "bilinmiyor"), "komşu temas")
    mantik(dis["kilitli"], "kilitli")
    if type(dis["destek_disleri"]) is not list:
        raise GirdiHatasi("destek_disleri liste olmalı.")
    for fdi in dis["destek_disleri"]:
        fdi_dogrula(fdi)
    if len(set(dis["destek_disleri"])) != len(dis["destek_disleri"]) or dis["fdi"] in dis["destek_disleri"]:
        raise GirdiHatasi("Destek dişleri tekil olmalı ve diş kendisini destek saymamalı.")


def istek_dogrula(istek):
    nesne(istek, ("surum", "vaka_kimligi", "koordinat", "geometri_revizyonu", "tam_ark", "ankraj", "strateji", "azami_asama", "disler"))
    secim(istek["surum"], ("1.0",), "sürüm")
    secim(istek["koordinat"], ("suvi_yerel_v1",), "koordinat")
    metin(istek["vaka_kimligi"], "vaka kimliği")
    metin(istek["geometri_revizyonu"], "geometri revizyonu")
    mantik(istek["tam_ark"], "tam ark")
    secim(istek["ankraj"], ("uzman_degerlendirdi", "yetersiz", "bilinmiyor"), "ankraj")
    secim(istek["strateji"], ("paralel", "distal_yuzde50"), "strateji")
    tam_sayi(istek["azami_asama"], 1, 500, "azami aşama")
    if type(istek["disler"]) is not list or not 1 <= len(istek["disler"]) <= 16:
        raise GirdiHatasi("Tek ark için 1–16 diş bekleniyor.")
    for dis in istek["disler"]:
        dis_dogrula(dis)
    kimlikler = [d["fdi"] for d in istek["disler"]]
    if len(kimlikler) != len(set(kimlikler)) or len({f // 10 <= 2 for f in kimlikler}) != 1:
        raise GirdiHatasi("FDI tekil ve tek çeneye ait olmalı.")
    for dis in istek["disler"]:
        if not set(dis["destek_disleri"]) <= set(kimlikler):
            raise GirdiHatasi("Destek dişlerinin tamamı ark girdisinde yer almalı.")


def json_oku(ham):
    def ciftler(ogeler):
        sonuc = {}
        for ad, deger in ogeler:
            if ad in sonuc:
                raise GirdiHatasi(f"Yinelenen JSON alanı: {ad}.")
            sonuc[ad] = deger
        return sonuc

    def sabit(deger):
        raise GirdiHatasi(f"Sonlu olmayan sayı: {deger}.")

    try:
        return json.loads(ham, object_pairs_hook=ciftler, parse_constant=sabit)
    except GirdiHatasi:
        raise
    except (ValueError, UnicodeError, RecursionError) as hata:
        raise GirdiHatasi("Geçerli UTF-8 JSON bekleniyor.") from hata
