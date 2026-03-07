import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    # --- YAPILANDIRMA ---
    # Render üzerinde aktif olan proxy adresin
    PROXY = "https://backdor-proxy.onrender.com/proxy?link="
    # Çekilecek Atom kanal listesi
    SOURCE_URL = "https://telegram-grubuma-ozellistelerim.umitm0dlive.workers.dev/Atom"
    FILE_NAME = "playlist.m3u"
    PACKAGE = "backdor22" 

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    print("🚀 Süreç başlatıldı: Atom kanalları çekiliyor...")

    try:
        # Kaynaktan ham veriyi çekiyoruz
        response = requests.get(SOURCE_URL, headers=headers, verify=False, timeout=30)
        
        if response.status_code == 200 and response.text.strip():
            lines = response.text.splitlines()
            count = 0
            
            with open(FILE_NAME, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")
                
                for line in lines:
                    line = line.strip()
                    if line.startswith("http"):
                        # Linklerin başına Render proxy'sini ekliyoruz
                        final_link = f"{PROXY}{line}"
                        f.write(f"{final_link}\n")
                        count += 1
                    elif line.startswith("#EXTINF"):
                        # Grup ismini paket adına (backdor22) göre güncelliyoruz
                        # Eğer group-title yoksa veya boşsa ekleme yapar
                        if 'group-title="' in line:
                            updated_inf = line.replace('group-title=""', f'group-title="{PACKAGE}"')
                        else:
                            updated_inf = line.replace('#EXTINF:-1', f'#EXTINF:-1 group-title="{PACKAGE}"')
                        f.write(f"{updated_inf}\n")
            
            print(f"✅ Başarılı: {count} adet kanal {FILE_NAME} dosyasına yazıldı.")
        else:
            print(f"❌ Kaynak hatası veya boş veri: Durum Kodu {response.status_code}")
            
    except Exception as e:
        print(f"❌ Script Hatası: {e}")

if __name__ == "__main__":
    main()
                
