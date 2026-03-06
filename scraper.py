import cloudscraper
import re

# YAPILANDIRMA
# Yeni verdiğin Blogspot adresini ana kaynak yaptık
SOURCES = ["https://larcivertsports1.blogspot.com/?m=1", "https://justintv.co/izle/"]
FILE_NAME = "playlist.m3u"
PACKAGE_NAME = "backdor22"
VERCEL_PROXY_URL = "https://m2-three-beta.vercel.app/api/proxy"

def get_stream_link():
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome','platform': 'windows','mobile': False})
    
    for url in SOURCES:
        try:
            print(f"Hedef taranıyor: {url}")
            res = scraper.get(url, timeout=20)
            
            # 1. Strateji: Blogspot içinde doğrudan m3u8 ara
            matches = re.findall(r'[\'"](https?://[^\'"]+\.m3u8[^\'"]*)[\'"]', res.text)
            if matches:
                for link in matches:
                    if "m3u8" in link and "chunklist" not in link:
                        return link.replace('\\/', '/')

            # 2. Strateji: Blogspot'un yönlendirdiği iframe'lerin içine gir
            iframes = re.findall(r'<iframe.*?src=["\'](.*?)["\']', res.text)
            for src in iframes:
                # Reklam olmayan, yayın içerebilecek iframe'leri seçiyoruz
                if 'blogspot' not in src and ('play' in src or 'live' in src or 'justin' in src):
                    if src.startswith('//'): src = 'https:' + src
                    print(f"Alt kaynak taranıyor: {src}")
                    f_res = scraper.get(src, timeout=10)
                    f_m3u8 = re.findall(r'[\'"](https?://[^\'"]+\.m3u8[^\'"]*)[\'"]', f_res.text)
                    if f_m3u8:
                        return f_m3u8[0].replace('\\/', '/')
        except Exception as e:
            print(f"Hata oluştu: {e}")
            continue
    return None

def save_m3u(link):
    if link:
        # Yakalanan linki Vercel Proxy ile zırhlıyoruz
        final_url = f"{VERCEL_PROXY_URL}?link={link}"
        print(f"Yayın Proxy ile hazır: {final_url}")
    else:
        # Yayın yoksa hata linki
        final_url = "https://raw.githubusercontent.com/nookjoook56-web/M2/main/error.m3u8"
        print("Sitede şu an aktif yayın bulunamadı.")

    content = f"#EXTM3U\n#EXTINF:-1 tvg-id=\"beinsport-feed1\" group-title=\"{PACKAGE_NAME}\",Beinsport FEED 1\n{final_url}"
    
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    stream = get_stream_link()
    save_m3u(stream)
    
