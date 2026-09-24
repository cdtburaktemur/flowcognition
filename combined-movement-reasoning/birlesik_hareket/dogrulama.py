# Telif hakkı © 2026 FlowCognition by suvilab.com — Tüm hakları saklıdır.
"""CAD sınırında kapalı sözleşme ve sonlu sayı denetimi."""

import json
import math


class GirdiHatasi(ValueError):
    """Geçersiz veya kapsam dışı istek."""


def nesne(deger, alanlar, yol, zorunlu=None):
    if not isinstance(deger, dict):
        raise GirdiHatasi(f"{yol}: nesne olmalı.")
    fazla = set(deger) - set(alanlar)
    eksik = set(alanlar if zorunlu is None else zorunlu) - set(deger)
    if fazla or eksik:
        raise GirdiHatasi(f"{yol}: bilinmeyen alanlar {sorted(fazla)}, eksik alanlar {sorted(eksik)}.")


def secim(deger, secenekler, yol):
    if not isinstance(deger, str) or deger not in secenekler:
        raise GirdiHatasi(f"{yol}: izin verilen değerler {list(secenekler)}.")


def sayi(deger, alt, ust, yol):
    if type(deger) not in (int, float) or not alt <= deger <= ust or not math.isfinite(deger):
        raise GirdiHatasi(f"{yol}: {alt} ile {ust} arasında sonlu sayı olmalı.")


def mantik(deger, yol):
    if type(deger) is not bool:
        raise GirdiHatasi(f"{yol}: true veya false olmalı.")


def metin(deger, yol):
    if not isinstance(deger, str) or not deger.strip() or len(deger) > 120:
        raise GirdiHatasi(f"{yol}: 1–120 karakterlik metin olmalı.")


def json_oku(metin_degeri):
    def ciftler(alanlar):
        sonuc = {}
        for ad, deger in alanlar:
            if ad in sonuc:
                raise GirdiHatasi(f"Yinelenen JSON alanı: {ad}.")
            sonuc[ad] = deger
        return sonuc

    def sabit(deger):
        raise GirdiHatasi(f"Sonlu olmayan JSON sayısı: {deger}.")

    try:
        return json.loads(metin_degeri, object_pairs_hook=ciftler, parse_constant=sabit)
    except GirdiHatasi:
        raise
    except (ValueError, UnicodeDecodeError, RecursionError) as hata:
        raise GirdiHatasi("Geçerli UTF-8 JSON bekleniyor.") from hata


HAREKET_ALANLARI = ("otelemenin_mesial_bileseni_mm", "otelemenin_bukkal_bileseni_mm",
                    "rotasyon_derece", "tip_derece", "tork_derece", "intruzyon_mm")
DIS_ALANLARI = ("fdi", "hareket", "periodontal", "kok_kemik", "temas_yolu",
               "atasman", "toplam_rotasyon_derece")
BAGLAM_ALANLARI = ("tam_ark", "ankraj", "plak_oturmasi", "kok_degerlendirmesi",
                  "materyal_protokolu", "cekimli_vaka")


def dogrula(istek):
    nesne(istek, ("sozlesme_surumu", "asama_kimligi", "koordinat_sistemi", "baglam", "disler"), "istek")
    secim(istek["sozlesme_surumu"], ("1.0",), "sozlesme_surumu")
    secim(istek["koordinat_sistemi"], ("dis_yerel_klinik_v1",), "koordinat_sistemi")
    metin(istek["asama_kimligi"], "asama_kimligi")
    baglam = istek["baglam"]
    nesne(baglam, BAGLAM_ALANLARI, "baglam")
    for alan in ("tam_ark", "cekimli_vaka"):
        mantik(baglam[alan], alan)
    for alan in ("ankraj", "kok_degerlendirmesi", "materyal_protokolu"):
        secim(baglam[alan], ("uygun", "yetersiz", "bilinmiyor"), alan)
    secim(baglam["plak_oturmasi"], ("uygun", "uyumsuz", "bilinmiyor"), "plak_oturmasi")
    disler = istek["disler"]
    if not isinstance(disler, list) or not 1 <= len(disler) <= 32:
        raise GirdiHatasi("disler: 1–32 eleman içermeli.")
    gorulen = set()
    for dis in disler:
        nesne(dis, DIS_ALANLARI, "diş")
        fdi = dis["fdi"]
        if type(fdi) is not int or fdi // 10 not in (1, 2, 3, 4) or fdi % 10 not in range(1, 9):
            raise GirdiHatasi("fdi: daimi diş numarası (11–48, geçerli kadran) olmalı.")
        if fdi in gorulen:
            raise GirdiHatasi(f"Yinelenen diş: {fdi}.")
        gorulen.add(fdi)
        nesne(dis["hareket"], HAREKET_ALANLARI, f"{fdi}.hareket")
        for alan in HAREKET_ALANLARI:
            alt, ust = (0, 5) if alan == "intruzyon_mm" else ((-10, 10) if alan.endswith("mm") else (-45, 45))
            sayi(dis["hareket"][alan], alt, ust, f"{fdi}.{alan}")
        sayi(dis["toplam_rotasyon_derece"], 0, 180, "toplam_rotasyon_derece")
        if dis["toplam_rotasyon_derece"] < abs(dis["hareket"]["rotasyon_derece"]):
            raise GirdiHatasi("Toplam rotasyon, aşama rotasyonunun mutlak değerinden küçük olamaz.")
        secim(dis["periodontal"], ("normal", "azalmis_destek", "aktif_hastalik", "bilinmiyor"), "periodontal")
        for alan in ("kok_kemik", "temas_yolu"):
            secim(dis[alan], ("uygun", "riskli", "bilinmiyor"), alan)
        secim(dis["atasman"], ("planli", "yok", "bilinmiyor"), "atasman")
    if len({fdi // 10 <= 2 for fdi in gorulen}) != 1:
        raise GirdiHatasi("Tek istekte yalnızca bir çene değerlendirilebilir.")
