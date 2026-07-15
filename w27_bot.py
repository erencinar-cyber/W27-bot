import requests
import datetime
import os
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
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
    # Bölme işleminden dolayı '<' işareti kaybolan etiketin artıklarını (class="..." vb.) '>' işaretine kadar siler
    metin = re.sub(r'^[^>]*>', '', metin)
    # Geriye kalan tüm normal HTML etiketlerini (<...>) siler
    metin = re.sub(r'<[^>]+>', ' ', metin)
    # Fazla boşlukları tek boşluğa indirir
    return " ".join(metin.split())

def yurt_kontrol():
    almanya_saati = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2)
    saat_str = almanya_saati.strftime("%H:%M")

    try:
        # Sanal Chrome Ayarları
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Tarayıcıyı başlat ve siteye git
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(W27_URL)
        
        # Tablonun yüklenmesi için 5 saniye bekle
        time.sleep(5)
        
        # Tam sayfa kodlarını al
        html = driver.page_source
        driver.quit() 
        
        bulunan_odalar = [] 
        
        satirlar = re.split(r'<tr', html, flags=re.IGNORECASE)
        if len(satirlar) < 3:
            satirlar = re.split(r'<div|<li', html, flags=re.IGNORECASE)
            
        for satir in satirlar:
            satir_kucuk = satir.lower()
            
            # Filtre menüsünü es geç, sadece gerçek ilanları al
            if "soon available" in satir_kucuk and "already taken" not in satir_kucuk and "book-property__control" not in satir_kucuk:
                saf_metin = html_temizle(satir)
                
                # Çok uzunsa kırp
                if len(saf_metin) > 300:
                    index = saf_metin.lower().find("soon available")
                    bas = max(0, index - 50)
                    son = min(len(saf_metin), index + 50)
                    saf_metin = "... " + saf_metin[bas:son] + " ..."
                    
                # Temiz metni listeye ekle
                if saf_metin and len(saf_metin) > 10:
                    bulunan_odalar.append(saf_metin)

        eski_odalar = []
        if os.path.exists(HAFIZA_DOSYASI):
            with open(HAFIZA_DOSYASI, "r", encoding="utf-8") as f:
                eski_odalar = [satir.strip() for satir in f.readlines() if satir.strip()]
        
        yeni_odalar = [oda for oda in bulunan_odalar if oda not in eski_odalar]
        
        if len(yeni_odalar) > 0:
            for oda_detayi in yeni_odalar:
                mesaj_gonder(f"🚨 [{saat_str}] DİKKAT! W27 Yurdunda YENİ BOŞ ODA!\n\nİlan Detayları:\n{oda_detayi}\n\n🔗 Hemen başvur: {W27_URL}")
            
            with open(HAFIZA_DOSYASI, "w", encoding="utf-8") as f:
                for oda in bulunan_odalar:
                    f.write(oda + "\n")
                    
        elif len(bulunan_odalar) == 0 and len(eski_odalar) > 0:
            with open(HAFIZA_DOSYASI, "w", encoding="utf-8") as f:
                f.write("")
                
        elif (almanya_saati.hour == 0 or almanya_saati.hour == 12) and almanya_saati.minute < 10:
            mesaj_gonder(f"ℹ️ [{saat_str}] Sistem çalışıyor, tarayıcı testi başarılı. Yeni boş oda YOK.")
            
    except Exception as e:
        mesaj_gonder(f"⚠️ [{saat_str}] HATA: Sanal tarayıcı başlatılamadı. Detay: {e}")

yurt_kontrol()
