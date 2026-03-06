from http.server import BaseHTTPRequestHandler
import requests

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Linki parametre olarak al (örn: /api/proxy?link=http://...)
        from urllib.parse import urlparse, parse_qs
        query = parse_qs(urlparse(self.path).query)
        target_link = query.get('link', [None])[0]

        if not target_link:
            self.send_response(400)
            self.end_headers()
            return

        # JustinTV'yi kandırmak için gereken headerlar
        headers = {
            'Referer': 'https://justintv.co/',
            'User-Agent': 'Mozilla/5.0'
        }
        
        req = requests.get(target_link, headers=headers, stream=True)
        self.send_response(200)
        self.send_header('Content-type', 'application/vnd.apple.mpegurl')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(req.content)
