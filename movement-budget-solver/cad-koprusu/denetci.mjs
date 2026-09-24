/* © 2026 FlowCognition by suvilab.com — Tüm hakları saklıdır. */
/** CAD'in kendi BVH/yol denetimini sürümlü aday sözleşmesine bağlar.
 * BVH algoritması değildir. yolDenetle tüm yol, kök/kemik ve karşıt arkı denetlemelidir.
 * Python GeometriDenetcisi ile aradaki taşıma katmanını CAD sağlar.
 */
export function denetciOlustur({ geometriRevizyonu, denetciAdi, yolDenetle }) {
  if (typeof yolDenetle !== "function" || !geometriRevizyonu || !denetciAdi) throw new Error("Denetçi, revizyon ve yol denetimi gerekli.");
  return async function denetle(aday) {
    const temel = { aday_ozeti: aday.aday_ozeti, geometri_revizyonu: geometriRevizyonu, denetci: denetciAdi };
    if (aday.geometri_revizyonu !== geometriRevizyonu) throw new Error("Geometri revizyonu uyuşmuyor.");
    if (aday.disler.some(dis => !dis.baslangic_pozu || !dis.bitis_pozu)) {
      return { ...temel, durum: "bilinmiyor", yol_denetlendi: false, sorunlu_disler: [], aciklama: "Başlangıç ve bitiş pozları eksik." };
    }
    const sonuc = await yolDenetle(structuredClone(aday.disler));
    if (sonuc.yol_denetlendi !== true || !["uygun", "carpisma"].includes(sonuc.durum)) {
      return { ...temel, durum: "bilinmiyor", yol_denetlendi: false, sorunlu_disler: [], aciklama: "Yol denetimi tamamlanmadı." };
    }
    if (!Array.isArray(sonuc.sorunlu_disler) || sonuc.sorunlu_disler.some(fdi => !aday.disler.some(dis => dis.fdi === fdi))) throw new Error("Geçersiz sorunlu diş listesi.");
    if (sonuc.durum === "uygun" && sonuc.sorunlu_disler.length) throw new Error("Uygun yanıtta sorunlu diş olamaz.");
    return { ...temel, durum: sonuc.durum, yol_denetlendi: true, sorunlu_disler: sonuc.sorunlu_disler, aciklama: sonuc.aciklama || "CAD yol denetimi tamamlandı." };
  };
}
