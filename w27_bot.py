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

def html_temizle(metin):
    # Tüm HTML kodlarını ( <...> şeklindeki her şeyi) boşlukla değiştirir
    metin = re.sub(r'<[^>]+>', ' ', metin)
    # Fazla boşlukları tek boşluğa indirir
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
        
        bulunan_odalar = [] 
        
        # Siteyi satırlara ayırıyoruz
        satirlar = re.split(r'<tr', html, flags=re.IGNORECASE)
        
        # Eğer site tablo (tr) kullanmıyorsa B planı olarak sayfayı farklı bloklara bölelim
        if len(satirlar) < 3:
            satirlar = re.split(r'<div|<li', html, flags=re.IGNORECASE)
            
        for satir in satirlar:
            if "soon available" in satir.lower():
                # O satırdaki bütün gizli kodları silip saf metni alıyoruz
                saf_metin = html_temizle(satir)
                
                # Eğer kod tüm sayfayı tek satır sandıysa (çok uzunsa) sadece ilanın olduğu kısmı kırp
                if len(saf_metin) > 300:
                    index = saf_metin.lower().find("soon available")
                    bas = max(0, index - 50)
                    son = min(len(saf_metin), index + 50)
                    saf_metin = "... " + saf_metin[bas:son] + " ..."
                    
                if saf_metin:
                    bulunan_odalar.append(saf_metin)

        # 1. Hafızadaki ESKİ odaları oku
        eski_odalar = []
        if os.path.exists(HAFIZA_DOSYASI):
            with open(HAFIZA_DOSYASI, "r", encoding="utf-8") as f:
                eski_odalar = [satir.strip() for satir in f.readlines() if satir.strip()]
        
        # 2. Sadece hafızada OLMAYAN (yepyeni açılan) odaları tespit et
        yeni_odalar = [oda for oda in bulunan_odalar if oda not in eski_odalar]
        
        # 3. YENİ bir oda varsa mesaj at!
        if len(yeni_odalar) > 0:
            for oda_detayi in yeni_odalar:
                mesaj_gonder(f"🚨 [{saat_str}] DİKKAT! W27 Yurdunda YENİ BOŞ ODA!\n\nİlan Detayları:\n{oda_detayi}\n\n🔗 Hemen başvur: {W27_URL}")
            
            # Güncel oda listesini hafızaya kaydet
            with open(HAFIZA_DOSYASI, "w", encoding="utf-8") as f:
                for oda in bulunan_odalar:
                    f.write(oda + "\n")
                    
        # 4. Bütün odalar kapıldıysa hafızayı sıfırla ki döngü yenilensin
        elif len(bulunan_odalar) == 0 and len(eski_odalar) > 0:
            with open(HAFIZA_DOSYASI, "w", encoding="utf-8") as f:
                f.write("")
                
        # 5. Gece 00.00 veya Öğlen 12.00 durum raporu (İstersen saati değiştirebilirsin)
        elif (almanya_saati.hour == 0 or almanya_saati.hour == 12) and almanya_saati.minute < 10:
            mesaj_gonder(f"ℹ️ [{saat_str}] Sistem çalışıyor, kontrol yapıldı. Yeni boş oda YOK.")
            
    except Exception as e:
        mesaj_gonder(f"⚠️ [{saat_str}] HATA: Siteye bağlanılamadı. Detay: {e}")

yurt_kontrol()
