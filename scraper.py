import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    # --- YAPILANDIRMA ---
    # Render üzerinde yeni kurduğun proxy
    PROXY = "https://backdor-proxy.onrender.com/proxy?link="
    # Çekilecek yeni kaynak adresi
    SOURCE_URL = "https://larcivertsports1.blogspot.com/?m=1"
    FILE_NAME = "playlist.m3u"
    PACKAGE = "backdor22" # Kayıtlı paket ismin

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    print("🚀 Atom kanalları çekiliyor...")

    try:
        # Kaynaktan ham veriyi çekiyoruz
        response = requests.get(SOURCE_URL, headers=headers, verify=False, timeout=20)
        if response.status_code == 200:
            lines = response.text.splitlines()
            
            with open(FILE_NAME, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")
                
                for line in lines:
                    if line.startswith("http"):
                        # Linklerin başına Render proxy'sini ekliyoruz
                        final_link = f"{PROXY}{line.strip()}"
                        f.write(f"{final_link}\n")
                    elif line.startswith("#EXTINF"):
                        # Grup ismini paket adına göre güncelliyoruz
                        updated_inf = line.replace('group-title=""', f'group-title="{PACKAGE}"')
                        f.write(f"{updated_inf}\n")
            
            print(f"✅ Başarılı: {FILE_NAME} oluşturuldu.")
        else:
            print(f"❌ Kaynak hatası: {response.status_code}")
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")

if __name__ == "__main__":
    main()
    
