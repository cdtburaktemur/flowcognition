# © 2026 FlowCognition by suvilab.com — Tüm hakları saklıdır.
"""CAD girdi şemasını üretir; çapraz alan kısıtları çalışma anında denetlenir."""

import json
from pathlib import Path


def nesne(alanlar, istege_bagli=()):
    return {"type":"object","properties":alanlar,"required":[a for a in alanlar if a not in istege_bagli],"additionalProperties":False}


def secim(*degerler):
    return {"type":"string","enum":list(degerler)}


def sayi(alt,ust):
    return {"type":"number","minimum":alt,"maximum":ust}


def vektor(n):
    return {"type":"array","minItems":n,"maxItems":n,"items":sayi(-1e6,1e6)}


eksenler = ("md_mm","bl_mm","ie_mm","rotasyon_derece","tip_derece","tork_derece")
metin = {"type":"string","minLength":1,"maxLength":200,"pattern":"\\S"}
fdi = {"type":"integer","enum":[10*k+d for k in range(1,5) for d in range(1,9)]}
poz = nesne({"konum_mm":vektor(3),"quaternion":vektor(4)})
donusum = nesne({"baslangic":poz,"hedef":poz,"cerceve_quaternion":vektor(4),"klinik_isaretler":nesne({a:{"type":"integer","enum":[-1,1]} for a in eksenler})})
dis = nesne({"fdi":fdi,"hareket":nesne({a:sayi(-30,30) if a.endswith("mm") else sayi(-179,179) for a in eksenler}),"atasman":secim("yok","planli","bilinmiyor"),"periodontal":secim("normal","azalmis","aktif_hastalik","bilinmiyor"),"kok":secim("uygun","riskli","bilinmiyor"),"komsu_temas":secim("uygun","dar","riskli","bilinmiyor"),"okluzal_temas":secim("uygun","riskli","bilinmiyor"),"destek_disleri":{"type":"array","uniqueItems":True,"items":fdi},"kilitli":{"type":"boolean"},"donusum":donusum},("donusum",))
sema = nesne({"surum":{"const":"1.0"},"vaka_kimligi":metin,"koordinat":{"const":"suvi_yerel_v1"},"geometri_revizyonu":metin,"tam_ark":{"type":"boolean"},"ankraj":secim("uzman_degerlendirdi","yetersiz","bilinmiyor"),"strateji":secim("paralel","distal_yuzde50"),"azami_asama":{"type":"integer","minimum":1,"maximum":500},"disler":{"type":"array","minItems":1,"maxItems":16,"items":dis}})
sema.update({"$schema":"https://json-schema.org/draft/2020-12/schema","title":"Suvi Flow hareket bütçesi isteği","$comment":"FDI tekilliği, tek çene, destek referansları, quaternion normu, dönme normu ve dönüşüm/hareket tutarlılığı çalışma anında ayrıca doğrulanır. © 2026 FlowCognition by suvilab.com"})
(Path(__file__).resolve().parents[1]/'hareket_butcesi/veri/istek.sema.json').write_text(json.dumps(sema,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
