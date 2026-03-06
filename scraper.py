import requests
from bs4 import BeautifulSoup
import os

# YAPILANDIRMA
TARGET_URL = "https://larcivertsports1.blogspot.com/?m=1"
FILE_NAME = "playlist.m3u"
PACKAGE_NAME = "backdor22" 

def get_latest_feed():
    try:
        # Gerçek bir tarayıcı gibi davranmak için headers önemli
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(TARGET_URL, headers=headers, timeout=15)
        response.raise_for_status() # Bağlantı hatası varsa direkt exception fırlatır
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Link arama: Hem büyük hem küçük harf duyarlılığını kaldırdık (.upper())
        link_tag = soup.find('a', string=lambda t: t and 'FEED 1' in t.upper())
        
        if link_tag and 'href' in link_tag.attrs:
            return link_tag['href']
            
    except Exception as e:
        print(f"Hata oluştu: {e}")
    return None

def write_m3u(link):
    # Playlist formatını daha temiz bir hale getirdik
    content = f"#EXTM3U\n"
    content += f'#EXTINF:-1 tvg-id="beinsport-feed1" group-title="{PACKAGE_NAME}",Beinsport FEED 1\n'
    content += f"{link}\n"
    
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    new_link = get_latest_feed()
    if new_link:
        write_m3u(new_link)
        print(f"Başarıyla güncellendi: {new_link}")
    else:
        print("Link bulunamadı veya site yapısı değişmiş.")
    
