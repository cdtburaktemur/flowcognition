# © 2026 FlowCognition by suvilab.com — Tüm hakları saklıdır.
"""Sabit başlangıç çerçevesinde öteleme ve quaternion logaritması.

Açılar Euler açıları değildir. Ortak ilerleme oranıyla yeniden üretim en kısa
quaternion yolunu korur. Pozun konumu aynı fiziksel pivotun dünya konumudur.
"""

import math
from .dogrulama import GirdiHatasi, EKSENLER, nesne, sayi


def vektor(deger, uzunluk, ad):
    if type(deger) not in (list, tuple) or len(deger) != uzunluk:
        raise GirdiHatasi(f"{ad}: {uzunluk} bileşen bekleniyor.")
    for oge in deger:
        sayi(oge, -1e6, 1e6, ad)
    return list(deger)


def quaternion(q):
    q = vektor(q, 4, "quaternion [x,y,z,w]")
    norm = math.sqrt(sum(x*x for x in q))
    if abs(norm - 1) > 1e-6:
        raise GirdiHatasi("Quaternion birim uzunlukta olmalı.")
    return [x / norm for x in q]


def eslenik(q):
    return [-q[0], -q[1], -q[2], q[3]]


def carp(a, b):
    x, y, z, w = a
    u, v, t, s = b
    return [w*u+x*s+y*t-z*v, w*v-x*t+y*s+z*u, w*t+x*v-y*u+z*s, w*s-x*u-y*v-z*t]


def dondur(q, v):
    return carp(carp(q, [*v, 0]), eslenik(q))[:3]


def logaritma(q):
    q = quaternion(q)
    if q[3] < 0 or (abs(q[3]) < 1e-15 and next((x for x in q[:3] if abs(x) > 1e-15), 1) < 0):
        q = [-x for x in q]
    s = math.sqrt(sum(x*x for x in q[:3]))
    if s < 1e-14:
        return [0., 0., 0.]
    aci = math.degrees(2 * math.atan2(s, max(0., q[3])))
    return [aci * x / s for x in q[:3]]


def ussel(v):
    aci = math.sqrt(sum(x*x for x in v))
    if aci < 1e-14:
        return [0., 0., 0., 1.]
    yari = math.radians(aci) / 2
    return [x/aci*math.sin(yari) for x in v] + [math.cos(yari)]


def donusum_dogrula(donusum):
    nesne(donusum, ("baslangic", "hedef", "cerceve_quaternion", "klinik_isaretler"), ad="dönüşüm")
    for ad in ("baslangic", "hedef"):
        nesne(donusum[ad], ("konum_mm", "quaternion"), ad=ad)
        vektor(donusum[ad]["konum_mm"], 3, "pivot konumu")
        quaternion(donusum[ad]["quaternion"])
    quaternion(donusum["cerceve_quaternion"])
    nesne(donusum["klinik_isaretler"], EKSENLER, ad="klinik işaretler")
    for ad in EKSENLER:
        if type(donusum["klinik_isaretler"][ad]) is not int or donusum["klinik_isaretler"][ad] not in (-1, 1):
            raise GirdiHatasi("Her klinik işaret -1 veya +1 olmalı.")


def hareket_ayristir(donusum):
    donusum_dogrula(donusum)
    bas, son = donusum["baslangic"], donusum["hedef"]
    cerceve = quaternion(donusum["cerceve_quaternion"])
    yerel = dondur(eslenik(cerceve), [b-a for a,b in zip(bas["konum_mm"], son["konum_mm"])])
    fark = carp(quaternion(son["quaternion"]), eslenik(quaternion(bas["quaternion"])))
    acilar = logaritma(carp(carp(eslenik(cerceve), fark), cerceve))
    # Yerel X: tork ekseni, Y: tip ekseni, Z: uzun eksen rotasyonu.
    degerler = [*yerel, acilar[2], acilar[1], acilar[0]]
    return {ad: deger * donusum["klinik_isaretler"][ad] for ad, deger in zip(EKSENLER, degerler)}


def poz_hesapla(donusum, ilerleme):
    sayi(ilerleme, 0, 1, "ilerleme")
    hareket = hareket_ayristir(donusum)
    isaret = donusum["klinik_isaretler"]
    yerel = [hareket[ad]*isaret[ad]*ilerleme for ad in EKSENLER[:3]]
    acilar = [hareket[ad]*isaret[ad]*ilerleme for ad in ("tork_derece", "tip_derece", "rotasyon_derece")]
    cerceve = quaternion(donusum["cerceve_quaternion"])
    fark = carp(carp(cerceve, ussel(acilar)), eslenik(cerceve))
    kayma = dondur(cerceve, yerel)
    return {"konum_mm": [a+b for a,b in zip(donusum["baslangic"]["konum_mm"], kayma)],
            "quaternion": quaternion(carp(fark, donusum["baslangic"]["quaternion"]))}
