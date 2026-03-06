import cloudscraper
import re
import json

SOURCES = ["https://justintv.co/izle/", "https://www.larcivertsports.com"]
FILE_NAME = "playlist.m3u"
PACKAGE_NAME = "backdor22"

def get_justin_api_link():
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome','platform': 'windows','mobile': False})
    
    for url in SOURCES:
        try:
            print(f"Derin tarama başlatıldı: {url}")
            res = scraper.get(url, timeout=20)
            
            # 1. Yöntem: Sayfa içindeki JSON bloklarından m3u8 ayıkla
            # JustinTV genellikle bir 'source' veya 'file' anahtarı kullanır
            json_m3u8 = re.findall(r'["\'](https?://[^\s"\']+\.m3u8[^\s"\']*)["\']', res.text)
            if json_m3u8:
                for link in json_m3u8:
                    if "m3u8" in link and "chunklist" not in link:
                        return link.replace('\\/', '/')

            # 2. Yöntem: Iframe'lerin içindeki 'data-config' veya 'src' katmanları
            iframes = re.findall(r'<iframe.*?src=["\'](.*?)["\']', res.text)
            for src in iframes:
                if 'justin' in src or 'play' in src or 'embed' in src:
                    if src.startswith('//'): src = 'https:' + src
                    # Iframe'in içine girip tekrar derinlemesine bakıyoruz
                    f_res = scraper.get(src, timeout=10)
                    # Iframe içinde şifrelenmiş veya gizlenmiş linkleri ara
                    f_m3u8 = re.findall(r'https?://[^\s"\']+\.m3u8[^\s"\']+', f_res.text)
                    if f_m3u8:
                        return f_m3u8[0].replace('\\/', '/')

        except Exception as e:
            print(f"Hata oluştu: {e}")
            continue
    return None

def save_m3u(link):
    # Eğer m3u8 bulunamazsa, kullanıcıyı siteye yönlendiren geçici bir yapı kurar
    is_valid = link and (".m3u8" in str(link))
    final_url = link if is_valid else "https://raw.githubusercontent.com/nookjoook56-web/M2/main/error.m3u8"
    
    content = f"#EXTM3U\n#EXTINF:-1 tvg-id=\"beinsport-feed1\" group-title=\"{PACKAGE_NAME}\",Beinsport FEED 1\n{final_url}"
    
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Sonuç kaydedildi: {final_url}")

if __name__ == "__main__":
    link = get_justin_api_link()
    save_m3u(link)
    
