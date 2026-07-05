import requests
import datetime
import os
import re

TOKEN = "8946108216:AAEFSr85bhDIuvui8ZK_xGf1kuL1bE0oJwI"
CHAT_ID = "-1004436817775"
W27_URL = "https://www.apartments-hn.de/en/book-apartment/"
HAFIZA_DOSYASI = "hafiza.txt"

def mesaj_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mesaj}
    try:
        requests.post(url, data=payload)
    except:
        pass

# HTML etiketlerini ve fazlalık boşlukları temizleyen yardımcı fonksiyon
def html_temizle(metin):
    metin = re.sub(r'<br\s*/?>', ' ', metin, flags=re.IGNORECASE)
    metin = re.sub(r'<[^>]+>', '', metin)
    return " ".join(metin.split())

def yurt_kontrol():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # Almanya saatini hesapla (UTC+2)
    almanya_saati = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2)
    saat_str = almanya_saati.strftime("%H:%M")

    try:
        cevap = requests.get(W27_URL, headers=headers)
        html = cevap.text
        
        # --- TEST KODU BAŞLANGICI ---
        kelime_sayisi = html.lower().count("soon available")
        mesaj_gonder(f"🕵️ TEST RAPORU [{saat_str}]: Bot siteyi okudu. Sitenin kodlarında 'soon available' kelimesini tam {kelime_sayisi} kez buldu.")
        # --- TEST KODU BİTİŞİ ---
        
        bulunan_odalar = {} # Odanın numarasını ve detaylarını tutacağımız sözlük
        
        satirlar = html.split('<tr')
        for satir in satirlar:
            if "soon available" in satir.lower():
                # Satırdaki tüm <td> (hücre) etiketlerini buluyoruz
                hucreler = re.findall(r'<td[^>]*>(.*?)</td>', satir, re.IGNORECASE | re.DOTALL)
                
                # Tabloda 6 sütun var, hepsini başarıyla çektiysek:
                if len(hucreler) >= 6:
                    oda_no = html_temizle(hucreler[0])
                    ozellik = html_temizle(hucreler[1])
                    cadde = html_temizle(hucreler[2])
                    metrekare = html_temizle(hucreler[3])
                    fiyat = html_temizle(hucreler[4])
                    durum_kutusu = html_temizle(hucreler[5])
                    
                    # Tarihi durum kutusunun içinden (örn: 2026-08-01) bulup çıkartıyoruz
                    tarih_match = re.search(r'\d{4}-\d{2}-\d{2}', durum_kutusu)
                    tarih = tarih_match.group(0) if tarih_match else "Belirtilmemiş"
                    
                    if oda_no:
                        detay = (f"🚪 Oda: {oda_no}\n"
                                 f"🛏 Özellik: {ozellik}\n"
                                 f"📍 Konum: {cadde}\n"
                                 f"📏 Boyut: {metrekare} m²\n"
                                 f"💶 Fiyat: {fiyat} €\n"
                                 f"📅 Tarih: {tarih}")
                        bulunan_odalar[oda_no] = detay

        # 1. Hafızadaki ESKİ odaları oku
        eski_odalar = []
        if os.path.exists(HAFIZA_DOSYASI):
            with open(HAFIZA_DOSYASI, "r", encoding="utf-8") as f:
                eski_odalar = [satir.strip() for satir in f.readlines() if satir.strip()]
        
        # 2. Sadece hafızada OLMAYAN (yepyeni açılan) odaları tespit et
        yeni_odalar = [oda_no for oda_no in bulunan_odalar.keys() if oda_no not in eski_odalar]
        
        # 3. YENİ bir oda varsa mesaj at!
        if len(yeni_odalar) > 0:
            for yeni_oda in yeni_odalar:
                oda_detayi = bulunan_odalar[yeni_oda]
                mesaj_gonder(f"🚨 [{saat_str}] DİKKAT! W27 Yurdunda YENİ BOŞ ODA!\n\n{oda_detayi}\n\n🔗 Hemen başvur: {W27_URL}")
            
            # Güncel oda listesini hafızaya kaydet
            with open(HAFIZA_DOSYASI, "w", encoding="utf-8") as f:
                for oda in bulunan_odalar.keys():
                    f.write(oda + "\n")
                    
        # 4. Bütün odalar kapıldıysa hafızayı sıfırla ki döngü yenilensin
        elif len(bulunan_odalar) == 0 and len(eski_odalar) > 0:
            with open(HAFIZA_DOSYASI, "w", encoding="utf-8") as f:
                f.write("")
                
        # 5. Gece 00.00, 04.00 veya Öğlen 12.00 durum raporu (Mesaj atılmadıysa)
        elif (almanya_saati.hour == 0 or almanya_saati.hour == 4 or almanya_saati.hour == 12) and almanya_saati.minute < 10:
            mesaj_gonder(f"ℹ️ [{saat_str}] Sistem tıkır tıkır çalışıyor, kontrol yapıldı. Yeni boş oda YOK.")
            
    except Exception as e:
        mesaj_gonder(f"⚠️ [{saat_str}] HATA: Siteye bağlanılamadı. Detay: {e}")

yurt_kontrol()
