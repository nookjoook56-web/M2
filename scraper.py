import requests
from bs4 import BeautifulSoup
import re
import os

# YAPILANDIRMA
SOURCES = [
    "https://www.larcivertsports.com",
    "https://justintv.co/izle/"
]
FILE_NAME = "playlist.m3u"
PACKAGE_NAME = "backdor22"

def fetch_stream(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Referer': url
    }
    try:
        print(f"Tarama başlıyor: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        
        # 1. YÖNTEM: Sayfa içindeki gizli m3u8 linklerini ara (Regex)
        found_m3u8 = re.findall(r'https?://[\w\.-]+/[\w\.-]+[/\w\.-]*\.m3u8[?\w\d=]*', response.text)
        if found_m3u8:
            return found_m3u8[0]

        # 2. YÖNTEM: iframe içindeki kaynakları kontrol et
        soup = BeautifulSoup(response.text, 'html.parser')
        iframes = soup.find_all('iframe')
        for ifrm in iframes:
            src = ifrm.get('src', '')
            if src:
                if src.startswith('/'):
                    src = f"{url.rstrip('/')}{src}"
                if "m3u8" in src or "stream" in src:
                    return src
    except Exception as e:
        print(f"Hata ({url}): {e}")
    return None

def main():
    final_link = None
    for site in SOURCES:
        link = fetch_stream(site)
        if link:
            final_link = link
            break
            
    stream_url = final_link if final_link else "https://beklemede.com/yayin-yok.m3u8"
    
    content = f"""#EXTM3U
#EXTINF:-1 tvg-id="beinsport-feed1" group-title="{PACKAGE_NAME}",Beinsport FEED 1
{stream_url}
"""
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Playlist güncellendi: {stream_url}")

if __name__ == "__main__":
    main()
