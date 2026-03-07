import requests
from bs4 import BeautifulSoup
import re
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    # --- YAPILANDIRMA ---
    # Render üzerinde aktif olan proxy adresin
    PROXY = "https://backdor-proxy.onrender.com/proxy?link="
    # Yeni eklenen Blogspot kaynağı
    START_URL = "https://larcivertsports1.blogspot.com/?m=1"
    FILE_NAME = "playlist.m3u"
    PACKAGE = "backdor22" # Kayıtlı paket ismin

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }

    def get_src(u, ref=None):
        try:
            if ref: headers['Referer'] = ref
            r = requests.get(PROXY + u, headers=headers, verify=False, timeout=15)
            return r.text if r.status_code == 200 else None
        except: return None

    print(f"🚀 {START_URL} taranıyor...")
    
    # 1. Ana Sayfa Analizi
    html = get_src(START_URL)
    if not html: 
        print("❌ Kaynak sayfa çekilemedi.")
        return

    # 2. Iframe ve Yayın Linki Arama
    # Blogspot üzerindeki iframe veya doğrudan m3u8 linklerini bulmaya çalışır
    soup = BeautifulSoup(html, 'html.parser')
    
    # Not: Bu kısım sitenin iç yapısına (iframe/script) göre dinamik link üretir
    # Örnek olarak beinsport-feed1 için m3u8 arayalım
    found_links = []
    
    # Sayfa içindeki tüm iframe'leri tara
    iframes = soup.find_all('iframe')
    for ifr in iframes:
        src = ifr.get('src')
        if src and "http" in src:
            found_links.append(("Kanal", src))

    if found_links:
        with open(FILE_NAME, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for name, link in found_links:
                # Render proxy eklenmiş final link
                final_url = f"{PROXY}{link}"
                f.write(f'#EXTINF:-1 group-title="{PACKAGE}",{name}\n')
                f.write(f'{final_url}\n')
        print(f"✅ Başarılı: {FILE_NAME} güncellendi.")
    else:
        print("❌ Sayfada aktif yayın linki bulunamadı.")

if __name__ == "__main__":
    main()
    
