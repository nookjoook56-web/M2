import cloudscraper
import re
import base64

SOURCES = ["https://justintv.co/izle/", "https://www.larcivertsports.com"]
FILE_NAME = "playlist.m3u"
PACKAGE_NAME = "backdor22"

def hunter():
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome','platform': 'windows','mobile': False})
    
    for url in SOURCES:
        try:
            print(f"Tarama: {url}")
            res = scraper.get(url, timeout=20)
            html = res.text

            # 1. Strateji: Ham m3u8 linklerini tara
            found = re.findall(r'[\'"](https?://[^\'"]+\.m3u8[^\'"]*)[\'"]', html)
            if found:
                for link in found:
                    if "playlist" in link or "stream" in link:
                        return link.replace('\\/', '/')

            # 2. Strateji: Base64 ile gizlenmiş linkleri çöz (Bazı playerlar yapar)
            b64_matches = re.findall(r'[A-Za-z0-9+/]{40,}', html)
            for b in b64_matches:
                try:
                    decoded = base64.b64decode(b).decode('utf-8')
                    if ".m3u8" in decoded:
                        return re.search(r'https?://[^\s\'"]+\.m3u8', decoded).group()
                except: continue

            # 3. Strateji: Iframe içine gir ve 'source' ara
            iframes = re.findall(r'iframe.*?src=["\'](.*?)["\']', html)
            for src in iframes:
                if 'justin' in src or 'play' in src:
                    if src.startswith('//'): src = 'https:' + src
                    f_res = scraper.get(src, timeout=10)
                    f_m3u8 = re.findall(r'[\'"](https?://[^\'"]+\.m3u8[^\'"]*)[\'"]', f_res.text)
                    if f_m3u8: return f_m3u8[0].replace('\\/', '/')
        except: continue
    return None

def save_m3u(link):
    # Link bulunamazsa dosyayı bozmamak için site linki yerine sabit bir 'Error' linki koyuyoruz
    final = link if link and "m3u8" in link else "https://raw.githubusercontent.com/nookjoook56-web/M2/main/error.m3u8"
    content = f"#EXTM3U\n#EXTINF:-1 tvg-id=\"beinsport-feed1\" group-title=\"{PACKAGE_NAME}\",Beinsport FEED 1\n{final}"
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    save_m3u(hunter())
    
