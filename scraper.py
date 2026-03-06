import requests
from bs4 import BeautifulSoup
import re
import urllib3

# Uyarıları kapat
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- YAPILANDIRMA (Hafızadaki Kayıtlı Bilgilerin) ---
VERCEL_PROXY = "https://m2-three-beta.vercel.app/api/proxy?link="
FILE_NAME = "playlist.m3u"
PACKAGE_NAME = "backdor22"
START_URL = "https://larcivertsports1.blogspot.com/?m=1"

def get_content(url, referer=None):
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
    print("🔄 Aşama 1: Blogspot ana sayfası ve kanal kartları taranıyor...")
    h1 = get_content(START_URL)
    if not h1: return

    # switchCh('b1', ...) yapısından kanal ID'lerini yakala
    card_matches = re.findall(r"switchCh\('(.*?)'.*?>(.*?)</div>", h1, re.DOTALL)
    
    # AMP linkini tespit et
    soup = BeautifulSoup(h1, 'html.parser')
    amp_link = soup.find('link', rel='amphtml')
    amp_url = amp_link.get('href') if amp_link else None
    
    if not amp_url:
        print("⚠️ AMP bulunamadı, işlem durduruldu.")
        return

    print(f"⚡ Aşama 2: AMP üzerinden Iframe taranıyor -> {amp_url}")
    h2 = get_content(amp_url)
    if not h2: return

    # AMP içindeki asıl yayıncı iframe linkini yakala
    ifr_match = re.search(r'src="(https?://[^"]+)"', h2)
    if not ifr_match: return
    ifr_url = ifr_match.group(1)

    print(f"📡 Aşama 3: Sunucu havuzu (baseUrls) ayıklanıyor...")
    h3 = get_content(ifr_url, referer=amp_url)
    if not h3: return

    # Iframe içindeki gizli baseUrls listesini bul
    bm = re.search(r'baseUrls\s*=\s*\[(.*?)\]', h3, re.DOTALL)
    if not bm:
        print("❌ Sunucu havuzu bulunamadı.")
        return

    raw_srvs = re.findall(r'["\'](https?://.*?)["\']', bm.group(1))
    active_servers = list(set([s.rstrip('/') for s in raw_srvs]))

    if active_servers:
        print(f"✅ {len(active_servers)} sunucu tespit edildi. Playlist oluşturuluyor...")
        with open(FILE_NAME, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            
            # Her bir sunucu için kanalları döngüye sok
            for srv in active_servers:
                # b1, b2 gibi ID'leri androstream formatına çevir
                for cid_short, cname_raw in card_matches:
                    clean_name = BeautifulSoup(cname_raw, "html.parser").text.strip()
                    # ID Dönüşümü (Örn: b1 -> androstreamlivebs1)
                    full_id = f"androstreamlive{cid_short.replace('b', 'bs')}"
                    
                    raw_m3u8 = f"{srv}/{full_id}.m3u8" if "checklist" in srv else f"{srv}/checklist/{full_id}.m3u8"
                    raw_m3u8 = raw_m3u8.replace("checklist//", "checklist/")
                    
                    # Vercel Proxy Entegrasyonu
                    final_url = f"{VERCEL_PROXY}{raw_m3u8}"
                    
                    f.write(f'#EXTINF:-1 tvg-id="{full_id}" group-title="{PACKAGE_NAME}",{clean_name}\n{final_url}\n')
        print(f"✨ Başarılı: {FILE_NAME} kaydedildi.")
    else:
        print("❌ Aktif sunucu bulunamadı.")

if __name__ == "__main__":
    main()
    
