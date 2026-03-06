import cloudscraper
import re

# YAPILANDIRMA
SOURCES = ["https://justintv.co/izle/", "https://www.larcivertsports.com"]
FILE_NAME = "playlist.m3u"
PACKAGE_NAME = "backdor22"
VERCEL_PROXY_URL = "https://m2-three-beta.vercel.app/api/proxy"

def get_stream_link():
    # Cloudflare korumasını aşmak için scraper oluşturur
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome','platform': 'windows','mobile': False})
    
    for url in SOURCES:
        try:
            print(f"Tarama yapılıyor: {url}")
            res = scraper.get(url, timeout=20)
            
            # 1. Yöntem: Doğrudan m3u8 linklerini tara
            matches = re.findall(r'[\'"](https?://[^\'"]+\.m3u8[^\'"]*)[\'"]', res.text)
            if matches:
                for link in matches:
                    if "m3u8" in link and "chunklist" not in link:
                        return link.replace('\\/', '/')

            # 2. Yöntem: Iframe içindeki gizli kaynakları tara
            iframes = re.findall(r'<iframe.*?src=["\'](.*?)["\']', res.text)
            for src in iframes:
                if 'justin' in src or 'play' in src:
                    if src.startswith('//'): src = 'https:' + src
                    f_res = scraper.get(src, timeout=10)
                    f_m3u8 = re.findall(r'[\'"](https?://[^\'"]+\.m3u8[^\'"]*)[\'"]', f_res.text)
                    if f_m3u8:
                        return f_m3u8[0].replace('\\/', '/')
        except Exception as e:
            print(f"Hata: {e}")
            continue
    return None

def save_m3u(link):
    # Link bulunduysa Vercel Proxy ile birleştirir, bulunamadıysa hata linki yazar
    if link:
        final_url = f"{VERCEL_PROXY_URL}?link={link}"
        print(f"Yayın bulundu: {final_url}")
    else:
        final_url = "https://raw.githubusercontent.com/nookjoook56-web/M2/main/error.m3u8"
        print("Yayın bulunamadı.")

    content = f"#EXTM3U\n#EXTINF:-1 tvg-id=\"beinsport-feed1\" group-title=\"{PACKAGE_NAME}\",Beinsport FEED 1\n{final_url}"
    
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    stream = get_stream_link()
    save_m3u(stream)
        
