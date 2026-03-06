import requests
from bs4 import BeautifulSoup
import re
import urllib3

# Uyarıları kapat
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- YAPILANDIRMA ---
# Vercel Proxy adresin (Sona ?link= eklendi)
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
    print("Süreç başlatıldı...")
    
    # 1. Aşama: Blogspot ve AMP tespiti
    h1 = get_src(START_URL)
    if not h1: return
    
    s = BeautifulSoup(h1, 'html.parser')
    lnk = s.find('link', rel='amphtml')
    amp_url = lnk.get('href') if lnk else None
    
    if not amp_url:
        print("AMP bulunamadı, doğrudan içerik taranıyor...")
        h2 = h1
        ref = START_URL
    else:
        print(f"AMP bulundu: {amp_url}")
        h2 = get_src(amp_url)
        ref = amp_url

    # 2. Aşama: Iframe içindeki sunucuları bulma
    ifr_match = re.search(r'src="(https?://[^"]+)"', h2)
    if not ifr_match:
        print("Iframe bulunamadı.")
        return
    
    ifr_url = ifr_match.group(1)
    h3 = get_src(ifr_url, referer=ref)
    if not h3: return

    # baseUrls içindeki sunucuları çek
    bm = re.search(r'baseUrls\s*=\s*\[(.*?)\]', h3, re.DOTALL)
    if not bm:
        print("Sunucu havuzu boş.")
        return

    srvs_raw = re.findall(r'["\'](https?://.*?)["\']', bm.group(1))
    active_servers = list(set([s.rstrip('/') for s in srvs_raw]))

    # 3. Aşama: Playlist Yazma
    channels = [
        ("androstreamlivebs1", 'beIN Sport 1 HD'),
        ("androstreamlivebs2", 'beIN Sport 2 HD'),
        ("androstreamlivess1", 'S Sport 1 HD'),
        ("androstreamlivetb", 'Tabii Spor HD')
    ]

    if active_servers:
        print(f"{len(active_servers)} sunucu aktif. Playlist güncelleniyor...")
        with open(FILE_NAME, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for srv in active_servers:
                for cid, cname in channels:
                    # Link yapısını kur
                    raw_url = f"{srv}/checklist/{cid}.m3u8" if "checklist" not in srv else f"{srv}/{cid}.m3u8"
                    raw_url = raw_url.replace("checklist//", "checklist/")
                    
                    # VERCEL PROXY İLE BİRLEŞTİR (En kritik nokta)
                    final_url = f"{VERCEL_PROXY}{raw_url}"
                    
                    f.write(f'#EXTINF:-1 tvg-id="{cid}" group-title="{PACKAGE_NAME}",{cname}\n{final_url}\n')
        print("Bitti.")
    else:
        print("Aktif sunucu bulunamadı.")

if __name__ == "__main__":
    main()
