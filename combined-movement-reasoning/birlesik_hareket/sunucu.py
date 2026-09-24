# Telif hakkı © 2026 FlowCognition by suvilab.com — Tüm hakları saklıdır.
"""Yalnız döngüsel adreste çalışan, veri saklamayan geliştirme servisi."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
import json

from .dogrulama import GirdiHatasi, json_oku
from .motor import degerlendir, veri_oku

AZAMI_GOVDE = 256 * 1024


class IstekIsleyici(BaseHTTPRequestHandler):
    """Sabit dosya listesi ve aynı köken denetimiyle yerel HTTP köprüsü."""

    server_version = "FlowCognition/0.1"

    def log_message(self, bicim, *degerler):
        # Hasta verisi ve istek adresleri günlüğe yazılmaz.
        pass

    def adres_uygun(self):
        adres = f"127.0.0.1:{self.server.server_port}"
        if self.headers.get("Host") != adres:
            self.yanit(403, {"hata": "Yalnız yerel servis adresi kabul edilir."})
            return False
        koken = self.headers.get("Origin")
        if koken is not None and koken != f"http://{adres}":
            self.yanit(403, {"hata": "Farklı kökenden istek kabul edilmez."})
            return False
        return True

    def yanit(self, kod, veri, tur="application/json; charset=utf-8"):
        govde = json.dumps(veri, ensure_ascii=False, allow_nan=False).encode("utf-8") if isinstance(veri, (dict, list)) else veri
        self.send_response(kod)
        self.send_header("Content-Type", tur)
        self.send_header("Content-Length", str(len(govde)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'")
        self.end_headers()
        self.wfile.write(govde)

    def do_GET(self):
        if not self.adres_uygun():
            return
        if self.path == "/api/v1/bilgi":
            self.yanit(200, {"politika": veri_oku("politika.json"), "ciftler": veri_oku("ciftler.json"), "kaynaklar": veri_oku("kaynaklar.json")})
        elif self.path == "/api/v1/sema":
            self.yanit(200, veri_oku("istek.sema.json"))
        elif self.path == "/api/v1/ornek":
            self.yanit(200, veri_oku("ornek.json"))
        elif self.path in ("/", "/uygulama.js", "/gorunum.css"):
            ad, tur = {"/": ("index.html", "text/html"), "/uygulama.js": ("uygulama.js", "text/javascript"), "/gorunum.css": ("gorunum.css", "text/css")}[self.path]
            self.yanit(200, files("birlesik_hareket").joinpath("arayuz", ad).read_bytes(), tur + "; charset=utf-8")
        else:
            self.yanit(404, {"hata": "Adres bulunamadı."})

    def do_POST(self):
        if not self.adres_uygun():
            return
        if self.path != "/api/v1/degerlendir":
            self.yanit(404, {"hata": "Adres bulunamadı."})
            return
        if self.headers.get("Content-Type", "").split(";")[0].strip() != "application/json":
            self.yanit(415, {"hata": "application/json bekleniyor."})
            return
        if self.headers.get("Transfer-Encoding") or len(self.headers.get_all("Content-Length", [])) != 1:
            self.yanit(400, {"hata": "Tek Content-Length zorunludur."})
            return
        try:
            uzunluk = int(self.headers.get("Content-Length", ""))
            if not 0 < uzunluk <= AZAMI_GOVDE:
                self.yanit(413, {"hata": "İstek 1–262144 bayt arasında olmalı."})
                return
            self.connection.settimeout(5)
            ham = self.rfile.read(uzunluk)
            if len(ham) != uzunluk:
                raise GirdiHatasi("Eksik istek gövdesi.")
            self.yanit(200, degerlendir(json_oku(ham)))
        except (GirdiHatasi, ValueError) as hata:
            self.yanit(422, {"hata": str(hata)})
        except TimeoutError:
            self.yanit(408, {"hata": "İstek okuma süresi aşıldı."})


def sun(port=8765):
    if not 1 <= port <= 65535:
        raise GirdiHatasi("Port 1–65535 aralığında olmalı.")
    with ThreadingHTTPServer(("127.0.0.1", port), IstekIsleyici) as sunucu:
        print(f"Birleşik hareket arayüzü: http://127.0.0.1:{port}\nDurdurmak için Ctrl+C.")
        try:
            sunucu.serve_forever()
        except KeyboardInterrupt:
            pass
