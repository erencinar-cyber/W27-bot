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
        # Sitedeki tüm yazıları küçük harfe çeviriyoruz ki büyük/küçük harf uyumsuzluğundan kaçmasın
        sayfa_icerigi = cevap.text.lower() 
        
        # Sitede "soon available" kelimesinin kaç kez geçtiğini sayıyoruz
        oda_sayisi = sayfa_icerigi.count("soon available")
        
        # Sitede "soon available" yazısı VARSA (oda açıldıysa):
        if oda_sayisi > 0:
            mesaj_gonder(f"🚨 DİKKAT! W27 {oda_sayisi} İLAN AÇIK, link: {W27_URL}")
        
        # Yazı YOKSA ve saat tam 00 veya 12 ise (günde 2 kez durum raporu):
        # (cron 10 dakikada bir çalıştığı için sadece o saatin ilk 10 dakikasında mesaj atması için minute < 10 ekli)
        elif (almanya_saati.hour == 4 or almanya_saati.hour == 16) and almanya_saati.minute < 10:
            mesaj_gonder(f"ℹ️ [{saat_str}] Sistem çalışıyor, W27 kontrol edildi. Şu an boş oda YOK.")
            
    except Exception as e:
        mesaj_gonder(f"⚠️ [{saat_str}] HATA: Siteye bağlanılamadı. GitHub ban yemiş olabilir! Detay: {e}")

# Kodu çalıştır
yurt_kontrol()
