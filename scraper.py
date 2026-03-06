import requests
from bs4 import BeautifulSoup
import os

# YAPILANDIRMA
TARGET_URL = "https://hedef-yayin-sitesi.com" # Burayı asıl site ile değiştir
FILE_NAME = "playlist.m3u"
PACKAGE_NAME = "backdor22" # Kayıtlı paket ismin

def get_latest_feed():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(TARGET_URL, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Sitedeki link yapısına göre burayı özelleştiriyoruz
        # Örnek: İçinde "FEED 1" geçen ilk linki bulur
        link_tag = soup.find('a', string=lambda t: t and 'FEED 1' in t)
        
        if link_tag and 'href' in link_tag.attrs:
            return link_tag['href']
    except Exception as e:
        print(f"Hata oluştu: {e}")
    return None

def write_m3u(link):
    content = f"""#EXTM3U
#EXTINF:-1 tvg-id="beinsport-feed1" group-title="{PACKAGE_NAME}",Beinsport FEED 1
{link}
"""
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    new_link = get_latest_feed()
    if new_link:
        write_m3u(new_link)
        print(f"Başarıyla güncellendi: {new_link}")
    else:
        print("Link bulunamadı, dosya güncellenmedi.")
        
