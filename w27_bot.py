import requests
import datetime

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
    
    # Almanya saatini hesapla (UTC+2)
    almanya_saati = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2)
    saat_str = almanya_saati.strftime("%H:%M")

    try:
        cevap = requests.get(W27_URL, headers=headers)
        sayfa_icerigi = cevap.text
        
        # Sitede uyarı yazısı VARSA:
        if "There are currently no more units available" in sayfa_icerigi:
            mesaj_gonder(f"ℹ️ [{saat_str}] Durum Raporu: W27 sitesi kontrol edildi. Şu an boş oda YOK.")
        # Sitede uyarı yazısı YOKSA (Ev açıldıysa):
        else:
            mesaj_gonder(f"🚨 [{saat_str}] DİKKAT! W27 yurdunda boş oda açılmış olabilir! Hemen linke tıkla: {W27_URL}")
            
    except Exception as e:
        mesaj_gonder(f"⚠️ [{saat_str}] HATA: Siteye bağlanılamadı. GitHub ban yemiş olabilir! Detay: {e}")

# Kodu çalıştır
yurt_kontrol()
