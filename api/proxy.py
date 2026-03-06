from http.server import BaseHTTPRequestHandler
import requests
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Link parametresini güvenli bir şekilde al
        query = parse_qs(urlparse(self.path).query)
        target_link = query.get('link', [None])[0]

        if not target_link:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Hata: Link parametresi eksik.")
            return

        # Blogspot ve sunucu korumalarını aşmak için başlıklar
        headers = {
            'Referer': 'https://larcivertsports1.blogspot.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            # Yayını stream olarak çek ve ilet
            req = requests.get(target_link, headers=headers, stream=True, timeout=10)
            self.send_response(req.status_code)
            
            # Gerekli header'ları ekle
            self.send_header('Content-type', 'application/vnd.apple.mpegurl')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # İçeriği parçalar halinde gönder
            self.wfile.write(req.content)
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())
            
