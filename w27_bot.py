import requests
import time

TOKEN = "8946108216:AAEFSr85bhDIuvui8ZK_xGf1kuL1bE0oJwI"
CHAT_ID = "8324006530" # Eğer kanala geçtiysen kanalın ID'sini yazmayı unutma
W27_URL = "https://www.apartments-hn.de/en/book-apartment/"

def mesaj_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": mesaj})

headers = {"User-Agent": "Mozilla/5.0"}

mesaj_gonder("🛠️ TEST BAŞLADI: Yurdun sitesine girip yazıyı okuyacağım...")

# Siteyi 3 kez kontrol edecek döngü
for i in range(3):
    try:
        cevap = requests.get(W27_URL, headers=headers)
        
        # Eğer "boş ev yok" yazısı SİTEDE VARSA:
        if "There are currently no more units available" in cevap.text:
            mesaj_gonder(f"🔍 Deneme {i+1}: Sitedeyim. 'Boş ev yok' yazısını bizzat gördüm. Sistem kusursuz.")
        else:
            mesaj_gonder(f"🚨 DİKKAT! O uyarı yazısı kaybolmuş!")
    except Exception as e:
        mesaj_gonder(f"Bağlantı hatası: {e}")
        
    time.sleep(10) # Ban yememek için 10 saniye bekle

mesaj_gonder("✅ TEST BİTTİ. İçin rahat olsun, bot kör değil. Lütfen GitHub'a eski orijinal kodu geri yapıştır!")
