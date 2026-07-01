import requests
import datetime

# Eğer kanala geçtiysen kanalın ID'sini, geçmediysen kendi ID'ni kullan
TOKEN = "8946108216:AAEFSr85bhDIuvui8ZK_xGf1kuL1bE0oJwI"
CHAT_ID = "8324006530" 
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
        
        if "There are currently no more units available" not in sayfa_icerigi:
            mesaj_gonder("🚨 W27 yurdunda boş oda açılmış olabilir! Hemen linke tıkla ve kontrol et: " + W27_URL)
            
    except Exception as e:
        pass # GitHub Actions hata durumunda kendi kendine tekrar deneyeceği için burayı sessiz geçiyoruz

# Saat uyarısını da düzelttik, artık güncel UTC formatını kullanıyoruz
almanya_saati = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2)

# Sistem her 10 dakikada bir çalışacağı için, saat 00:00 ile 00:10 arasına denk gelen o tek seferde gece raporu atacak
if almanya_saati.hour == 0 and 0 <= almanya_saati.minute < 10:
    mesaj_gonder("🌙 İyi geceler Erenciğim, GitHub üzerinden W27 nöbetine sorunsuz devam ediyorum!")

yurt_kontrol()
