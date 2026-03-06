import requests
from bs4 import BeautifulSoup
import re

# YAPILANDIRMA
TARGET_URL = "https://www.larcivertsports.com/"
FILE_NAME = "playlist.m3u"
PACKAGE_NAME = "backdor22"

def get_latest_feed():
    try:
        # Site bot koruması kullanabileceği için User-Agent ekliyoruz
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        }
        response = requests.get(TARGET_URL, headers=headers, timeout=20)
        response.raise_for_status() # Bağlantı hatası varsa durdur
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Sitedeki tüm linkleri (a etiketlerini) tara
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link['href']
            text = link.get_text().upper()
            
            # BEIN, FEED veya SPORT 1 anahtar kelimelerini ara
            if "BEIN" in text or "FEED" in text or "SPORT 1" in text:
                # Sadece m3u8 veya stream içeren linkleri filtrele (opsiyonel)
                return href
                
        # Eğer özel kelime bulamazsa, ilk canlı yayın linkini dene
        for link in links:
            if "canli" in link['href'] or "izle" in link['href']:
                return link['href']

    except Exception as e:
        print(f"Hata: {e}")
    return None

def write_m3u(link):
    # Eğer link bulunamazsa dosyayı boş bırakmamak için bir uyarı ekleyelim
    final_link = link if link else "https://beklemede.com/yayin-yok.m3u8"
    
    content = f"""#EXTM3U
#EXTINF:-1 tvg-id="beinsport-feed1" group-title="{PACKAGE_NAME}",Beinsport FEED 1
{final_link}
"""
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Playlist yazıldı: {final_link}")

if __name__ == "__main__":
    found_link = get_latest_feed()
    write_m3u(found_link)
    
