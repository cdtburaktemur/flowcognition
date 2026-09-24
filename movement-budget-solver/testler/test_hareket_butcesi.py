# © 2026 FlowCognition by suvilab.com — Tüm hakları saklıdır.
"""Movement Budget Solver davranış ve sözleşme testleri."""

from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hareket_butcesi import (GirdiHatasi, asama_tahmini, asama_yuku,
                              etkin_butce, hareket_ayristir, json_oku,
                              planla, poz_hesapla)
from hareket_butcesi.kurallar import kurallari_yukle, veri_oku


class MotorTestleri(unittest.TestCase):
    def setUp(self):
        self.istek = veri_oku("ornek.json")
        self.kanin = next(d for d in self.istek["disler"] if d["fdi"] == 13)
        self.politika = kurallari_yukle()

    def test_ornek_planlanan_hareketi_korur(self):
        sonuc = planla(self.istek)
        self.assertEqual(sonuc["durum"], "geometri_bekleniyor")
        self.assertTrue(sonuc["tamamlandi"])
        self.assertFalse(sonuc["klinik_onay"])
        self.assertFalse(sonuc["geometri_dogrulandi"])
        toplam = {ad: sum(a["hareket"][ad] for a in sonuc["asamalar"] for _ in [0] if any(d["fdi"] == 13 for d in [a])) for ad in ()}
        kalan = sonuc["kalan_hareketler"]
        self.assertNotIn("13", kalan)
        self.assertEqual(sonuc["girdi_ozeti"], planla(self.istek)["girdi_ozeti"])

    def test_butce_ataşman_ve_rotasyon_grubu(self):
        yok = etkin_butce(self.kanin, self.politika)
        planli = deepcopy(self.kanin)
        planli["atasman"] = "planli"
        var = etkin_butce(planli, self.politika)
        self.assertLess(yok["rotasyon_derece"]["tercih"], var["rotasyon_derece"]["tercih"])
        self.assertEqual(yok["rotasyon_derece"]["temel"], var["rotasyon_derece"]["temel"])
        self.assertEqual(yok["rotasyon_derece"]["kanit"], "muhendislik_politikasi")

    def test_birlestirilmis_yuk_tekil_hareketten_buyuk(self):
        butce = etkin_butce(self.kanin, self.politika)
        tek = deepcopy(self.kanin["hareket"])
        tek["rotasyon_derece"] = 0
        tek["tip_derece"] = 0
        tek["tork_derece"] = 0
        tek_yuk = asama_yuku(tek, butce, self.politika)["toplam_yuk"]
        birlesik = asama_yuku(self.kanin["hareket"], butce, self.politika)
        self.assertGreater(birlesik["toplam_yuk"], tek_yuk)
        self.assertTrue(birlesik["eslesim_cezalari"])

    def test_asama_alt_siniri_ve_birlesik_tahmin(self):
        butce = etkin_butce(self.kanin, self.politika)
        tahmin = asama_tahmini(self.kanin["hareket"], butce, self.politika)
        self.assertGreaterEqual(tahmin["birlesik_yol_tahmini"], tahmin["tekil_tercih_tahmini"])
        self.assertGreater(tahmin["birlesik_yol_tahmini"], 0)

    def test_distal_yuzde_50_siralamasi(self):
        istek = deepcopy(self.istek)
        istek["strateji"] = "distal_yuzde50"
        istek["disler"] = [d for d in istek["disler"] if d["fdi"] in (13, 14, 15, 16)]
        for dis in istek["disler"]:
            dis["destek_disleri"] = []
        for fdi, miktar in ((13, -0.5), (14, -0.5), (15, -0.5)):
            next(d for d in istek["disler"] if d["fdi"] == fdi)["hareket"]["md_mm"] = miktar
        sonuc = planla(istek)
        self.assertGreaterEqual(len(sonuc["asamalar"]), 3)
        # Posterior sıradaki dişin ilk yarım ilerlemesi oluşmadan bir önceki hareket başlatılmaz.
        for i, asama in enumerate(sonuc["asamalar"][:-1]):
            once = {d["fdi"]: d["bitis_ilerleme"] for d in asama["disler"]}
            if 13 in once:
                self.assertGreaterEqual(once[13], 0)

    def test_carpisma_geri_beslemesi_erteleme_veya_kucultme(self):
        sayac = {"n": 0}
        def denetci(aday):
            sayac["n"] += 1
            return {"durum": "carpisma" if sayac["n"] == 1 else "uygun",
                    "aday_ozeti": aday["aday_ozeti"],
                    "geometri_revizyonu": aday["geometri_revizyonu"],
                    "yol_denetlendi": True,
                    "sorunlu_disler": [13] if sayac["n"] == 1 else [],
                    "denetci": "sentetik-bvh", "aciklama": "Sentetik denetim"}
        sonuc = planla(self.istek, geometri_denetçisi=denetci)
        self.assertEqual(sonuc["durum"], "geometri_denetimli_taslak")
        self.assertTrue(sonuc["geometri_dogrulandi"])
        self.assertTrue(any(o["tur"] == "carpisma" for o in sonuc["olaylar"]))

    def test_geometri_bilinmiyor_uygulanmaz(self):
        def denetci(aday):
            return {"durum": "bilinmiyor", "aday_ozeti": aday["aday_ozeti"], "geometri_revizyonu": aday["geometri_revizyonu"], "yol_denetlendi": False, "sorunlu_disler": [], "denetci": "bvh", "aciklama": "Mesh yüklenmedi"}
        sonuc = planla(self.istek, geometri_denetçisi=denetci)
        self.assertEqual(sonuc["durum"], "geometri_bekleniyor")
        self.assertFalse(sonuc["geometri_dogrulandi"])

    def test_geometri_yaniti_stale_reddedilir(self):
        def denetci(aday):
            return {"durum": "uygun", "aday_ozeti": "eski", "geometri_revizyonu": aday["geometri_revizyonu"], "yol_denetlendi": True, "sorunlu_disler": [], "denetci": "bvh", "aciklama": "Uygun"}
        sonuc = planla(self.istek, geometri_denetçisi=denetci)
        self.assertEqual(sonuc["durum"], "denetci_hatasi")
        self.assertFalse(sonuc["geometri_dogrulandi"])


class GeometriTestleri(unittest.TestCase):
    def donusum(self):
        return {"baslangic": {"konum_mm": [0, 0, 0], "quaternion": [0, 0, 0, 1]}, "hedef": {"konum_mm": [1, 2, 3], "quaternion": [0, 0, 0, 1]}, "cerceve_quaternion": [0, 0, 0, 1], "klinik_isaretler": {a: 1 for a in ("md_mm", "bl_mm", "ie_mm", "rotasyon_derece", "tip_derece", "tork_derece")}}

    def test_donusum_ayristirma(self):
        self.assertEqual(hareket_ayristir(self.donusum())["md_mm"], 1)
        self.assertEqual(hareket_ayristir(self.donusum())["ie_mm"], 3)

    def test_poz_interpolasyonu(self):
        poz = poz_hesapla(self.donusum(), .5)
        self.assertEqual(poz["konum_mm"], [0.5, 1.0, 1.5])
        self.assertEqual(poz["quaternion"], [0.0, 0.0, 0.0, 1.0])

    def test_gecersiz_quaternion(self):
        d = self.donusum()
        d["hedef"]["quaternion"] = [0, 0, 0, 2]
        with self.assertRaises(GirdiHatasi):
            hareket_ayristir(d)


class SozlesmeTestleri(unittest.TestCase):
    def setUp(self):
        self.istek = veri_oku("ornek.json")

    def test_eksik_alan(self):
        del self.istek["ankraj"]
        with self.assertRaises(GirdiHatasi):
            planla(self.istek)

    def test_bilinmeyen_alan(self):
        self.istek["surpriz"] = 1
        with self.assertRaises(GirdiHatasi):
            planla(self.istek)

    def test_belirsiz_klinik_veri_durdurur(self):
        self.istek["disler"][2]["komsu_temas"] = "bilinmiyor"
        sonuc = planla(self.istek)
        self.assertEqual(sonuc["durum"], "veri_yetersiz")

    def test_aktif_hastalik_engeller(self):
        self.istek["disler"][2]["periodontal"] = "aktif_hastalik"
        self.assertEqual(planla(self.istek)["durum"], "engellendi")

    def test_sayisal_json_sabitleri(self):
        for ham in ('{"a":NaN}', '{"a":Infinity}', '{"a":1,"a":2}', '{'):
            with self.assertRaises(GirdiHatasi):
                json_oku(ham)

    def test_hareket_toplami_ve_girdi_degismez(self):
        once = deepcopy(self.istek)
        planla(self.istek)
        self.assertEqual(self.istek, once)


if __name__ == "__main__":
    unittest.main()
