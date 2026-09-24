# Telif hakkı © 2026 FlowCognition by suvilab.com — Tüm hakları saklıdır.
"""Dosya veya yerel servis üzerinden kullanım."""

import argparse
import json
from pathlib import Path
import sys

from .dogrulama import GirdiHatasi, json_oku
from .motor import degerlendir


def calistir():
    ayrac = argparse.ArgumentParser(description="Birleşik hareket karar desteği — özel yazılım")
    alt = ayrac.add_subparsers(dest="islem", required=True)
    incele = alt.add_parser("degerlendir", help="Bir aşama JSON dosyasını değerlendir")
    incele.add_argument("dosya", type=Path)
    incele.add_argument("--cikti", type=Path)
    sun = alt.add_parser("sun", help="Yerel değerlendirme arayüzünü başlat")
    sun.add_argument("--port", type=int, default=8765)
    secenek = ayrac.parse_args()
    try:
        if secenek.islem == "sun":
            from .sunucu import sun
            sun(secenek.port)
            return
        sonuc = degerlendir(json_oku(secenek.dosya.read_text(encoding="utf-8-sig")))
        cikti = json.dumps(sonuc, ensure_ascii=False, indent=2, allow_nan=False)
        if secenek.cikti:
            secenek.cikti.write_text(cikti + "\n", encoding="utf-8")
        else:
            sys.stdout.reconfigure(encoding="utf-8")
            print(cikti)
    except (GirdiHatasi, OSError) as hata:
        print(f"Hata: {hata}", file=sys.stderr)
        raise SystemExit(2) from hata


if __name__ == "__main__":
    calistir()
