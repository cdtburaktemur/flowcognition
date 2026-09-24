# © 2026 FlowCognition by suvilab.com — Tüm hakları saklıdır.
"""Yalnız yerel arayüz. CAD denetçisi bağlı olmayan taslak uç noktası."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
import json
from .cozucu import planla
from .dogrulama import GirdiHatasi, json_oku
from .geometri import hareket_ayristir
from .kurallar import veri_oku, kurallari_yukle
from .geri_bildirim import geri_bildirim_ozeti


class IstekIsleyici(BaseHTTPRequestHandler):
    server_version = "SuviFlow/0.1"

    def log_message(self, *args):
        pass

    def yanit(self,kod,veri,tur="application/json; charset=utf-8"):
        govde = veri if isinstance(veri,bytes) else json.dumps(veri,ensure_ascii=False,allow_nan=False).encode()
        self.send_response(kod)
        self.send_header("Content-Type",tur)
        self.send_header("Content-Length",str(len(govde)))
        self.send_header("Cache-Control","no-store")
        self.send_header("X-Content-Type-Options","nosniff")
        self.send_header("Content-Security-Policy","default-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'")
        self.end_headers()
        self.wfile.write(govde)

    def koken_uygun(self):
        adres = f"127.0.0.1:{self.server.server_port}"
        if self.headers.get("Host") != adres or self.headers.get("Origin",f"http://{adres}") != f"http://{adres}":
            self.yanit(403,{"hata":"Yalnız aynı yerel köken kabul edilir."})
            return False
        return True

    def do_GET(self):
        if not self.koken_uygun():
            return
        if self.path == "/api/v1/ornek":
            self.yanit(200,veri_oku("ornek.json"))
        elif self.path == "/api/v1/bilgi":
            self.yanit(200,{"politika":kurallari_yukle(),"kaynaklar":veri_oku("kaynaklar.json")})
        elif self.path == "/api/v1/sema":
            self.yanit(200,veri_oku("istek.sema.json"))
        elif self.path in ("/","/uygulama.js","/gorunum.css"):
            ad,tur = {"/":("index.html","text/html"),"/uygulama.js":("uygulama.js","text/javascript"),"/gorunum.css":("gorunum.css","text/css")}[self.path]
            self.yanit(200,files("hareket_butcesi").joinpath("arayuz",ad).read_bytes(),tur+"; charset=utf-8")
        else:
            self.yanit(404,{"hata":"Adres bulunamadı."})

    def do_POST(self):
        if not self.koken_uygun():
            return
        islemler = {"/api/v1/planla":planla,"/api/v1/ayristir":hareket_ayristir,"/api/v1/geri-bildirim":geri_bildirim_ozeti}
        if self.path not in islemler:
            self.yanit(404,{"hata":"Adres bulunamadı."})
            return
        try:
            if self.headers.get("Transfer-Encoding") or len(self.headers.get_all("Content-Length",[]))!=1:
                self.yanit(400,{"hata":"Tek Content-Length gerekli."})
                return
            uzunluk = int(self.headers["Content-Length"])
            if not 0 < uzunluk <= 262144:
                self.yanit(413,{"hata":"İstek boyutu 1–262144 bayt olmalı."})
                return
            self.connection.settimeout(5)
            ham = self.rfile.read(uzunluk)
            if len(ham) != uzunluk:
                raise GirdiHatasi("Eksik istek gövdesi.")
            if self.headers.get("Content-Type","").split(";")[0].strip() != "application/json":
                self.yanit(415,{"hata":"application/json gerekli."})
                return
            self.yanit(200,islemler[self.path](json_oku(ham)))
        except (ValueError,UnicodeError) as hata:
            self.yanit(422,{"hata":str(hata)})
        except TimeoutError:
            self.yanit(408,{"hata":"Okuma süresi aşıldı."})


def sun(port=8766):
    if type(port) is not int or not 1<=port<=65535:
        raise GirdiHatasi("Geçerli port bekleniyor.")
    with ThreadingHTTPServer(("127.0.0.1",port),IstekIsleyici) as sunucu:
        print(f"Movement Budget Solver: http://127.0.0.1:{port}/ — Durdurmak için Ctrl+C.",flush=True)
        try:
            sunucu.serve_forever()
        except KeyboardInterrupt:
            pass
