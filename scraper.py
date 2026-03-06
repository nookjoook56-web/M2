import requests
from bs4 import BeautifulSoup
import re
import urllib3
import concurrent.futures # Hızlı test için

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# YAPILANDIRMA
VERCEL_PROXY = "https://m2-three-beta.vercel.app/api/proxy?link="
FILE_NAME = "playlist.m3u"
PACKAGE_NAME = "backdor22"
START_URL = "https://larcivertsports1.blogspot.com/?m=1"

class Scraper:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        }

    def fetch(self, url, referer=None):
        try:
            if referer: self.headers['Referer'] = referer
            response = self.session.get(url, headers=self.headers, verify=False, timeout=15)
            return response.text if response.status_code == 200 else None
        except Exception as e:
            print(f"Hata: {url} -> {e}")
            return None

    def check_server(self, server_url):
        """Sunucunun gerçekten aktif olup olmadığını test eder."""
        test_url = f"{server_url.rstrip('/')}/test.m3u8" # Dummy test
        try:
            r = self.session.head(test_url, timeout=5)
            return server_url if r.status_code != 404 else None
        except:
            return None

    def run(self):
        # 1. Aşama: Blogspot Ana Sayfa
        print("🔍 Blogspot taranıyor...")
        html = self.fetch(START_URL)
        if not html: return

        # 2. Aşama: AMP Linki (Daha esnek regex)
        amp_match = re.search(r'link rel="amphtml" href="(.*?)"', html)
        amp_url = amp_match.group(1) if amp_match else None
        if not amp_url: return

        # 3. Aşama: AMP İçeriği ve Iframe
        print(f"⚡ AMP Analizi: {amp_url}")
        amp_html = self.fetch(amp_url)
        if not amp_html: return
        
        # [src] veya normal src içindeki iframe'i yakala
        ifr_match = re.search(r'src="(https?://[^"]+)"', amp_html)
        ifr_url = ifr_match.group(1) if ifr_match else None
        if not ifr_url: return

        # 4. Aşama: Sunucu Havuzu (BaseUrls)
        print("🌐 Sunucular ayıklanıyor...")
        ifr_html = self.fetch(ifr_url, referer=amp_url)
        if not ifr_html: return

        base_urls_match = re.search(r'baseUrls\s*=\s*\[(.*?)\]', ifr_html, re.DOTALL)
        if not base_urls_match: return

        raw_urls = re.findall(r'["\'](https?://.*?)["\']', base_urls_match.group(1))
        unique_srvs = list(set([u.rstrip('/') for u in raw_urls]))

        # 5. Aşama: Playlist Oluşturma (Andro-Panel Formatı)
        channels = [
            ("androstreamlivebs1", 'beIN Sport 1'),
            ("androstreamlivebs2", 'beIN Sport 2'),
            ("androstreamlivebs3", 'beIN Sport 3'),
            ("androstreamlivess1", 'S Sport 1'),
            ("androstreamlivetb", 'Tabii Spor'),
            ("androstreamliveexn", 'Exxen Spor')
        ]

        if unique_srvs:
            print(f"✅ {len(unique_srvs)} sunucu bulundu. Yazılıyor...")
            with open(FILE_NAME, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")
                for srv in unique_srvs:
                    for cid, name in channels:
                        raw_link = f"{srv}/{cid}.m3u8" if "checklist" in srv else f"{srv}/checklist/{cid}.m3u8"
                        raw_link = raw_link.replace("checklist//", "checklist/")
                        
                        # Vercel Proxy Entegrasyonu
                        final_link = f"{VERCEL_PROXY}{raw_link}"
                        
                        f.write(f'#EXTINF:-1 tvg-id="{cid}" group-title="{PACKAGE_NAME}",{name} ({srv.split("//")[1][:10]})\n')
                        f.write(f'{final_link}\n')
            print(f"✨ Bitti! {FILE_NAME} güncel.")

if __name__ == "__main__":
    Scraper().run()
