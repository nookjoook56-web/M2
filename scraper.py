import cloudscraper
import re

# YAPILANDIRMA
SOURCES = ["https://larcivertsports1.blogspot.com/?m=1", "https://justintv.co/izle/"]
FILE_NAME = "playlist.m3u"
PACKAGE_NAME = "backdor22"
VERCEL_PROXY_URL = "https://m2-three-beta.vercel.app/api/proxy"

def get_stream_link():
    # Cloudflare ve Blogspot korumalarını aşmak için özel tarayıcı simülasyonu
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome','platform': 'windows','mobile': False})
    
    for url in SOURCES:
        try:
            print(f"Hedef taranıyor: {url}")
            res = scraper.get(url, timeout=20)
            
            # 1. Strateji: Sayfa içinde doğrudan m3u8 linklerini tara
            matches = re.findall(r'[\'"](https?://[^\'"]+\.m3u8[^\'"]*)[\'"]', res.text)
            if matches:
                for link in matches:
                    if "m3u8" in link and "chunklist" not in link:
                        return link.replace('\\/', '/')

            # 2. Strateji: Blogspot'un içindeki iframe/embed yapılarını tara
            # Blogspot genellikle yayını başka bir sayfadan iframe ile çeker
            iframes = re.findall(r'<iframe.*?src=["\'](.*?)["\']', res.text)
            for src in iframes:
                # Reklam linklerini eleyip sadece potansiyel yayıncıları tarıyoruz
                if 'google' not in src and ('play' in src or 'live' in src or 'justin' in src or 'stream' in src):
                    if src.startswith('//'): src = 'https:' + src
                    print(f"Alt kaynak (iframe) taranıyor: {src}")
                    f_res = scraper.get(src, timeout=10)
                    f_m3u8 = re.findall(r'[\'"](https?://[^\'"]+\.m3u8[^\'"]*)[\'"]', f_res.text)
                    if f_m3u8:
                        return f_m3u8[0].replace('\\/', '/')
        except Exception as e:
            print(f"Hata ({url}): {e}")
            continue
    return None

def save_m3u(link):
    if link:
        # Yakalanan linki Vercel Proxy adresine parametre olarak ekliyoruz
        final_url = f"{VERCEL_PROXY_URL}?link={link}"
        print(f"Yayın yakalandı ve Proxy'ye hazırlandı: {final_url}")
    else:
        # Eğer kaynaklarda o an yayın yoksa hata linkine yönlendiriyoruz
        final_url = "https://raw.githubusercontent.com/nookjoook56-web/M2/main/error.m3u8"
        print("Aktif yayın bulunamadı.")

    # M3U Dosya İçeriği (backdor22 paket isminizle)
    content = f"#EXTM3U\n#EXTINF:-1 tvg-id=\"beinsport-feed1\" group-title=\"{PACKAGE_NAME}\",Beinsport FEED 1\n{final_url}"
    
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    stream = get_stream_link()
    save_m3u(stream)
    
