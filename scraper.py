import cloudscraper
import re

# Kayıtlı bilgilerine göre yapılandırma
SOURCES = ["https://justintv.co/izle/", "https://www.larcivertsports.com"]
FILE_NAME = "playlist.m3u"
PACKAGE_NAME = "backdor22" 

def get_stream():
    # Cloudflare korumasını aşan özel tarayıcı
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})
    
    for url in SOURCES:
        try:
            print(f"Kaynak taranıyor: {url}")
            response = scraper.get(url, timeout=20)
            
            # 1. Adım: Doğrudan m3u8 ara
            links = re.findall(r'[\'"](https?://[^\'"]+\.m3u8[^\'"]*)[\'"]', response.text)
            if links:
                return links[0].replace('\\/', '/')

            # 2. Adım: Iframe içinde ara (JustinTV klasiği)
            iframes = re.findall(r'iframe.*?src=["\'](.*?)["\']', response.text)
            for frame_url in iframes:
                if frame_url.startswith('//'): frame_url = 'https:' + frame_url
                if 'justin' in frame_url or 'play' in frame_url:
                    f_res = scraper.get(frame_url, timeout=10)
                    f_links = re.findall(r'[\'"](https?://[^\'"]+\.m3u8[^\'"]*)[\'"]', f_res.text)
                    if f_links:
                        return f_links[0].replace('\\/', '/')
        except Exception as e:
            print(f"Hata: {e}")
    return None

def save(link):
    # Eğer link bulunamazsa 'Yayın Yok' yerine en azından siteyi döndür ki boş kalmasın
    final_url = link if link else "https://justintv.co/izle/"
    content = f"#EXTM3U\n#EXTINF:-1 tvg-id=\"beinsport-feed1\" group-title=\"{PACKAGE_NAME}\",Beinsport FEED 1\n{final_url}"
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    found_link = get_stream()
    save(found_link)
            
