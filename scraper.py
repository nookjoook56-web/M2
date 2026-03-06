import cloudscraper
import re

SOURCES = [
    "https://justintv.co/izle/",
    "https://www.larcivertsports.com"
]
FILE_NAME = "playlist.m3u"
PACKAGE_NAME = "backdor22"

def hunt_stream():
    # Cloudflare engellerini aşmak için scraper oluştur
    scraper = cloudscraper.create_scraper()
    
    for url in SOURCES:
        try:
            print(f"Tarama yapılıyor: {url}")
            response = scraper.get(url, timeout=20)
            
            # 1. Adım: Sayfa kaynağında doğrudan .m3u8 ara
            m3u8_matches = re.findall(r'[\'"](https?://[^\'"]+\.m3u8[^\'"]*)[\'"]', response.text)
            
            if m3u8_matches:
                # Reklam olmayan, içinde 'stream' veya 'live' geçen ilk linki al
                for link in m3u8_matches:
                    clean_link = link.replace('\\/', '/')
                    if "m3u8" in clean_link:
                        return clean_link

            # 2. Adım: iframe'lerin içindeki gizli linkleri ara
            iframes = re.findall(r'<iframe.*?src=["\'](.*?)["\']', response.text)
            for frame_url in iframes:
                if frame_url.startswith('//'): frame_url = 'https:' + frame_url
                if frame_url.startswith('/'): frame_url = url + frame_url
                
                try:
                    frame_res = scraper.get(frame_url, timeout=10)
                    inner_m3u8 = re.findall(r'[\'"](https?://[^\'"]+\.m3u8[^\'"]*)[\'"]', frame_res.text)
                    if inner_m3u8:
                        return inner_m3u8[0].replace('\\/', '/')
                except:
                    continue
                    
        except Exception as e:
            print(f"Hata ({url}): {e}")
    return None

def save_playlist(link):
    final_link = link if link else "https://beklemede.com/yayin-yok.m3u8"
    content = f"#EXTM3U\n#EXTINF:-1 tvg-id=\"beinsport-feed1\" group-title=\"{PACKAGE_NAME}\",Beinsport FEED 1\n{final_link}"
    
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Sonuç: {final_link}")

if __name__ == "__main__":
    link = hunt_stream()
    save_playlist(link)
                        
