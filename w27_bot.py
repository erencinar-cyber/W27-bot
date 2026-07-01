import requests
import datetime

TOKEN = "8946108216:AAEFSr85bhDIuvui8ZK_xGf1kuL1bE0oJwI"
CHAT_ID = "8324006530" # Kanal ID'sine geçtiysen eksi (-) işaretli ID'yi yazmayı unutma
W27_URL = "https://www.apartments-hn.de/en/book-apartment/"

def mesaj_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mesaj}
    try:
        requests.post(url, data=payload)
    except:
        pass

def yurt_kontrol():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        cevap = requests.get(W27_URL, headers=headers)
        sayfa_icerigi = cevap.text
        
        # Eğer yurdun sitesindeki o olumsuz yazı ortadan kalkarsa:
        if "There are currently no more units available" not in sayfa_icerigi:
            mesaj_gonder("🚨 W27 yurdunda boş oda açılmış olabilir! Hemen linke tıkla ve kontrol et: " + W27_URL)
            
    except Exception as e:
        pass 

# Almanya Saati Hesaplama (UTC+2)
almanya_saati = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2)

# Her sabah 04:22 ile 04:33 arasındaki o ilk sorguda günaydın raporu gönderir
if almanya_saati.hour == 4 and 29 <= almanya_saati.minute < 40:
    mesaj_gonder("☀️ Günaydın Erenciğim, ev hala yok ama ben nöbetteyim!")

# Web sitesini kontrol eden asıl fonksiyonu tetikliyoruz
yurt_kontrol()
