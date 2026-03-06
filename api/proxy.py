from http.server import BaseHTTPRequestHandler
import requests
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. Gelen link parametresini güvenli bir şekilde al
        query = parse_qs(urlparse(self.path).query)
        target_link = query.get('link', [None])[0]

        if not target_link:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Hata: Gecerli bir link parametresi bulunamadi.")
            return

        # 2. Blogspot sunucularının beklediği kritik başlıklar (Headers)
        headers = {
            'Referer': 'https://larcivertsports1.blogspot.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Origin': 'https://larcivertsports1.blogspot.com'
        }
        
        try:
            # 3. Yayını (m3u8/ts) hedef sunucudan çek
            # Stream=True kullanarak veriyi parça parça aktarıyoruz (hız için önemli)
            req = requests.get(target_link, headers=headers, stream=True, timeout=10)
            
            # 4. Yanıtı başlat ve CORS (Erişim) izinlerini ekle
            self.send_response(req.status_code)
            self.send_header('Content-type', req.headers.get('Content-Type', 'application/vnd.apple.mpegurl'))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.end_headers()
            
            # 5. Veriyi istemciye (oynatıcıya) yaz
            self.wfile.write(req.content)

        except Exception as e:
            # Hata durumunda log bas
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Proxy Hatasi: {str(e)}".encode())
            
