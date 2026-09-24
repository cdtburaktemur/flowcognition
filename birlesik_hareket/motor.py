# Telif hakkı © 2026 FlowCognition by suvilab.com — Tüm hakları saklıdır.
"""Deterministik, kaynak izlenebilir birleşik hareket taraması."""

from hashlib import sha256
from importlib.resources import files
from itertools import combinations
import json
import math

from .dogrulama import dogrula

ONCELIK = {"hareket_yok": 0, "kosullu_aday": 1, "uzman_incelemesi": 2,
           "ayirma_degerlendirilmeli": 3, "veri_yetersiz": 4, "engellendi": 5}


def veri_oku(ad):
    return json.loads(files("birlesik_hareket").joinpath("veri", ad).read_text(encoding="utf-8"))


def ozet(deger):
    return sha256(json.dumps(deger, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def en_ciddi(durumlar):
    return max(durumlar, key=ONCELIK.__getitem__, default="hareket_yok")


def hareket_buyuklukleri(dis):
    hareket = dis["hareket"]
    return {
        "oteleme": math.hypot(hareket["otelemenin_mesial_bileseni_mm"], hareket["otelemenin_bukkal_bileseni_mm"]),
        "rotasyon": abs(hareket["rotasyon_derece"]),
        "tip": abs(hareket["tip_derece"]),
        "tork": abs(hareket["tork_derece"]),
        "intruzyon": hareket["intruzyon_mm"],
    }


def bulgu(kod, durum, gerekce, kaynaklar=(), **ayrinti):
    return {"kod": kod, "durum": durum, "gerekce": gerekce, "kaynaklar": list(kaynaklar), **ayrinti}


def degerlendir(istek):
    """Tek çenenin tek aşamasını değerlendirir; girdiyi değiştirmez, klinik onay vermez."""
    dogrula(istek)
    politika = veri_oku("politika.json")
    ciftler = veri_oku("ciftler.json")
    kaynaklar = veri_oku("kaynaklar.json")
    sinir = politika["sinirlar"]
    baglam = istek["baglam"]
    ark = []
    sonuclar = []
    if not baglam["tam_ark"]:
        ark.append(bulgu("A01", "veri_yetersiz", "Tüm mevcut dişler, pasif ankraj dişleriyle birlikte gönderilmelidir."))
    for alan in ("ankraj", "plak_oturmasi", "kok_degerlendirmesi", "materyal_protokolu"):
        deger = baglam[alan]
        if deger != "uygun":
            durum = "veri_yetersiz" if deger == "bilinmiyor" else "engellendi"
            ark.append(bulgu("A02", durum, f"{alan}: {deger}; aşama ilerletilmeden değerlendirme tamamlanmalı."))
    for dis in sorted(istek["disler"], key=lambda oge: oge["fdi"]):
        fdi = dis["fdi"]
        buyukluk = hareket_buyuklukleri(dis)
        aktif = [ad for ad, miktar in buyukluk.items() if miktar > 0]
        bulgular = []
        # Pasif dişlerin sağlık ve geometri sorunları da ark ankrajını etkileyebilir.
        for alan in ("periodontal", "kok_kemik", "temas_yolu"):
            deger = dis[alan]
            if deger == "bilinmiyor":
                bulgular.append(bulgu("D01", "veri_yetersiz", f"{alan} değerlendirmesi eksik."))
            elif deger in ("aktif_hastalik", "riskli"):
                bulgular.append(bulgu("D02", "engellendi", f"{alan}: {deger}; plan yeniden incelenmeli."))
            elif deger == "azalmis_destek":
                bulgular.append(bulgu("D03", "uzman_incelemesi", "Azalmış periodontal destek için hasta özelinde biyomekanik değerlendirme gerekir.", ["K08"]))
        if aktif and dis["atasman"] == "bilinmiyor":
            bulgular.append(bulgu("D04", "veri_yetersiz", "Ataşman planı bilinmiyor."))
        elif dis["atasman"] == "yok" and any(ad in aktif for ad in ("rotasyon", "tork", "intruzyon")):
            bulgular.append(bulgu("D05", "uzman_incelemesi", "Tutuculuk ve yardımcı mekanik gereksinimi incelenmeli; ataşman varlığı da başarı garantisi değildir.", ["K01", "K03"]))
        esikler = {"oteleme": sinir["otelemenin_buyuklugu_mm"], "rotasyon": sinir["rotasyon_derece"],
                   "tip": sinir["tip_derece"], "tork": sinir["tork_derece"], "intruzyon": sinir["intruzyon_mm"]}
        oranlar = {ad: buyukluk[ad] / esikler[ad] for ad in buyukluk}
        for ad in aktif:
            if oranlar[ad] > 1 + 1e-12:
                bulgular.append(bulgu("D06", "ayirma_degerlendirilmeli", f"{ad} miktarı araştırma politikasının tarama eşiğini aşıyor.", hareket=ad, miktar=buyukluk[ad], esik=esikler[ad], kanit="muhendislik_ihtiyati"))
        bileske = math.hypot(buyukluk["oteleme"], buyukluk["intruzyon"])
        talep = sum(oran ** 2 for oran in oranlar.values())
        if bileske > sinir["dogrusal_bileske_mm"] + 1e-12:
            bulgular.append(bulgu("D07", "ayirma_degerlendirilmeli", "Üç doğrusal bileşenin normu politika eşiğini aşıyor.", kanit="muhendislik_ihtiyati"))
        if len(aktif) > 1 and talep > sinir["birlesik_talep"] + 1e-12:
            bulgular.append(bulgu("D08", "ayirma_degerlendirilmeli", "Normalize kareler toplamı birleşik talep eşiğini aşıyor; bu değer kuvvet, stres veya başarı olasılığı değildir.", kanit="muhendislik_ihtiyati"))
        eslesmeler = []
        for cift in combinations(aktif, 2):
            kural = next(k for k in ciftler if set(k["hareketler"]) == set(cift)).copy()
            # Klinik çalışma üst molarlara, distal yöne ve belirli yardımcı mekaniklere özgüdür.
            if set(cift) == {"oteleme", "rotasyon"} and fdi // 10 in (1, 2) and fdi % 10 in (6, 7) and dis["hareket"]["otelemenin_mesial_bileseni_mm"] < 0 and dis["hareket"]["otelemenin_bukkal_bileseni_mm"] == 0 and dis["atasman"] == "planli" and not baglam["cekimli_vaka"]:
                kural.update(durum="kosullu_aday", gerekce="Üst molar distalizasyonu ve derotasyonu için sınırlı klinik dayanak vardır. Çalışmadaki ataşman, elastik ve ardışık distalizasyon koşulları uzman tarafından eşleştirilmelidir; aynı aşama güvenliği kanıtlanmış değildir.")
            eslesmeler.append(kural)
        if len(aktif) >= 3:
            bulgular.append(bulgu("D09", "ayirma_degerlendirilmeli", "Üç veya daha fazla hareket için ikili uyumluluk yeterli değildir; ayrı aşama seçenekleri uzman tarafından değerlendirilmeli.", kanit="muhendislik_ihtiyati"))
        if buyukluk["rotasyon"] > 0 and fdi % 10 in (3, 4, 5):
            bulgular.append(bulgu("D10", "uzman_incelemesi", "Kanin ve premolar morfolojisi rotasyon tutuculuğunu güçleştirebilir.", ["K01", "K03"]))
            if dis["toplam_rotasyon_derece"] > 15:
                bulgular.append(bulgu("D11", "ayirma_degerlendirilmeli", "Toplam rotasyon 15 dereceyi aşıyor; küçük aşama miktarı toplam hareket güçlüğünü ortadan kaldırmaz.", ["K01"], kanit="dolayli_klinik"))
        if "tork" in aktif or "intruzyon" in aktif:
            bulgular.append(bulgu("D12", "uzman_incelemesi", "Kök veya dikey hareket gerçek kök konumu ve ankraj ile değerlendirilmelidir.", ["K02", "K07"]))
        durum = en_ciddi(["kosullu_aday" if aktif else "hareket_yok"] + [b["durum"] for b in bulgular] + [e["durum"] for e in eslesmeler])
        sonuclar.append({"fdi": fdi, "durum": durum, "aktif_hareketler": aktif, "ciftler": eslesmeler, "bulgular": bulgular,
                         "olcumler": {"dogrusal_bileske_mm": bileske, "normalize_kareler_toplami": talep, "esik_oranlari": oranlar}})
    on = [d for d in istek["disler"] if d["fdi"] % 10 <= 3 and d["hareket"]["intruzyon_mm"] > 0]
    arka = [d for d in istek["disler"] if d["fdi"] % 10 >= 4 and d["hareket"]["intruzyon_mm"] > 0]
    if on and arka:
        ark.append(bulgu("A03", "ayirma_degerlendirilmeli", "Anterior ve posterior intrüzyon aynı aşamada ankraj çatışması yaratabilir; yardımcı ankrajın varlığı tek başına bu uyarıyı kaldırmaz.", ["K04", "K10"], kanit="dolayli_kanit_ve_ihtiyat"))
    if all(sonuc["aktif_hareketler"] for sonuc in sonuclar):
        ark.append(bulgu("A04", "uzman_incelemesi", "Gönderilen bütün dişler aktif; pasif ankraj veya alternatif ankraj kaynağı gözden geçirilmeli.", ["K04"]))
    if baglam["cekimli_vaka"]:
        ark.append(bulgu("A05", "uzman_incelemesi", "Çekimli vaka: boşluk kapatma, kök paralelliği ve karşılıklı ankraj hareketleri ayrıca incelenmeli.", ["K07", "K09"]))
    if any(d["hareket"]["otelemenin_mesial_bileseni_mm"] < 0 and d["fdi"] % 10 >= 4 for d in istek["disler"]) and any(d["hareket"]["tork_derece"] != 0 and d["fdi"] % 10 <= 3 for d in istek["disler"]):
        ark.append(bulgu("A06", "uzman_incelemesi", "Posterior distalizasyon ve anterior tork aynı arktaki ankrajı etkiler; tork yönü ve kök hedefi CAD üzerinde incelenmeli.", ["K04"]))
    durum = en_ciddi([s["durum"] for s in sonuclar] + [a["durum"] for a in ark])
    kullanilan = set()
    for sonuc in sonuclar:
        for oge in sonuc["bulgular"] + sonuc["ciftler"]:
            kullanilan.update(oge["kaynaklar"])
    for oge in ark:
        kullanilan.update(oge["kaynaklar"])
    return {"sozlesme_surumu": "1.0", "motor_surumu": "0.1.0", "asama_kimligi": istek["asama_kimligi"],
            "durum": durum, "klinik_onay": False, "otomatik_uygulama": False,
            "aciklama": "Araştırma amaçlı karar desteği; koşullu aday dahil hiçbir çıktı klinik güvenlik onayı değildir.",
            "girdi_ozeti": ozet(istek), "bilgi_tabani_ozeti": ozet([politika, ciftler, kaynaklar]),
            "politika": politika, "disler": sonuclar, "ark_bulgulari": ark,
            "kaynaklar": [k for k in kaynaklar if k["kimlik"] in kullanilan]}
