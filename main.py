"""
EduAI UZ v5.0 - Smarter Learning, Better Future
Barcha muammolar hal qilindi:
  - Logo PNG (logo.png) ko'rsatish, yo'q bo'lsa SVG (bulutchasiz)
  - Demo va Google kirish yo'q - faqat Email/Parol
  - Session token: bir marta kirgandan keyin qayta so'ralmaydi
  - Chat sidebar: Claude uslubida (New Chat, Search, Recents)
  - Fanlar tezkor tugmalari olib tashlandi
  - 3 til: O'zbek / English / Русский
  - Mobil: bottom navigation
  - AI: super maximal system prompt
"""

import streamlit as st
import os, json, time, hashlib, datetime, re, base64, uuid
from pathlib import Path
from dotenv import load_dotenv
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import requests
import google.generativeai as genai
import gspread
from google.oauth2.service_account import Credentials

load_dotenv()

# ── CONFIG ────────────────────────────────────────────────────────────────────
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
ADMIN_EMAILS  = ["muhammadaliortiqov54@gmail.com"]
TELEGRAM_USER = "Ortiqov_ali"

PLANS = {
    "free":    {"nom":"Bepul",          "name":"Free",    "имя":"Бесплатно", "narx":0,     "emoji":"🆓"},
    "student": {"nom":"Student Premium","name":"Student", "имя":"Студент",   "narx":29900, "emoji":"⭐"},
    "pro":     {"nom":"Pro Premium",    "name":"Pro",     "имя":"Про",       "narx":59900, "emoji":"🏆"},
    "teacher": {"nom":"O'qituvchi",     "name":"Teacher", "имя":"Учитель",   "narx":99900, "emoji":"👨‍🏫"},
}
FREE_Q   = 20
FREE_T   = 5

# ── PAPKALAR ──────────────────────────────────────────────────────────────────
for _d in ["data/users","data/history","data/announce","data/books","data/sessions"]:
    Path(_d).mkdir(parents=True, exist_ok=True)

# ── TIL ───────────────────────────────────────────────────────────────────────
TR = {
    "login":        {"uz":"Kirish",             "en":"Login",          "ru":"Войти"},
    "register":     {"uz":"Ro'yxatdan o'tish",  "en":"Register",       "ru":"Регистрация"},
    "email":        {"uz":"📧 Email",           "en":"📧 Email",       "ru":"📧 Email"},
    "password":     {"uz":"🔑 Parol",           "en":"🔑 Password",    "ru":"🔑 Пароль"},
    "login_btn":    {"uz":"Kirish ->",           "en":"Login ->",        "ru":"Войти ->"},
    "reg_btn":      {"uz":"Ro'yxatdan o'tish ->","en":"Register ->",     "ru":"Зарегистрироваться ->"},
    "wrong_pass":   {"uz":"❌ Email yoki parol noto'g'ri!","en":"❌ Wrong email or password!","ru":"❌ Неверный email или пароль!"},
    "pass_short":   {"uz":"⚠️ Parol kamida 6 belgi!","en":"⚠️ Min 6 characters!","ru":"⚠️ Минимум 6 символов!"},
    "name_empty":   {"uz":"⚠️ Ism kiriting!","en":"⚠️ Enter name!","ru":"⚠️ Введите имя!"},
    "email_exists": {"uz":"❌ Email allaqachon ro'yxatdan o'tgan!","en":"❌ Email already registered!","ru":"❌ Email уже зарегистрирован!"},
    "reg_ok":       {"uz":"✅ Muvaffaqiyatli! 'Kirish' tabiga o'ting.","en":"✅ Success! Go to Login tab.","ru":"✅ Успешно! Перейдите на вход."},
    "name":         {"uz":"👤 Ism","en":"👤 Name","ru":"👤 Имя"},
    "new_chat":     {"uz":"Yangi suhbat","en":"New chat","ru":"Новый чат"},
    "search":       {"uz":"Qidirish...","en":"Search...","ru":"Поиск..."},
    "today":        {"uz":"Bugun","en":"Today","ru":"Сегодня"},
    "yesterday":    {"uz":"Kecha","en":"Yesterday","ru":"Вчера"},
    "older":        {"uz":"Oldingi","en":"Earlier","ru":"Ранее"},
    "chat":         {"uz":"Suhbat","en":"Chat","ru":"Чат"},
    "analytics":    {"uz":"Analitika","en":"Analytics","ru":"Аналитика"},
    "tests":        {"uz":"Testlar","en":"Tests","ru":"Тесты"},
    "flashcard":    {"uz":"Flashcard","en":"Flashcard","ru":"Флэшкарты"},
    "tournament":   {"uz":"Turnir","en":"Tournament","ru":"Турнир"},
    "library":      {"uz":"Kutubxona","en":"Library","ru":"Библиотека"},
    "books":        {"uz":"Kitoblar","en":"Books","ru":"Книги"},
    "premium":      {"uz":"Premium","en":"Premium","ru":"Премиум"},
    "settings":     {"uz":"Sozlamalar","en":"Settings","ru":"Настройки"},
    "admin":        {"uz":"Admin","en":"Admin","ru":"Админ"},
    "logout":       {"uz":"🚪 Chiqish","en":"🚪 Logout","ru":"🚪 Выйти"},
    "welcome":      {"uz":"Assalomu alaykum! Men EduAI UZman. 👋","en":"Hello! I am EduAI UZ. 👋","ru":"Привет! Я EduAI UZ. 👋"},
    "welcome_sub":  {"uz":"Savolingizni yozing - tushuntiraman!","en":"Ask me anything!","ru":"Задайте вопрос!"},
    "ask_me":       {"uz":"Savolingizni yozing...","en":"Ask anything...","ru":"Введите вопрос..."},
    "thinking":     {"uz":"⏳ AI o'ylamoqda...","en":"⏳ AI thinking...","ru":"⏳ AI думает..."},
    "mode_chat":    {"uz":"💬 Oddiy suhbat","en":"💬 Regular chat","ru":"💬 Обычный чат"},
    "mode_code":    {"uz":"👨‍💻 Kod rejimi","en":"👨‍💻 Code mode","ru":"👨‍💻 Режим кода"},
    "mode_book":    {"uz":"📖 Kitob tahlili","en":"📖 Book analysis","ru":"📖 Анализ книги"},
    "clear":        {"uz":"🗑️ Tozalash","en":"🗑️ Clear","ru":"🗑️ Очистить"},
    "get_premium":  {"uz":"💎 Premium olish","en":"💎 Get Premium","ru":"💎 Получить Premium"},
    "daily_limit":  {"uz":"⚠️ Kunlik {n} savol limitiga yetdingiz!","en":"⚠️ Daily limit of {n} reached!","ru":"⚠️ Достигнут дневной лимит {n}!"},
    "streak":       {"uz":"kun streak","en":"day streak","ru":"дней подряд"},
    "level":        {"uz":"Daraja","en":"Level","ru":"Уровень"},
    "save":         {"uz":"💾 Saqlash","en":"💾 Save","ru":"💾 Сохранить"},
    "welcome_title":{"uz":"Xush kelibsiz! 👋","en":"Welcome! 👋","ru":"Добро пожаловать! 👋"},
}

def t(key, **kw):
    lang = st.session_state.get("lang","uz")
    txt  = TR.get(key, {}).get(lang, TR.get(key, {}).get("uz", key))
    for k, v in kw.items():
        txt = txt.replace("{"+k+"}", str(v))
    return txt

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EduAI UZ",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── LOGO ──────────────────────────────────────────────────────────────────────
def get_logo_b64(sz=160) -> str:
    """PNG logo borligini tekshiradi, yo'q bo'lsa SVG ishlatadi."""
    for fn in ["logo.png", "assets/logo.png", "data/logo.png"]:
        p = Path(fn)
        if p.exists():
            with open(p, "rb") as f:
                b = base64.b64encode(f.read()).decode()
            return f'<img src="data:image/png;base64,{b}" width="{sz}" height="{sz}" style="display:block;margin:0 auto;object-fit:contain;border-radius:0;"/>'
    # Fallback SVG - bulutchasiz, asl logoga o'xshash
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="{sz}" height="{sz}">
<defs>
  <linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" style="stop-color:#00d4ff"/><stop offset="50%" style="stop-color:#5a7fff"/>
    <stop offset="100%" style="stop-color:#8b5cf6"/>
  </linearGradient>
  <linearGradient id="g2" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" style="stop-color:#a8c8ff"/><stop offset="100%" style="stop-color:#8b5cf6"/>
  </linearGradient>
  <filter id="glow"><feGaussianBlur stdDeviation="3" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <filter id="glow2"><feGaussianBlur stdDeviation="6" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>

<!-- MIYA (bulutchasiz, yaxlit ellips + bo'linma) -->
<g filter="url(#glow2)" opacity="0.95">
  <!-- Asosiy miya shakli -->
  <ellipse cx="148" cy="170" rx="76" ry="68" fill="none" stroke="url(#g1)" stroke-width="3.5" stroke-linecap="round"/>
  <!-- Yuqori bo'rtmalar -->
  <path d="M100,130 Q88,112 100,100 Q114,89 128,102" fill="none" stroke="url(#g1)" stroke-width="3" stroke-linecap="round"/>
  <path d="M148,100 Q148,86 160,82 Q174,78 180,94" fill="none" stroke="url(#g1)" stroke-width="3" stroke-linecap="round"/>
  <!-- Pastki bo'rtmalar -->
  <path d="M120,216 Q106,230 96,222 Q82,210 90,196" fill="none" stroke="url(#g1)" stroke-width="3" stroke-linecap="round"/>
  <path d="M168,222 Q172,236 160,240 Q146,244 142,228" fill="none" stroke="url(#g1)" stroke-width="3" stroke-linecap="round"/>
  <!-- Miya bo'limlari chiziqlari -->
  <line x1="148" y1="102" x2="148" y2="236" stroke="url(#g1)" stroke-width="2" stroke-dasharray="5,5" opacity="0.4"/>
  <path d="M98,170 Q120,155 148,162 Q176,169 194,155" fill="none" stroke="url(#g1)" stroke-width="1.8" opacity="0.5"/>

  <!-- KITOB (o'ng tomon) -->
  <path d="M234,70 C258,63 296,73 312,94 L318,238 C300,220 262,210 238,214 Z"
    fill="none" stroke="url(#g2)" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
  <line x1="210" y1="84" x2="234" y2="220" stroke="url(#g2)" stroke-width="3" stroke-linecap="round"/>
  <path d="M210,84 C186,77 150,87 138,106 L134,238 C152,222 188,212 208,216 Z"
    fill="none" stroke="url(#g2)" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>
</g>

<!-- AI CHIP -->
<g filter="url(#glow)">
  <rect x="184" y="132" width="74" height="74" rx="12" fill="#06061a" stroke="url(#g1)" stroke-width="3"/>
  <rect x="196" y="144" width="50" height="50" rx="7" fill="#0a0a22" stroke="url(#g1)" stroke-width="1.8" opacity="0.7"/>
  <!-- Pinlar yuqori -->
  <line x1="198" y1="132" x2="198" y2="118" stroke="#00d4ff" stroke-width="2.2" stroke-linecap="round"/>
  <line x1="212" y1="132" x2="212" y2="115" stroke="#00d4ff" stroke-width="2.2" stroke-linecap="round"/>
  <line x1="226" y1="132" x2="226" y2="118" stroke="#00d4ff" stroke-width="2.2" stroke-linecap="round"/>
  <line x1="240" y1="132" x2="240" y2="115" stroke="#8b5cf6" stroke-width="2.2" stroke-linecap="round"/>
  <!-- Pinlar pastki -->
  <line x1="198" y1="206" x2="198" y2="220" stroke="#00d4ff" stroke-width="2.2" stroke-linecap="round"/>
  <line x1="212" y1="206" x2="212" y2="222" stroke="#00d4ff" stroke-width="2.2" stroke-linecap="round"/>
  <line x1="226" y1="206" x2="226" y2="220" stroke="#00d4ff" stroke-width="2.2" stroke-linecap="round"/>
  <!-- Pinlar chap -->
  <line x1="184" y1="148" x2="168" y2="148" stroke="#00d4ff" stroke-width="2.2" stroke-linecap="round"/>
  <line x1="184" y1="162" x2="164" y2="162" stroke="#8b5cf6" stroke-width="2.2" stroke-linecap="round"/>
  <line x1="184" y1="176" x2="168" y2="176" stroke="#00d4ff" stroke-width="2.2" stroke-linecap="round"/>
  <line x1="184" y1="190" x2="164" y2="190" stroke="#8b5cf6" stroke-width="2.2" stroke-linecap="round"/>
  <!-- Pinlar o'ng -->
  <line x1="258" y1="148" x2="274" y2="148" stroke="#00d4ff" stroke-width="2.2" stroke-linecap="round"/>
  <line x1="258" y1="162" x2="276" y2="162" stroke="#8b5cf6" stroke-width="2.2" stroke-linecap="round"/>
  <line x1="258" y1="176" x2="274" y2="176" stroke="#00d4ff" stroke-width="2.2" stroke-linecap="round"/>
  <line x1="258" y1="190" x2="276" y2="190" stroke="#8b5cf6" stroke-width="2.2" stroke-linecap="round"/>
  <!-- AI matn -->
  <text x="221" y="176" text-anchor="middle" dominant-baseline="middle"
    font-family="Arial Black,sans-serif" font-weight="900" font-size="24"
    fill="url(#g1)" filter="url(#glow)">AI</text>
</g>

<!-- Miya-chip ulanish chiziqlari -->
<g stroke="#00d4ff" stroke-width="2" fill="none" opacity="0.9" stroke-linecap="round">
  <line x1="160" y1="132" x2="184" y2="148"/>
  <line x1="138" y1="152" x2="164" y2="162"/>
  <line x1="142" y1="176" x2="168" y2="176"/>
  <line x1="146" y1="200" x2="164" y2="190"/>
  <circle cx="156" cy="130" r="4.5" fill="#06061a" stroke-width="2.2"/>
  <circle cx="134" cy="150" r="4.5" fill="#06061a" stroke-width="2.2"/>
  <circle cx="136" cy="174" r="4.5" stroke="#8b5cf6" fill="#06061a" stroke-width="2.2"/>
  <circle cx="140" cy="202" r="4.5" stroke="#8b5cf6" fill="#06061a" stroke-width="2.2"/>
</g>

<!-- MATN -->
<text x="100" y="296" font-family="Arial Black,sans-serif" font-weight="900" font-size="66" fill="white" letter-spacing="-2">Edu</text>
<text x="238" y="296" font-family="Arial Black,sans-serif" font-weight="900" font-size="66" fill="url(#g1)" letter-spacing="-2">AI</text>
<!-- UZ -->
<line x1="116" y1="314" x2="156" y2="314" stroke="url(#g1)" stroke-width="1.8"/>
<text x="200" y="320" text-anchor="middle" font-family="Arial,sans-serif" font-weight="700"
  font-size="15" fill="#00d4ff" letter-spacing="6">UZ</text>
<line x1="244" y1="314" x2="284" y2="314" stroke="url(#g1)" stroke-width="1.8"/>
<!-- Tagline -->
<text x="200" y="344" text-anchor="middle" font-family="Arial,sans-serif"
  font-size="10" fill="#6b7fa3" letter-spacing="2.8">SMARTER LEARNING, BETTER FUTURE</text>
</svg>"""
    b = base64.b64encode(svg.encode()).decode()
    return f'<img src="data:image/svg+xml;base64,{b}" width="{sz}" height="{sz}" style="display:block;margin:0 auto;"/>'

# ── CSS ───────────────────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""<style>
/* ─ Reset ─ */
*{box-sizing:border-box;margin:0;padding:0;}
:root{
  --c1:#00d4ff; --c2:#8b5cf6; --c3:#00ff9f;
  --bg:#0a0a10; --bg2:#111118; --bg3:#181824;
  --txt:#e8eaf6; --muted:#8892b0;
  --glass:rgba(255,255,255,.04);
  --bd:rgba(0,212,255,.15);
  --r:14px;
}
.stApp{background:var(--bg)!important;color:var(--txt)!important;font-family:'Segoe UI',system-ui,sans-serif!important;}
.stApp::before{content:'';position:fixed;inset:0;
  background:radial-gradient(ellipse 80% 50% at 10% 5%,rgba(0,100,200,.18) 0,transparent 55%),
             radial-gradient(ellipse 60% 40% at 90% 90%,rgba(139,92,246,.15) 0,transparent 55%);
  pointer-events:none;z-index:0;}

/* ─ Hide Streamlit chrome ─ */
#MainMenu,footer,[data-testid="collapsedControl"],
section[data-testid="stSidebar"]{display:none!important;}
.stMainBlockContainer,.block-container{padding:0!important;max-width:100%!important;}
div[data-testid="stVerticalBlock"]{gap:0!important;}

/* ==============================================
   LAYOUT
============================================== */
#app-wrap{display:flex;height:100vh;overflow:hidden;position:relative;z-index:1;}

/* ─ Sidebar ─ */
#sb{
  width:256px;min-width:256px;
  background:linear-gradient(180deg,#0d0d1e,#0a0a16);
  border-right:1px solid var(--bd);
  display:flex;flex-direction:column;height:100vh;
  transition:transform .25s ease,width .25s ease;
  position:relative;z-index:10;flex-shrink:0;
}
#sb.hidden{transform:translateX(-256px);width:0;min-width:0;}

/* sidebar logo+new chat row */
.sb-top{padding:14px 12px 10px;border-bottom:1px solid var(--bd);}
.sb-brand{display:flex;align-items:center;gap:8px;margin-bottom:12px;}
.sb-brand-txt{font-weight:800;font-size:.95rem;
  background:linear-gradient(135deg,var(--c1),var(--c2));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.sb-new-btn{
  width:100%;padding:9px 14px;
  background:rgba(0,212,255,.08);
  border:1px solid rgba(0,212,255,.2);
  border-radius:10px;color:var(--c1);
  font-size:.85rem;font-weight:600;cursor:pointer;
  display:flex;align-items:center;gap:8px;
  transition:background .2s;
}
.sb-new-btn:hover{background:rgba(0,212,255,.15);}

/* sidebar search */
.sb-search{padding:8px 12px;}
.sb-search input{
  width:100%;background:rgba(255,255,255,.05);
  border:1px solid var(--bd);border-radius:9px;
  padding:7px 12px;color:var(--txt);font-size:.82rem;
  outline:none;transition:border-color .2s;
}
.sb-search input:focus{border-color:rgba(0,212,255,.35);}

/* sidebar history */
.sb-hist{flex:1;overflow-y:auto;padding:0 6px 6px;}
.sb-hist::-webkit-scrollbar{width:3px;}
.sb-hist::-webkit-scrollbar-thumb{background:var(--c2);border-radius:3px;}
.sb-date{font-size:.7rem;color:var(--muted);
  padding:8px 8px 3px;font-weight:700;text-transform:uppercase;letter-spacing:.9px;}
.sb-item{
  padding:8px 10px;border-radius:9px;
  font-size:.82rem;color:var(--txt);
  cursor:pointer;transition:background .15s;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
  margin-bottom:1px;
}
.sb-item:hover{background:rgba(255,255,255,.07);}
.sb-item.active{background:rgba(0,212,255,.1);color:var(--c1);}

/* sidebar footer */
.sb-foot{
  border-top:1px solid var(--bd);
  padding:10px 12px;
}
.sb-user{
  display:flex;align-items:center;gap:10px;
  padding:8px 8px;border-radius:10px;cursor:pointer;
  transition:background .15s;margin-bottom:5px;
}
.sb-user:hover{background:rgba(255,255,255,.06);}
.sb-avatar{
  width:32px;height:32px;border-radius:50%;
  background:linear-gradient(135deg,var(--c2),var(--c1));
  display:flex;align-items:center;justify-content:center;
  font-weight:800;font-size:.85rem;color:#fff;flex-shrink:0;
}
.xbar{height:4px;background:rgba(255,255,255,.06);border-radius:4px;margin:3px 0 8px;}
.xbar-fill{height:100%;border-radius:4px;background:linear-gradient(90deg,var(--c2),var(--c1));}

/* ─ Main ─ */
#main{flex:1;display:flex;flex-direction:column;height:100vh;overflow:hidden;min-width:0;}

/* ─ Topbar ─ */
#topbar{
  height:50px;border-bottom:1px solid var(--bd);
  background:rgba(10,10,16,.96);backdrop-filter:blur(10px);
  display:flex;align-items:center;padding:0 14px;gap:10px;
  flex-shrink:0;z-index:5;
}
.tb-toggle{
  background:none;border:none;color:var(--muted);
  cursor:pointer;padding:6px 8px;border-radius:8px;
  font-size:1.1rem;transition:color .2s,background .2s;flex-shrink:0;
}
.tb-toggle:hover{background:rgba(255,255,255,.08);color:var(--txt);}
.tb-title{font-weight:600;font-size:.92rem;color:var(--txt);flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.lang-row{display:flex;gap:3px;flex-shrink:0;}
.lang-btn{
  background:none;border:1px solid var(--bd);border-radius:7px;
  padding:4px 7px;color:var(--muted);font-size:.72rem;cursor:pointer;
  transition:all .2s;
}
.lang-btn.on{background:rgba(0,212,255,.12);color:var(--c1);border-color:rgba(0,212,255,.3);}

/* ─ Page nav ─ */
.page-nav{
  display:flex;gap:0;padding:0 4px;
  border-bottom:1px solid var(--bd);
  background:rgba(10,10,16,.9);flex-shrink:0;
  overflow-x:auto;
}
.page-nav::-webkit-scrollbar{height:0;}
.pn-item{
  padding:10px 13px;font-size:.8rem;font-weight:500;
  color:var(--muted);cursor:pointer;border:none;background:none;
  border-bottom:2px solid transparent;white-space:nowrap;
  transition:color .2s,border-color .2s;
}
.pn-item:hover{color:var(--txt);}
.pn-item.on{color:var(--c1);border-bottom-color:var(--c1);}

/* ─ Content ─ */
#content{flex:1;overflow-y:auto;position:relative;}
#content::-webkit-scrollbar{width:4px;}
#content::-webkit-scrollbar-thumb{background:rgba(255,255,255,.12);border-radius:4px;}

/* ==============================================
   CHAT
============================================== */
.chat-wrap{max-width:800px;margin:0 auto;padding:20px 16px 100px;}

/* welcome screen */
.welcome-box{
  display:flex;flex-direction:column;align-items:center;
  justify-content:center;min-height:60vh;text-align:center;padding:32px 16px;
}
.welcome-box h2{font-size:1.4rem;color:var(--txt);margin:12px 0 6px;}
.welcome-box p{color:var(--muted);font-size:.9rem;}

/* chat messages */
.msg-u{display:flex;justify-content:flex-end;margin:10px 0;}
.msg-u .bbl{
  background:linear-gradient(135deg,rgba(0,100,200,.5),rgba(0,212,255,.25));
  border:1px solid rgba(0,212,255,.3);
  border-radius:18px 18px 4px 18px;
  padding:12px 16px;max-width:78%;color:#fff;
  line-height:1.58;font-size:.92rem;word-wrap:break-word;
}
.msg-a{display:flex;gap:10px;margin:10px 0;align-items:flex-start;}
.msg-a .ai-ic{
  width:28px;height:28px;border-radius:50%;
  background:linear-gradient(135deg,var(--c2),var(--c1));
  display:flex;align-items:center;justify-content:center;
  font-weight:800;font-size:.7rem;color:#fff;flex-shrink:0;margin-top:2px;
}
.msg-a .bbl{
  background:var(--bg3);
  border:1px solid rgba(139,92,246,.2);
  border-radius:4px 18px 18px 18px;
  padding:12px 16px;max-width:86%;
  color:var(--txt);line-height:1.68;font-size:.92rem;word-wrap:break-word;
}
.msg-ts{font-size:.66rem;color:var(--muted);margin-top:4px;}

/* mode + style bar */
.mode-bar{
  display:flex;gap:6px;flex-wrap:wrap;
  padding:10px 16px 6px;max-width:800px;margin:0 auto;
  border-bottom:1px solid rgba(255,255,255,.04);
  flex-shrink:0;
}
.mode-chip{
  padding:5px 13px;border-radius:20px;font-size:.78rem;font-weight:600;
  border:1px solid var(--bd);color:var(--muted);background:none;cursor:pointer;
  transition:all .2s;white-space:nowrap;
}
.mode-chip.on{background:rgba(0,212,255,.14);border-color:rgba(0,212,255,.38);color:var(--c1);}

/* input bar */
#inp-bar{
  position:sticky;bottom:0;
  background:rgba(10,10,16,.98);backdrop-filter:blur(12px);
  border-top:1px solid var(--bd);padding:10px 16px 14px;
  flex-shrink:0;
}
.inp-inner{max-width:800px;margin:0 auto;}

/* ==============================================
   UI COMPONENTS
============================================== */
.gc{
  background:var(--glass);border:1px solid var(--bd);
  border-radius:var(--r);padding:16px;
  backdrop-filter:blur(10px);margin-bottom:12px;
  transition:border-color .25s;
}
.gc:hover{border-color:rgba(0,212,255,.28);}

.xo{background:rgba(255,255,255,.07);border-radius:20px;height:8px;overflow:hidden;margin:4px 0;}
.xi{height:100%;border-radius:20px;background:linear-gradient(90deg,var(--c2),var(--c1));transition:width .8s;}

.sc{background:var(--glass);border:1px solid var(--bd);border-radius:12px;padding:14px;text-align:center;}
.sn{font-size:1.9rem;font-weight:700;
  background:linear-gradient(135deg,var(--c1),var(--c2));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;}

.bdg{display:inline-block;padding:3px 9px;border-radius:20px;font-size:.7rem;font-weight:600;
  background:linear-gradient(135deg,var(--c2),var(--c1));color:#fff;margin:2px;}
.pfree{background:linear-gradient(135deg,#3a3a4a,#555)!important;}
.pstudent{background:linear-gradient(135deg,#d97706,#fbbf24)!important;}
.ppro{background:linear-gradient(135deg,var(--c2),var(--c1))!important;}
.pteacher{background:linear-gradient(135deg,#059669,#10b981)!important;}

.ann{background:linear-gradient(135deg,rgba(0,212,255,.05),rgba(139,92,246,.05));
  border-left:3px solid var(--c1);border-radius:8px;padding:10px 14px;margin:5px 0;}

.fc{background:linear-gradient(135deg,rgba(0,212,255,.07),rgba(139,92,246,.07));
  border:1px solid rgba(0,212,255,.22);border-radius:18px;
  padding:32px;text-align:center;min-height:160px;
  display:flex;align-items:center;justify-content:center;font-size:1.15rem;}

/* ─ Login ─ */
.login-page{min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px;}
.login-box{
  background:rgba(10,10,30,.96);border:1px solid rgba(0,212,255,.16);
  border-radius:22px;padding:36px 32px;max-width:400px;width:100%;
  backdrop-filter:blur(18px);box-shadow:0 20px 60px rgba(0,0,0,.7);
}

/* ─ Streamlit overrides ─ */
.stButton>button{
  background:linear-gradient(135deg,var(--c2),var(--c1))!important;
  color:#fff!important;border:none!important;border-radius:9px!important;
  font-weight:600!important;transition:opacity .2s!important;
}
.stButton>button:hover{opacity:.82!important;}
.stTextInput>div>div>input,.stTextArea>div>div>textarea{
  background:rgba(255,255,255,.05)!important;
  border:1px solid var(--bd)!important;
  color:var(--txt)!important;border-radius:9px!important;
}
.stTabs [data-baseweb="tab"]{color:var(--muted)!important;}
.stTabs [aria-selected="true"]{color:var(--c1)!important;border-bottom:2px solid var(--c1)!important;}
[data-testid="metric-container"]{
  background:var(--glass)!important;border:1px solid var(--bd)!important;border-radius:11px!important;
}
::-webkit-scrollbar{width:4px;}
::-webkit-scrollbar-thumb{background:var(--c2);border-radius:4px;}

/* ─ Mobile ─ */
@media(max-width:760px){
  #sb{position:fixed;top:0;left:0;height:100vh;z-index:200;transform:translateX(0);}
  #sb.hidden{transform:translateX(-260px);}
  #mob-nav{
    display:flex!important;
    position:fixed;bottom:0;left:0;right:0;z-index:100;
    background:rgba(10,10,20,.97);border-top:1px solid var(--bd);
    padding:6px 0 calc(6px + env(safe-area-inset-bottom));
    backdrop-filter:blur(16px);
  }
  .chat-wrap{padding-bottom:80px!important;}
  #inp-bar{padding-bottom:calc(12px + env(safe-area-inset-bottom))!important;}
  .page-nav{display:none!important;}
}
@media(min-width:761px){#mob-nav{display:none!important;}}
.mn-item{
  flex:1;display:flex;flex-direction:column;align-items:center;gap:2px;
  padding:5px 2px;color:var(--muted);font-size:.58rem;cursor:pointer;
  border:none;background:none;transition:color .2s;
}
.mn-item.on{color:var(--c1);}
.mn-item .ic{font-size:1.2rem;line-height:1.2;}

/* ─ Animations ─ */
@keyframes fadeUp{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}
.fu{animation:fadeUp .35s ease forwards;}
@keyframes fl{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
.fl{animation:fl 3s ease-in-out infinite;display:inline-block;}

/* sb overlay for mobile */
#sb-overlay{display:none;position:fixed;inset:0;z-index:190;background:rgba(0,0,0,.5);}
@media(max-width:760px){
  #sb-overlay.show{display:block;}
}
</style>""", unsafe_allow_html=True)

# ── DATA LAYER ────────────────────────────────────────────────────────────────
def uid_of(email: str) -> str:
    return hashlib.md5(email.lower().encode()).hexdigest()[:12]

def uf(uid): return Path(f"data/users/{uid}.json")
def hf(uid, cid=None): return Path(f"data/history/{uid}{'_'+cid if cid else ''}.json")

def load_user(uid: str) -> dict:
    if "@" in uid: uid = uid_of(uid)
    p = uf(uid)
    if p.exists():
        try:
            with open(p, encoding="utf-8") as f: return json.load(f)
        except: pass
    return {
        "id":uid,"name":"","email":"","avatar":"",
        "created":datetime.datetime.now().isoformat(),
        "xp":0,"badges":[],"test_scores":[],
        "mood_history":[],"streak":0,
        "last_active":datetime.date.today().isoformat(),
        "total_messages":0,"topics":{},"flashcards":[],
        "daily_q":0,"daily_date":"",
        "monthly_t":0,"monthly_date":"",
        "premium":"free","premium_exp":"",
        "password":"","lang":"uz",
        "settings":{"ai_style":"o'qituvchi"},
        "chats":[],"active_chat":None,
    }

def save_user(u: dict):
    with open(uf(u["id"]), "w", encoding="utf-8") as f:
        json.dump(u, f, ensure_ascii=False, indent=2)

def load_hist(uid: str, cid=None) -> list:
    p = hf(uid, cid)
    if p.exists():
        try:
            with open(p, encoding="utf-8") as f: return json.load(f)
        except: pass
    return []

def save_hist(uid: str, h: list, cid=None):
    with open(hf(uid, cid), "w", encoding="utf-8") as f:
        json.dump(h, f, ensure_ascii=False, indent=2)

def push_msg(uid: str, role: str, text: str, cid=None) -> list:
    h = load_hist(uid, cid)
    h.append({"role":role,"content":text,"ts":datetime.datetime.now().isoformat()})
    save_hist(uid, h, cid)
    return h

def all_users() -> list:
    res = []
    for p in Path("data/users").glob("*.json"):
        try:
            with open(p, encoding="utf-8") as f: res.append(json.load(f))
        except: pass
    return res

def load_ann() -> list:
    p = Path("data/announce/list.json")
    if p.exists():
        try:
            with open(p, encoding="utf-8") as f: return json.load(f)
        except: pass
    return []

def save_ann(lst):
    with open("data/announce/list.json","w",encoding="utf-8") as f:
        json.dump(lst, f, ensure_ascii=False, indent=2)

# ── SESSION ───────────────────────────────────────────────────────────────────
def mk_token(uid: str) -> str:
    token = hashlib.sha256(f"{uid}_{datetime.date.today()}_{uuid.uuid4()}".encode()).hexdigest()
    with open(f"data/sessions/{token}.json","w") as f:
        json.dump({"uid":uid,"date":datetime.date.today().isoformat()}, f)
    return token

def chk_token(token: str):
    if not token: return None
    p = Path(f"data/sessions/{token}.json")
    if not p.exists(): return None
    try:
        with open(p) as f: d = json.load(f)
        age = (datetime.date.today() - datetime.date.fromisoformat(d.get("date","2000-01-01"))).days
        if age > 7: p.unlink(); return None
        return d.get("uid")
    except: return None

# ── PREMIUM ───────────────────────────────────────────────────────────────────
def is_prem(u):
    p = u.get("premium","free")
    if p == "free": return False
    exp = u.get("premium_exp","")
    if exp:
        try:
            if datetime.date.fromisoformat(exp) < datetime.date.today():
                u["premium"]="free"; save_user(u); return False
        except: pass
    return p in ["student","pro","teacher"]

def get_plan(u): return u.get("premium","free")
def is_admin(u): return u.get("email","") in ADMIN_EMAILS

def can_ask(u):
    if is_prem(u): return True
    today = datetime.date.today().isoformat()
    if u.get("daily_date") != today: u["daily_q"]=0; u["daily_date"]=today; save_user(u)
    return u.get("daily_q",0) < FREE_Q

def inc_q(u): u["daily_q"]=u.get("daily_q",0)+1; save_user(u)

# ── GAMIFICATION ──────────────────────────────────────────────────────────────
LVS = [0,100,250,500,900,1400,2100,3000,4200,5800,8000]
LN = {
    "uz":["Yangi boshlovchi","Talaba","Izlanuvchi","Bilimdon","Ekspert",
          "Master","Ustoz","Akademik","Professor","Dono","Inson AI"],
    "en":["Newcomer","Student","Explorer","Scholar","Expert",
          "Master","Mentor","Academic","Professor","Sage","AI Human"],
    "ru":["Новичок","Студент","Исследователь","Знаток","Эксперт",
          "Мастер","Наставник","Академик","Профессор","Мудрец","Человек ИИ"],
}
BDGS = {
    "start":  {"e":"🚀","n":"Birinchi qadam","t":"1-suhbat"},
    "active": {"e":"📚","n":"Faol o'quvchi", "t":"50 xabar"},
    "tester": {"e":"🏆","n":"Test ustasi",   "t":"5 test"},
    "streak": {"e":"🔥","n":"7 kun streak",  "t":"7 kun ketma-ket"},
    "scholar":{"e":"🎓","n":"Bilimdon",      "t":"500 XP"},
    "prem":   {"e":"💎","n":"Premium",       "t":"Premium obuna"},
    "champ":  {"e":"🥇","n":"Turnir g'olibi","t":"Turnirda 1-o'rin"},
}

def lv_info(xp: int, lang="uz"):
    lv = 1
    for i,v in enumerate(LVS):
        if xp >= v: lv = i+1
    lv = min(lv, len(LVS))
    names = LN.get(lang, LN["uz"])
    name  = names[lv-1]
    cur   = LVS[lv-1]
    nxt   = LVS[lv] if lv < len(LVS) else LVS[-1]+1000
    return lv, name, cur, nxt

def add_xp(u, n):
    lang = st.session_state.get("lang","uz")
    old = lv_info(u["xp"], lang)[0]
    u["xp"] = u.get("xp",0) + n
    new = lv_info(u["xp"], lang)[0]
    if new > old: st.balloons(); st.success(f"🎉 {lv_info(u['xp'],lang)[1]} darajasiga ko'tarildingiz!")
    save_user(u); return u

def chk_bdg(u):
    e = set(u.get("badges",[]))
    cid = u.get("active_chat")
    hl  = len(load_hist(u["id"], cid))
    for bid, cond in [
        ("start",  hl >= 1),
        ("active", u.get("total_messages",0) >= 50),
        ("tester", len(u.get("test_scores",[])) >= 5),
        ("scholar",u.get("xp",0) >= 500),
        ("prem",   is_prem(u)),
    ]:
        if cond and bid not in e:
            e.add(bid); st.toast(f"{BDGS[bid]['e']} {BDGS[bid]['n']}!", icon="🏅")
    u["badges"] = list(e); save_user(u); return u

def upd_streak(u):
    today = datetime.date.today().isoformat()
    yest  = (datetime.date.today()-datetime.timedelta(1)).isoformat()
    last  = u.get("last_active","")
    if last == today: return u
    u["streak"] = u.get("streak",0)+1 if last==yest else 1
    u["last_active"] = today
    if u["streak"]>=7 and "streak" not in u.get("badges",[]):
        u.setdefault("badges",[]).append("streak"); st.toast("🔥 7 kun streak!",icon="🏅")
    save_user(u); return u

# ── CHAT MGMT ────────────────────────────────────────────────────────────────
def new_chat(u) -> str:
    cid = uuid.uuid4().hex[:8]
    u.setdefault("chats",[]).insert(0, {
        "id":cid,"title":"Yangi suhbat",
        "created":datetime.datetime.now().isoformat(),
        "updated":datetime.datetime.now().isoformat(),
    })
    u["active_chat"] = cid
    save_user(u); return cid

def set_chat_title(u, cid, first_msg):
    title = first_msg[:38]+("…" if len(first_msg)>38 else "")
    for c in u.get("chats",[]):
        if c["id"]==cid: c["title"]=title; c["updated"]=datetime.datetime.now().isoformat(); break
    save_user(u)

def chat_groups(chats):
    today     = datetime.date.today()
    yesterday = today - datetime.timedelta(1)
    g = {"today":[],"yesterday":[],"older":[]}
    for c in chats:
        try: d = datetime.date.fromisoformat(c.get("updated","")[:10])
        except: d = today
        if d==today: g["today"].append(c)
        elif d==yesterday: g["yesterday"].append(c)
        else: g["older"].append(c)
    return g

# ── AI ────────────────────────────────────────────────────────────────────────
def sys_prompt(u, mode="chat") -> str:
    lang = u.get("lang","uz")
    lv, name, _, _ = lv_info(u.get("xp",0), lang)
    style  = u.get("settings",{}).get("ai_style","o'qituvchi")
    mood   = (u.get("mood_history",[{}])[-1].get("mood","neytral") if u.get("mood_history") else "neytral")
    plan   = get_plan(u)

    lang_rules = {
        "uz": "MAJBURIY: FAQAT O'ZBEK TILIDA javob ber (boshqa til so'ramasa)",
        "en": "MANDATORY: ALWAYS respond in ENGLISH only",
        "ru": "OBYAZATELNO: VSEGDA otvechay tolko na RUSSKOM YAZYKE",
    }
    lang_rule = lang_rules.get(lang, lang_rules["uz"])
    uname = u.get("name") or "Oquvchi"

    p = (
        "Sen EduAI UZ - O'zbekistonning eng kuchli AI ta'lim yordamchisissan.\n"
        "Sen dunyadagi eng yaxshi AI o'qituvchisan.\n\n"
        "=== FOYDALANUVCHI ===\n"
        "Ism: " + uname + " | Daraja: " + name + " (Lv." + str(lv) + ")"
        " | Kayfiyat: " + mood + " | Uslub: " + style + " | Plan: " + plan.upper() + "\n\n"
        "=== ASOSIY QOIDALAR ===\n"
        "1. " + lang_rule + "\n"
        "2. Har doim ANIQ, ILMIY TO'G'RI ma'lumot ber\n"
        "3. Murakkab narsalarni ODDIY misollar bilan tushuntir\n"
        "4. BOSQICHMA-BOSQICH o'rgat (step-by-step)\n"
        "5. Foydalanuvchini rag'batlantir, xatolarni muloyimlik bilan to'g'irla\n"
        "6. MARKDOWN ishlatuvchi: sarlavhalar, jadvallar, kod bloklari\n"
        "7. O'rinli emojilar: ok noto'g'ri eslatma yulduz chiroq\n"
        "8. Kayfiyatga mos: xursand=energetik, xafa=yumshoq, stressli=tinchlantiruvchi\n"
        "9. Har javob oxirida 1-2 ta qiziqarli savol ber\n"
        "10. Premium: chuqurroq tahlil + ko'proq misol + amaliy topshiriqlar\n"
        "11. Matematik hisoblashlarda barcha qadamlarni ko'rsat\n"
        "12. Dasturlashda: kod ``` ichida, xatolarni aniqla\n\n"
        "=== JAVOB SIFATI ===\n"
        "- Kirish, asosiy tushuntirish, misol, xulosa, savol\n"
        "- Kamida 3-5 asosiy nuqta\n"
        "- Hayotiy va amaliy misollar\n"
        "- SUPER AI darajasida javob ber - har doim MAKSIMAL YORDAM!"
    )

    if mode == "konspekt":
        p += (
            "\n\n=== REJIM: KONSPEKT ===\n"
            "# [Mavzu nomi]\n"
            "## Asosiy tushunchalar va ta'riflar\n"
            "## Muhim qoidalar\n"
            "## Misollar va amaliy qo'llash\n"
            "## Formulalar / Algoritmlar\n"
            "## Taqqoslash jadvali\n"
            "## O'z-o'zini tekshirish (5-7 savol)\n"
            "## Qo'shimcha manbalar"
        )
    elif mode == "test":
        p += (
            "\n\nREJIM: TEST - FAQAT sof JSON qaytargin (boshqa hech narsa yozma):\n"
            "[{\"savol\":\"...\",\"variantlar\":[\"A) ...\",\"B) ...\",\"C) ...\",\"D) ...\"],"
            "\"togri_javob\":\"A\",\"izoh\":\"...\"}]"
        )
    elif mode == "mental":
        p += (
            "\n\nREJIM: KAYFIYAT - FAQAT sof JSON:\n"
            "{\"kayfiyat\":\"xursand|neytral|xafa|stressli\",\"daraja\":5,\"sabab\":\"...\",\"maslahat\":\"...\"}"
        )
    elif mode == "kod":
        p += (
            "\n\nREJIM: DASTURLASH - kodni ``` ichida yoz, "
            "har satrni tushuntir, xatolarni aniqla."
        )

    return p


def call_json(u, prompt, mode="test", max_tok=3000) -> str:
    if not api_key: return "[]"
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        # Tizim ko'rsatmasi va foydalanuvchi so'rovini birlashtirish
        full_prompt = f"{sys_prompt(u, mode)}\n\nFoydalanuvchi so'rovi: {prompt}"
        
        response = model.generate_content(full_prompt)
        raw = response.text
        
        # JSONni tozalash (re.sub qismi o'sha holicha qolsa ham bo'ladi)
        raw = re.sub(r"```json\s?|\s?```", "", raw).strip()
        
        # Sizning JSON qidirish mantiqingiz...
        for bra in ["[", "{"]:
            s = raw.find(bra)
            e = raw.rfind("]" if bra=="[" else "}")+1
            if s>=0 and e>s: return raw[s:e]
        return raw
    except: return "[]"

def mood_of(u, text) -> dict:
    raw = call_json(u, f"Tahlil: {text}", "mental", 256)
    try: return json.loads(raw)
    except: return {"kayfiyat":"neytral","daraja":5,"sabab":"","maslahat":"Yaxshi kun!"}

def gen_test(u, topic, n=5) -> list:
    raw = call_json(u, f"'{topic}' bo'yicha {n} ta sifatli test savoli yar.", "test", 3000)
    try: return json.loads(raw)
    except: return []

def gen_konspekt(u, hist) -> str:
    if not hist: return "Suhbat tarixi yo'q."
    txt = "\n".join([m["role"].upper() + ": " + m["content"] for m in hist[-20:]])
    msg = "Konspekt yar:\n" + txt
    return call_ai(u, [{"role":"user","content":msg}], "konspekt")

def gen_flash(u, topic, n=10) -> list:
    fmt = '[{"savol":"...","javob":"..."}]'
    p1 = topic + ' -- ' + str(n) + " ta flashcard. O'zbek tilida."
    p2 = topic + ' boyicha ' + str(n) + ' ta flashcard yar. Format: ' + fmt
    raw  = call_json(u, p1, 'test', 2000)
    raw2 = call_json(u, p2, 'mental', 2000)
    try: return json.loads(raw2)
    except:
        try: return json.loads(raw)
        except: return []


# ── BOOKS ─────────────────────────────────────────────────────────────────────
def load_books():
    p = Path("data/books/list.json")
    if p.exists():
        try:
            with open(p,encoding="utf-8") as f: return json.load(f)
        except: pass
    return []

def save_books(books):
    with open("data/books/list.json","w",encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=2)

BOOK_CATS = ["📐 Matematika","🔬 Fizika","🧪 Kimyo","🧬 Biologiya",
             "💻 Informatika","🌍 Tarix","📖 Adabiyot","🌐 Ingliz tili"]

# ── SIDEBAR HTML ──────────────────────────────────────────────────────────────
def sb_html(u) -> str:
    lang   = st.session_state.get("lang","uz")
    lv,nm,cur,nxt = lv_info(u.get("xp",0), lang)
    xp     = u.get("xp",0)
    pct    = min((xp-cur)/max(nxt-cur,1)*100, 100)
    plan   = get_plan(u)
    pi     = PLANS.get(plan,{})
    init   = (u.get("name","?") or "?")[0].upper()
    active = u.get("active_chat","")
    chats  = u.get("chats",[])
    grps   = chat_groups(chats)

    hist_html = ""
    for gk, glbl in [("today",t("today")),("yesterday",t("yesterday")),("older",t("older"))]:
        items = grps.get(gk,[])
        if not items: continue
        hist_html += f"<div class='sb-date'>{glbl}</div>"
        for c in items:
            cls = "sb-item active" if c["id"]==active else "sb-item"
            cid_v = c["id"]
            ctitle_v = c.get("title", "...")
            hist_html += "<div class='" + cls + "' onclick='pickChat(\"" + cid_v + "\")'" + ">" + ctitle_v + "</div>"
    if not hist_html:
        hist_html = f"<div style='color:var(--muted);font-size:.78rem;padding:12px 8px;'>{t('welcome_sub')}</div>"

    return f"""<div id="sb">
  <div class="sb-top">
    <div class="sb-brand">
      <span style="font-size:1.25rem;">🎓</span>
      <span class="sb-brand-txt">EduAI UZ</span>
    </div>
    <button class="sb-new-btn" onclick="doNewChat()">
      <span style="font-size:1rem;">✏️</span> {t('new_chat')}
    </button>
  </div>
  <div class="sb-search">
    <input id="sb-srch" type="text" placeholder="{t('search')}" oninput="sbFilter(this.value)"/>
  </div>
  <div class="sb-hist" id="sb-hist">{hist_html}</div>
  <div class="sb-foot">
    <div class="sb-user">
      <div class="sb-avatar">{init}</div>
      <div style="flex:1;min-width:0;">
        <div style="font-weight:600;font-size:.84rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{u.get('name','')}</div>
        <div style="font-size:.7rem;color:var(--muted);">Lv.{lv} · {xp} XP · 🔥{u.get('streak',0)}</div>
      </div>
      <span class="bdg p{plan}" style="font-size:.62rem;">{pi.get('emoji','')}</span>
    </div>
    <div class="xbar"><div class="xbar-fill" style="width:{pct:.0f}%;"></div></div>
  </div>
</div>
<div id="sb-overlay" onclick="closeSb()"></div>"""

# ── APP SHELL HTML ────────────────────────────────────────────────────────────
def shell_html(u, page):
    lang = st.session_state.get("lang","uz")
    pages = [
        ("chat","💬",t("chat")),("analytics","📊",t("analytics")),
        ("tests","📝",t("tests")),("flashcard","🃏",t("flashcard")),
        ("tournament","🏆",t("tournament")),("library","📚",t("library")),
        ("books","📖",t("books")),("premium","💎",t("premium")),
        ("settings","⚙️",t("settings")),
    ]
    if is_admin(u): pages.append(("admin","🛡️",t("admin")))

    nav_parts = []
    for k, em, lb in pages:
        cls = "on" if page == k else ""
        nav_parts.append('<button class="pn-item ' + cls + '" onclick="goPage(\'' + k + '\')">' + em + " " + lb + '</button>')
    nav = "".join(nav_parts)

    mob_parts = []
    for k, em, lb in pages[:6]:
        cls = "on" if page == k else ""
        mob_parts.append('<button class="mn-item ' + cls + '" onclick="goPage(\'' + k + '\')" title="' + lb + '"><span class="ic">' + em + '</span><span>' + lb + '</span></button>')
    mob = "".join(mob_parts)

    flag_map = {"uz": "🇺🇿", "en": "🇬🇧", "ru": "🇷🇺"}
    lbs_parts = []
    for c in ["uz", "en", "ru"]:
        cls = "on" if lang == c else ""
        lbs_parts.append('<button class="lang-btn ' + cls + '" onclick="setLang(\'' + c + '\')">' + flag_map[c] + '</button>')
    lbs = "".join(lbs_parts)

    titles = {k:lb for k,_,lb in pages}
    title  = titles.get(page, "EduAI UZ")

    return f"""
{sb_html(u)}
<div id="main">
  <div id="topbar">
    <button class="tb-toggle" onclick="toggleSb()">☰</button>
    <span class="tb-title">{title}</span>
    <div class="lang-row">{lbs}</div>
  </div>
  <div class="page-nav">{nav}</div>
  <div id="content">
</div><!-- #content opened, Streamlit content goes here -->
<div id="mob-nav">{mob}</div>
<script>
var SB_OPEN = true;
function toggleSb(){{
  var sb=document.getElementById('sb');
  var ov=document.getElementById('sb-overlay');
  if(sb.classList.contains('hidden')){{sb.classList.remove('hidden');if(window.innerWidth<=760){{ov.classList.add('show');}}}}
  else{{sb.classList.add('hidden');ov.classList.remove('show');}}
}}
function closeSb(){{document.getElementById('sb').classList.add('hidden');document.getElementById('sb-overlay').classList.remove('show');}}
function doNewChat(){{setParam('action','new_chat');}}
function pickChat(id){{setParam('chat_id',id);}}
function goPage(pg){{setParam('page',pg);}}
function setLang(l){{setParam('lang',l);}}
function setParam(k,v){{
  var url=new URL(window.parent.location.href);
  // clear action after use
  if(k!='action')url.searchParams.delete('action');
  url.searchParams.set(k,v);
  window.parent.history.replaceState(null,'',url);
  window.parent.location.reload();
}}
function sbFilter(q){{
  document.querySelectorAll('.sb-item').forEach(function(el){{
    el.style.display=el.textContent.toLowerCase().includes(q.toLowerCase())?'':'none';
  }});
}}
// Close sidebar on mobile by default
if(window.innerWidth<=760){{document.getElementById('sb').classList.add('hidden');}}
</script>"""

# ─────────────────────────────────────────────────────────────────────────────
# ── LOGIN PAGE ────────────────────────────────────────────────────────────────
def page_login():
    lang = st.session_state.get("lang","uz")

    st.markdown('<div class="login-page"><div class="login-box fu">', unsafe_allow_html=True)

    # Til
    c1,c2,c3 = st.columns(3)
    with c1:
        if st.button("🇺🇿 O'zbek", use_container_width=True, type="primary" if lang=="uz" else "secondary"):
            st.session_state["lang"]="uz"; st.rerun()
    with c2:
        if st.button("🇬🇧 English", use_container_width=True, type="primary" if lang=="en" else "secondary"):
            st.session_state["lang"]="en"; st.rerun()
    with c3:
        if st.button("🇷🇺 Русский", use_container_width=True, type="primary" if lang=="ru" else "secondary"):
            st.session_state["lang"]="ru"; st.rerun()

    # Logo
    st.markdown(f'<div class="fl" style="margin:20px 0 16px;">{get_logo_b64(160)}</div>', unsafe_allow_html=True)

    # Title
    st.markdown(f'<h2 style="text-align:center;color:#fff;margin-bottom:18px;font-size:1.3rem;">{t("welcome_title")}</h2>',
                unsafe_allow_html=True)

    # Announcements
    for a in [x for x in load_ann() if x.get("public")][-1:]:
        st.markdown(f'<div class="ann">📢 <b>{a["title"]}</b> - {a["text"]}</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs([t("login"), t("register")])

    with tab1:
        with st.form("lf"):
            email = st.text_input(t("email"), placeholder="email@gmail.com")
            pwd   = st.text_input(t("password"), type="password")
            sub   = st.form_submit_button(t("login_btn"), use_container_width=True)
        if sub:
            email = email.strip().lower()
            uid   = uid_of(email)
            u     = load_user(uid)
            if u.get("email") and u.get("password") == hashlib.md5(pwd.encode()).hexdigest():
                u = upd_streak(u); u["lang"] = lang; save_user(u)
                if not u.get("chats"): new_chat(u)
                token = mk_token(uid)
                cid   = u.get("active_chat")
                st.session_state.update({
                    "user":u, "page":"chat",
                    "hist":load_hist(uid,cid),
                    "tok":token, "lang":lang,
                })
                st.rerun()
            else:
                st.error(t("wrong_pass"))

    with tab2:
        with st.form("rf"):
            rname  = st.text_input(t("name"))
            remail = st.text_input(t("email"), placeholder="email@gmail.com", key="re")
            rpwd   = st.text_input(t("password"), type="password", key="rp")
            rsub   = st.form_submit_button(t("reg_btn"), use_container_width=True)
        if rsub:
            if not rname.strip(): st.warning(t("name_empty"))
            elif len(rpwd)<6: st.warning(t("pass_short"))
            else:
                remail = remail.strip().lower()
                uid    = uid_of(remail)
                exist  = load_user(uid)
                if exist.get("email"): st.error(t("email_exists"))
                else:
                    nu = load_user(uid)
                    nu.update({"id":uid,"name":rname.strip(),"email":remail,
                               "password":hashlib.md5(rpwd.encode()).hexdigest(),
                               "lang":lang})
                    save_user(nu); st.success(t("reg_ok"))

    st.markdown('</div></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# ── CHAT PAGE ─────────────────────────────────────────────────────────────────
def page_chat(u):
    hist   = st.session_state.get("hist",[])
    cid    = u.get("active_chat")
    lang   = st.session_state.get("lang","uz")
    MODES  = [t("mode_chat"), t("mode_code"), t("mode_book")]
    MODE_K = ["chat","kod","kitob"]

    # Mode / Style selector bar
    STYLES = {
        "uz":["o'qituvchi","do'st","mentor","akademik","qiziqarli"],
        "en":["teacher","friend","mentor","academic","fun"],
        "ru":["учитель","друг","ментор","академик","весёлый"],
    }.get(lang, ["o'qituvchi","do'st","mentor","akademik","qiziqarli"])

    c1,c2,c3 = st.columns([3,2,1])
    with c1:
        if "cm" not in st.session_state: st.session_state["cm"]=0
        sel = st.selectbox("",MODES,index=st.session_state["cm"],label_visibility="collapsed",key="msel")
        st.session_state["cm"] = MODES.index(sel)
    with c2:
        cs = u.get("settings",{}).get("ai_style","o'qituvchi")
        idx = STYLES.index(cs) if cs in STYLES else 0
        sty = st.selectbox("",STYLES,index=idx,label_visibility="collapsed",key="ssel")
        u.setdefault("settings",{})["ai_style"] = sty
    with c3:
        if st.button(t("clear"),use_container_width=True,key="clr"):
            save_hist(u["id"],[],cid); st.session_state["hist"]=[]; st.rerun()

    # Messages
    if not hist:
        st.markdown(f"""<div class="welcome-box">
          <div class="fl" style="font-size:2.8rem;">🎓</div>
          <h2>{t('welcome')}</h2>
          <p>{t('welcome_sub')}</p>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
        for m in hist:
            role = m.get("role","user")
            txt  = m.get("content","").replace("<","&lt;").replace(">","&gt;").replace("\n","<br>")
            ts   = m.get("ts","")[:16].replace("T"," ")
            if role=="user":
                st.markdown(f'<div class="msg-u"><div><div class="bbl">{txt}</div><div class="msg-ts" style="text-align:right;">{ts}</div></div></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="msg-a"><div class="ai-ic">AI</div><div><div class="bbl">{txt}</div><div class="msg-ts">EduAI · {ts}</div></div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Limit check
    if not can_ask(u):
        st.warning(t("daily_limit",n=FREE_Q))
        if st.button(t("get_premium"),key="prem_btn"):
            st.session_state["page"]="premium"; st.rerun()
        return

    # Input
    inp = st.chat_input(t("ask_me"), key="ci")
    if "pend" in st.session_state:
        inp = st.session_state.pop("pend")

    if inp and inp.strip():
        mode = MODE_K[st.session_state.get("cm",0)]
        if not hist: set_chat_title(u, cid, inp)
        if u.get("total_messages",0) % 5 == 0:
            md = mood_of(u, inp)
            u.setdefault("mood_history",[]).append({
                "ts":datetime.datetime.now().isoformat(),
                "mood":md.get("kayfiyat","neytral"),"daraja":md.get("daraja",5)})
        hist = push_msg(u["id"],"user",inp,cid); st.session_state["hist"]=hist
        with st.spinner(t("thinking")): reply = call_ai(u,hist,mode)
        hist = push_msg(u["id"],"assistant",reply,cid); st.session_state["hist"]=hist
        u["total_messages"]=u.get("total_messages",0)+1; inc_q(u)
        u=add_xp(u,5); u=chk_bdg(u); st.session_state["user"]=u
        for c in u.get("chats",[]):
            if c["id"]==cid: c["updated"]=datetime.datetime.now().isoformat(); break
        save_user(u); st.rerun()

# ── ANALYTICS ─────────────────────────────────────────────────────────────────
def page_analytics(u):
    st.markdown("## 📊 Analitika")
    lang  = st.session_state.get("lang","uz")
    cid   = u.get("active_chat")
    hist  = load_hist(u["id"],cid)
    tests = u.get("test_scores",[])
    moods = u.get("mood_history",[])
    aus   = all_users()
    avg   = round(np.mean([s["ball"] for s in tests]),1) if tests else 0
    rnk   = sorted(aus,key=lambda x:x.get("xp",0),reverse=True)
    mr    = next((i+1 for i,x in enumerate(rnk) if x["id"]==u["id"]),"-")

    cols=st.columns(5)
    for col,n,lb in [(cols[0],u.get("xp",0),"XP"),(cols[1],len(hist),"Xabarlar"),
                     (cols[2],len(tests),"Testlar"),(cols[3],f"{avg}%","O'rtacha"),(cols[4],f"#{mr}","Reyting")]:
        with col:
            st.markdown(f"<div class='sc'><div class='sn'>{n}</div><div style='color:var(--muted);font-size:.8rem;'>{lb}</div></div>",unsafe_allow_html=True)

    st.markdown("---")
    cl,cr=st.columns(2)
    with cl:
        st.markdown("### 🕸️ Bilim Xaritasi")
        tp=u.get("topics",{}); cats=list(tp.keys())[:8] if tp else ["Matematika","Fizika","Kimyo","Biologiya","Informatika","Tarix","Ingliz","Adabiyot"]
        vals=[tp[k] for k in cats] if tp else [__import__('random').randint(10,90) for _ in cats]
        fig=go.Figure(go.Scatterpolar(r=vals+[vals[0]],theta=cats+[cats[0]],fill="toself",
            fillcolor="rgba(0,212,255,.09)",line=dict(color="#00d4ff",width=2)))
        fig.update_layout(polar=dict(radialaxis=dict(range=[0,100],gridcolor="rgba(255,255,255,.07)"),
            angularaxis=dict(gridcolor="rgba(255,255,255,.07)",tickfont=dict(color="#e8eaf6"))),
            paper_bgcolor="rgba(0,0,0,0)",font=dict(color="#e8eaf6"),height=340,showlegend=False,margin=dict(l=40,r=40,t=20,b=20))
        st.plotly_chart(fig,use_container_width=True)
    with cr:
        st.markdown("### 📈 Test Natijalari")
        if tests:
            df=pd.DataFrame(tests[-20:])
            fig2=go.Figure(go.Scatter(x=list(range(len(df))),y=df["ball"],mode="lines+markers",
                line=dict(color="#00d4ff",width=2),marker=dict(size=8,color=df["ball"],colorscale="RdYlGn",cmin=0,cmax=100)))
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e8eaf6"),height=340,
                xaxis=dict(gridcolor="rgba(255,255,255,.04)"),yaxis=dict(gridcolor="rgba(255,255,255,.04)",range=[0,100]),
                margin=dict(l=16,r=16,t=16,b=16))
            st.plotly_chart(fig2,use_container_width=True)
        else: st.info("Hali test natijalari yo'q.")

    if moods:
        st.markdown("### 🌡️ Kayfiyat Tarixi")
        mm={"xursand":4,"neytral":3,"stressli":2,"xafa":1}
        days=[m.get("ts","")[:10] for m in moods[-30:]]; scores=[mm.get(m.get("mood","neytral"),3) for m in moods[-30:]]
        fig3=go.Figure(go.Heatmap(z=[scores],x=days,y=["Kayfiyat"],
            colorscale=[[0,"#ff4444"],[.33,"#ff9900"],[.66,"#00d4ff"],[1,"#00ff9f"]],
            zmin=1,zmax=4,colorbar=dict(tickvals=[1,2,3,4],ticktext=["Xafa","Stressli","Neytral","Xursand"],
                tickfont=dict(color="#e8eaf6"))))
        fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)",font=dict(color="#e8eaf6"),height=140,margin=dict(l=16,r=16,t=8,b=28))
        st.plotly_chart(fig3,use_container_width=True)

    st.markdown("### 🏅 Badge'lar")
    bdgs=u.get("badges",[])
    if bdgs:
        cols=st.columns(min(len(bdgs),5))
        for i,bid in enumerate(bdgs):
            b=BDGS.get(bid,{})
            with cols[i%5]:
                st.markdown(f"<div class='gc' style='text-align:center;padding:10px;'><div style='font-size:1.7rem;'>{b.get('e','🏅')}</div><div style='font-size:.78rem;font-weight:700;'>{b.get('n','')}</div><div style='font-size:.65rem;color:var(--muted);'>{b.get('t','')}</div></div>",unsafe_allow_html=True)
    else: st.info("Hali badge yo'q.")

# ── TESTS ─────────────────────────────────────────────────────────────────────
def page_tests(u):
    st.markdown("## 📝 Test Markazi")
    if not is_prem(u):
        today_m=datetime.date.today().strftime("%Y-%m")
        if u.get("monthly_date","")!=today_m: u["monthly_t"]=0; u["monthly_date"]=today_m; save_user(u)
        used=u.get("monthly_t",0)
        st.markdown(f"<div style='font-size:.8rem;color:var(--muted);margin-bottom:6px;'>Oylik: {used}/{FREE_T}</div>",unsafe_allow_html=True)
        if used>=FREE_T:
            st.warning("⚠️ Oylik limit!"); 
            if st.button(t("get_premium")): st.session_state["page"]="premium"; st.rerun()
            return

    ts=st.session_state.get("ts")
    if ts is None:
        with st.container():
            st.markdown("<div class='gc'>",unsafe_allow_html=True)
            mavzu=st.text_input("Mavzu","",placeholder="Kvadrat tenglamalar, Python, Tarix...")
            c1,c2,c3=st.columns(3)
            with c1: soni=st.slider("Savollar",3,20,5)
            with c2: daraja=st.selectbox("Qiyinlik",["Boshlang'ich","O'rta","Yuqori"])
            with c3: ltil=st.selectbox("Til",["O'zbek","Ingliz","Rus"])
            st.markdown("</div>",unsafe_allow_html=True)
        if st.button("🚀 Test Boshlash",use_container_width=True):
            if mavzu.strip():
                with st.spinner("Test yaratilmoqda..."):
                    qs=gen_test(u,f"{mavzu} ({daraja}, {ltil} tilida)",soni)
                if qs:
                    st.session_state["ts"]={"qs":qs,"cur":0,"ans":[],"mavzu":mavzu}
                    if not is_prem(u): u["monthly_t"]=u.get("monthly_t",0)+1; save_user(u); st.session_state["user"]=u
                    st.rerun()
                else: st.error("Test yaratishda xato.")
            else: st.warning("Mavzu kiriting!")
        sc=u.get("test_scores",[])
        if sc:
            st.markdown("### 📊 O'tgan Testlar")
            for s in reversed(sc[-8:]):
                e="✅" if s["ball"]>=70 else "⚠️" if s["ball"]>=50 else "❌"
                st.markdown(f"<div class='gc' style='padding:10px;display:flex;justify-content:space-between;'><span>{e} <b>{s.get('mavzu','')}</b></span><span style='color:var(--c1);'>{s['ball']}% · {s.get('sana','')[:10]}</span></div>",unsafe_allow_html=True)
    else:
        qs=ts["qs"]; cur=ts["cur"]; ans=ts["ans"]
        if cur>=len(qs):
            ok=sum(1 for a in ans if a.get("ok")); total=len(qs); ball=round(ok/total*100)
            e="🏆" if ball>=80 else "📚" if ball>=50 else "📖"
            st.markdown(f"<div class='gc' style='text-align:center;'><div style='font-size:3rem;'>{e}</div><h2>Test yakunlandi!</h2><div class='sn' style='font-size:2.6rem;'>{ball}%</div><p>{ok}/{total} to'g'ri</p></div>",unsafe_allow_html=True)
            xpe=ok*25+(50 if ball>=80 else 0)
            u=add_xp(u,xpe); u.setdefault("test_scores",[]).append({"mavzu":ts["mavzu"],"ball":ball,"togri":ok,"jami":total,"sana":datetime.datetime.now().isoformat()})
            u=chk_bdg(u); st.session_state["user"]=u; st.success(f"🎉 +{xpe} XP!")
            for i,(q,a) in enumerate(zip(qs,ans)):
                ok2=a.get("ok",False)
                st.markdown(f"<div class='gc' style='border-color:{'#00ff9f' if ok2 else '#ff4444'};padding:10px;'><b>{'✅' if ok2 else '❌'} {i+1}. {q.get('savol','')}</b><br><span style='color:var(--c1);'>Sizning: {a.get('javob','')}</span><br><span style='color:#00ff9f;'>To'g'ri: {q.get('togri_javob','')}</span><br><small style='color:var(--muted);'>{q.get('izoh','')}</small></div>",unsafe_allow_html=True)
            ca,cb=st.columns(2)
            with ca:
                if st.button("🔄 Yangi Test",use_container_width=True): st.session_state["ts"]=None; st.rerun()
            with cb:
                if st.button("📊 Analitika",use_container_width=True): st.session_state.update({"page":"analytics","ts":None}); st.rerun()
        else:
            q=qs[cur]
            st.markdown(f"<div style='font-size:.8rem;color:var(--muted);margin-bottom:3px;'>Savol {cur+1}/{len(qs)}</div><div class='xo'><div class='xi' style='width:{cur/len(qs)*100:.0f}%;'></div></div>",unsafe_allow_html=True)
            st.markdown(f"<div class='gc'><h3>❓ {q.get('savol','')}</h3></div>",unsafe_allow_html=True)
            for v in q.get("variantlar",[]):
                if st.button(v,key=f"v{cur}_{v}",use_container_width=True):
                    ok2=v[0].upper()==q.get("togri_javob","").upper()
                    ans.append({"javob":v,"ok":ok2}); ts["cur"]=cur+1; ts["ans"]=ans; st.session_state["ts"]=ts
                    if ok2: st.success("✅ To'g'ri!")
                    else: st.error(f"❌ To'g'ri: {q.get('togri_javob','')}")
                    time.sleep(0.3); st.rerun()

# ── FLASHCARD ─────────────────────────────────────────────────────────────────
def page_flashcard(u):
    st.markdown("## 🃏 Flashcard")
    if not is_prem(u):
        st.warning("⭐ Flashcard faqat Premium uchun!")
        if st.button(t("get_premium")): st.session_state["page"]="premium"; st.rerun()
        return
    tab1,tab2=st.tabs(["📖 O'rganish","➕ Yaratish"])
    with tab1:
        cards=u.get("flashcards",[])
        if not cards: st.info("Hali karta yo'q.")
        else:
            if "fci" not in st.session_state: st.session_state["fci"]=0
            if "fcs" not in st.session_state: st.session_state["fcs"]=False
            idx=st.session_state["fci"]%len(cards); card=cards[idx]
            st.markdown(f"<div style='text-align:center;color:var(--muted);font-size:.8rem;margin-bottom:6px;'>{idx+1}/{len(cards)}</div>",unsafe_allow_html=True)
            if not st.session_state["fcs"]:
                st.markdown(f"<div class='fc'><div><div style='font-size:.75rem;color:var(--muted);margin-bottom:8px;'>❓ SAVOL</div><div style='font-size:1.25rem;font-weight:700;'>{card.get('savol','')}</div></div></div>",unsafe_allow_html=True)
                if st.button("👁️ Javobni ko'rish",use_container_width=True): st.session_state["fcs"]=True; st.rerun()
            else:
                st.markdown(f"<div class='fc' style='border-color:#00ff9f;'><div><div style='font-size:.75rem;color:#00ff9f;margin-bottom:8px;'>✅ JAVOB</div><div style='font-size:1.1rem;'>{card.get('javob','')}</div></div></div>",unsafe_allow_html=True)
                ca,cb,cc=st.columns(3)
                with ca:
                    if st.button("😓 Qiyin",use_container_width=True): st.session_state["fcs"]=False; st.rerun()
                with cb:
                    if st.button("🤔 O'rtacha",use_container_width=True): st.session_state.update({"fci":(idx+1)%len(cards),"fcs":False}); st.rerun()
                with cc:
                    if st.button("✅ Bildim!",use_container_width=True):
                        u=add_xp(u,3); st.session_state.update({"user":u,"fci":(idx+1)%len(cards),"fcs":False}); st.rerun()
    with tab2:
        mavzu=st.text_input("Mavzu","",placeholder="Ingliz so'zlari, Python...")
        soni=st.slider("Nechta",5,30,10)
        if st.button("🤖 AI bilan Yaratish",use_container_width=True):
            if mavzu.strip():
                with st.spinner("Yaratilmoqda..."): fcs=gen_flash(u,mavzu,soni)
                if fcs:
                    u.setdefault("flashcards",[]).extend(fcs); save_user(u); u=add_xp(u,20); st.session_state["user"]=u
                    st.success(f"✅ {len(fcs)} ta karta! +20 XP"); st.rerun()
                else: st.error("Xato yuz berdi.")
            else: st.warning("Mavzu kiriting!")
        if u.get("flashcards"):
            st.markdown(f"**Jami:** {len(u['flashcards'])} ta karta")
            if st.button("🗑️ Hammasini o'chirish"):
                u["flashcards"]=[]; save_user(u); st.session_state["user"]=u; st.rerun()

# ── TOURNAMENT ────────────────────────────────────────────────────────────────
def page_tournament(u):
    st.markdown("## 🏆 Turnir & Reyting")
    tab1,tab2=st.tabs(["🏅 Reyting","⚔️ Haftalik Turnir"])
    with tab1:
        lang=st.session_state.get("lang","uz")
        aus=all_users(); rnk=sorted(aus,key=lambda x:x.get("xp",0),reverse=True)
        for i,x in enumerate(rnk[:20]):
            is_me=x["id"]==u["id"]
            re2="🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else f"{i+1}."
            lv2,ln2,_,_=lv_info(x.get("xp",0),lang)
            bg="rgba(0,212,255,.06)" if is_me else "transparent"
            bd="rgba(0,212,255,.3)" if is_me else "rgba(255,255,255,.04)"
            pe=PLANS.get(x.get("premium","free"),{}).get("emoji","")
            st.markdown(f"<div style='background:{bg};border:1px solid {bd};border-radius:9px;padding:9px 14px;margin:3px 0;display:flex;align-items:center;justify-content:space-between;'><div style='display:flex;align-items:center;gap:10px;'><span style='font-size:1rem;width:30px;'>{re2}</span><div><div style='font-weight:{'700' if is_me else '400'};font-size:.88rem;'>{x.get('name','?')} {pe}{'  <- Sen' if is_me else ''}</div><div style='font-size:.7rem;color:var(--muted);'>Lv.{lv2} {ln2}</div></div></div><div style='text-align:right;'><div style='color:var(--c1);font-weight:700;font-size:.88rem;'>{x.get('xp',0)} XP</div><div style='font-size:.7rem;color:var(--muted);'>{len(x.get('test_scores',[]))} test</div></div></div>",unsafe_allow_html=True)
    with tab2:
        if not is_prem(u):
            st.warning("⭐ Turnir uchun Premium kerak!")
            if st.button(t("get_premium")): st.session_state["page"]="premium"; st.rerun()
            return
        st.markdown("<div class='gc'>",unsafe_allow_html=True)
        we=datetime.datetime.now()+datetime.timedelta(days=(6-datetime.datetime.now().weekday()))
        st.markdown(f"**⚔️ Haftalik Turnir** | Tugash: {we.strftime('%d.%m.%Y')} | **Sovrin: 🏆 500 XP + Badge!**")
        if "trns" not in st.session_state:
            if st.button("⚔️ Qatnashish!",use_container_width=True):
                with st.spinner("Test yaratilmoqda..."): qs=gen_test(u,"Matematika yuqori daraja",10)
                st.session_state.update({"trns":True,"trnq":qs,"trna":[],"trnc":0}); st.rerun()
        else:
            qs=st.session_state.get("trnq",[]); cur=st.session_state.get("trnc",0); ans=st.session_state.get("trna",[])
            if cur>=len(qs):
                ok=sum(1 for a in ans if a); ball=round(ok/max(len(qs),1)*100); st.success(f"🏆 {ball}% ({ok}/{len(qs)})")
                if ball>=70:
                    u=add_xp(u,500)
                    if "champ" not in u.get("badges",[]): u.setdefault("badges",[]).append("champ")
                    save_user(u); st.session_state["user"]=u; st.balloons(); st.success("🥇 +500 XP!")
                if st.button("🔄 Qayta"):
                    for k in ["trns","trnq","trna","trnc"]: st.session_state.pop(k,None)
                    st.rerun()
            elif qs:
                q=qs[cur]; st.markdown(f"**Savol {cur+1}/{len(qs)}:** {q.get('savol','')}")
                for v in q.get("variantlar",[]):
                    if st.button(v,key=f"tv{cur}_{v}",use_container_width=True):
                        ans.append(v[0].upper()==q.get("togri_javob","").upper())
                        st.session_state.update({"trna":ans,"trnc":cur+1}); st.rerun()
        st.markdown("</div>",unsafe_allow_html=True)

# ── LIBRARY ───────────────────────────────────────────────────────────────────
def page_library(u):
    st.markdown("## 📚 Kutubxona")
    tab1,tab2,tab3=st.tabs(["💬 Suhbat Tarixi","📝 Konspekt","🎓 Sertifikatlar"])
    with tab1:
        all_chats=u.get("chats",[])
        if all_chats:
            names=[c.get("title","Suhbat") for c in all_chats]
            sel=st.selectbox("Chat",names,index=0)
            idx=names.index(sel); cid=all_chats[idx]["id"]
            hist=load_hist(u["id"],cid)
        else:
            hist=load_hist(u["id"]); cid=None
        srch=st.text_input("🔍","",placeholder="Qidirish...",label_visibility="collapsed")
        filt=[m for m in hist if srch.lower() in m.get("content","").lower()] if srch else hist
        st.markdown(f"*{len(filt)} ta xabar*")
        for m in reversed(filt[-50:]):
            role=m.get("role","user"); c="var(--c1)" if role=="user" else "var(--c2)"
            ts=m.get("ts","")[:16].replace("T"," "); txt=m.get("content","")[:200]
            st.markdown(f"<div class='gc' style='padding:10px;border-color:{c}33;'><span style='color:{c};font-size:.75rem;'>{'👤' if role=='user' else '🤖'} {ts}</span><br><span style='font-size:.87rem;'>{txt}{'...' if len(m.get('content',''))>200 else ''}</span></div>",unsafe_allow_html=True)
    with tab2:
        cid2=u.get("active_chat"); hist2=load_hist(u["id"],cid2)
        n=st.slider("Oxirgi xabarlar",5,50,20)
        if st.button("📝 Konspekt Yaratish",use_container_width=True):
            if hist2:
                with st.spinner("Yaratilmoqda..."): k=gen_konspekt(u,hist2[-n:])
                st.markdown(k); u=add_xp(u,15); st.session_state["user"]=u
                st.download_button("⬇️ Yuklab olish",k.encode(),f"konspekt_{datetime.date.today()}.md","text/markdown")
            else: st.warning("Avval suhbat qiling!")
    with tab3:
        scs=[s for s in u.get("test_scores",[]) if s.get("ball",0)>=70]
        if scs:
            for s in scs[-5:]:
                st.markdown(f"""<div style='background:linear-gradient(135deg,#080820,#160828);border:2px solid var(--c1);border-radius:14px;padding:24px;text-align:center;margin-bottom:12px;'>
<div style='font-size:2.2rem;'>🎓</div>
<h2 style='background:linear-gradient(135deg,var(--c1),var(--c2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;'>SERTIFIKAT</h2>
<h3 style='color:#fff;margin:6px 0;'>{u.get('name','')}</h3>
<p style='color:var(--c1);'>{s.get('mavzu','')}</p>
<p style='color:var(--muted);'>{s['ball']}% · {s.get('sana','')[:10]}</p>
<p style='color:var(--muted);font-size:.72rem;'>EduAI UZ · Smarter Learning, Better Future</p></div>""",unsafe_allow_html=True)
        else: st.info("70%+ ball to'plab sertifikat oling!")

# ── BOOKS ─────────────────────────────────────────────────────────────────────
def page_books(u):
    st.markdown("## 📖 Kitoblar")
    books=load_books()
    c1,c2=st.columns([3,1])
    with c1: srch=st.text_input("","",placeholder="🔍 Kitob nomi...",label_visibility="collapsed")
    with c2: cat=st.selectbox("",["Hammasi"]+BOOK_CATS,label_visibility="collapsed")
    filt=books
    if cat!="Hammasi": filt=[b for b in filt if b.get("kategoriya")==cat]
    if srch: filt=[b for b in filt if srch.lower() in b.get("nom","").lower() or srch.lower() in b.get("muallif","").lower()]
    if not filt:
        st.markdown("<div class='gc' style='text-align:center;'><div style='font-size:2.5rem;'>📚</div><p style='color:var(--muted);'>Hali kitob qo'shilmagan</p></div>",unsafe_allow_html=True)
        return
    cols=st.columns(3)
    for i,book in enumerate(filt):
        with cols[i%3]:
            cover=book.get("rasm","")
            img=(f"<img src='{cover}' style='width:100%;height:150px;object-fit:cover;border-radius:10px 10px 0 0;'/>" if cover else "<div style='width:100%;height:150px;background:linear-gradient(135deg,rgba(0,212,255,.1),rgba(139,92,246,.15));border-radius:10px 10px 0 0;display:flex;align-items:center;justify-content:center;font-size:2.8rem;'>📖</div>")
            st.markdown(f"<div class='gc' style='padding:0;overflow:hidden;'>{img}<div style='padding:11px;'><div style='font-size:.7rem;color:var(--c1);margin-bottom:3px;'>{book.get('kategoriya','')}</div><div style='font-weight:700;font-size:.88rem;margin-bottom:3px;'>{book.get('nom','')}</div><div style='font-size:.76rem;color:var(--muted);'>✍️ {book.get('muallif','')}</div></div></div>",unsafe_allow_html=True)
            if st.button("🤖 O'rgan",key=f"bk{i}",use_container_width=True):
                st.session_state["pend"]=f"'{book.get('nom','')}' kitobini tushuntir. Muallif: {book.get('muallif','')}"
                st.session_state["page"]="chat"; st.rerun()

# ── PREMIUM ───────────────────────────────────────────────────────────────────
def page_premium(u):
    st.markdown("## 💎 Premium")
    lang=st.session_state.get("lang","uz")
    cur=get_plan(u)
    data=[
        ("free","🆓","Bepul",0,["✅ Kuniga 20 savol","✅ Asosiy chat","✅ Oyiga 5 test","❌ Flashcard","❌ Turnir"]),
        ("student","⭐","Student",29900,["✅ Cheksiz savol","✅ Cheksiz test","✅ Flashcard","✅ Turnirlar","✅ Sertifikat"]),
        ("pro","🏆","Pro",59900,["✅ Student +","✅ Virtual sinf","✅ Ota-ona panel","✅ Maxsus sertifikat","✅ Reyting bonus"]),
        ("teacher","👨‍🏫","O'qituvchi",99900,["✅ Pro +","✅ Sinf boshqarish","✅ O'z testlari","✅ O'quvchi monitoring","✅ Admin panel"]),
    ]
    cols=st.columns(4)
    for col,(pid,em,nom,narx,feats) in zip(cols,data):
        with col:
            is_cur=cur==pid; bd="var(--c1)" if is_cur else "rgba(255,255,255,.07)"
            price_txt = "Bepul" if narx==0 else f"{narx:,} so'm"
            joriy_txt = '<div style="color:#00ff9f;font-size:.8rem;font-weight:700;">&#10003; Joriy</div>' if is_cur else ""
            feats_txt = "<br>".join(feats)
            st.markdown(
                f"<div style='background:rgba(0,0,0,.25);border:2px solid {bd};"
                f"border-radius:13px;padding:16px;text-align:center;min-height:300px;'>"
                f"<div style='font-size:2rem;'>{em}</div>"
                f"<h3 style='color:#fff;margin:5px 0 3px;font-size:.95rem;'>{nom}</h3>"
                f"<div style='font-size:1.2rem;font-weight:700;color:var(--c1);margin:8px 0;'>{price_txt}</div>"
                f"<div style='text-align:left;font-size:.76rem;color:var(--muted);margin:8px 0;'>{feats_txt}</div>"
                f"{joriy_txt}</div>",
                unsafe_allow_html=True)
            if not is_cur and pid!="free":
                if st.button("Sotib olish",key=f"pb{pid}",use_container_width=True):
                    st.session_state["selp"]=pid
    sel=st.session_state.get("selp")
    if sel and sel!="free":
        pi=PLANS.get(sel,{}); nom2=pi.get("nom" if lang=="uz" else "name" if lang=="en" else "имя","")
        msg=f"Assalomu alaykum! EduAI UZ da {nom2} ({pi.get('narx',0):,} so'm/oy) olmoqchiman. Email: {u.get('email','')}"
        st.markdown("---")
        st.markdown(f"<div class='gc' style='text-align:center;'><h3>💬 Telegram orqali sotib olish</h3><p style='color:var(--muted);'>{pi.get('emoji','')} <b>{nom2}</b> - <b style='color:var(--c1);'>{pi.get('narx',0):,} so'm/oy</b></p><a href='https://t.me/{TELEGRAM_USER}?text={msg}' target='_blank' style='display:inline-block;background:#2AABEE;color:#fff;padding:11px 28px;border-radius:11px;text-decoration:none;font-weight:700;margin:10px 0;'>📱 @{TELEGRAM_USER}</a><p style='color:var(--muted);font-size:.76rem;margin-top:8px;'>📧 {u.get('email','')}</p></div>",unsafe_allow_html=True)

# ── SETTINGS ──────────────────────────────────────────────────────────────────
def page_settings(u):
    st.markdown("## ⚙️ Sozlamalar")
    lang=st.session_state.get("lang","uz")
    c1,c2=st.columns(2)
    with c1:
        st.markdown("<div class='gc'>",unsafe_allow_html=True)
        st.markdown("### 👤 Profil")
        nn=st.text_input("Ism",u.get("name",""))
        stls=["o'qituvchi","do'st","mentor","akademik","qiziqarli"]
        cs=u.get("settings",{}).get("ai_style","o'qituvchi")
        ns=st.selectbox("AI uslubi",stls,index=stls.index(cs) if cs in stls else 0)
        lmap={"uz":"🇺🇿 O'zbek","en":"🇬🇧 English","ru":"🇷🇺 Русский"}
        nl=st.selectbox("Til",list(lmap.keys()),index=list(lmap.keys()).index(lang),format_func=lambda x:lmap[x])
        if st.button(t("save")):
            u["name"]=nn; u.setdefault("settings",{})["ai_style"]=ns; u["lang"]=nl
            save_user(u); st.session_state.update({"user":u,"lang":nl}); st.success("✅ Saqlandi!"); st.rerun()
        st.markdown("</div>",unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='gc'>",unsafe_allow_html=True)
        st.markdown("### 📊 Statistika")
        lv,nm,_,_=lv_info(u.get("xp",0),lang)
        st.metric(t("level"),f"Lv.{lv} - {nm}"); st.metric("XP",u.get("xp",0))
        st.metric(t("streak"),f"{u.get('streak',0)} {t('streak')} 🔥"); st.metric("Xabarlar",u.get("total_messages",0))
        st.metric("Obuna",PLANS.get(get_plan(u),{}).get("nom",""))
        st.markdown("</div>",unsafe_allow_html=True)
    st.markdown("<div class='gc'>",unsafe_allow_html=True)
    st.markdown("### ⚠️ Ma'lumotlar")
    ca,cb,cc=st.columns(3)
    with ca:
        if st.button("🗑️ Tarixni tozalash"):
            cid=u.get("active_chat"); save_hist(u["id"],[],cid); st.session_state["hist"]=[]; st.success("✅")
    with cb:
        h=load_hist(u["id"],u.get("active_chat"))
        st.download_button("⬇️ Tarix",json.dumps(h,ensure_ascii=False,indent=2).encode(),"history.json","application/json")
    with cc:
        st.download_button("⬇️ Profil",json.dumps(u,ensure_ascii=False,indent=2).encode(),"profile.json","application/json")
    st.markdown("</div>",unsafe_allow_html=True)

# ── ADMIN ─────────────────────────────────────────────────────────────────────
def page_admin(u):
    if not is_admin(u): st.error("❌ Ruxsat yo'q!"); return
    st.markdown("## 🛡️ Admin Panel")
    aus=all_users(); prems=[x for x in aus if is_prem(x)]; txp=sum(x.get("xp",0) for x in aus)
    c1,c2,c3,c4=st.columns(4)
    with c1: st.metric("👥 Foydalanuvchilar",len(aus))
    with c2: st.metric("💎 Premium",len(prems))
    with c3: st.metric("⚡ Jami XP",f"{txp:,}")
    with c4: st.metric("📊 O'rtacha",f"{txp//max(len(aus),1):,}")

    tab1,tab2,tab3,tab4=st.tabs(["👥 Foydalanuvchilar","💎 Premium","📢 E'lonlar","📖 Kitoblar"])
    with tab1:
        srch=st.text_input("","",placeholder="Qidirish...",label_visibility="collapsed")
        filt=[x for x in aus if not srch or srch.lower() in x.get("name","").lower() or srch.lower() in x.get("email","").lower()]
        lang=st.session_state.get("lang","uz")
        for x in sorted(filt,key=lambda z:z.get("xp",0),reverse=True)[:50]:
            plan=x.get("premium","free"); lv2,ln2,_,_=lv_info(x.get("xp",0),lang)
            st.markdown(f"<div class='gc' style='padding:9px;'><b>{x.get('name','?')}</b> {'🛡️' if x.get('email','') in ADMIN_EMAILS else ''} <span class='bdg p{plan}'>{plan}</span><br><small style='color:var(--muted);'>{x.get('email','')} | Lv.{lv2} | {x.get('xp',0)} XP | 🔥{x.get('streak',0)}</small></div>",unsafe_allow_html=True)
    with tab2:
        emails=[x.get("email","") for x in aus if x.get("email")]
        te=st.selectbox("Foydalanuvchi",[""]+emails); np2=st.selectbox("Plan",list(PLANS.keys()))
        exp=st.date_input("Tugash",datetime.date.today()+datetime.timedelta(days=30))
        ca,cb=st.columns(2)
        with ca:
            if st.button("✅ Yoqish",use_container_width=True):
                if te:
                    for x in aus:
                        if x.get("email")==te:
                            x["premium"]=np2; x["premium_exp"]=exp.isoformat()
                            if np2!="free" and "prem" not in x.get("badges",[]): x.setdefault("badges",[]).append("prem")
                            save_user(x); st.success(f"✅ {te} ga {np2}!")
        with cb:
            if st.button("❌ O'chirish",use_container_width=True):
                if te:
                    for x in aus:
                        if x.get("email")==te: x["premium"]="free"; x["premium_exp"]=""; save_user(x); st.success("✅")
        for x in [z for z in aus if is_prem(z)]:
            xplan = x.get("premium","")
            xname = x.get("name","")
            xemail = x.get("email","")
            xexp = x.get("premium_exp","")
            st.markdown(
                f"<div class='gc' style='padding:8px;'>"
                f"<b>{xname}</b> <span class='bdg p{xplan}'>{xplan}</span><br>"
                f"<small style='color:var(--muted);'>{xemail} - {xexp}</small></div>",
                unsafe_allow_html=True)
    with tab3:
        anns=load_ann()
        at=st.text_input("Sarlavha",""); atx=st.text_area("Matn","",height=70); ap=st.checkbox("Kirish sahifasida",value=True)
        if st.button("📢 Yuborish",use_container_width=True):
            if at.strip() and atx.strip():
                anns.append({"id":len(anns)+1,"title":at,"text":atx,"public":ap,"date":datetime.datetime.now().isoformat()})
                save_ann(anns); st.success("✅")
        for a in reversed(anns):
            ca2,cb2=st.columns([5,1])
            with ca2: st.markdown(f"<div class='ann'><b>{a['title']}</b><br>{a['text']}</div>",unsafe_allow_html=True)
            with cb2:
                if st.button("🗑️",key=f"da{a['id']}"): anns=[x for x in anns if x["id"]!=a["id"]]; save_ann(anns); st.rerun()
    with tab4:
        books=load_books()
        st.markdown("<div class='gc'>",unsafe_allow_html=True)
        st.markdown("#### ➕ Yangi Kitob")
        c1,c2=st.columns(2)
        with c1:
            bnom=st.text_input("Nomi","",key="bn"); bauth=st.text_input("Muallif","",key="ba")
            bcat=st.selectbox("Kategoriya",BOOK_CATS,key="bc"); bdara=st.selectbox("Daraja",["Boshlang'ich","O'rta","Yuqori"],key="bd")
        with c2:
            bimg=st.text_input("Rasm URL","",key="bi",placeholder="https://..."); byil=st.text_input("Yil","",key="by")
            btil=st.selectbox("Til",["O'zbek","Rus","Ingliz"],key="bt")
        btavsif=st.text_area("Tavsif","",key="btv",height=70)
        if st.button("✅ Qo'shish",use_container_width=True,key="ab"):
            if bnom.strip() and bauth.strip():
                books.append({"id":len(books)+1,"nom":bnom.strip(),"muallif":bauth.strip(),
                              "kategoriya":bcat,"daraja":bdara,"tavsif":btavsif.strip(),
                              "rasm":bimg.strip(),"yil":byil.strip(),"til":btil,
                              "views":0,"qoshildi":datetime.datetime.now().isoformat()})
                save_books(books); st.success("✅ Qo'shildi!"); st.rerun()
            else: st.warning("Nom va muallif kiriting!")
        st.markdown("</div>",unsafe_allow_html=True)
        st.markdown(f"**Kitoblar: {len(books)} ta**")
        for b in sorted(books,key=lambda x:x.get("qoshildi",""),reverse=True):
            ca3,cb3=st.columns([5,1])
            with ca3: st.markdown(f"<div class='gc' style='padding:9px;'><b>{b.get('nom','')}</b> <span class='bdg' style='font-size:.65rem;'>{b.get('kategoriya','')}</span><br><small style='color:var(--muted);'>✍️ {b.get('muallif','')} | 👁️ {b.get('views',0)}</small></div>",unsafe_allow_html=True)
            with cb3:
                if st.button("🗑️",key=f"db{b['id']}"): books=[x for x in books if x["id"]!=b["id"]]; save_books(books); st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    inject_css()

    if "lang" not in st.session_state:
        st.session_state["lang"] = "uz"

    # ── Auto-login: session token ──────────────────────────────────────────
    if "user" not in st.session_state:
        params = st.query_params
        tok    = params.get("sess","") or st.session_state.get("tok","")
        if tok:
            uid = chk_token(tok)
            if uid:
                u = load_user(uid)
                if u.get("email"):
                    u = upd_streak(u)
                    if not u.get("chats"): new_chat(u)
                    cid = u.get("active_chat")
                    st.session_state.update({
                        "user":u, "page":"chat",
                        "hist":load_hist(uid,cid),
                        "tok":tok, "lang":u.get("lang","uz"),
                    })
                    if "sess" in st.query_params:
                        st.query_params.clear()
                    st.rerun()

    # ── Login page ────────────────────────────────────────────────────────
    if "user" not in st.session_state:
        page_login()
        return

    # ── Handle URL params ─────────────────────────────────────────────────
    u      = st.session_state["user"]
    params = st.query_params

    if "lang" in params:
        nl = params["lang"]
        if nl in ["uz","en","ru"]:
            st.session_state["lang"] = nl
            u["lang"] = nl; save_user(u)

    if "page" in params:
        pg = params["page"]
        if pg in ["chat","analytics","tests","flashcard","tournament","library","books","premium","settings","admin"]:
            st.session_state["page"] = pg

    if params.get("action") == "new_chat":
        cid = new_chat(u)
        st.session_state.update({"hist":[],"user":u})
        st.query_params.clear(); st.rerun()

    if "chat_id" in params:
        cid = params["chat_id"]
        if cid in [c["id"] for c in u.get("chats",[])]:
            u["active_chat"] = cid; save_user(u)
            st.session_state.update({"user":u,"hist":load_hist(u["id"],cid)})
        st.query_params.clear()

    # Clear processed params
    if any(k in params for k in ["page","lang","action","chat_id"]):
        st.query_params.clear()

    st.session_state["user"] = u

    # ── Init hist ────────────────────────────────────────────────────────
    if "hist" not in st.session_state:
        if not u.get("chats"): new_chat(u); st.session_state["user"]=u
        st.session_state["hist"] = load_hist(u["id"], u.get("active_chat"))

    if "page" not in st.session_state:
        st.session_state["page"] = "chat"

    pg = st.session_state.get("page","chat")

    # ── Render shell ─────────────────────────────────────────────────────
    st.markdown('<div id="app-wrap">', unsafe_allow_html=True)
    st.markdown(shell_html(u, pg), unsafe_allow_html=True)

    # ── Page content ─────────────────────────────────────────────────────
    dispatch = {
        "chat":page_chat, "analytics":page_analytics,
        "tests":page_tests, "flashcard":page_flashcard,
        "tournament":page_tournament, "library":page_library,
        "books":page_books, "premium":page_premium,
        "settings":page_settings, "admin":page_admin,
    }
    dispatch.get(pg, page_chat)(u)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Logout (sidebar footer) ───────────────────────────────────────────
    with st.sidebar:
        if st.button(t("logout"), key="lo_btn", use_container_width=True):
            st.session_state.clear(); st.query_params.clear(); st.rerun()

if __name__ == "__main__":
    main()