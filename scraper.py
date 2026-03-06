import requests
from bs4 import BeautifulSoup
import re
import urllib3
import os

# Uyarıları kapat
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- YAPILANDIRMA ---
VERCEL_PROXY = "https://m2-three-beta.vercel.app/api/proxy?link="
FILE_NAME = "playlist.m3u"
PACKAGE_NAME = "backdor22"
START_URL = "https://larcivertsports1.blogspot.com/?m=1"

def get_src(url, referer=None):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    }
    if referer:
        headers['Referer'] = referer
    try:
        r = requests.get(url, headers=headers, verify=False, timeout=20)
        return r.text if r.status_code == 200 else None
    except:
        return None

def main():
    # 1. Aşama: Blogspot Ana Sayfa ve AMP Linki Tespiti
    print("Step 1: Blogspot taranıyor...")
    h1 = get_src(START_URL)
    if not h1: 
        print("Hata: Blogspot ana sayfasına ulaşılamadı.")
        return

    s = BeautifulSoup(h1, 'html.parser')
    lnk = s.find('link', rel='amphtml')
    amp_url = lnk.get('href') if lnk else None
    if not amp_url:
        print("Hata: AMP linki bulunamadı.")
        return

    # 2. Aşama: AMP Sayfası ve Iframe Ayıklama
    print(f"Step 2: AMP Analizi yapılıyor -> {amp_url}")
    h2 = get_src(amp_url)
    if not h2: return

    # AMP içindeki [src] veya normal src iframe yapısını yakala
    ifr_match = re.search(r'src="(https?://[^"]+)"', h2)
    if not ifr_match:
        print("Hata: Yayın Iframe linki bulunamadı.")
        return
    ifr_url = ifr_match.group(1)

    # 3. Aşama: Iframe İçinden Sunucu Havuzunu (baseUrls) Çekme
    print(f"Step 3: Iframe taranıyor -> {ifr_url}")
    h3 = get_src(ifr_url, ref=amp_url)
    if not h3: return

    bm = re.search(r'baseUrls\s*=\s*\[(.*?)\]', h3, re.DOTALL)
    if not bm:
        print("Hata: Sunucu havuzu (baseUrls) bulunamadı.")
        return

    # Sunucu linklerini temizle ve listele
    cl = bm.group(1).replace('"', '').replace("'", "").replace("\n", "").replace("\r", "")
    srvs = [x.strip() for x in cl.split(',') if x.strip().startswith("http")]
    active_servers = list(set([s.rstrip('/') for s in srvs]))

    # 4. Aşama: Playlist Oluşturma
    channels = [
        ("androstreamlivebs1", 'beIN Sport 1 HD'),
        ("androstreamlivebs2", 'beIN Sport 2 HD'),
        ("androstreamlivebs3", 'beIN Sport 3 HD'),
        ("androstreamlivebs4", 'beIN Sport 4 HD'),
        ("androstreamlivess1", 'S Sport 1 HD'),
        ("androstreamlivess2", 'S Sport 2 HD'),
        ("androstreamlivetb", 'Tabii Spor HD'),
        ("androstreamliveexn", 'Exxen Spor HD'),
    ]

    if active_servers:
        print(f"Step 4: {len(active_servers)} sunucu ile Playlist yazılıyor...")
        with open(FILE_NAME, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            
            for srv in active_servers:
                for cid, cname in channels:
                    # Link yapısını oluştur (checklist kontrolü ile)
                    raw_url = f"{srv}/checklist/{cid}.m3u8" if "checklist" not in srv else f"{srv}/{cid}.m3u8"
                    raw_url = raw_url.replace("checklist//", "checklist/")
                    
                    # Vercel Proxy entegrasyonu
                    proxied_url = f"{VERCEL_PROXY}{raw_url}"
                    
                    # M3U Satırını Yaz
                    f.write(f'#EXTINF:-1 tvg-id="{cid}" group-title="{PACKAGE_NAME}",{cname} (Srv:{srv.split("//")[1][:5]})\n')
                    f.write(f'{proxied_url}\n')
                    
        print(f"✨ Başarılı: {FILE_NAME} dosyası oluşturuldu.")
    else:
        print("Hata: Hiç aktif sunucu bulunamadı.")

if __name__ == "__main__":
    main()
        
