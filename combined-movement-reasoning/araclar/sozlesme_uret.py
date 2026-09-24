# Telif hakkı © 2026 FlowCognition by suvilab.com — Tüm hakları saklıdır.
"""Girdi şemasını ve tamamen sentetik örneği üretir."""

import json
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
VERI = KOK / "birlesik_hareket" / "veri"


def secim(*degerler):
    return {"type": "string", "enum": list(degerler)}


def nesne(alanlar):
    return {"type": "object", "properties": alanlar, "required": list(alanlar), "additionalProperties": False}


def sayi(alt, ust):
    return {"type": "number", "minimum": alt, "maximum": ust}


hareket = nesne({
    "otelemenin_mesial_bileseni_mm": sayi(-10, 10),
    "otelemenin_bukkal_bileseni_mm": sayi(-10, 10),
    "rotasyon_derece": sayi(-45, 45),
    "tip_derece": sayi(-45, 45),
    "tork_derece": sayi(-45, 45),
    "intruzyon_mm": sayi(0, 5),
})
dis = nesne({
    "fdi": {"type": "integer", "enum": [10 * k + d for k in range(1, 5) for d in range(1, 9)]},
    "hareket": hareket,
    "periodontal": secim("normal", "azalmis_destek", "aktif_hastalik", "bilinmiyor"),
    "kok_kemik": secim("uygun", "riskli", "bilinmiyor"),
    "temas_yolu": secim("uygun", "riskli", "bilinmiyor"),
    "atasman": secim("planli", "yok", "bilinmiyor"),
    "toplam_rotasyon_derece": sayi(0, 180),
})
sema = nesne({
    "sozlesme_surumu": {"const": "1.0"},
    "asama_kimligi": {"type": "string", "minLength": 1, "maxLength": 120, "pattern": "\\S"},
    "koordinat_sistemi": {"const": "dis_yerel_klinik_v1"},
    "baglam": nesne({
        "tam_ark": {"type": "boolean"},
        "ankraj": secim("uygun", "yetersiz", "bilinmiyor"),
        "plak_oturmasi": secim("uygun", "uyumsuz", "bilinmiyor"),
        "kok_degerlendirmesi": secim("uygun", "yetersiz", "bilinmiyor"),
        "materyal_protokolu": secim("uygun", "yetersiz", "bilinmiyor"),
        "cekimli_vaka": {"type": "boolean"},
    }),
    "disler": {"type": "array", "minItems": 1, "maxItems": 32, "items": dis},
})
sema.update({"$schema": "https://json-schema.org/draft/2020-12/schema", "title": "Birleşik hareket aşama isteği", "$comment": "FDI tekilliği, tek çene ve toplam rotasyon tutarlılığı ayrıca çalışma anında doğrulanır."})
ornek = {"sozlesme_surumu": "1.0", "asama_kimligi": "sentetik-asama-01", "koordinat_sistemi": "dis_yerel_klinik_v1",
         "baglam": {"tam_ark": True, "ankraj": "uygun", "plak_oturmasi": "uygun", "kok_degerlendirmesi": "uygun", "materyal_protokolu": "uygun", "cekimli_vaka": False}, "disler": []}
for fdi in [11, 12, 13, 14, 15, 16, 17, 21, 22, 23, 24, 25, 26, 27]:
    oge = {"fdi": fdi, "hareket": {alan: 0 for alan in hareket["properties"]}, "periodontal": "normal", "kok_kemik": "uygun", "temas_yolu": "uygun", "atasman": "yok", "toplam_rotasyon_derece": 0}
    if fdi == 16:
        oge["hareket"].update(otelemenin_mesial_bileseni_mm=-0.1, rotasyon_derece=0.4)
        oge.update(atasman="planli", toplam_rotasyon_derece=8)
    ornek["disler"].append(oge)
for ad, deger in (("istek.sema.json", sema), ("ornek.json", ornek)):
    (VERI / ad).write_text(json.dumps(deger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
