import requests
import re

SOURCES = [
    "https://www.larcivertsports.com",
    "https://justintv.co/izle/"
]
FILE_NAME = "playlist.m3u"

def super_hunter(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    try:
        r = requests.get(url, headers=headers, timeout=15)
        # Sadece HTML içinde değil, JavaScript blokları içinde de m3u8 ara
        # Bu regex daha geniş kapsamlıdır
        matches = re.findall(r'[\'"](https?://[^\'"]+\.m3u8[^\'"]*)[\'"]', r.text)
        
        if matches:
            # Geçersiz veya reklam linklerini filtrele
            for link in matches:
                if "chunklist" not in link and "playlist.m3u8" in link or "stream" in link:
                    return link.replace('\\/', '/') # Kaçış karakterlerini düzelt
            return matches[0].replace('\\/', '/')
            
    except:
        pass
    return None

# Ana döngüde super_hunter'ı kullan
# (Geri kalan write_m3u kısımları aynı kalabilir)
