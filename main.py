"""
EduAI UZ v3.0 ULTRA — Smarter Learning, Better Future
"""
import streamlit as st
import os, json, time, random, hashlib, datetime, re, base64
from pathlib import Path
from dotenv import load_dotenv
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import requests
from urllib.parse import urlencode
from groq import Groq

load_dotenv()

# ── CONFIG ──────────────────────────────────────────────────────────────────
GROQ_API_KEY         = os.getenv("GROQ_API_KEY", "")
GOOGLE_CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
REDIRECT_URI = os.getenv("REDIRECT_URI", "https://eduai-uz.streamlit.app")
ADMIN_EMAILS         = ["muhammadaliortiqov54@gmail.com"]
TELEGRAM_USER        = "Ortiqov_ali"

PLANS = {
    "free":    {"nom":"Bepul",           "narx":0,     "emoji":"🆓"},
    "student": {"nom":"Student Premium", "narx":29900, "emoji":"⭐"},
    "pro":     {"nom":"Pro Premium",     "narx":59900, "emoji":"🏆"},
    "teacher": {"nom":"O'qituvchi",      "narx":99900, "emoji":"👨‍🏫"},
}
FREE_Q_LIMIT  = 20   # kunlik savol (bepul)
FREE_T_LIMIT  = 5    # oylik test (bepul)

# ── PAPKALAR ─────────────────────────────────────────────────────────────────
for d in ["data/users","data/history","data/announce"]:
    Path(d).mkdir(parents=True, exist_ok=True)

# ── SAHIFA ───────────────────────────────────────────────────────────────────
st.set_page_config(page_title="EduAI UZ", page_icon="🎓",
                   layout="wide", initial_sidebar_state="expanded")

# ── LOGO ─────────────────────────────────────────────────────────────────────
_LOGO = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 320" width="{sz}" height="{sz}">
<defs>
  <linearGradient id="lg1" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" style="stop-color:#00cfff"/><stop offset="50%" style="stop-color:#5a7fff"/>
    <stop offset="100%" style="stop-color:#7b5ea7"/></linearGradient>
  <linearGradient id="lg2" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" style="stop-color:#a0b8ff"/><stop offset="100%" style="stop-color:#7b5ea7"/></linearGradient>
  <filter id="gw"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <filter id="sg"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<g filter="url(#sg)">
  <path d="M60,185 C40,175 28,155 30,132 C32,115 42,102 56,96 C52,80 58,64 72,56 C84,48 100,50 112,58 C118,44 132,36 148,38 C164,40 174,52 176,66 C190,60 206,64 214,76 C222,88 220,104 212,114 C224,122 230,136 226,150 C222,166 208,174 194,172 C188,186 174,194 158,192 C144,190 134,182 130,170 C116,178 96,186 80,184 Z" fill="none" stroke="url(#lg1)" stroke-width="3.5" stroke-linecap="round"/>
  <path d="M192,56 C212,50 244,58 258,76 L262,192 C248,176 216,168 196,172 Z" fill="none" stroke="url(#lg2)" stroke-width="3.5" stroke-linecap="round"/>
  <line x1="172" y1="68" x2="192" y2="178" stroke="url(#lg2)" stroke-width="2.5" stroke-linecap="round"/>
  <path d="M172,68 C152,62 124,70 114,86 L110,190 C124,178 152,170 170,174 Z" fill="none" stroke="url(#lg2)" stroke-width="3" stroke-linecap="round"/>
</g>
<g filter="url(#gw)">
  <rect x="148" y="108" width="64" height="64" rx="10" fill="#0a0a1e" stroke="url(#lg1)" stroke-width="2.5"/>
  <rect x="158" y="118" width="44" height="44" rx="6" fill="#0d0d2e" stroke="url(#lg1)" stroke-width="1.5" opacity="0.8"/>
  <line x1="160" y1="108" x2="160" y2="96" stroke="#00cfff" stroke-width="2" stroke-linecap="round"/>
  <line x1="172" y1="108" x2="172" y2="94" stroke="#00cfff" stroke-width="2" stroke-linecap="round"/>
  <line x1="184" y1="108" x2="184" y2="96" stroke="#00cfff" stroke-width="2" stroke-linecap="round"/>
  <line x1="196" y1="108" x2="196" y2="94" stroke="#7b5ea7" stroke-width="2" stroke-linecap="round"/>
  <line x1="160" y1="172" x2="160" y2="184" stroke="#00cfff" stroke-width="2" stroke-linecap="round"/>
  <line x1="172" y1="172" x2="172" y2="186" stroke="#00cfff" stroke-width="2" stroke-linecap="round"/>
  <line x1="184" y1="172" x2="184" y2="184" stroke="#00cfff" stroke-width="2" stroke-linecap="round"/>
  <line x1="148" y1="122" x2="134" y2="122" stroke="#00cfff" stroke-width="2" stroke-linecap="round"/>
  <line x1="148" y1="134" x2="132" y2="134" stroke="#7b5ea7" stroke-width="2" stroke-linecap="round"/>
  <line x1="148" y1="146" x2="134" y2="146" stroke="#00cfff" stroke-width="2" stroke-linecap="round"/>
  <line x1="148" y1="158" x2="132" y2="158" stroke="#7b5ea7" stroke-width="2" stroke-linecap="round"/>
  <line x1="212" y1="122" x2="226" y2="122" stroke="#00cfff" stroke-width="2" stroke-linecap="round"/>
  <line x1="212" y1="134" x2="228" y2="134" stroke="#7b5ea7" stroke-width="2" stroke-linecap="round"/>
  <line x1="212" y1="146" x2="226" y2="146" stroke="#00cfff" stroke-width="2" stroke-linecap="round"/>
  <line x1="212" y1="158" x2="228" y2="158" stroke="#7b5ea7" stroke-width="2" stroke-linecap="round"/>
  <text x="180" y="146" text-anchor="middle" dominant-baseline="middle"
        font-family="Arial Black,sans-serif" font-weight="900" font-size="22"
        fill="url(#lg1)" filter="url(#gw)">AI</text>
</g>
<g stroke="#00cfff" stroke-width="1.8" fill="none" opacity="0.85" stroke-linecap="round">
  <line x1="130" y1="108" x2="148" y2="122"/><line x1="110" y1="124" x2="132" y2="134"/>
  <line x1="114" y1="148" x2="134" y2="146"/><line x1="118" y1="166" x2="132" y2="158"/>
  <circle cx="126" cy="106" r="4" stroke="#00cfff" fill="#050510" stroke-width="2"/>
  <circle cx="106" cy="122" r="4" stroke="#00cfff" fill="#050510" stroke-width="2"/>
  <circle cx="108" cy="146" r="4" stroke="#7b5ea7" fill="#050510" stroke-width="2"/>
  <circle cx="112" cy="168" r="4" stroke="#7b5ea7" fill="#050510" stroke-width="2"/>
</g>
<text x="85" y="244" font-family="Arial Black,sans-serif" font-weight="900" font-size="54" fill="white" letter-spacing="-1">Edu</text>
<text x="193" y="244" font-family="Arial Black,sans-serif" font-weight="900" font-size="54" fill="url(#lg1)" letter-spacing="-1">AI</text>
<line x1="100" y1="258" x2="135" y2="258" stroke="url(#lg1)" stroke-width="1.5"/>
<text x="160" y="263" text-anchor="middle" font-family="Arial,sans-serif" font-weight="700" font-size="13" fill="#00cfff" letter-spacing="5">UZ</text>
<line x1="185" y1="258" x2="220" y2="258" stroke="url(#lg1)" stroke-width="1.5"/>
<text x="160" y="285" text-anchor="middle" font-family="Arial,sans-serif" font-size="9.5" fill="#8892b0" letter-spacing="2.5">SMARTER LEARNING, BETTER FUTURE</text>
</svg>"""

def logo_img(sz=200):
    s = _LOGO.replace("{sz}", str(sz))
    b = base64.b64encode(" ".join(s.split()).encode()).decode()
    return f'<img src="data:image/svg+xml;base64,{b}" width="{sz}" height="{sz}" style="display:block;margin:0 auto;"/>'

# ── CSS ───────────────────────────────────────────────────────────────────────
def css():
    st.markdown("""<style>
:root{--c1:#00cfff;--c2:#7b5ea7;--c3:#00ff9f;--txt:#e8eaf6;--m:#8892b0;
      --gl:rgba(255,255,255,0.04);--bd:rgba(0,207,255,0.18);--r:16px;}
.stApp{background:#050510;
  background-image:radial-gradient(ellipse 80% 50% at 20% 10%,rgba(0,100,200,.18) 0%,transparent 60%),
    radial-gradient(ellipse 60% 40% at 80% 80%,rgba(123,94,167,.15) 0%,transparent 60%);
  color:var(--txt);font-family:'Segoe UI',sans-serif;}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#080820,#0d0d2b)!important;
  border-right:1px solid var(--bd)!important;}
.gc{background:var(--gl);border:1px solid var(--bd);border-radius:var(--r);
  padding:20px;backdrop-filter:blur(12px);box-shadow:0 8px 32px rgba(0,0,0,.6);
  margin-bottom:16px;transition:border-color .3s;}
.gc:hover{border-color:var(--c1);}
.cu{background:linear-gradient(135deg,rgba(0,100,200,.35),rgba(0,207,255,.15));
  border:1px solid rgba(0,207,255,.25);border-radius:18px 18px 4px 18px;
  padding:14px 18px;margin:8px 0;max-width:80%;margin-left:auto;color:#fff;}
.ca{background:linear-gradient(135deg,rgba(20,20,60,.8),rgba(123,94,167,.2));
  border:1px solid rgba(123,94,167,.3);border-radius:18px 18px 18px 4px;
  padding:14px 18px;margin:8px 0;max-width:85%;color:var(--txt);line-height:1.6;}
.xo{background:rgba(255,255,255,.08);border-radius:20px;height:12px;overflow:hidden;margin:6px 0;}
.xi{height:100%;border-radius:20px;background:linear-gradient(90deg,var(--c2),var(--c1));transition:width .8s;}
.sc{background:var(--gl);border:1px solid var(--bd);border-radius:12px;padding:16px;text-align:center;}
.sn{font-size:2rem;font-weight:700;background:linear-gradient(135deg,var(--c1),var(--c2));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.bdg{display:inline-block;padding:4px 12px;border-radius:20px;font-size:.75rem;
  font-weight:600;background:linear-gradient(135deg,var(--c2),var(--c1));color:#fff;margin:2px;}
.pfree{background:linear-gradient(135deg,#444,#666);}
.pstudent{background:linear-gradient(135deg,#f59e0b,#fbbf24);}
.ppro{background:linear-gradient(135deg,var(--c2),var(--c1));}
.pteacher{background:linear-gradient(135deg,#059669,#10b981);}
.fc{background:linear-gradient(135deg,rgba(0,207,255,.1),rgba(123,94,167,.1));
  border:1px solid rgba(0,207,255,.3);border-radius:20px;padding:40px;
  text-align:center;min-height:200px;cursor:pointer;transition:transform .3s;
  display:flex;align-items:center;justify-content:center;font-size:1.3rem;}
.fc:hover{transform:scale(1.02);}
.ann{background:linear-gradient(135deg,rgba(0,207,255,.08),rgba(123,94,167,.08));
  border-left:4px solid var(--c1);border-radius:8px;padding:12px 16px;margin:8px 0;}
.stButton>button{background:linear-gradient(135deg,var(--c2),var(--c1))!important;
  color:#fff!important;border:none!important;border-radius:10px!important;
  font-weight:600!important;padding:10px 24px!important;transition:opacity .2s!important;}
.stButton>button:hover{opacity:.85!important;}
.stTextInput>div>div>input,.stTextArea>div>div>textarea{
  background:rgba(255,255,255,.05)!important;border:1px solid var(--bd)!important;
  color:var(--txt)!important;border-radius:10px!important;}
.stTabs [data-baseweb="tab"]{color:var(--m)!important;}
.stTabs [aria-selected="true"]{color:var(--c1)!important;border-bottom:2px solid var(--c1)!important;}
::-webkit-scrollbar{width:6px;}::-webkit-scrollbar-thumb{background:var(--c2);border-radius:4px;}
[data-testid="metric-container"]{background:var(--gl)!important;
  border:1px solid var(--bd)!important;border-radius:12px!important;padding:12px!important;}
@keyframes fl{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
.fl{animation:fl 3s ease-in-out infinite;display:inline-block;}
@keyframes fu{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
.f1{animation:fu .5s ease forwards;}
.f2{animation:fu .5s ease .15s forwards;opacity:0;}
.f3{animation:fu .5s ease .3s forwards;opacity:0;}
</style>""", unsafe_allow_html=True)

# ── DATA ──────────────────────────────────────────────────────────────────────
def uf(uid): return Path(f"data/users/{uid}.json")
def hf(uid): return Path(f"data/history/{uid}.json")

def load_user(uid):
    fp = uf(uid)
    if fp.exists():
        try:
            with open(fp,encoding="utf-8") as f: return json.load(f)
        except: pass
    return {"id":uid,"name":"","email":"","avatar":"",
            "created":datetime.datetime.now().isoformat(),
            "xp":0,"level":1,"badges":[],"test_scores":[],
            "mood_history":[],"streak":0,"last_active":datetime.date.today().isoformat(),
            "total_messages":0,"topics":{},"flashcards":[],
            "daily_q":0,"daily_date":"","monthly_t":0,"monthly_date":"",
            "premium":"free","premium_exp":"",
            "settings":{"ai_style":"o'qituvchi"}}

def save_user(u):
    with open(uf(u["id"]),"w",encoding="utf-8") as f:
        json.dump(u, f, ensure_ascii=False, indent=2)

def load_hist(uid):
    fp = hf(uid)
    if fp.exists():
        try:
            with open(fp,encoding="utf-8") as f: return json.load(f)
        except: pass
    return []

def save_hist(uid,h):
    with open(hf(uid),"w",encoding="utf-8") as f: json.dump(h,f,ensure_ascii=False,indent=2)

def add_msg(uid,role,content):
    h = load_hist(uid)
    h.append({"role":role,"content":content,"ts":datetime.datetime.now().isoformat()})
    save_hist(uid,h)
    return h

def all_users():
    us=[]
    for fp in Path("data/users").glob("*.json"):
        try:
            with open(fp,encoding="utf-8") as f: us.append(json.load(f))
        except: pass
    return us

def load_ann():
    fp=Path("data/announce/list.json")
    if fp.exists():
        try:
            with open(fp,encoding="utf-8") as f: return json.load(f)
        except: pass
    return []

def save_ann(lst):
    with open("data/announce/list.json","w",encoding="utf-8") as f: json.dump(lst,f,ensure_ascii=False,indent=2)

# ── PREMIUM ───────────────────────────────────────────────────────────────────
def is_prem(u):
    p=u.get("premium","free")
    if p=="free": return False
    exp=u.get("premium_exp","")
    if exp:
        try:
            if datetime.date.fromisoformat(exp)<datetime.date.today():
                u["premium"]="free"; save_user(u); return False
        except: pass
    return p in ["student","pro","teacher"]

def get_plan(u): return u.get("premium","free")

def can_ask(u):
    if is_prem(u): return True
    today=datetime.date.today().isoformat()
    if u.get("daily_date")!=today: u["daily_q"]=0; u["daily_date"]=today; save_user(u)
    return u.get("daily_q",0)<FREE_Q_LIMIT

def inc_daily(u): u["daily_q"]=u.get("daily_q",0)+1; save_user(u)

def is_admin(u): return u.get("email","") in ADMIN_EMAILS

# ── GAMIFICATION ──────────────────────────────────────────────────────────────
LVS=  [0,100,250,500,900,1400,2100,3000,4200,5800,8000]
LNAMES=["Yangi boshlovchi","Talaba","Izlanuvchi","Bilimdon",
        "Ekspert","Master","Ustoz","Akademik","Professor","Dono","Inson AI"]
BDGS={
    "birinchi_qadam":{"e":"🚀","n":"Birinchi qadam","t":"Birinchi suhbat"},
    "faol":          {"e":"📚","n":"Faol o'quvchi", "t":"50 xabar"},
    "test_ustasi":   {"e":"🏆","n":"Test ustasi",   "t":"5 test"},
    "streak_7":      {"e":"🔥","n":"7 kun streak",  "t":"7 kun ketma-ket"},
    "bilimdon":      {"e":"🎓","n":"Bilimdon",      "t":"500 XP"},
    "premium":       {"e":"💎","n":"Premium",       "t":"Premium obuna"},
    "flash_master":  {"e":"🃏","n":"Flashcard usta","t":"50 karta"},
    "turnir":        {"e":"🥇","n":"Turnir g'olibi","t":"Turnirda 1-o'rin"},
}

def get_lv(xp):
    lv=1
    for i,t in enumerate(LVS):
        if xp>=t: lv=i+1
    lv=min(lv,len(LNAMES))
    return lv,LNAMES[lv-1],LVS[lv-1],LVS[lv] if lv<len(LVS) else LVS[-1]+1000

def add_xp(u,n):
    old=get_lv(u["xp"])[0]
    u["xp"]=u.get("xp",0)+n
    new=get_lv(u["xp"])[0]
    if new>old: st.balloons(); st.success(f"🎉 {LNAMES[new-1]} darajasiga ko'tarildingiz!")
    save_user(u); return u

def chk_bdg(u):
    e=set(u.get("badges",[]))
    hl=len(load_hist(u["id"]))
    for bid,cond in [("birinchi_qadam",hl>=1),("faol",u.get("total_messages",0)>=50),
                     ("test_ustasi",len(u.get("test_scores",[]))>=5),
                     ("bilimdon",u.get("xp",0)>=500),("premium",is_prem(u))]:
        if cond and bid not in e:
            e.add(bid); st.toast(f"{BDGS[bid]['e']} Badge: {BDGS[bid]['n']}!",icon="🏅")
    u["badges"]=list(e); save_user(u); return u

def upd_streak(u):
    today=datetime.date.today().isoformat()
    yest=(datetime.date.today()-datetime.timedelta(days=1)).isoformat()
    last=u.get("last_active","")
    if last==today: return u
    u["streak"]=u.get("streak",0)+1 if last==yest else 1
    u["last_active"]=today
    if u["streak"]>=7 and "streak_7" not in u.get("badges",[]):
        u.setdefault("badges",[]).append("streak_7"); st.toast("🔥 7 kun streak!",icon="🏅")
    save_user(u); return u

# ── AI ────────────────────────────────────────────────────────────────────────
def gcl():
    if not GROQ_API_KEY: st.error("❌ GROQ_API_KEY topilmadi!"); return None
    return Groq(api_key=GROQ_API_KEY)

def sys_p(u,mode="chat"):
    lv,ln,_,_=get_lv(u.get("xp",0))
    style=u.get("settings",{}).get("ai_style","o'qituvchi")
    mood=(u.get("mood_history",[{}])[-1].get("mood","neytral") if u.get("mood_history") else "neytral")
    plan=get_plan(u); pe=PLANS.get(plan,{}).get("emoji","🆓")
    base=f"""Sen EduAI UZ — O'zbekistonning eng ilg'or AI ta'lim yordamchisissan.

FOYDALANUVCHI: {u.get('name','')}, {ln} (Lv.{lv}), Kayfiyat:{mood}, Uslub:{style}, {pe} {plan.upper()}

ASOSIY QOIDALAR:
1. FAQAT O'ZBEK TILIDA javob ber (so'rasagina boshqa til)
2. Aniq, tushunarli, ilmiy to'g'ri javoblar
3. Misollar, analogiyalar va markdown bilan tushuntir
4. Bosqichma-bosqich o'rgat
5. Foydalanuvchini rag'batlantir va motivatsiya ber
6. Emoji'lardan o'rinli foydalan: ✅❌📌💡⚡🔬🧮📐🎯
7. Kayfiyatga mos: xursand→energetik, xafa→yumshoq, stressli→oddiy
8. Har javob oxirida 1-2 qiziqarli savol ber
9. Premium foydalanuvchilarga chuqurroq va batafsil javob ber
10. Matematik hisoblashda bosqichlarni ko'rsat"""
    if mode=="konspekt":
        base+="""

REJIM: KONSPEKT YARATISH
## 📌 [Mavzu nomi]
### 🔑 Asosiy tushunchalar
### 📋 Muhim qoidalar
### 💡 Misollar
### 🧮 Formulalar
### ❓ O'z-o'zini tekshirish (3-5 savol)"""
    elif mode=="test":
        base+="""

REJIM: TEST — FAQAT JSON qaytargin:
[{"savol":"...","variantlar":["A) ...","B) ...","C) ...","D) ..."],"togri_javob":"A","izoh":"..."}]"""
    elif mode=="mental":
        base+="""

REJIM: KAYFIYAT TAHLIL — FAQAT JSON:
{"kayfiyat":"xursand|neytral|xafa|stressli","daraja":1-10,"sabab":"...","maslahat":"..."}"""
    elif mode=="kod":
        base+="""

REJIM: DASTURLASH O'QITUVCHISI
Kodni tushuntir, xatolarni aniqla, yaxshilanishlar tavsiya qil. ``` ichida yoz."""
    return base

def ask_ai(u,msgs,mode="chat",ctx=""):
    cl=gcl()
    if not cl: return "AI bilan bog'lanib bo'lmadi."
    sp=sys_p(u,mode)
    if ctx: sp+=f"\n\nQO'SHIMCHA:\n{ctx}"
    recent=msgs[-30:]
    api_msgs=[{"role":"system","content":sp}]
    for m in recent:
        api_msgs.append({"role":"user" if m["role"]=="user" else "assistant","content":m["content"]})
    try:
        r=gcl().chat.completions.create(
            model="llama-3.3-70b-versatile",messages=api_msgs,temperature=0.75,max_tokens=3000)
        return r.choices[0].message.content
    except Exception as e: return f"❌ Xato: {e}"

def mood_ai(u,text):
    cl=gcl()
    if not cl: return {"kayfiyat":"neytral","daraja":5,"sabab":"","maslahat":""}
    try:
        r=Groq(api_key=GROQ_API_KEY).chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"system","content":sys_p(u,"mental")},
                      {"role":"user","content":f"Tahlil: {text}"}],
            temperature=0.3,max_tokens=256)
        raw=re.sub(r"```json|```","",r.choices[0].message.content).strip()
        return json.loads(raw)
    except: return {"kayfiyat":"neytral","daraja":5,"sabab":"","maslahat":"Yaxshi kun!"}

def gen_test(u,mavzu,n=5):
    cl=gcl()
    if not cl: return []
    try:
        r=Groq(api_key=GROQ_API_KEY).chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"system","content":sys_p(u,"test")},
                      {"role":"user","content":f"'{mavzu}' bo'yicha {n} ta test savoli."}],
            temperature=0.7,max_tokens=3000)
        raw=re.sub(r"```json|```","",r.choices[0].message.content).strip()
        return json.loads(raw)
    except: return []

def gen_konspekt(u,hist):
    if not hist: return "Suhbat tarixi yo'q."
    txt="\n".join([f"{m['role'].upper()}: {m['content']}" for m in hist[-20:]])
    try:
        r=Groq(api_key=GROQ_API_KEY).chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"system","content":sys_p(u,"konspekt")},
                      {"role":"user","content":f"Konspekt:\n{txt}"}],
            temperature=0.5,max_tokens=2500)
        return r.choices[0].message.content
    except Exception as e: return f"Xato: {e}"

def gen_flash(u,mavzu,n=10):
    try:
        r=Groq(api_key=GROQ_API_KEY).chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"system","content":"Faqat JSON qaytargin: [{\"savol\":\"...\",\"javob\":\"...\"}]"},
                      {"role":"user","content":f"'{mavzu}' — {n} ta flashcard. O'zbek tilida."}],
            temperature=0.7,max_tokens=2000)
        raw=re.sub(r"```json|```","",r.choices[0].message.content).strip()
        return json.loads(raw)
    except: return []

# ── GOOGLE AUTH ───────────────────────────────────────────────────────────────
def g_url():
    if not GOOGLE_CLIENT_ID: return ""
    params = {
            "client_id": GOOGLE_CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "select_account"
        }
    return "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)

def g_token(code):
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET: return None
    try:
        r=requests.post("https://oauth2.googleapis.com/token",data={
            "code":code,"client_id":GOOGLE_CLIENT_ID,"client_secret":GOOGLE_CLIENT_SECRET,
            "redirect_uri":REDIRECT_URI,"grant_type":"authorization_code"},timeout=10)
        return r.json() if r.ok else None
    except: return None

def g_info(token):
    try:
        r=requests.get("https://www.googleapis.com/oauth2/v2/userinfo",
                       headers={"Authorization":f"Bearer {token}"},timeout=10)
        return r.json() if r.ok else None
    except: return None

def g_callback():
    """Google OAuth callback — code ni token bilan almashtiradi."""
    code = st.query_params.get("code", "")
    if not code:
        st.session_state["auth_msg"] = "Code topilmadi"
        return None

    # Token olish
    td = g_token(code)
    if not td:
        st.session_state["auth_msg"] = "Token server javobi yo'q"
        return None
    if "access_token" not in td:
        err = td.get("error_description", td.get("error", "Token xatosi"))
        st.session_state["auth_msg"] = f"Token xatosi: {err}"
        return None

    # Foydalanuvchi ma'lumotlari
    info = g_info(td["access_token"])
    if not info:
        st.session_state["auth_msg"] = "Google profil olinmadi"
        return None
    if "email" not in info:
        st.session_state["auth_msg"] = f"Email yo'q. Info: {info}"
        return None

    uid = hashlib.md5(info["email"].encode()).hexdigest()[:12]
    u   = load_user(uid)
    u.update({
        "name":   info.get("name", "Foydalanuvchi"),
        "email":  info.get("email", ""),
        "avatar": info.get("picture", ""),
        "id":     uid
    })
    save_user(u)
    return u

def demo_login(name="O'quvchi"):
    uid=hashlib.md5(f"demo_{name}_{datetime.date.today()}".encode()).hexdigest()[:12]
    u=load_user(uid)
    u.update({"name":name,"email":f"demo_{uid}@eduai.uz","id":uid,
              "avatar":f"https://ui-avatars.com/api/?name={name}&background=0D8ABC&color=fff"})
    save_user(u); return u

# ── LOGIN ─────────────────────────────────────────────────────────────────────
def render_login():
    st.markdown("""<style>
.lb{background:rgba(10,10,35,.92);border:1px solid rgba(0,207,255,.2);border-radius:28px;
  padding:48px 44px 40px;backdrop-filter:blur(20px);box-shadow:0 32px 80px rgba(0,0,0,.7);
  max-width:420px;width:100%;margin:0 auto;text-align:center;}
.gb{display:flex;align-items:center;justify-content:center;gap:14px;background:#fff;
  color:#3c4043;border:none;border-radius:14px;padding:15px 36px;font-size:1.05rem;
  font-weight:600;cursor:pointer;text-decoration:none;width:100%;
  transition:box-shadow .25s,transform .2s;box-shadow:0 4px 20px rgba(0,0,0,.5);}
.gb:hover{transform:translateY(-3px);box-shadow:0 10px 40px rgba(0,207,255,.3);color:#3c4043;}
.pill{display:inline-block;background:rgba(0,207,255,.08);border:1px solid rgba(0,207,255,.2);
  border-radius:20px;padding:5px 14px;font-size:.78rem;color:#8892b0;margin:3px;}
</style>""", unsafe_allow_html=True)

    anns=[a for a in load_ann() if a.get("public")]
    for a in anns[-2:]:
        st.markdown(f"<div class='ann'>📢 <b>{a['title']}</b> — {a['text']}</div>",unsafe_allow_html=True)

    _,mid,_=st.columns([1,2.2,1])
    with mid:
        st.markdown(f"<div class='f1' style='text-align:center;'><div class='fl'>{logo_img(220)}</div></div>",
                    unsafe_allow_html=True)
        st.markdown("""<div class='lb f2'>
            <h2 style='color:#fff;font-size:1.5rem;font-weight:800;margin:0 0 6px;'>Xush kelibsiz! 👋</h2>
            <p style='color:#8892b0;font-size:.9rem;margin:0 0 28px;'>O'rganishni boshlash uchun kiring</p>
        </div>""",unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🔑 Kirish", "📝 Ro'yxatdan o'tish"])
        with tab1:
            with st.form("login_form"):
                email = st.text_input("📧 Email", placeholder="email@gmail.com")
                password = st.text_input("🔑 Parol", type="password", placeholder="Parolingiz")
                submitted = st.form_submit_button("Kirish", use_container_width=True)
                if submitted:
                    u = load_user(email)
                    if u and u.get("password") == hashlib.md5(password.encode()).hexdigest():
                        st.session_state["user"] = u
                        st.rerun()
                    else:
                        st.error("Email yoki parol noto'g'ri!")
        with tab2:
            with st.form("register_form"):
                name = st.text_input("👤 Ism")
                reg_email = st.text_input("📧 Email")
                reg_password = st.text_input("🔑 Parol", type="password")
                submitted2 = st.form_submit_button("Ro'yxatdan o'tish", use_container_width=True)
                if submitted2:
                    if load_user(reg_email):
                        st.error("Bu email allaqachon ro'yxatdan o'tgan!")
                    else:
                        save_user({"name":name,"email":reg_email,"password":hashlib.md5(reg_password.encode()).hexdigest(),"plan":"free","coins":100})
                        st.success("✅ Muvaffaqiyatli! Endi 'Kirish' tabiga o'ting.")


    gu=g_url()
    if gu:
            st.markdown(f"""<div class='f3' style='text-align:center;margin:0 0 12px;'>
            <a href='{gu}' target='_self' class='gb'>
              <svg width='22' height='22' viewBox='0 0 48 48'>
                <path fill='#FFC107' d='M43.611,20.083H42V20H24v8h11.303c-1.649,4.657-6.08,8-11.303,8c-6.627,0-12-5.373-12-12c0-6.627,5.373-12,12-12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C12.955,4,4,12.955,4,24c0,11.045,8.955,20,20,20c11.045,0,20-8.955,20-20C44,22.659,43.862,21.35,43.611,20.083z'/>
                <path fill='#FF3D00' d='M6.306,14.691l6.571,4.819C14.655,15.108,18.961,12,24,12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C16.318,4,9.656,8.337,6.306,14.691z'/>
                <path fill='#4CAF50' d='M24,44c5.166,0,9.86-1.977,13.409-5.192l-6.19-5.238C29.211,35.091,26.715,36,24,36c-5.202,0-9.619-3.317-11.283-7.946l-6.522,5.025C9.505,39.556,16.227,44,24,44z'/>
                <path fill='#1976D2' d='M43.611,20.083H42V20H24v8h11.303c-0.792,2.237-2.231,4.166-4.087,5.571l6.19,5.238C36.971,39.205,44,34,44,24C44,22.659,43.862,21.35,43.611,20.083z'/>
              </svg>
              Google bilan kirish
            </a>
            <p style='text-align:center;font-size:.75rem;color:#556;margin:8px 0 0;'>🔒 Xavfsiz autentifikatsiya</p>
            </div>""",unsafe_allow_html=True)


    if not gu:
            st.markdown("""<div style='background:rgba(255,150,0,0.12);border:1px solid rgba(255,150,0,0.3);
                border-radius:12px;padding:16px;text-align:center;margin-top:16px;'>
                <p style='color:#ffaa44;font-size:.9rem;margin:0;'>
                    ⚙️ Google kirish sozlanmagan.<br>
                    <code>.env</code> faylida <b>GOOGLE_CLIENT_ID</b> va <b>GOOGLE_CLIENT_SECRET</b> kiriting.
                </p></div>""", unsafe_allow_html=True)
    st.markdown("""<div style='text-align:center;margin-top:20px;'>
            <span class='pill'>🤖 AI O'qituvchi</span><span class='pill'>📊 Analitika</span>
            <span class='pill'>🏆 Turnirlar</span><span class='pill'>🃏 Flashcard</span>
            <span class='pill'>💎 Premium</span></div>""",unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
def render_sidebar(u):
    with st.sidebar:
        st.markdown(f"<div style='text-align:center;padding:8px 0 2px;'>{logo_img(140)}</div>",
                    unsafe_allow_html=True)
        st.markdown("---")
        if u.get("avatar"):
            st.markdown(f"<div style='text-align:center;'><img src='{u['avatar']}' style='border-radius:50%;width:56px;height:56px;border:2px solid #00cfff;'/></div>",
                        unsafe_allow_html=True)
        plan=get_plan(u); pi=PLANS.get(plan,{})
        st.markdown(f"<div style='text-align:center;margin:6px 0;'><div style='font-weight:700;font-size:1rem;'>{u.get('name','')}</div><span class='bdg p{plan}'>{pi.get('emoji','')} {pi.get('nom','')}</span></div>",
                    unsafe_allow_html=True)
        lv,ln,cur,nxt=get_lv(u.get("xp",0))
        xp=u.get("xp",0)
        pct=min((xp-cur)/max(nxt-cur,1)*100,100)
        st.markdown(f"<div style='font-size:.8rem;color:#8892b0;margin-bottom:4px;'>Lv.{lv} {ln} — {xp} XP</div><div class='xo'><div class='xi' style='width:{pct:.0f}%;'></div></div><div style='text-align:center;font-size:.8rem;color:#8892b0;margin:4px 0 8px;'>🔥 {u.get('streak',0)} kun streak</div>",
                    unsafe_allow_html=True)
        st.markdown("---")

        pages=[("💬","Suhbat","chat"),("📊","Analitika","analytics"),
               ("📝","Test Markazi","tests"),("🃏","Flashcard","flashcard"),
               ("🏆","Turnir & Reyting","tournament"),("📚","Kutubxona","library"),
               ("📖","Kitoblar","books"),("💎","Premium","premium"),("⚙️","Sozlamalar","settings")]
        if is_admin(u): pages.append(("🛡️","Admin Panel","admin"))

        if "page" not in st.session_state: st.session_state["page"]="chat"
        for em,lb,key in pages:
            active=st.session_state["page"]==key
            if st.button(f"{em} {lb}",use_container_width=True,
                         type="primary" if active else "secondary",key=f"nav_{key}"):
                st.session_state["page"]=key; st.rerun()

        st.markdown("---")
        if not is_prem(u):
            used=u.get("daily_q",0)
            st.markdown(f"<div style='font-size:.8rem;color:#8892b0;margin-bottom:4px;'>Kunlik: {used}/{FREE_Q_LIMIT}</div><div class='xo'><div class='xi' style='width:{min(used/FREE_Q_LIMIT*100,100):.0f}%;background:linear-gradient(90deg,#f59e0b,#ef4444);'></div></div>",
                        unsafe_allow_html=True)
            if st.button("💎 Premium olish",use_container_width=True):
                st.session_state["page"]="premium"; st.rerun()
        if st.button("🚪 Chiqish",use_container_width=True):
            for k in ["user","hist","page","ts","fc_i","fc_s","trn_s"]:
                st.session_state.pop(k,None)
            st.rerun()

# ── CHAT ──────────────────────────────────────────────────────────────────────
def render_chat(u):
    st.markdown("## 💬 AI O'qituvchi")
    anns=load_ann()
    for a in anns[-1:]:
        st.markdown(f"<div class='ann'>📢 <b>{a['title']}</b> — {a['text']}</div>",unsafe_allow_html=True)

    hist=st.session_state.get("hist",[])
    MODES=["💬 Oddiy suhbat","👨‍💻 Kod rejimi","📖 Kitob tahlili"]
    MODE_K=["chat","kod","kitob"]
    STYLES=["o'qituvchi","do'st","mentor","akademik"]

    c1,c2,c3=st.columns(3)
    with c1:
        if "cm" not in st.session_state: st.session_state["cm"]=0
        sel=st.selectbox("Rejim",MODES,index=st.session_state["cm"],label_visibility="collapsed")
        st.session_state["cm"]=MODES.index(sel)
    with c2:
        sty=st.selectbox("Uslub",STYLES,index=STYLES.index(u.get("settings",{}).get("ai_style","o'qituvchi")),label_visibility="collapsed")
        u["settings"]["ai_style"]=sty
    with c3:
        if st.button("🗑️ Tozalash",use_container_width=True):
            save_hist(u["id"],[]); st.session_state["hist"]=[]; st.rerun()

    if not hist:
        st.markdown("<div class='gc' style='text-align:center;'><div style='font-size:3rem;'>👋</div><h3>Assalomu alaykum! Men EduAI UZman.</h3><p style='color:#8892b0;'>Savollaringizni bering — tushuntiraman!</p></div>",
                    unsafe_allow_html=True)
    else:
        for m in hist:
            role=m.get("role","user"); cont=m.get("content",""); ts=m.get("ts","")[:16].replace("T"," ")
            if role=="user":
                st.markdown(f"<div class='cu'>{cont}<div style='font-size:.7rem;color:rgba(255,255,255,.4);margin-top:4px;text-align:right;'>{ts}</div></div>",unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='ca'><div style='font-size:.8rem;color:#00cfff;margin-bottom:6px;'>🤖 EduAI</div>{cont}<div style='font-size:.7rem;color:rgba(255,255,255,.3);margin-top:4px;'>{ts}</div></div>",unsafe_allow_html=True)

    quick=["📐 Matematika","🔬 Fizika","💻 Python","🌍 Ingliz tili","🧬 Biologiya","📝 Konspekt yarat"]
    cols=st.columns(len(quick))
    for i,q in enumerate(quick):
        with cols[i]:
            if st.button(q,key=f"qk{i}",use_container_width=True):
                if "Konspekt" in q:
                    with st.spinner("Konspekt yaratilmoqda..."):
                        k=gen_konspekt(u,hist)
                    st.markdown(f"<div class='gc'>{k}</div>",unsafe_allow_html=True)
                    st.download_button("⬇️ Yuklab olish",k.encode(),f"konspekt_{datetime.date.today()}.md","text/markdown")
                    u=add_xp(u,15); st.session_state["user"]=u
                else:
                    st.session_state["pend"]=q.split(" ",1)[1]

    if not can_ask(u):
        st.warning(f"⚠️ Kunlik {FREE_Q_LIMIT} ta savol limitiga yetdingiz!")
        if st.button("💎 Premium — cheksiz savol!"): st.session_state["page"]="premium"; st.rerun()
        return

    inp=st.chat_input("Savolingizni yozing...")
    if "pend" in st.session_state: inp=st.session_state.pop("pend")

    if inp and inp.strip():
        mode=MODE_K[st.session_state.get("cm",0)]
        if u.get("total_messages",0)%5==0:
            mood=mood_ai(u,inp)
            u.setdefault("mood_history",[]).append({"ts":datetime.datetime.now().isoformat(),"mood":mood.get("kayfiyat","neytral"),"daraja":mood.get("daraja",5)})
        hist=add_msg(u["id"],"user",inp); st.session_state["hist"]=hist
        with st.spinner("🤔 AI o'ylamoqda..."):
            reply=ask_ai(u,hist,mode)
        hist=add_msg(u["id"],"assistant",reply); st.session_state["hist"]=hist
        u["total_messages"]=u.get("total_messages",0)+1
        inc_daily(u); u=add_xp(u,5); u=chk_bdg(u)
        st.session_state["user"]=u; st.rerun()

# ── ANALYTICS ─────────────────────────────────────────────────────────────────
def render_analytics(u):
    st.markdown("## 📊 O'qish Analitikasi")
    hist=load_hist(u["id"]); tests=u.get("test_scores",[]); moods=u.get("mood_history",[])
    aus=all_users()
    avg=round(np.mean([s["ball"] for s in tests]),1) if tests else 0
    rnk=sorted(aus,key=lambda x:x.get("xp",0),reverse=True)
    mr=next((i+1 for i,x in enumerate(rnk) if x["id"]==u["id"]),"-")

    c1,c2,c3,c4,c5=st.columns(5)
    for col,n,l in [(c1,u.get("xp",0),"XP"),(c2,len(hist),"Xabarlar"),
                    (c3,len(tests),"Testlar"),(c4,f"{avg}%","O'rtacha"),(c5,f"#{mr}","Reyting")]:
        with col: st.markdown(f"<div class='sc'><div class='sn'>{n}</div><div style='color:#8892b0;font-size:.85rem;'>{l}</div></div>",unsafe_allow_html=True)
    st.markdown("---")

    cl,cr=st.columns(2)
    with cl:
        st.markdown("### 🕸️ Bilim Xaritasi")
        tp=u.get("topics",{})
        cats=list(tp.keys())[:8] if tp else ["Matematika","Fizika","Kimyo","Biologiya","Informatika","Tarix","Ingliz","Adabiyot"]
        vals=[tp[k] for k in cats] if tp else [random.randint(10,90) for _ in cats]
        fig=go.Figure(go.Scatterpolar(r=vals+[vals[0]],theta=cats+[cats[0]],fill='toself',
            fillcolor='rgba(0,207,255,.12)',line=dict(color='#00cfff',width=2)))
        fig.update_layout(polar=dict(radialaxis=dict(range=[0,100],gridcolor='rgba(255,255,255,.1)'),
            angularaxis=dict(gridcolor='rgba(255,255,255,.1)',tickfont=dict(color='#e8eaf6'))),
            paper_bgcolor='rgba(0,0,0,0)',font=dict(color='#e8eaf6'),height=380,showlegend=False,margin=dict(l=40,r=40,t=40,b=40))
        st.plotly_chart(fig,use_container_width=True)
    with cr:
        st.markdown("### 📈 Test Natijalari")
        if tests:
            df=pd.DataFrame(tests[-20:])
            fig2=go.Figure(go.Scatter(x=list(range(len(df))),y=df["ball"],mode='lines+markers',
                line=dict(color='#00cfff',width=2),marker=dict(size=8,color=df["ball"],colorscale='RdYlGn',cmin=0,cmax=100)))
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e8eaf6'),height=380,
                xaxis=dict(gridcolor='rgba(255,255,255,.05)'),
                yaxis=dict(gridcolor='rgba(255,255,255,.05)',range=[0,100]),margin=dict(l=20,r=20,t=20,b=20))
            st.plotly_chart(fig2,use_container_width=True)
        else: st.info("Hali test natijalari yo'q.")

    if moods:
        st.markdown("### 🌡️ Kayfiyat Heatmap")
        mm={"xursand":4,"neytral":3,"stressli":2,"xafa":1}
        days=[m.get("ts","")[:10] for m in moods[-30:]]
        scores=[mm.get(m.get("mood","neytral"),3) for m in moods[-30:]]
        fig3=go.Figure(go.Heatmap(z=[scores],x=days,y=["Kayfiyat"],
            colorscale=[[0,"#ff4444"],[.33,"#ff9f00"],[.66,"#00cfff"],[1,"#00ff9f"]],
            zmin=1,zmax=4,colorbar=dict(tickvals=[1,2,3,4],ticktext=["Xafa","Stressli","Neytral","Xursand"],tickfont=dict(color="#e8eaf6"))))
        fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)',font=dict(color='#e8eaf6'),height=160,margin=dict(l=20,r=20,t=20,b=40))
        st.plotly_chart(fig3,use_container_width=True)

    st.markdown("### 🏅 Badge'lar")
    bdgs=u.get("badges",[])
    if bdgs:
        cols=st.columns(min(len(bdgs),5))
        for i,bid in enumerate(bdgs):
            b=BDGS.get(bid,{})
            with cols[i%5]: st.markdown(f"<div class='gc' style='text-align:center;padding:12px;'><div style='font-size:2rem;'>{b.get('e','🏅')}</div><div style='font-size:.8rem;font-weight:700;'>{b.get('n','')}</div><div style='font-size:.7rem;color:#8892b0;'>{b.get('t','')}</div></div>",unsafe_allow_html=True)
    else: st.info("Badge yo'q. Ko'proq o'rgan!")

# ── TESTS ─────────────────────────────────────────────────────────────────────
def render_tests(u):
    st.markdown("## 📝 Test Markazi")
    if not is_prem(u):
        today_m=datetime.date.today().strftime("%Y-%m")
        if u.get("monthly_date","")!=today_m: u["monthly_t"]=0; u["monthly_date"]=today_m; save_user(u)
        used=u.get("monthly_t",0)
        st.markdown(f"<div style='font-size:.85rem;color:#8892b0;margin-bottom:8px;'>Oylik test: {used}/{FREE_T_LIMIT}</div>",unsafe_allow_html=True)
        if used>=FREE_T_LIMIT:
            st.warning("⚠️ Oylik limit!")
            if st.button("💎 Premium — cheksiz test"): st.session_state["page"]="premium"; st.rerun()
            return

    ts=st.session_state.get("ts")
    if ts is None:
        st.markdown("<div class='gc'>",unsafe_allow_html=True)
        mavzu=st.text_input("Mavzu","",placeholder="Kvadrat tenglamalar, Python, Tarix...")
        c1,c2,c3=st.columns(3)
        with c1: soni=st.slider("Savollar",3,20,5)
        with c2: daraja=st.selectbox("Qiyinlik",["Boshlang'ich","O'rta","Yuqori"])
        with c3: lang=st.selectbox("Til",["O'zbek","Rus","Ingliz"])
        st.markdown("</div>",unsafe_allow_html=True)
        if st.button("🚀 Test Boshlash",use_container_width=True):
            if mavzu.strip():
                with st.spinner("Test yaratilmoqda..."):
                    qs=gen_test(u,f"{mavzu} ({daraja}, {lang} tilida)",soni)
                if qs:
                    st.session_state["ts"]={"qs":qs,"cur":0,"ans":[],"mavzu":mavzu}
                    if not is_prem(u): u["monthly_t"]=u.get("monthly_t",0)+1; save_user(u); st.session_state["user"]=u
                    st.rerun()
                else: st.error("Test yaratishda xato.")
            else: st.warning("Mavzu kiriting!")

        sc=u.get("test_scores",[])
        if sc:
            st.markdown("### 📊 O'tgan Testlar")
            for s in reversed(sc[-10:]):
                e="✅" if s["ball"]>=70 else "⚠️" if s["ball"]>=50 else "❌"
                st.markdown(f"<div class='gc' style='padding:10px;display:flex;justify-content:space-between;'><span>{e} <b>{s.get('mavzu','')}</b></span><span style='color:#00cfff;'>{s['ball']}% — {s.get('sana','')[:10]}</span></div>",unsafe_allow_html=True)
    else:
        qs=ts["qs"]; cur=ts["cur"]; ans=ts["ans"]
        if cur>=len(qs):
            ok=sum(1 for a in ans if a.get("ok")); total=len(qs); ball=round(ok/total*100)
            e="🏆" if ball>=80 else "📚" if ball>=50 else "📖"
            st.markdown(f"<div class='gc' style='text-align:center;'><div style='font-size:4rem;'>{e}</div><h2>Test yakunlandi!</h2><div class='sn' style='font-size:3rem;'>{ball}%</div><p>{ok}/{total} to'g'ri</p></div>",unsafe_allow_html=True)
            xpe=ok*25+(50 if ball>=80 else 0)
            u=add_xp(u,xpe)
            u.setdefault("test_scores",[]).append({"mavzu":ts["mavzu"],"ball":ball,"togri":ok,"jami":total,"sana":datetime.datetime.now().isoformat()})
            u=chk_bdg(u); st.session_state["user"]=u; st.success(f"🎉 +{xpe} XP!")
            for i,(q,a) in enumerate(zip(qs,ans)):
                ok2=a.get("ok",False)
                st.markdown(f"<div class='gc' style='border-color:{'#00ff9f' if ok2 else '#ff4444'};'><b>{'✅' if ok2 else '❌'} {i+1}. {q.get('savol','')}</b><br><span style='color:#00cfff;'>Sizning: {a.get('javob','')}</span><br><span style='color:#00ff9f;'>To'g'ri: {q.get('togri_javob','')}</span><br><small style='color:#8892b0;'>{q.get('izoh','')}</small></div>",unsafe_allow_html=True)
            ca,cb=st.columns(2)
            with ca:
                if st.button("🔄 Yangi Test",use_container_width=True): st.session_state["ts"]=None; st.rerun()
            with cb:
                if st.button("📊 Analitika",use_container_width=True): st.session_state.update({"page":"analytics","ts":None}); st.rerun()
        else:
            q=qs[cur]
            st.markdown(f"<div style='font-size:.85rem;color:#8892b0;margin-bottom:4px;'>Savol {cur+1}/{len(qs)}</div><div class='xo'><div class='xi' style='width:{cur/len(qs)*100:.0f}%;'></div></div>",unsafe_allow_html=True)
            st.markdown(f"<div class='gc'><h3>❓ {q.get('savol','')}</h3></div>",unsafe_allow_html=True)
            for v in q.get("variantlar",[]):
                if st.button(v,key=f"v{cur}_{v}",use_container_width=True):
                    ok2=v[0].upper()==q.get("togri_javob","").upper()
                    ans.append({"javob":v,"ok":ok2}); ts["cur"]=cur+1; ts["ans"]=ans
                    st.session_state["ts"]=ts
                    if ok2: st.success("✅ To'g'ri!")
                    else: st.error(f"❌ To'g'ri: {q.get('togri_javob','')}")
                    time.sleep(0.4); st.rerun()

# ── FLASHCARD ─────────────────────────────────────────────────────────────────
def render_flashcard(u):
    st.markdown("## 🃏 Flashcard — Tez Yodlash")
    if not is_prem(u):
        st.warning("⭐ Flashcard faqat Premium foydalanuvchilarga!")
        if st.button("💎 Premium olish"): st.session_state["page"]="premium"; st.rerun()
        return

    t1,t2=st.tabs(["📖 O'rganish","➕ Yangi Yaratish"])
    with t1:
        cards=u.get("flashcards",[])
        if not cards: st.info("Hali karta yo'q. 'Yangi Yaratish' da yarating!")
        else:
            if "fc_i" not in st.session_state: st.session_state["fc_i"]=0
            if "fc_s" not in st.session_state: st.session_state["fc_s"]=False
            idx=st.session_state["fc_i"]%len(cards); card=cards[idx]
            st.markdown(f"<div style='text-align:center;color:#8892b0;font-size:.85rem;margin-bottom:8px;'>{idx+1}/{len(cards)}</div>",unsafe_allow_html=True)
            if not st.session_state["fc_s"]:
                st.markdown(f"<div class='fc'><div><div style='font-size:.8rem;color:#8892b0;margin-bottom:8px;'>❓ SAVOL</div><div style='font-size:1.4rem;font-weight:700;'>{card.get('savol','')}</div></div></div>",unsafe_allow_html=True)
                if st.button("👁️ Javobni ko'rish",use_container_width=True): st.session_state["fc_s"]=True; st.rerun()
            else:
                st.markdown(f"<div class='fc' style='border-color:#00ff9f;'><div><div style='font-size:.8rem;color:#00ff9f;margin-bottom:8px;'>✅ JAVOB</div><div style='font-size:1.2rem;'>{card.get('javob','')}</div></div></div>",unsafe_allow_html=True)
                ca,cb,cc=st.columns(3)
                with ca:
                    if st.button("😓 Qiyin",use_container_width=True): st.session_state["fc_s"]=False; st.rerun()
                with cb:
                    if st.button("🤔 O'rtacha",use_container_width=True):
                        st.session_state.update({"fc_i":(idx+1)%len(cards),"fc_s":False}); st.rerun()
                with cc:
                    if st.button("✅ Bildim!",use_container_width=True):
                        u=add_xp(u,3); st.session_state.update({"user":u,"fc_i":(idx+1)%len(cards),"fc_s":False}); st.rerun()

    with t2:
        st.markdown("<div class='gc'>",unsafe_allow_html=True)
        mavzu=st.text_input("Mavzu","",placeholder="Ingliz tili so'zlari, Python terminlari...")
        soni=st.slider("Nechta karta",5,30,10)
        if st.button("🤖 AI bilan Yaratish",use_container_width=True):
            if mavzu.strip():
                with st.spinner("Yaratilmoqda..."): fcs=gen_flash(u,mavzu,soni)
                if fcs:
                    u.setdefault("flashcards",[]).extend(fcs); save_user(u)
                    u=add_xp(u,20); st.session_state["user"]=u
                    st.success(f"✅ {len(fcs)} ta karta! +20 XP"); st.rerun()
                else: st.error("Xato. Mavzuni o'zgartiring.")
            else: st.warning("Mavzu kiriting!")
        st.markdown("</div>",unsafe_allow_html=True)
        if u.get("flashcards"):
            st.markdown(f"**Jami:** {len(u['flashcards'])} ta karta")
            if st.button("🗑️ Barcha kartalarni o'chirish"):
                u["flashcards"]=[]; save_user(u); st.session_state["user"]=u; st.rerun()

# ── TOURNAMENT ────────────────────────────────────────────────────────────────
def render_tournament(u):
    st.markdown("## 🏆 Turnir & Reyting")
    t1,t2=st.tabs(["🏅 Reyting","⚔️ Haftalik Turnir"])

    with t1:
        aus=all_users()
        rnk=sorted(aus,key=lambda x:x.get("xp",0),reverse=True)
        for i,x in enumerate(rnk[:20]):
            is_me=x["id"]==u["id"]
            re2="🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else f"{i+1}."
            lv2,ln2,_,_=get_lv(x.get("xp",0))
            bg="rgba(0,207,255,.08)" if is_me else "transparent"
            bd="rgba(0,207,255,.4)" if is_me else "rgba(255,255,255,.05)"
            pe=PLANS.get(x.get("premium","free"),{}).get("emoji","")
            st.markdown(f"""<div style='background:{bg};border:1px solid {bd};border-radius:10px;
                padding:10px 16px;margin:4px 0;display:flex;align-items:center;justify-content:space-between;'>
                <div style='display:flex;align-items:center;gap:12px;'>
                    <span style='font-size:1.2rem;width:36px;'>{re2}</span>
                    <div><div style='font-weight:{"700" if is_me else "400"};'>{x.get('name','?')} {pe} {"← Sen" if is_me else ""}</div>
                    <div style='font-size:.75rem;color:#8892b0;'>Lv.{lv2} {ln2}</div></div>
                </div>
                <div style='text-align:right;'>
                    <div style='color:#00cfff;font-weight:700;'>{x.get('xp',0)} XP</div>
                    <div style='font-size:.75rem;color:#8892b0;'>{len(x.get('test_scores',[]))} test</div>
                </div></div>""",unsafe_allow_html=True)

    with t2:
        if not is_prem(u):
            st.warning("⭐ Turnir uchun Premium kerak!")
            if st.button("💎 Premium olish"): st.session_state["page"]="premium"; st.rerun()
            return
        st.markdown("<div class='gc'>",unsafe_allow_html=True)
        st.markdown("### ⚔️ Haftalik Matematika Turniri")
        we=datetime.datetime.now()+datetime.timedelta(days=(6-datetime.datetime.now().weekday()))
        st.markdown(f"<p style='color:#8892b0;'>Tugash: {we.strftime('%d.%m.%Y')}</p>",unsafe_allow_html=True)
        st.markdown("**Sovrin:** 🏆 500 XP + Turnir g'olibi badge!")

        if "trn_s" not in st.session_state:
            if st.button("⚔️ Turnirga Qatnashish!",use_container_width=True):
                with st.spinner("Test yaratilmoqda..."):
                    qs=gen_test(u,"Matematika yuqori daraja, juda qiyin",10)
                st.session_state.update({"trn_s":True,"trn_qs":qs,"trn_ans":[],"trn_cur":0}); st.rerun()
        else:
            qs=st.session_state.get("trn_qs",[]); cur=st.session_state.get("trn_cur",0)
            ans=st.session_state.get("trn_ans",[])
            if cur>=len(qs):
                ok=sum(1 for a in ans if a); ball=round(ok/max(len(qs),1)*100)
                st.success(f"🏆 Turnir: {ball}% ({ok}/{len(qs)})")
                if ball>=70:
                    u=add_xp(u,500)
                    if "turnir" not in u.get("badges",[]): u.setdefault("badges",[]).append("turnir")
                    save_user(u); st.session_state["user"]=u; st.balloons()
                    st.success("🥇 +500 XP va Turnir g'olibi badge!")
                if st.button("🔄 Qayta"):
                    for k in ["trn_s","trn_qs","trn_ans","trn_cur"]: st.session_state.pop(k,None)
                    st.rerun()
            elif qs:
                q=qs[cur]
                st.markdown(f"**Savol {cur+1}/{len(qs)}:** {q.get('savol','')}")
                for v in q.get("variantlar",[]):
                    if st.button(v,key=f"tv{cur}_{v}",use_container_width=True):
                        ok2=v[0].upper()==q.get("togri_javob","").upper()
                        ans.append(ok2); st.session_state.update({"trn_ans":ans,"trn_cur":cur+1}); st.rerun()
        st.markdown("</div>",unsafe_allow_html=True)

# ── LIBRARY ───────────────────────────────────────────────────────────────────
def render_library(u):
    st.markdown("## 📚 Kutubxona")
    t1,t2,t3=st.tabs(["💬 Suhbat Tarixi","📝 Konspekt","🎓 Sertifikatlar"])
    with t1:
        hist=load_hist(u["id"])
        srch=st.text_input("🔍","",placeholder="Qidirish...",label_visibility="collapsed")
        filt=[m for m in hist if srch.lower() in m.get("content","").lower()] if srch else hist
        st.markdown(f"*{len(filt)} ta xabar*")
        for m in reversed(filt[-50:]):
            role=m.get("role","user"); c="#00cfff" if role=="user" else "#7b5ea7"
            ts=m.get("ts","")[:16].replace("T"," "); txt=m.get("content","")[:200]
            st.markdown(f"<div class='gc' style='padding:10px;border-color:{c}40;'><span style='color:{c};font-size:.8rem;'>{'👤' if role=='user' else '🤖'} {ts}</span><br><span style='font-size:.9rem;'>{txt}{'...' if len(m.get('content',''))>200 else ''}</span></div>",unsafe_allow_html=True)
    with t2:
        hist=load_hist(u["id"]); n=st.slider("Oxirgi xabarlar",5,50,20)
        if st.button("📝 Konspekt Yaratish",use_container_width=True):
            if hist:
                with st.spinner("Yaratilmoqda..."): k=gen_konspekt(u,hist[-n:])
                st.markdown(f"<div class='gc'>{k}</div>",unsafe_allow_html=True)
                u=add_xp(u,15); st.session_state["user"]=u
                st.download_button("⬇️ Yuklab olish",k.encode(),(f"konspekt_{datetime.date.today()}.md"),"text/markdown")
            else: st.warning("Avval suhbat qiling!")
    with t3:
        scs=[s for s in u.get("test_scores",[]) if s.get("ball",0)>=70]
        if scs:
            for s in scs[-5:]:
                st.markdown(f"""<div style='background:linear-gradient(135deg,#0a0a2e,#1a0a3e);
                    border:2px solid #00cfff;border-radius:16px;padding:32px;text-align:center;margin-bottom:16px;'>
                    <div style='font-size:3rem;'>🎓</div>
                    <h2 style='background:linear-gradient(135deg,#00cfff,#7b5ea7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;'>SERTIFIKAT</h2>
                    <h3 style='color:#fff;'>{u.get('name','')}</h3>
                    <h3 style='color:#00cfff;'>{s.get('mavzu','')}</h3>
                    <p style='color:#8892b0;'>{s['ball']}% natija — {s.get('sana','')[:10]}</p>
                    <p style='color:#8892b0;font-size:.8rem;'>EduAI UZ</p>
                </div>""",unsafe_allow_html=True)
        else: st.info("70%+ ball to'plab sertifikat oling!")

# ── PREMIUM ───────────────────────────────────────────────────────────────────
def render_premium(u):
    st.markdown("## 💎 Premium Obuna")
    cur=get_plan(u)
    plans_data=[
        ("free","🆓","Bepul",0,["✅ Kuniga 20 savol","✅ Asosiy chat","✅ Oyiga 5 test","❌ Flashcard","❌ Turnir","❌ Cheksiz"]),
        ("student","⭐","Student",29900,["✅ Cheksiz savol","✅ Cheksiz test","✅ Flashcard","✅ Turnirlar","✅ Sertifikat","✅ Barcha badge"]),
        ("pro","🏆","Pro",59900,["✅ Student barchasi","✅ Do'stlar tizimi","✅ Virtual sinf","✅ Ota-ona panel","✅ Maxsus sertifikat","✅ Reyting g'olibi"]),
        ("teacher","👨‍🏫","O'qituvchi",99900,["✅ Pro barchasi","✅ Sinf boshqarish","✅ O'z testlari","✅ O'quvchi monitoringi","✅ Admin panel","✅ Cheksiz hamma narsa"]),
    ]
    cols=st.columns(4)
    for col,(pid,em,nom,narx,feats) in zip(cols,plans_data):
        with col:
            is_cur=cur==pid; bd="#00cfff" if is_cur else "rgba(255,255,255,.1)"
            bg="rgba(0,207,255,.05)" if is_cur else "rgba(255,255,255,.02)"
            st.markdown(f"""<div style='background:{bg};border:2px solid {bd};border-radius:16px;
                padding:20px;text-align:center;min-height:380px;'>
                <div style='font-size:2.5rem;'>{em}</div>
                <h3 style='color:#fff;margin:8px 0 4px;'>{nom}</h3>
                <div style='font-size:1.5rem;font-weight:700;color:#00cfff;margin:12px 0;'>
                    {"Bepul" if narx==0 else f"{narx:,} so'm/oy"}</div>
                <div style='text-align:left;font-size:.82rem;color:#8892b0;margin:12px 0;'>{"<br>".join(feats)}</div>
                {"<div style='color:#00ff9f;font-weight:700;margin-top:8px;'>✅ Joriy</div>" if is_cur else ""}
            </div>""",unsafe_allow_html=True)
            if not is_cur and pid!="free":
                if st.button(f"Sotib olish",key=f"bp_{pid}",use_container_width=True):
                    st.session_state["sel_plan"]=pid

    sel=st.session_state.get("sel_plan")
    if sel and sel!="free":
        pi=PLANS.get(sel,{})
        st.markdown("---")
        msg=f"Assalomu alaykum! EduAI UZ da {pi.get('nom','')} ({pi.get('narx',0):,} so'm/oy) olmoqchiman. Email: {u.get('email','')}"
        st.markdown(f"""<div class='gc' style='text-align:center;'>
            <h3>💬 Telegram orqali sotib olish</h3>
            <p style='color:#8892b0;'>{pi.get('emoji','')} <b>{pi.get('nom','')}</b> — <b style='color:#00cfff;'>{pi.get('narx',0):,} so'm/oy</b></p>
            <p style='color:#8892b0;'>1️⃣ Telegram'ga o'ting → 2️⃣ Gaplashing → 3️⃣ To'lang → 4️⃣ Premium yoqiladi</p>
            <a href='https://t.me/{TELEGRAM_USER}?text={msg}' target='_blank'
               style='display:inline-block;background:#2AABEE;color:#fff;padding:14px 32px;
               border-radius:12px;text-decoration:none;font-weight:700;font-size:1rem;margin:12px 0;'>
               📱 @{TELEGRAM_USER} ga yozing
            </a>
            <p style='color:#8892b0;font-size:.8rem;'>📧 Emailingiz: <b style='color:#00cfff;'>{u.get('email','Google bilan kiring')}</b></p>
        </div>""",unsafe_allow_html=True)

# ── SETTINGS ──────────────────────────────────────────────────────────────────
def render_settings(u):
    st.markdown("## ⚙️ Sozlamalar")
    c1,c2=st.columns(2)
    with c1:
        st.markdown("<div class='gc'>",unsafe_allow_html=True)
        st.markdown("### 👤 Profil")
        nn=st.text_input("Ism",u.get("name",""))
        styles=["o'qituvchi","do'st","mentor","akademik","qiziqarli"]
        ns=st.selectbox("AI uslubi",styles,index=styles.index(u.get("settings",{}).get("ai_style","o'qituvchi")))
        if st.button("💾 Saqlash"):
            u["name"]=nn; u.setdefault("settings",{})["ai_style"]=ns
            save_user(u); st.session_state["user"]=u; st.success("✅ Saqlandi!")
        st.markdown("</div>",unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='gc'>",unsafe_allow_html=True)
        st.markdown("### 📊 Statistika")
        lv,ln,_,_=get_lv(u.get("xp",0))
        st.metric("Daraja",f"Lv.{lv} — {ln}"); st.metric("Jami XP",u.get("xp",0))
        st.metric("Streak",f"{u.get('streak',0)} kun 🔥"); st.metric("Xabarlar",u.get("total_messages",0))
        st.metric("Obuna",PLANS.get(get_plan(u),{}).get("nom",""))
        st.markdown("</div>",unsafe_allow_html=True)

    st.markdown("<div class='gc'>",unsafe_allow_html=True)
    st.markdown("### ⚠️ Xavfli Zona")
    ca,cb,cc=st.columns(3)
    with ca:
        if st.button("🗑️ Tarixni tozalash"):
            save_hist(u["id"],[]); st.session_state["hist"]=[]
            st.success("✅ Tozalandi!")
    with cb:
        h=load_hist(u["id"])
        st.download_button("⬇️ Tarixni yuklab olish",json.dumps(h,ensure_ascii=False,indent=2).encode(),f"history_{u['id']}.json","application/json")
    with cc:
        st.download_button("⬇️ Profilni yuklab olish",json.dumps(u,ensure_ascii=False,indent=2).encode(),f"profile_{u['id']}.json","application/json")
    st.markdown("</div>",unsafe_allow_html=True)


# ── KITOBLAR ──────────────────────────────────────────────────────────────────
BOOK_CATEGORIES = {
    "📐 Matematika": ["Algebra","Geometriya","Trigonometriya","Analitik geometriya","Oliy matematika"],
    "🔬 Fizika":     ["Mexanika","Elektr","Optika","Atom fizikasi","Termodinamika"],
    "🧪 Kimyo":      ["Umumiy kimyo","Organik kimyo","Anorganik kimyo","Analitik kimyo"],
    "🧬 Biologiya":  ["Zoologiya","Botanika","Anatomiya","Genetika","Ekologiya"],
    "💻 Informatika":["Python","JavaScript","Algoritmlar","Ma'lumotlar bazasi","Tarmoqlar"],
    "🌍 Tarix":      ["O'zbekiston tarixi","Jahon tarixi","Arxeologiya"],
    "📖 Adabiyot":   ["O'zbek adabiyoti","Jahon adabiyoti","She'riyat"],
    "🌐 Ingliz tili":["Grammar","Vocabulary","IELTS","Speaking","Writing"],
    "📚 Badiiy":     ["Roman","Hikoya","Qissa","Detektiv","Fantastika"],
}

def load_books():
    fp = Path("data/books/list.json")
    if fp.exists():
        try:
            with open(fp, encoding="utf-8") as f: return json.load(f)
        except: pass
    return []

def save_books(books):
    Path("data/books").mkdir(parents=True, exist_ok=True)
    with open("data/books/list.json", "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=2)

def render_books(u):
    st.markdown("## 📚 Kitoblar Kutubxonasi")

    books = load_books()

    # Kategoriya filtri
    cats = ["Hammasi"] + list(BOOK_CATEGORIES.keys())
    sel_cat = st.selectbox("Kategoriya", cats, label_visibility="collapsed")

    # Qidirish
    c1, c2 = st.columns([3, 1])
    with c1:
        search = st.text_input("", "", placeholder="🔍 Kitob nomi yoki muallif...", label_visibility="collapsed")
    with c2:
        sort_by = st.selectbox("", ["Yangi", "Mashhur", "A-Z"], label_visibility="collapsed")

    # Filterlash
    filtered = books
    if sel_cat != "Hammasi":
        filtered = [b for b in filtered if b.get("kategoriya") == sel_cat]
    if search:
        filtered = [b for b in filtered
                    if search.lower() in b.get("nom","").lower()
                    or search.lower() in b.get("muallif","").lower()
                    or search.lower() in b.get("tavsif","").lower()]
    if sort_by == "A-Z":
        filtered = sorted(filtered, key=lambda x: x.get("nom",""))
    elif sort_by == "Mashhur":
        filtered = sorted(filtered, key=lambda x: x.get("views",0), reverse=True)
    else:
        filtered = sorted(filtered, key=lambda x: x.get("qoshildi",""), reverse=True)

    if not filtered:
        st.markdown("""<div class='gc' style='text-align:center;'>
            <div style='font-size:3rem;'>📚</div>
            <h3 style='color:#8892b0;'>Hali kitob qo'shilmagan</h3>
            <p style='color:#445;'>Admin yangi kitoblar qo'shishi kutilmoqda</p>
        </div>""", unsafe_allow_html=True)
        return

    st.markdown(f"<p style='color:#8892b0;font-size:.85rem;'>{len(filtered)} ta kitob topildi</p>",
                unsafe_allow_html=True)

    # Kitoblar grid
    cols = st.columns(3)
    for i, book in enumerate(filtered):
        with cols[i % 3]:
            cover = book.get("rasm", "")
            cat   = book.get("kategoriya", "")
            st.markdown(f"""<div class='gc' style='padding:0;overflow:hidden;cursor:pointer;'>
                {"<img src='" + cover + "' style='width:100%;height:180px;object-fit:cover;border-radius:16px 16px 0 0;'/>" if cover else
                 "<div style='width:100%;height:180px;background:linear-gradient(135deg,rgba(0,207,255,.15),rgba(123,94,167,.2));border-radius:16px 16px 0 0;display:flex;align-items:center;justify-content:center;font-size:4rem;'>📖</div>"}
                <div style='padding:14px;'>
                    <div style='font-size:.75rem;color:#00cfff;margin-bottom:4px;'>{cat}</div>
                    <div style='font-weight:700;font-size:.95rem;margin-bottom:4px;'>{book.get("nom","")}</div>
                    <div style='font-size:.8rem;color:#8892b0;margin-bottom:8px;'>✍️ {book.get("muallif","")}</div>
                    <div style='font-size:.8rem;color:#8892b0;margin-bottom:10px;'>{book.get("tavsif","")[:80]}{"..." if len(book.get("tavsif",""))>80 else ""}</div>
                    <div style='display:flex;justify-content:space-between;align-items:center;'>
                        <span style='font-size:.75rem;color:#8892b0;'>👁️ {book.get("views",0)}</span>
                        <span class='bdg'>{book.get("daraja","Boshlang'ich")}</span>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

            # AI bilan muhokama
            if st.button(f"🤖 AI bilan o'rgan", key=f"book_{i}", use_container_width=True):
                st.session_state["book_chat"] = book
                st.session_state["page"] = "chat"
                # Savol sifatida yuborish
                prompt = f"'{book.get('nom','')}' kitobini tushuntir va o'rgatishni boshla. Muallif: {book.get('muallif','')}"
                st.session_state["pend"] = prompt
                # View count oshirish
                all_books = load_books()
                for b in all_books:
                    if b.get("id") == book.get("id"):
                        b["views"] = b.get("views", 0) + 1
                save_books(all_books)
                st.rerun()

    # Premium bo'lmasa cheklash
    if not is_prem(u) and len(filtered) > 6:
        st.markdown("""<div class='gc' style='text-align:center;margin-top:8px;'>
            <p style='color:#8892b0;'>💎 Premium bilan barcha kitoblarga kirish!</p>
        </div>""", unsafe_allow_html=True)
        if st.button("💎 Premium olish", use_container_width=True):
            st.session_state["page"] = "premium"
            st.rerun()

# ── ADMIN ─────────────────────────────────────────────────────────────────────

def render_admin_books():
    """Admin uchun kitob boshqaruv paneli."""
    st.markdown("### 📖 Kitoblar Boshqaruvi")
    books = load_books()
    cats  = list(BOOK_CATEGORIES.keys())

    st.markdown("<div class='gc'>", unsafe_allow_html=True)
    st.markdown("#### ➕ Yangi Kitob Qo'shish")
    c1, c2 = st.columns(2)
    with c1:
        b_nom     = st.text_input("Kitob nomi", "", key="b_nom")
        b_muallif = st.text_input("Muallif", "", key="b_muallif")
        b_cat     = st.selectbox("Kategoriya", cats, key="b_cat")
        b_daraja  = st.selectbox("Daraja", ["Boshlang'ich","O'rta","Yuqori","Universitet"], key="b_daraja")
    with c2:
        b_rasm   = st.text_input("Rasm URL (ixtiyoriy)", "", key="b_rasm",
                                  placeholder="https://... yoki bo'sh qoldiring")
        b_yil    = st.text_input("Nashr yili", "", key="b_yil", placeholder="2024")
        b_sahifa = st.text_input("Sahifalar soni", "", key="b_sahifa", placeholder="320")
        b_til    = st.selectbox("Til", ["O'zbek","Rus","Ingliz"], key="b_til")
    b_tavsif = st.text_area("Tavsif", "", key="b_tavsif", height=100,
                             placeholder="Kitob haqida qisqacha ma'lumot...")
    b_link   = st.text_input("Yuklab olish linki (ixtiyoriy)", "", key="b_link")

    if st.button("✅ Kitob Qo'shish", use_container_width=True, key="add_book_btn"):
        if b_nom.strip() and b_muallif.strip():
            new_book = {
                "id":       len(books) + 1,
                "nom":      b_nom.strip(),
                "muallif":  b_muallif.strip(),
                "kategoriya": b_cat,
                "daraja":   b_daraja,
                "tavsif":   b_tavsif.strip(),
                "rasm":     b_rasm.strip(),
                "yil":      b_yil.strip(),
                "sahifa":   b_sahifa.strip(),
                "til":      b_til,
                "link":     b_link.strip(),
                "views":    0,
                "qoshildi": datetime.datetime.now().isoformat(),
            }
            books.append(new_book)
            save_books(books)
            st.success(f"✅ '{b_nom}' kitob qo'shildi!")
            st.rerun()
        else:
            st.warning("Kitob nomi va muallif kiriting!")
    st.markdown("</div>", unsafe_allow_html=True)

    # Kitoblar ro'yxati
    st.markdown(f"#### 📋 Barcha Kitoblar ({len(books)} ta)")
    if not books:
        st.info("Hali kitob qo'shilmagan.")
    else:
        for b in sorted(books, key=lambda x: x.get("qoshildi",""), reverse=True):
            ca, cb = st.columns([5, 1])
            with ca:
                st.markdown(f"""<div style='background:rgba(0,207,255,.05);border:1px solid rgba(0,207,255,.15);
                    border-radius:10px;padding:12px;margin-bottom:6px;'>
                    <div style='display:flex;gap:12px;align-items:start;'>
                        {"<img src='" + b["rasm"] + "' style='width:50px;height:60px;object-fit:cover;border-radius:6px;'/>" if b.get("rasm") else "<div style='width:50px;height:60px;background:rgba(123,94,167,.3);border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:1.5rem;'>📖</div>"}
                        <div>
                            <b style='color:#fff;'>{b.get("nom","")}</b>
                            <span class='bdg' style='font-size:.7rem;margin-left:6px;'>{b.get("kategoriya","")}</span><br>
                            <small style='color:#8892b0;'>✍️ {b.get("muallif","")} | {b.get("yil","")} | {b.get("sahifa","")} bet | {b.get("til","")}</small><br>
                            <small style='color:#8892b0;'>👁️ {b.get("views",0)} ko'rildi | {b.get("daraja","")}</small>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)
            with cb:
                if st.button("🗑️", key=f"del_book_{b['id']}"):
                    books = [x for x in books if x["id"] != b["id"]]
                    save_books(books)
                    st.success("O'chirildi!")
                    st.rerun()

def render_admin(u):
    if not is_admin(u): st.error("❌ Ruxsat yo'q!"); return
    st.markdown("## 🛡️ Admin Panel")
    aus=all_users()
    c1,c2,c3,c4=st.columns(4)
    prems=[x for x in aus if is_prem(x)]
    txp=sum(x.get("xp",0) for x in aus)
    with c1: st.metric("👥 Foydalanuvchilar",len(aus))
    with c2: st.metric("💎 Premium",len(prems))
    with c3: st.metric("⚡ Jami XP",f"{txp:,}")
    with c4: st.metric("📊 O'rtacha XP",f"{txp//max(len(aus),1):,}")

    t1,t2,t3,t4,t5=st.tabs(["👥 Foydalanuvchilar","💎 Premium","📢 E'lonlar","📖 Kitoblar","📊 Statistika"])
    with t1:
        srch=st.text_input("Qidirish","",placeholder="Ism yoki email...",label_visibility="collapsed")
        filt=[x for x in aus if srch.lower() in x.get("name","").lower() or srch.lower() in x.get("email","").lower()] if srch else aus
        for x in sorted(filt,key=lambda z:z.get("xp",0),reverse=True)[:50]:
            plan=x.get("premium","free"); lv2,ln2,_,_=get_lv(x.get("xp",0))
            st.markdown(f"""<div style='background:rgba(255,50,50,.05);border:1px solid rgba(255,50,50,.2);
                border-radius:12px;padding:10px 16px;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center;'>
                <div><b>{x.get('name','?')}</b> {'🛡️' if x.get('email','') in ADMIN_EMAILS else ''}
                <span class='bdg p{plan}'>{PLANS.get(plan,{}).get('emoji','')} {plan}</span><br>
                <small style='color:#8892b0;'>{x.get('email','')} | Lv.{lv2} | {x.get('xp',0)} XP | 🔥{x.get('streak',0)}</small></div>
                <div style='color:#00cfff;font-size:.85rem;'>{x.get('created','')[:10]}</div>
            </div>""",unsafe_allow_html=True)

    with t2:
        st.markdown("### 💎 Premium Boshqarish")
        emails=[x.get("email","") for x in aus if x.get("email")]
        te=st.selectbox("Foydalanuvchi",[""] + emails)
        np2=st.selectbox("Yangi Plan",list(PLANS.keys()))
        exp=st.date_input("Tugash sanasi",datetime.date.today()+datetime.timedelta(days=30))
        ca,cb=st.columns(2)
        with ca:
            if st.button("✅ Premium Yoqish",use_container_width=True):
                if te:
                    for x in aus:
                        if x.get("email")==te:
                            x["premium"]=np2; x["premium_exp"]=exp.isoformat(); save_user(x)
                            if np2!="free" and "premium" not in x.get("badges",[]): x.setdefault("badges",[]).append("premium"); save_user(x)
                            st.success(f"✅ {te} ga {np2} yoqildi!")
                else: st.warning("Foydalanuvchi tanlang!")
        with cb:
            if st.button("❌ Premium O'chirish",use_container_width=True):
                if te:
                    for x in aus:
                        if x.get("email")==te: x["premium"]="free"; x["premium_exp"]=""; save_user(x); st.success("✅ O'chirildi!")
        st.markdown("### Joriy Premium Foydalanuvchilar")
        for x in aus:
            if is_prem(x):
                st.markdown(f"<div style='background:rgba(0,207,255,.05);border:1px solid rgba(0,207,255,.2);border-radius:10px;padding:10px;margin-bottom:6px;'><b>{x.get('name','')}</b> <span class='bdg p{x.get('premium','')}'>{x.get('premium','')}</span><br><small style='color:#8892b0;'>{x.get('email','')} — {x.get('premium_exp','')}</small></div>",unsafe_allow_html=True)

    with t3:
        anns=load_ann()
        st.markdown("<div class='gc'>",unsafe_allow_html=True)
        at=st.text_input("Sarlavha",""); atx=st.text_area("Matn","",height=80)
        ap=st.checkbox("Kirish sahifasida ko'rinsin",value=True)
        if st.button("📢 E'lon Yuborish",use_container_width=True):
            if at.strip() and atx.strip():
                anns.append({"id":len(anns)+1,"title":at,"text":atx,"public":ap,
                             "date":datetime.datetime.now().isoformat(),"author":u.get("name","Admin")})
                save_ann(anns); st.success("✅ Yuborildi!")
            else: st.warning("Sarlavha va matn kiriting!")
        st.markdown("</div>",unsafe_allow_html=True)
        for a in reversed(anns):
            ca,cb=st.columns([5,1])
            with ca: st.markdown(f"<div class='ann'><b>{a['title']}</b><br>{a['text']}<br><small style='color:#8892b0;'>{a.get('date','')[:16]}</small></div>",unsafe_allow_html=True)
            with cb:
                if st.button("🗑️",key=f"da{a['id']}"):
                    anns=[x for x in anns if x["id"]!=a["id"]]; save_ann(anns); st.rerun()

    with t4:
        render_admin_books()
    with t5:
        st.markdown("### 📊 Platform Statistikasi")
        dates=[(datetime.date.today()-datetime.timedelta(days=i)).isoformat() for i in range(29,-1,-1)]
        counts=[random.randint(1,max(len(aus)//2,1)) for _ in dates]
        fig=go.Figure(go.Bar(x=dates,y=counts,marker_color='#00cfff',opacity=0.8))
        fig.update_layout(title="Kunlik Faol Foydalanuvchilar",paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',font=dict(color='#e8eaf6'),height=280,
            xaxis=dict(gridcolor='rgba(255,255,255,.05)'),yaxis=dict(gridcolor='rgba(255,255,255,.05)'),
            margin=dict(l=20,r=20,t=40,b=40))
        st.plotly_chart(fig,use_container_width=True)

        pc={};
        for x in aus: p=x.get("premium","free"); pc[p]=pc.get(p,0)+1
        if pc:
            fig2=go.Figure(go.Pie(labels=[PLANS.get(k,{}).get("nom",k) for k in pc],
                values=list(pc.values()),hole=0.4,marker_colors=["#444","#f59e0b","#7b5ea7","#059669"]))
            fig2.update_layout(title="Obuna Taqsimoti",paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e8eaf6'),height=280,margin=dict(l=20,r=20,t=40,b=20))
            st.plotly_chart(fig2,use_container_width=True)

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    css()

    # ── Google OAuth callback qayta ishlash ──
    code = st.query_params.get("code", "")
    
    if code and "user" not in st.session_state:
        # Spinner ko'rsatish
        ph = st.empty()
        ph.markdown("""<div style='text-align:center;padding:80px 20px;'>
            <div style='font-size:3rem;margin-bottom:16px;'>⏳</div>
            <h3 style='color:#00cfff;'>Google orqali kirilmoqda...</h3>
            <p style='color:#8892b0;'>Iltimos kuting</p>
        </div>""", unsafe_allow_html=True)
        
        u = g_callback()
        ph.empty()  # Spinnerni o'chirish
        
        if u:
            # Muvaffaqiyatli — session'ga saqlash
            u = upd_streak(u)
            u = chk_bdg(u)
            st.session_state["user"]  = u
            st.session_state["hist"]  = load_hist(u["id"])
            st.session_state["page"]  = "chat"
            # URL dan code parametrini olib tashlash
            st.query_params.clear()
            st.rerun()
        else:
            # Xato — login sahifasiga qaytish
            st.query_params.clear()
            st.session_state["auth_error"] = True
            st.rerun()
        return

    # Auth xato xabari
    if st.session_state.pop("auth_error", False):
        msg = st.session_state.pop("auth_msg", "Noma'lum xato")
        st.error(f"❌ Google kirish xatosi: {msg}")
        with st.expander("🔧 Xato tafsilotlari"):
            st.code(f"""
Tekshiring:
1. .env faylida GOOGLE_CLIENT_SECRET to'liq yozilganmi?
2. Google Console da Redirect URI: http://localhost:8501 bormi?
3. Xato: {msg}
""")

    # ── Foydalanuvchi tekshirish ──
    if "user" not in st.session_state or not st.session_state["user"]:
        render_login()
        return

    # ── Asosiy ilova ──
    u = st.session_state["user"]
    if "hist" not in st.session_state:
        st.session_state["hist"] = load_hist(u["id"])
    
    render_sidebar(u)

    pg = st.session_state.get("page", "chat")
    {
        "chat":       render_chat,
        "analytics":  render_analytics,
        "tests":      render_tests,
        "flashcard":  render_flashcard,
        "tournament": render_tournament,
        "library":    render_library,
        "books":      render_books,
        "premium":    render_premium,
        "settings":   render_settings,
        "admin":      render_admin,
    }.get(pg, render_chat)(u)

if __name__=="__main__":
    main()