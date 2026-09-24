# Telif hakkı © 2026 FlowCognition by suvilab.com — Tüm hakları saklıdır.
"""Karar öncelikleri, kapsam ve yanlış güven üretmeme regresyonları."""

from copy import deepcopy
from itertools import combinations
import unittest

from birlesik_hareket import GirdiHatasi, degerlendir
from birlesik_hareket.dogrulama import json_oku
from birlesik_hareket.motor import veri_oku


class MotorTestleri(unittest.TestCase):
    def setUp(self):
        self.istek = veri_oku("ornek.json")
        self.dis = next(d for d in self.istek["disler"] if d["fdi"] == 16)

    def sonuc(self):
        return degerlendir(self.istek)

    def test_ornek_kosullu_ama_onaysiz(self):
        sonuc = self.sonuc()
        self.assertEqual(sonuc["durum"], "kosullu_aday")
        self.assertFalse(sonuc["klinik_onay"])
        self.assertFalse(sonuc["otomatik_uygulama"])

    def test_deterministik_ve_girdi_degismez(self):
        once = deepcopy(self.istek)
        self.assertEqual(self.sonuc(), self.sonuc())
        self.assertEqual(once, self.istek)

    def test_tum_on_cift_kapsaniyor(self):
        self.dis["hareket"].update(otelemenin_mesial_bileseni_mm=.01, rotasyon_derece=.1, tip_derece=.1, tork_derece=.1, intruzyon_mm=.01)
        sonuc = next(d for d in self.sonuc()["disler"] if d["fdi"] == 16)
        self.assertEqual(len(sonuc["ciftler"]), 10)
        self.assertEqual(sonuc["durum"], "ayirma_degerlendirilmeli")

    def test_her_cift_tekil_kayit(self):
        ciftler = veri_oku("ciftler.json")
        self.assertEqual({frozenset(c["hareketler"]) for c in ciftler}, {frozenset(c) for c in combinations(("oteleme", "rotasyon", "tip", "tork", "intruzyon"), 2)})

    def test_eksik_klinik_veri_onay_uretemez(self):
        for alan in ("ankraj", "plak_oturmasi", "kok_degerlendirmesi", "materyal_protokolu"):
            with self.subTest(alan=alan):
                istek = deepcopy(self.istek)
                istek["baglam"][alan] = "bilinmiyor"
                self.assertEqual(degerlendir(istek)["durum"], "veri_yetersiz")

    def test_bilinen_risk_eksik_veriden_oncelikli(self):
        self.istek["baglam"]["ankraj"] = "bilinmiyor"
        self.dis["kok_kemik"] = "riskli"
        self.assertEqual(self.sonuc()["durum"], "engellendi")

    def test_pasif_disin_riski_arkta_kaybolmaz(self):
        self.istek["disler"][0]["periodontal"] = "aktif_hastalik"
        self.assertEqual(self.sonuc()["durum"], "engellendi")

    def test_kismi_ark_yetersiz(self):
        self.istek["baglam"]["tam_ark"] = False
        self.assertEqual(self.sonuc()["durum"], "veri_yetersiz")

    def test_dis_basina_sinir_yeterli_degil(self):
        self.dis["hareket"].update(otelemenin_mesial_bileseni_mm=-.18, rotasyon_derece=.9)
        self.assertEqual(self.sonuc()["durum"], "ayirma_degerlendirilmeli")

    def test_oteleme_ve_intruzyon_bileskesi(self):
        self.dis["hareket"].update(otelemenin_mesial_bileseni_mm=.2, otelemenin_bukkal_bileseni_mm=.2, intruzyon_mm=.15)
        sonuc = next(d for d in self.sonuc()["disler"] if d["fdi"] == 16)
        self.assertAlmostEqual(sonuc["olcumler"]["dogrusal_bileske_mm"], (.04 + .04 + .0225) ** .5)
        self.assertIn("D07", [b["kod"] for b in sonuc["bulgular"]])

    def test_sifir_ve_esik_davranisi(self):
        self.dis["hareket"].update(otelemenin_mesial_bileseni_mm=0, rotasyon_derece=0)
        self.assertEqual(self.sonuc()["durum"], "hareket_yok")
        self.dis["hareket"]["otelemenin_mesial_bileseni_mm"] = .2
        self.assertEqual(self.sonuc()["durum"], "kosullu_aday")
        self.dis["hareket"]["otelemenin_mesial_bileseni_mm"] = .201
        self.assertEqual(self.sonuc()["durum"], "ayirma_degerlendirilmeli")

    def test_molar_kaniti_mesiale_tasinmaz(self):
        self.dis["hareket"]["otelemenin_mesial_bileseni_mm"] = .1
        self.assertEqual(self.sonuc()["durum"], "uzman_incelemesi")

    def test_molar_kaniti_cekimli_vakaya_tasinmaz(self):
        self.istek["baglam"]["cekimli_vaka"] = True
        sonuc = next(d for d in self.sonuc()["disler"] if d["fdi"] == 16)
        self.assertEqual(sonuc["ciftler"][0]["durum"], "uzman_incelemesi")

    def test_molar_kaniti_alt_ceneye_tasinmaz(self):
        for dis in self.istek["disler"]:
            dis["fdi"] += 20
        self.assertEqual(self.sonuc()["durum"], "uzman_incelemesi")

    def test_on_arka_intruzyon_uyarisi(self):
        self.dis["hareket"]["intruzyon_mm"] = .01
        self.istek["disler"][0]["hareket"]["intruzyon_mm"] = .01
        self.assertIn("A03", [b["kod"] for b in self.sonuc()["ark_bulgulari"]])

    def test_toplam_rotasyon_kucuk_asamaya_ragmen_kontrol_edilir(self):
        self.dis["fdi"] = 18
        hedef = next(d for d in self.istek["disler"] if d["fdi"] == 14)
        hedef["hareket"]["rotasyon_derece"] = .1
        hedef["toplam_rotasyon_derece"] = 20
        self.assertEqual(self.sonuc()["durum"], "ayirma_degerlendirilmeli")

    def test_hicbir_kaynak_kimligi_kirik_degil(self):
        kimlikler = {k["kimlik"] for k in veri_oku("kaynaklar.json")}
        for cift in veri_oku("ciftler.json"):
            self.assertLessEqual(set(cift["kaynaklar"]), kimlikler)

    def test_ozet_girdi_degisimini_yakalar(self):
        once = self.sonuc()["girdi_ozeti"]
        self.dis["hareket"]["rotasyon_derece"] = .3
        self.assertNotEqual(once, self.sonuc()["girdi_ozeti"])


class GirdiTestleri(unittest.TestCase):
    def setUp(self):
        self.istek = veri_oku("ornek.json")

    def test_gecersiz_sayilar(self):
        for deger in (float("nan"), float("inf"), float("-inf"), True, "0.1", None, 10 ** 400, [], {}):
            with self.subTest(deger=str(deger)[:20]):
                self.istek["disler"][0]["hareket"]["tip_derece"] = deger
                with self.assertRaises(GirdiHatasi):
                    degerlendir(self.istek)

    def test_bilinmeyen_alan_reddedilir(self):
        self.istek["disler"][0]["hareket"]["torque"] = 1
        with self.assertRaises(GirdiHatasi):
            degerlendir(self.istek)

    def test_eksik_alan_reddedilir(self):
        del self.istek["disler"][0]["hareket"]["tip_derece"]
        with self.assertRaises(GirdiHatasi):
            degerlendir(self.istek)

    def test_fdi_kapsami(self):
        for deger in (0, 19, 49, 51, True, "16", 16.0):
            self.istek["disler"][0]["fdi"] = deger
            with self.subTest(deger=deger), self.assertRaises(GirdiHatasi):
                degerlendir(self.istek)

    def test_tekillik(self):
        self.istek["disler"].append(deepcopy(self.istek["disler"][0]))
        with self.assertRaises(GirdiHatasi):
            degerlendir(self.istek)

    def test_iki_cene_reddedilir(self):
        self.istek["disler"][0]["fdi"] = 31
        with self.assertRaises(GirdiHatasi):
            degerlendir(self.istek)

    def test_negatif_intruzyon_reddedilir(self):
        self.istek["disler"][0]["hareket"]["intruzyon_mm"] = -.1
        with self.assertRaises(GirdiHatasi):
            degerlendir(self.istek)

    def test_tutarsiz_toplam_reddedilir(self):
        self.istek["disler"][0]["hareket"]["rotasyon_derece"] = 1
        with self.assertRaises(GirdiHatasi):
            degerlendir(self.istek)

    def test_bos_dis_listesi(self):
        self.istek["disler"] = []
        with self.assertRaises(GirdiHatasi):
            degerlendir(self.istek)

    def test_yanlis_eksen(self):
        self.istek["koordinat_sistemi"] = "global"
        with self.assertRaises(GirdiHatasi):
            degerlendir(self.istek)

    def test_json_yinelenen_alan_ve_sabitler(self):
        for metin in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}', '{', '1' * 5000):
            with self.subTest(metin=metin[:30]), self.assertRaises(GirdiHatasi):
                json_oku(metin)


if __name__ == "__main__":
    unittest.main()
