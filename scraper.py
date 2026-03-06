import cloudscraper
import re
import json

# YAPILANDIRMA
SOURCES = ["https://justintv.co/izle/", "https://www.larcivertsports.com"]
FILE_NAME = "playlist.m3u"
PACKAGE_NAME = "backdor22" # Kayıtlı paket ismin
VERCEL_PROXY_URL = "https://m2-three-beta.vercel.app/api/proxy"

def get_justin_api_link():
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome','platform': 'windows','mobile': False})
    
    for url in SOURCES:
        try:
            print(f"Derin tarama başlatıldı: {url}")
            res = scraper.get(url, timeout=20)
            
            # 1. Yöntem: JSON ve Sayfa Kaynağından m3u8 Ayıkla
            json_m3u8 = re.findall(r'["\'](https?://[^\s"\']+\.m3u8[^\s"\']*)["\']', res.text)
            if json_m3u8:
                for link in json_m3u8:
                    if "m3u8" in link and "chunklist" not in link:
                        return link.replace('\\/', '/')

            # 2. Yöntem: Iframe Katmanlarını Tara
            iframes = re.findall(r'<iframe.*?src=["\'](.*?)["\']', res.text)
            for src in iframes:
                if 'justin' in src or 'play' in src or 'embed' in src:
                    if src.startswith('//'): src = 'https:' + src
                    f_res = scraper.get(src, timeout=10)
                    f_m3u8 = re.findall(r'https?://[^\s"\']+\.m3u8[^\s"\']+', f_res.text)
                    if f_m3u8:
                        return f_m3u8[0].replace('\\/', '/')
        except Exception as e:
            print(f"Hata: {e}")
            continue
    return None

def save_m3u(link):
    # Eğer link bulunduysa Proxy ile birleştir, bulunamadıysa hata linki koy
    if link and "m3u8" in link:
        final_link = f"{VERCEL_PROXY_URL}?link={link}"
    else:
        final_link = "https://raw.githubusercontent.com/nookjoook56-web/M2/main/error.m3u8"
    
    # M3U formatında içeriği oluştur
    content = f"#EXTM3U\n#EXTINF:-1 tvg-id=\"beinsport-feed1\" group-title=\"{PACKAGE_NAME}\",Beinsport FEED 1\n{final_link}"
    
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Playlist Güncellendi: {final_link}")

if __name__ == "__main__":
    found_link = get_justin_api_link()
    save_m3u(found_link)
    
