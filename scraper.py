import requests
from bs4 import BeautifulSoup
import re

# YAPILANDIRMA
BASE_URL = "https://www.larcivertsports.com"
FILE_NAME = "playlist.m3u"
PACKAGE_NAME = "backdor22"

def get_deep_link():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': BASE_URL
    }

    try:
        # 1. ADIM: Ana sayfayı tara ve maç/kanal sayfasını bul
        response = requests.get(BASE_URL, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        target_page = None
        # İçinde "BEIN", "SPORT" veya "CANLI" geçen linkleri ara
        for a in soup.find_all('a', href=True):
            text = a.get_text().upper()
            href = a['href']
            if any(key in text for key in ["BEIN", "FEED", "SPORT 1", "CANLI"]):
                target_page = href if href.startswith('http') else f"{BASE_URL.rstrip('/')}/{href.lstrip('/')}"
                break
        
        if not target_page:
            return None

        # 2. ADIM: Bulunan sayfanın içine gir (Derinleşme)
        print(f"Hedef sayfa bulundu: {target_page}")
        res_sub = requests.get(target_page, headers=headers, timeout=15)
        sub_soup = BeautifulSoup(res_sub.text, 'html.parser')
        
        # 3. ADIM: m3u8 veya iframe içindeki asıl kaynağı ara
        # Önce sayfa içindeki tüm metni tarayıp m3u8 linki var mı bakalım (Regex)
        m3u8_links = re.findall(r'https?://[\w\.-]+/[\w\.-]+[/\w\.-]*\.m3u8[?\w\d=]*', res_sub.text)
        if m3u8_links:
            return m3u8_links[0]
            
        # Eğer direkt link yoksa, iframe içindeki 'src' leri kontrol et
        iframes = sub_soup.find_all('iframe')
        for ifrm in iframes:
            if 'src' in ifrm.attrs:
                src = ifrm['src']
                if "m3u8" in src or "stream" in src:
                    return src
                # Bazı siteler yayıncıyı başka bir linke gömer
                if "atv" in src or "trgol" in src: # Örnek yayıncılar
                    return src

    except Exception as e:
        print(f"Hata: {e}")
    return None

def write_m3u(link):
    # Link bulunamazsa eski linki korumak yerine 'Yayın Yok' mesajı veriyoruz
    final_link = link if link else "https://beklemede.com/yayin-yok.m3u8"
    
    content = f"""#EXTM3U
#EXTINF:-1 tvg-id="beinsport-feed1" group-title="{PACKAGE_NAME}",Beinsport FEED 1
{final_link}
"""
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"İşlem Tamam: {final_link}")

if __name__ == "__main__":
    final_source = get_deep_link()
    write_m3u(final_source)
