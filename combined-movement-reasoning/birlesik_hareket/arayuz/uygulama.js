/* © 2026 FlowCognition by suvilab.com — Tüm hakları saklıdır. */
"use strict";
const sec = (kimlik) => document.getElementById(kimlik);
const adlar = {oteleme:"Öteleme",rotasyon:"Rotasyon",tip:"Tip",tork:"Tork",intruzyon:"İntrüzyon"};
const durumlar = {hareket_yok:"Hareket yok",kosullu_aday:"Koşullu aday · klinik onay değil",uzman_incelemesi:"Uzman incelemesi",ayirma_degerlendirilmeli:"Ayrı aşamalar değerlendirilmeli",veri_yetersiz:"Veri yetersiz",engellendi:"Değerlendirme engellendi"};
const kanitlar = {dolayli_klinik:"Dolaylı klinik kanıt",biyomekanik_cikarim:"Biyomekanik çıkarım",dolayli_sonlu_eleman:"Dolaylı sonlu eleman bulgusu",sonlu_eleman:"Sonlu eleman bulgusu",muhendislik_ihtiyati:"Mühendislik ihtiyatı",dolayli_kanit_ve_ihtiyat:"Dolaylı kanıt ve ihtiyat"};
const alanlar = {otelemenin_mesial_bileseni_mm:"Mesial (+) / distal (−) · mm",otelemenin_bukkal_bileseni_mm:"Bukkal (+) / lingual (−) · mm",rotasyon_derece:"Rotasyon · derece",tip_derece:"Mesial kron tipi (+) · derece",tork_derece:"Bukkal kron açısı (+) · derece",intruzyon_mm:"İntrüzyon (+) · mm"};
let veri, sonSonuc;
function oge(tur, metin, sinif) { const sonuc=document.createElement(tur); if(metin!==undefined)sonuc.textContent=metin;if(sinif)sonuc.className=sinif;return sonuc; }
function gecersizKil(){sonSonuc=undefined;sec("indir").disabled=true;sec("sonuc").replaceChildren(oge("p","Girdi değişti. Güncel sonuç için yeniden değerlendirin."));}
function jsonYaz(){sec("girdi").value=JSON.stringify(veri,null,2);gecersizKil();}
function disGoster(){
 const dis=veri.disler.find(d=>d.fdi===Number(sec("dis").value));sec("alanlar").replaceChildren();if(!dis)return;
 for(const [alan,baslik] of Object.entries(alanlar)){
  const kutu=oge("div"),etiket=oge("label",baslik),girdi=oge("input");etiket.htmlFor=alan;girdi.id=alan;girdi.type="number";girdi.step=alan.endsWith("mm")?"0.01":"0.1";girdi.value=dis.hareket[alan];
  girdi.addEventListener("input",()=>{dis.hareket[alan]=girdi.value===""?null:Number(girdi.value);jsonYaz();});kutu.append(etiket,girdi);sec("alanlar").append(kutu);
 }
}
function formKur(){
 if(!veri||!Array.isArray(veri.disler)||veri.disler.length===0||veri.disler.some(d=>!d||typeof d.hareket!=="object"||d.hareket===null))throw new Error("Diş listesi ve hareket nesneleri gerekli.");
 sec("dis").replaceChildren(...veri.disler.map(d=>{const o=oge("option",`Diş ${d.fdi}`);o.value=d.fdi;return o;}));
 sec("dis").value=veri.disler.some(d=>d.fdi===16)?16:veri.disler[0].fdi;disGoster();
}
async function ornekYukle(){try{veri=await (await fetch("/api/v1/ornek")).json();formKur();sec("dis").disabled=false;jsonYaz();sec("hata").textContent="";}catch(hata){sec("hata").textContent=hata.message;}}
sec("ornek").addEventListener("click",ornekYukle);sec("dis").addEventListener("change",disGoster);
sec("girdi").addEventListener("input",()=>{gecersizKil();sec("alanlar").replaceChildren(oge("p","JSON düzenleniyor. Hızlı alanları güncellemek için forma aktarın."));sec("dis").disabled=true;});
sec("aktar").addEventListener("click",()=>{try{veri=JSON.parse(sec("girdi").value);formKur();sec("dis").disabled=false;gecersizKil();sec("hata").textContent="";}catch(hata){sec("hata").textContent=hata.message;}});
sec("degerlendir").addEventListener("click",async()=>{
 sec("hata").textContent="";sec("degerlendir").disabled=true;gecersizKil();
 try{
  const gonderilen=sec("girdi").value;
  const yanit=await fetch("/api/v1/degerlendir",{method:"POST",headers:{"Content-Type":"application/json"},body:gonderilen});const sonuc=await yanit.json();if(!yanit.ok)throw new Error(sonuc.hata);
  if(sec("girdi").value!==gonderilen)throw new Error("Değerlendirme sırasında girdi değişti; yeniden değerlendirin.");
  sonSonuc=sonuc;sec("indir").disabled=false;const hedef=sec("sonuc");hedef.replaceChildren(oge("div",durumlar[sonuc.durum],`durum ${sonuc.durum}`),oge("p",sonuc.aciklama));
  for(const b of sonuc.ark_bulgulari){const kutu=oge("div",undefined,"bulgu");kutu.append(oge("strong",`Ark · ${b.kod}`),oge("p",b.gerekce));hedef.append(kutu);}
  for(const d of sonuc.disler.filter(d=>d.durum!=="hareket_yok")){
   const kutu=oge("div",undefined,"bulgu");kutu.append(oge("h3",`Diş ${d.fdi} · ${durumlar[d.durum]}`));
   for(const b of [...d.ciftler,...d.bulgular]){kutu.append(oge("p",b.gerekce),oge("div",`${kanitlar[b.kanit]||"Veri / politika denetimi"} · ${b.kaynaklar.join(", ")||"Mühendislik kuralı"}`,"kucuk"));}
   kutu.append(oge("p",`Doğrusal bileşke: ${d.olcumler.dogrusal_bileske_mm.toFixed(3)} mm · Normalize talep: ${d.olcumler.normalize_kareler_toplami.toFixed(3)} (olasılık değildir)`,"kucuk"));hedef.append(kutu);
  }
  hedef.append(oge("p",`Politika: ${sonuc.politika.kimlik} · Klinik doğrulama: yok`,"kucuk"));
 }catch(hata){sec("hata").textContent=hata.message;sec("sonuc").replaceChildren(oge("p","Değerlendirme üretilemedi."));}finally{sec("degerlendir").disabled=false;}
});
sec("indir").addEventListener("click",()=>{if(!sonSonuc)return;const adres=URL.createObjectURL(new Blob([JSON.stringify(sonSonuc,null,2)],{type:"application/json"}));const bag=oge("a");bag.href=adres;bag.download="hareket-degerlendirmesi.json";bag.click();setTimeout(()=>URL.revokeObjectURL(adres),1000);});
async function bilgiYukle(){
 try{const bilgi=await(await fetch("/api/v1/bilgi")).json();for(const cift of bilgi.ciftler){const satir=oge("tr");satir.append(oge("td",cift.hareketler.map(h=>adlar[h]).join(" + ")),oge("td",durumlar[cift.durum]),oge("td",`${kanitlar[cift.kanit]} · ${cift.kaynaklar.join(", ")}`));sec("ciftler").append(satir);}
 for(const k of bilgi.kaynaklar){const kutu=oge("div",undefined,"kaynak"),bag=oge("a",`${k.kimlik} · ${k.yil} · ${k.baslik}`);bag.href=k.baglanti;bag.target="_blank";bag.rel="noopener noreferrer";kutu.append(bag,oge("p",k.bulgu),oge("p",k.sinir));sec("kaynaklar").append(kutu);}}
 catch(hata){sec("hata").textContent=`Kaynaklar yüklenemedi: ${hata.message}`;}
}
ornekYukle();bilgiYukle();
