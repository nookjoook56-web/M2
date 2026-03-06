from http.server import BaseHTTPRequestHandler
import requests
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        target = query.get('link', [None])[0]

        if not target:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Hata: Link yok.")
            return

        # Daha agresif bir header yapısı
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://larcivertsports1.blogspot.com/',
            'Origin': 'https://larcivertsports1.blogspot.com'
        }
        
        try:
            # Stream=False yaparak Vercel'in parça parça gönderme sorununu aşalım
            resp = requests.get(target, headers=headers, timeout=10, verify=False)
            
            self.send_response(resp.status_code)
            self.send_header('Content-type', 'application/vnd.apple.mpegurl')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(resp.content)
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Proxy Hatasi: {str(e)}".encode())
            
