# © 2026 FlowCognition by suvilab.com — Tüm hakları saklıdır.
"""Gerçek hasta içermeyen örnek vaka üretimi."""

import json
from pathlib import Path

kok = Path(__file__).resolve().parents[1]
eksenler = ("md_mm", "bl_mm", "ie_mm", "rotasyon_derece", "tip_derece", "tork_derece")
ornek = {"surum":"1.0", "vaka_kimligi":"sentetik-kanin-01", "koordinat":"suvi_yerel_v1", "geometri_revizyonu":"sentetik-geometri-1", "tam_ark":True, "ankraj":"uzman_degerlendirdi", "strateji":"paralel", "azami_asama":200, "disler":[]}
for fdi in [11,12,13,14,15,16,17,21,22,23,24,25,26,27]:
    dis = {"fdi":fdi,"hareket":dict.fromkeys(eksenler,0),"atasman":"yok","periodontal":"normal","kok":"uygun","komsu_temas":"uygun","okluzal_temas":"uygun","destek_disleri":[],"kilitli":False}
    if fdi == 13:
        dis["hareket"] = dict(zip(eksenler,[-2.8,.65,.4,17.5,4.2,-6.8]))
        dis["destek_disleri"] = [16,26]
    ornek["disler"].append(dis)
(kok / 'hareket_butcesi/veri/ornek.json').write_text(json.dumps(ornek,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
