# © 2026 FlowCognition by suvilab.com — Tüm hakları saklıdır.
"""Sürümlü mühendislik politikası, izlenebilir katsayılar ve bütçe hesabı."""

from copy import deepcopy
from hashlib import sha256
from importlib.resources import files
from itertools import combinations
from functools import lru_cache
import json
import math

from .dogrulama import GirdiHatasi, EKSENLER, dis_dogrula, dis_grubu, hareket_dogrula, nesne, sayi, tam_sayi, metin


@lru_cache(maxsize=8)
def _paket_verisi(ad):
    return json.loads(files("hareket_butcesi").joinpath("veri", ad).read_text(encoding="utf-8"))


def veri_oku(ad):
    return deepcopy(_paket_verisi(ad))


def ozet(veri):
    return sha256(json.dumps(veri, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode()).hexdigest()


def kurallari_yukle():
    return politika_dogrula(veri_oku("politika.json"))


def politika_dogrula(politika):
    ornek = veri_oku("politika.json")
    nesne(politika, ornek.keys(), ad="politika")
    for ad in ("kimlik", "surum", "telif", "aciklama"):
        metin(politika[ad], ad)
    if politika["kanit"] != ornek["kanit"]:
        raise GirdiHatasi("Deneysel politika kanıt niteliği yükseltilemez.")
    if politika["klinik_dogrulama"] is not False:
        raise GirdiHatasi("Bu sürüm klinik doğrulanmış politika kabul etmez.")
    for bolum in ("limitler", "grup_rotasyon", "yon_katsayilari", "degistiriciler", "agirliklar"):
        nesne(politika[bolum], ornek[bolum].keys(), ad=bolum)
    for ad, limit in politika["limitler"].items():
        nesne(limit, ("tercih", "uyari", "azami", "birim", "kaynaklar"), ad=ad)
        for seviye in ("tercih", "uyari", "azami"):
            sayi(limit[seviye], 1e-6, 10, ad)
        if not limit["tercih"] <= limit["uyari"] <= limit["azami"] or limit["birim"] != ornek["limitler"][ad]["birim"]:
            raise GirdiHatasi("Eşikler tercih ≤ uyarı ≤ azami sırasını ve birimi korumalı.")
        if type(limit["kaynaklar"]) is not list or not limit["kaynaklar"] or any(type(k) is not str for k in limit["kaynaklar"]) or not set(limit["kaynaklar"]) <= {k["kimlik"] for k in veri_oku("kaynaklar.json")}:
            raise GirdiHatasi("Limit kaynağı katalogda bulunmalı.")
    for bolum in ("grup_rotasyon", "yon_katsayilari", "degistiriciler"):
        for ad, deger in politika[bolum].items():
            sayi(deger, .05, 179 if ad == "buyuk_rotasyon_esigi" else 1, ad)
    for ad, deger in politika["agirliklar"].items():
        sayi(deger, .1, 10, ad)
    beklenen = {frozenset(c) for c in combinations(politika["agirliklar"], 2)}
    if type(politika["eslesimler"]) is not list or len(politika["eslesimler"]) != len(beklenen):
        raise GirdiHatasi("Tüm hareket çiftleri tekil olarak tanımlanmalı.")
    gorulen = set()
    for es in politika["eslesimler"]:
        nesne(es, ("cift", "katsayi"), ad="eşleşim")
        if type(es["cift"]) is not list or len(es["cift"]) != 2 or any(type(ad) is not str for ad in es["cift"]):
            raise GirdiHatasi("Eşleşim iki hareket adı içermeli.")
        anahtar = frozenset(es["cift"])
        if anahtar not in beklenen or anahtar in gorulen:
            raise GirdiHatasi("Bilinmeyen veya yinelenen eşleşim.")
        gorulen.add(anahtar)
        sayi(es["katsayi"], 1, 3, "eşleşim katsayısı")
    for ad in ("yuk_kabul", "yuk_uyari", "dogrusal_azami_mm"):
        sayi(politika[ad], .01, 5, ad)
    if politika["yuk_kabul"] > politika["yuk_uyari"]:
        raise GirdiHatasi("Kabul eşiği uyarı eşiğini aşamaz.")
    tam_sayi(politika["en_fazla_yeniden_deneme"], 0, 16, "yeniden deneme")
    sayi(politika["kucultme_orani"], .1, .9, "küçültme oranı")
    return deepcopy(politika)


def etkin_butce(dis, politika=None):
    dis_dogrula(dis)
    p = kurallari_yukle() if politika is None else politika_dogrula(politika)
    hareket, grup = dis["hareket"], dis_grubu(dis["fdi"])
    sonuc = {}
    for ad in EKSENLER:
        tur = ("intruzyon" if hareket[ad] >= 0 else "ekstruzyon") if ad == "ie_mm" else ad
        yon = ("mesial" if hareket[ad] >= 0 else "distal") if ad == "md_mm" else ("bukkal" if hareket[ad] >= 0 else "lingual") if ad == "bl_mm" else tur if ad == "ie_mm" else ("pozitif_aci" if hareket[ad] >= 0 else "negatif_aci")
        iz = [{"neden": "yön: " + yon, "katsayi": p["yon_katsayilari"][yon], "kaynaklar": [], "koken": "muhendislik_politikasi"}]
        def ekle(neden, katsayi, kaynaklar):
            iz.append({"neden": neden, "katsayi": katsayi, "kaynaklar": kaynaklar, "koken": "muhendislik_politikasi"})
        if ad == "rotasyon_derece":
            ekle("diş grubu: " + grup, p["grup_rotasyon"][grup], ["M01", "M02"])
            if abs(hareket[ad]) > p["degistiriciler"]["buyuk_rotasyon_esigi"]:
                ekle("toplam rotasyon büyüklüğü", p["degistiriciler"]["buyuk_rotasyon"], ["M01"])
        if dis["atasman"] == "yok":
            anahtar = {"rotasyon_derece": "atasmansiz_rotasyon", "tork_derece": "atasmansiz_tork", "ekstruzyon": "atasmansiz_ekstruzyon"}.get(tur)
            if anahtar:
                ekle("ataşman yok", p["degistiriciler"][anahtar], ["M02", "M04"])
        if dis["komsu_temas"] == "dar" and ad in ("md_mm", "bl_mm", "rotasyon_derece"):
            ekle("dar komşu temas", p["degistiriciler"]["dar_temas"], [])
        if dis["periodontal"] == "azalmis":
            ekle("azalmış periodontal destek", p["degistiriciler"]["azalmis_destek"], ["M09"])
        katsayi = math.prod(i["katsayi"] for i in iz)
        temel = p["limitler"][tur]
        sonuc[ad] = {s: temel[s]*katsayi for s in ("tercih", "uyari", "azami")}
        sonuc[ad].update(birim=temel["birim"], hareket=tur, yon=yon, temel={s:temel[s] for s in ("tercih", "uyari", "azami")}, katsayi=katsayi, iz=iz, kaynaklar=temel["kaynaklar"], kanit="muhendislik_politikasi", kanit_guveni="dogrulanmadi")
    return sonuc


def asama_yuku(hareket, butce, politika=None):
    hareket_dogrula(hareket)
    p = kurallari_yukle() if politika is None else politika
    nesne(butce, EKSENLER, ad="etkin bütçe")
    for ad in EKSENLER:
        if type(butce[ad]) is not dict or not {"tercih", "uyari", "azami", "hareket"} <= butce[ad].keys():
            raise GirdiHatasi("Etkin bütçe eşikleri eksik.")
        for seviye in ("tercih", "uyari", "azami"):
            sayi(butce[ad][seviye], 1e-12, 10, ad)
        if not butce[ad]["tercih"] <= butce[ad]["uyari"] <= butce[ad]["azami"]:
            raise GirdiHatasi("Etkin eşikler sıralı olmalı.")
    oran = {ad: abs(hareket[ad])/butce[ad]["tercih"] for ad in EKSENLER}
    dikey = "intruzyon" if hareket["ie_mm"] >= 0 else "ekstruzyon"
    if butce["ie_mm"]["hareket"] != dikey and hareket["ie_mm"] != 0:
        raise GirdiHatasi("Dikey bütçe hareket yönüyle uyuşmuyor.")
    talepler = {"oteleme": math.hypot(oran["md_mm"], oran["bl_mm"]), "rotasyon": oran["rotasyon_derece"], "tip": oran["tip_derece"], "tork": oran["tork_derece"], "intruzyon": 0., "ekstruzyon": 0.}
    talepler[dikey] = oran["ie_mm"]
    temel = sum(p["agirliklar"][ad]*deger**2 for ad,deger in talepler.items())
    cezalar = []
    for es in p["eslesimler"]:
        a,b = es["cift"]
        ceza = 2*(es["katsayi"]-1)*math.sqrt(p["agirliklar"][a]*p["agirliklar"][b])*talepler[a]*talepler[b]
        if ceza > 0:
            cezalar.append({"cift": es["cift"], "katki": ceza, "katsayi": es["katsayi"], "kanit": "muhendislik_politikasi"})
    toplam = temel + sum(c["katki"] for c in cezalar)
    bileske = math.sqrt(sum(hareket[ad]**2 for ad in EKSENLER[:3]))
    sert = [ad for ad in EKSENLER if abs(hareket[ad]) > butce[ad]["azami"] + 1e-10]
    uyari = [ad for ad in EKSENLER if abs(hareket[ad]) > butce[ad]["uyari"] + 1e-10]
    durum = "bol" if sert or bileske > p["dogrusal_azami_mm"] + 1e-10 or toplam > p["yuk_uyari"] + 1e-10 else "uyari" if uyari or toplam > p["yuk_kabul"] + 1e-10 else "butce_icinde"
    return {"durum": durum, "temel_yuk": temel, "eslesim_cezalari": cezalar, "toplam_yuk": toplam, "dogrusal_bileske_mm": bileske, "azami_asimlari": sert, "uyari_asimlari": uyari, "klinik_onay": False}


def asama_tahmini(hareket, butce, politika=None):
    p = kurallari_yukle() if politika is None else politika
    yuk = asama_yuku(hareket, butce, p)
    tercih = {ad: math.ceil(abs(hareket[ad])/butce[ad]["tercih"] - 1e-12) for ad in EKSENLER}
    sert = max([abs(hareket[ad])/butce[ad]["azami"] for ad in EKSENLER] + [yuk["dogrusal_bileske_mm"]/p["dogrusal_azami_mm"]])
    birlesik = max(sert, math.sqrt(yuk["toplam_yuk"]/p["yuk_kabul"]), max(abs(hareket[ad])/butce[ad]["uyari"] for ad in EKSENLER))
    return {"tekil_tercih_sayilari": tercih, "tekil_tercih_tahmini": max(tercih.values()), "sert_limit_alt_siniri": max(0, math.ceil(sert - 1e-12)), "birlesik_yol_tahmini": max(0, math.ceil(birlesik - 1e-12)), "azami_ilerleme": 1. if birlesik == 0 else min(1., 1/birlesik), "aciklama": "Sabit politika ve doğrusal/quaternion yolu için tahmin; klinik süre veya nihai ark aşama sayısı değildir."}


def ongorulebilirlik(dis):
    if dis["hareket"]["rotasyon_derece"] != 0:
        return {"hasta_tahmini": None, "literatur_araligi": [0.36, 0.85], "kaynaklar": ["M02"], "kanit_guveni": "dusuk_orta", "aciklama": "Farklı klinik çalışmalardaki rotasyon doğruluğu aralığı; hasta tahmini değil."}
    return {"hasta_tahmini": None, "literatur_araligi": None, "kaynaklar": ["M03"] if dis["hareket"]["ie_mm"] > 0 else [], "kanit_guveni": "hasta_duzeyinde_belirsiz", "aciklama": "Bu hasta ve hareket için kalibre edilmiş öngörülebilirlik yok."}
