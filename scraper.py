import requests
from bs4 import BeautifulSoup
import re
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    # 1. GÜNCEL PROXY ADRESİN
    PROXY = "https://backdor-proxy.onrender.com/proxy?link="
    START = "https://larcivertsports1.blogspot.com/?m=1"
    FILE_NAME = "playlist.m3u"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    }

    # Kanal listesi (Kısa tutulmuştur, test amaçlı)
    channels = [
        ("androstreamlivebs1", 'TR:beIN Sport 1 HD'),
        ("androstreamlivebs2", 'TR:beIN Sport 2 HD'),
        ("androstreamlivess1", 'TR:S Sport 1 HD'),
        ("androstreamlivetb", 'TR:Tabii HD'),
    ]

    def get_src(u, ref=None):
        try:
            if ref: headers['Referer'] = ref
            # Proxy üzerinden çekim yapıyoruz
            r = requests.get(PROXY + u, headers=headers, verify=False, timeout=15)
            return r.text if r.status_code == 200 else None
        except Exception as e:
            print(f"Bağlantı Hatası: {e}")
            return None

    print("🚀 Süreç başlatıldı...")
    
    # BLOGSPOT TARAMA
    h1 = get_src(START)
    if not h1:
        print("❌ Blogspot ana sayfası çekilemedi!")
        return

    # AMP BULMA
    s = BeautifulSoup(h1, 'html.parser')
    lnk = s.find('link', rel='amphtml')
    if not lnk:
        print("❌ AMP linki bulunamadı!")
        return
    amp = lnk.get('href')
    print(f"🔗 AMP bulundu: {amp}")

    # IFRAME BULMA
    h2 = get_src(amp)
    if not h2: return
    m = re.search(r'src="(https?://[^"]+)"', h2)
    if not m:
        print("❌ Iframe linki ayıklanamadı!")
        return
    ifr = m.group(1)
    print(f"📺 Iframe yakalandı: {ifr}")

    # SUNUCU HAVUZU (baseUrls)
    h3 = get_src(ifr, ref=amp)
    if not h3: return
    bm = re.search(r'baseUrls\s*=\s*\[(.*?)\]', h3, re.DOTALL)
    if not bm:
        print("❌ Sunucu listesi (baseUrls) bulunamadı!")
        return

    cl = bm.group(1).replace('"', '').replace("'", "").replace("\n", "").replace("\r", "")
    srvs = [x.strip() for x in cl.split(',') if x.strip().startswith("http")]
    active_servers = list(set(srvs))
    
    if active_servers:
        print(f"✅ {len(active_servers)} sunucu bulundu. Playlist yazılıyor...")
        with open(FILE_NAME, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for srv in active_servers:
                srv = srv.rstrip('/')
                for cid, cname in channels:
                    # Link yapısı oluşturma
                    raw_url = f"{srv}/checklist/{cid}.m3u8" if "checklist" not in srv else f"{srv}/{cid}.m3u8"
                    raw_url = raw_url.replace("checklist//", "checklist/")
                    
                    # PROXY EKLEME (KRİTİK ADIM)
                    final_link = f"{PROXY}{raw_url}"
                    
                    f.write(f'#EXTINF:-1 tvg-id="sport.tr" group-title="backdor22",{cname}\n{final_link}\n')
        print(f"✨ Bitti: {FILE_NAME} kaydedildi.")
    else:
        print("❌ Aktif sunucu bulunamadı.")

if __name__ == "__main__":
    main()
                        
