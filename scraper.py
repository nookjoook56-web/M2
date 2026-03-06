        except:
            continue
    return None

def save_m3u(link):
    # Kayıtlı bilgilerinize göre yapılandırma uygulanıyor
    if link:
        # Yakalanan ham m3u8 linkini Vercel Proxy adresine parametre olarak ekliyoruz
        final_url = f"{VERCEL_PROXY_URL}?link={link}"
        print(f"Yayın yakalandı ve Proxy'ye yönlendirildi: {final_url}")
    else:
        # Eğer kaynaklarda o an yayın yoksa hata linkine yönlendiriyoruz
        final_url = "https://raw.githubusercontent.com/nookjoook56-web/M2/main/error.m3u8"
        print("Aktif yayın bulunamadı, bekleme linki yazılıyor.")

    # M3U Dosya İçeriği (Paket adı: backdor22)
    content = f"""#EXTM3U
#EXTINF:-1 tvg-id="beinsport-feed1" group-title="{PACKAGE_NAME}",Beinsport FEED 1
{final_url}
"""
    
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    stream = get_stream_link()
    save_m3u(stream)
    
