# © 2026 FlowCognition by suvilab.com — Tüm hakları saklıdır.
"""Yerel servis ve JSON dosya işlemleri."""

import argparse
import json
from pathlib import Path
import sys
from .cozucu import planla
from .dogrulama import GirdiHatasi, json_oku
from .geometri import hareket_ayristir
from .kurallar import veri_oku
from .geri_bildirim import geri_bildirim_ozeti


def calistir():
    ayrac = argparse.ArgumentParser(description="Movement Budget Solver · Suvi Flow · Özel yazılım")
    komutlar = ayrac.add_subparsers(dest="islem",required=True)
    for ad in ("planla","ayristir","geri-bildirim"):
        komut = komutlar.add_parser(ad)
        komut.add_argument("dosya",type=Path)
        komut.add_argument("--cikti",type=Path)
        if ad == "planla":
            komut.add_argument("--politika",type=Path)
    komutlar.add_parser("ornek")
    sun = komutlar.add_parser("sun")
    sun.add_argument("--port",type=int,default=8766)
    secenek = ayrac.parse_args()
    try:
        if secenek.islem == "sun":
            from .sunucu import sun
            sun(secenek.port)
            return
        if secenek.islem == "ornek":
            sonuc = veri_oku("ornek.json")
        else:
            istek = json_oku(secenek.dosya.read_text(encoding="utf-8-sig"))
            if secenek.islem == "planla":
                politika = json_oku(secenek.politika.read_text(encoding="utf-8-sig")) if secenek.politika else None
                sonuc = planla(istek,politika)
            else:
                sonuc = hareket_ayristir(istek) if secenek.islem == "ayristir" else geri_bildirim_ozeti(istek)
        cikti = json.dumps(sonuc,ensure_ascii=False,indent=2,allow_nan=False)
        if getattr(secenek,"cikti",None):
            secenek.cikti.write_text(cikti+'\n',encoding='utf-8')
        else:
            sys.stdout.reconfigure(encoding="utf-8")
            print(cikti)
    except (OSError,GirdiHatasi) as hata:
        print(f"Hata: {hata}",file=sys.stderr)
        raise SystemExit(2) from hata


if __name__ == "__main__":
    calistir()
