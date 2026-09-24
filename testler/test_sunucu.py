# Telif hakkı © 2026 FlowCognition by suvilab.com — Tüm hakları saklıdır.
"""Gerçek yerel soket üzerinden HTTP sözleşmesi denetimleri."""

from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
import json
import threading
import unittest

from birlesik_hareket.motor import veri_oku
from birlesik_hareket.sunucu import IstekIsleyici


class SunucuTestleri(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sunucu = ThreadingHTTPServer(("127.0.0.1", 0), IstekIsleyici)
        cls.isci = threading.Thread(target=cls.sunucu.serve_forever, daemon=True)
        cls.isci.start()

    @classmethod
    def tearDownClass(cls):
        cls.sunucu.shutdown()
        cls.sunucu.server_close()
        cls.isci.join()

    def istek(self, yol, govde=None, baslik=None):
        baglanti = HTTPConnection("127.0.0.1", self.sunucu.server_port, timeout=5)
        try:
            baglanti.request("POST" if govde is not None else "GET", yol, govde, baslik or {})
            yanit = baglanti.getresponse()
            return yanit.status, yanit.read(), dict(yanit.getheaders())
        finally:
            baglanti.close()

    def test_hazir_icerikler(self):
        for yol in ("/", "/uygulama.js", "/gorunum.css", "/api/v1/bilgi", "/api/v1/sema", "/api/v1/ornek"):
            with self.subTest(yol=yol):
                kod, govde, baslik = self.istek(yol)
                self.assertEqual(kod, 200)
                self.assertTrue(govde)
                self.assertEqual(baslik["Cache-Control"], "no-store")

    def test_gecerli_degerlendirme(self):
        kod, govde, _ = self.istek("/api/v1/degerlendir", json.dumps(veri_oku("ornek.json")).encode(), {"Content-Type": "application/json"})
        self.assertEqual(kod, 200)
        self.assertEqual(json.loads(govde)["durum"], "kosullu_aday")

    def test_gecersiz_girdi(self):
        kod, _, _ = self.istek("/api/v1/degerlendir", b"{}", {"Content-Type": "application/json"})
        self.assertEqual(kod, 422)

    def test_yabanci_koken(self):
        kod, _, _ = self.istek("/api/v1/degerlendir", b"{}", {"Content-Type": "application/json", "Origin": "https://ornek.test"})
        self.assertEqual(kod, 403)

    def test_yanlis_icerik_turu(self):
        self.assertEqual(self.istek("/api/v1/degerlendir", b"{}")[0], 415)

    def test_yanlis_host(self):
        self.assertEqual(self.istek("/", baslik={"Host": "ornek.test"})[0], 403)

    def test_yol_siniri(self):
        self.assertEqual(self.istek("/../LICENSE")[0], 404)

    def test_buyuk_govde(self):
        self.assertEqual(self.istek("/api/v1/degerlendir", b" " * 262145, {"Content-Type": "application/json"})[0], 413)


if __name__ == "__main__":
    unittest.main()
