import streamlit as st
import joblib
import matplotlib.pyplot as plt
import numpy as np
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from io import BytesIO
import json
import os
import re
import google.generativeai as genai
import streamlit.components.v1 as components

# ---------------- GEMINI CONFIG ----------------
GEMINI_API_KEY = "AIzaSyDYG1LgQPxLkMlTq1Tu7FNbEbQodSUJ8kQ"
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-2.5-flash")

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="CareerAI", page_icon="🚀", layout="wide")

# ---------------- JS STYLE INJECTOR ----------------
components.html("""
<script>
function applyStyles() {
    var doc = window.parent.document;
    var inputs = doc.querySelectorAll('input[type="text"], input[type="password"], input:not([type]), textarea');
    inputs.forEach(function(el) {
        el.style.setProperty('color', '#f1f5f9', 'important');
        el.style.setProperty('background', 'transparent', 'important');
        el.style.setProperty('caret-color', '#38bdf8', 'important');
        el.style.setProperty('-webkit-text-fill-color', '#f1f5f9', 'important');
        el.style.setProperty('border', 'none', 'important');
        el.style.setProperty('padding', '12px 16px', 'important');
        el.addEventListener('input', function() {
            this.style.setProperty('color', '#f1f5f9', 'important');
            this.style.setProperty('-webkit-text-fill-color', '#f1f5f9', 'important');
        });
        el.addEventListener('focus', function() {
            this.style.setProperty('border-color', '#38bdf8', 'important');
            this.style.setProperty('box-shadow', '0 0 0 3px rgba(56,189,248,0.15)', 'important');
        });
        el.addEventListener('blur', function() {
            this.style.setProperty('border-color', 'rgba(56,189,248,0.25)', 'important');
            this.style.setProperty('box-shadow', 'none', 'important');
        });
    });
    var buttons = doc.querySelectorAll('.stButton > button, button[kind]');
    buttons.forEach(function(el) {
        el.style.setProperty('color', '#ffffff', 'important');
        el.style.setProperty('background', 'linear-gradient(135deg,#38bdf8,#6366f1,#22c55e)', 'important');
        el.style.setProperty('border', 'none', 'important');
        el.style.setProperty('border-radius', '12px', 'important');
        el.style.setProperty('font-weight', '600', 'important');
        var children = el.querySelectorAll('*');
        children.forEach(function(child) { child.style.setProperty('color', '#ffffff', 'important'); });
    });
    var style = doc.getElementById('careerAI-placeholder-fix');
    if (!style) {
        style = doc.createElement('style');
        style.id = 'careerAI-placeholder-fix';
        style.textContent = [
            'input::placeholder, textarea::placeholder { color: #475569 !important; opacity: 1 !important; }',
            'input::-webkit-input-placeholder { color: #475569 !important; }',
            'input:-webkit-autofill, input:-webkit-autofill:hover, input:-webkit-autofill:focus {',
            '    -webkit-box-shadow: 0 0 0px 1000px #0d1929 inset !important;',
            '    -webkit-text-fill-color: #f1f5f9 !important;',
            '    caret-color: #38bdf8 !important;',
            '}'
        ].join('');
        doc.head.appendChild(style);
    }
}
applyStyles();
setTimeout(applyStyles, 300);
setTimeout(applyStyles, 800);
setTimeout(applyStyles, 1500);
var observer = new MutationObserver(function() { applyStyles(); });
observer.observe(window.parent.document.body, { childList: true, subtree: true });
</script>
""", height=0)

# ---------------- GLOBAL CSS ----------------
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
*, *::before, *::after { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"] {
    background-color: #050d1a !important;
    font-family: 'DM Sans', sans-serif;
    color: #e2e8f0;
}
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 80% 60% at 20% 10%, rgba(56,189,248,0.07) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 80% 80%, rgba(99,102,241,0.08) 0%, transparent 60%),
        radial-gradient(ellipse 40% 40% at 50% 50%, rgba(34,197,94,0.04) 0%, transparent 60%);
    pointer-events: none;
    z-index: 0;
}
[data-testid="stMain"] { position: relative; z-index: 1; }
section.main > div { padding-top: 2rem; padding-bottom: 4rem; }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
h1, h2, h3 { font-family: 'Syne', sans-serif !important; }
[data-testid="stSidebar"] {
    background: rgba(10, 20, 40, 0.95) !important;
    border-right: 1px solid rgba(56,189,248,0.1);
}
[data-testid="stProgress"] > div {
    background: rgba(255,255,255,0.06) !important;
    border-radius: 99px !important;
    height: 6px !important;
}
[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #38bdf8, #6366f1, #22c55e) !important;
    border-radius: 99px !important;
    box-shadow: 0 0 12px rgba(56,189,248,0.6) !important;
}
[data-testid="stRadio"] label {
    color: #94a3b8 !important;
    font-size: 0.9rem !important;
    padding: 6px 12px;
    border-radius: 8px;
    transition: color 0.2s;
}
[data-testid="stRadio"] label:hover { color: #38bdf8 !important; }
.stButton > button {
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 12px 28px !important;
    border-radius: 12px !important;
    border: none !important;
    cursor: pointer !important;
    background: linear-gradient(135deg, #38bdf8 0%, #6366f1 50%, #22c55e 100%) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 20px rgba(56,189,248,0.25) !important;
    transition: all 0.25s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(56,189,248,0.4) !important;
    filter: brightness(1.1);
}
.stButton > button > div > p,
.stButton > button p,
.stButton > button span { color: #ffffff !important; }
[data-testid="stDownloadButton"] button {
    background: linear-gradient(135deg, #1e3a5f, #1e293b) !important;
    border: 1px solid rgba(56,189,248,0.3) !important;
    color: #38bdf8 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    border-radius: 12px !important;
    padding: 12px 28px !important;
}
[data-testid="stDownloadButton"] button p,
[data-testid="stDownloadButton"] button span { color: #38bdf8 !important; }
div[data-baseweb="base-input"] { background-color: transparent !important; border: none !important; }
[data-testid="stTextInput"] div[data-baseweb="input"],
[data-testid="stTextArea"] div[data-baseweb="textarea"] {
    background-color: #0f172a !important;
    border: 1px solid rgba(56,189,248,0.25) !important;
    border-radius: 10px !important;
}
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background-color: transparent !important;
    color: #f1f5f9 !important;
    -webkit-text-fill-color: #f1f5f9 !important;
    caret-color: #38bdf8 !important;
}
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #050d1a; }
::-webkit-scrollbar-thumb { background: rgba(56,189,248,0.3); border-radius: 99px; }
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
defaults = {
    "logged_in": False,
    "step": 0,
    "scores": {},
    "ai_roadmap": "",
    "chat_history": [],
    "recommendations": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------- USER FILE ----------------
USER_FILE = "users.json"
if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f:
        json.dump({"admin": "1234"}, f)

def load_users():
    with open(USER_FILE) as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

# ---------------- LOGIN PAGE ----------------
def auth_page():
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;padding-top:60px;">
        <div style="text-align:center;margin-bottom:36px;">
            <div style="width:72px;height:72px;background:linear-gradient(135deg,#38bdf8,#6366f1);
                border-radius:20px;display:flex;align-items:center;justify-content:center;
                font-size:2rem;margin:0 auto 20px;box-shadow:0 8px 24px rgba(56,189,248,0.35);">🚀</div>
            <h1 style="font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;
                background:linear-gradient(90deg,#38bdf8,#a78bfa);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                margin-bottom:8px;">CareerAI</h1>
            <p style="color:#64748b;font-size:0.95rem;">Your intelligent career compass</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        menu = st.radio("", ["Login", "Register"], horizontal=True, label_visibility="collapsed")
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        users = load_users()
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if menu == "Login":
            if st.button("Sign In →", use_container_width=True):
                if username in users and users[username] == password:
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")
        else:
            if st.button("Create Account →", use_container_width=True):
                if username and password:
                    users[username] = password
                    save_users(users)
                    st.success("Account created! Please sign in.")
                else:
                    st.warning("Please fill in all fields.")

if not st.session_state.logged_in:
    auth_page()
    st.stop()

# ---------------- MODEL ----------------
model = joblib.load("career_model.pkl")

# ---------------- DATA ----------------
options = {
    "Strongly Disagree": 1,
    "Disagree": 2,
    "Neutral": 3,
    "Agree": 4,
    "Strongly Agree": 5
}

questions = {
    "Analytical": [
        "I enjoy solving complex problems",
        "I like logical reasoning",
        "I analyze before making decisions",
        "I enjoy mathematics and statistics",
        "I like structured, systematic thinking"
    ],
    "Technical": [
        "I enjoy working with technology",
        "I like coding and programming",
        "I enjoy understanding how machines work",
        "I like building and optimizing systems",
        "I enjoy tackling technical challenges"
    ],
    "Creative": [
        "I enjoy designing visuals or products",
        "I like artistic and expressive activities",
        "I enjoy brainstorming creative ideas",
        "I like thinking in visuals and concepts",
        "I enjoy innovation and original thinking"
    ],
    "Financial": [
        "I enjoy understanding financial markets",
        "I like budgeting and planning finances",
        "I enjoy business math and economics",
        "I manage money and resources well",
        "I enjoy analyzing investments and risk"
    ],
    "Social": [
        "I enjoy interacting with diverse people",
        "I thrive in collaborative team settings",
        "I like taking on leadership roles",
        "I enjoy mentoring and helping others",
        "I like presenting and public speaking"
    ]
}

categories = list(questions.keys())

CATEGORY_META = {
    "Analytical": {"icon": "🧠", "color": "#38bdf8", "desc": "Logic & Problem Solving"},
    "Technical":  {"icon": "⚙️", "color": "#6366f1", "desc": "Technology & Engineering"},
    "Creative":   {"icon": "🎨", "color": "#f472b6", "desc": "Design & Innovation"},
    "Financial":  {"icon": "📈", "color": "#22c55e", "desc": "Finance & Business"},
    "Social":     {"icon": "🤝", "color": "#fb923c", "desc": "Leadership & People"},
}

CAREER_META = {
    "Software Engineer":  {"icon": "💻", "color": "#38bdf8"},
    "Data Scientist":     {"icon": "📊", "color": "#6366f1"},
    "Designer":           {"icon": "🎨", "color": "#f472b6"},
    "Financial Analyst":  {"icon": "📈", "color": "#22c55e"},
    "Marketing Manager":  {"icon": "📣", "color": "#fb923c"},
    "Doctor":             {"icon": "🩺", "color": "#34d399"},
    "Teacher":            {"icon": "📚", "color": "#fbbf24"},
    "Lawyer":             {"icon": "⚖️", "color": "#a78bfa"},
    "Entrepreneur":       {"icon": "🚀", "color": "#f87171"},
    "HR Manager":         {"icon": "🤝", "color": "#67e8f9"},
}

def get_career_icon(career):
    for key, val in CAREER_META.items():
        if key.lower() in career.lower():
            return val["icon"], val["color"]
    return "🎯", "#38bdf8"

# ================================================================
# RECOMMENDATION SYSTEM
# ================================================================
def get_recommendations(career, scores):
    prompt = (
        "You are an expert career advisor and education consultant.\n\n"
        f"Career Target: {career}\n"
        f"User Skill Scores (out of 25): "
        f"Analytical={scores.get('Analytical',0)}, "
        f"Technical={scores.get('Technical',0)}, "
        f"Creative={scores.get('Creative',0)}, "
        f"Financial={scores.get('Financial',0)}, "
        f"Social={scores.get('Social',0)}\n\n"
        "Respond ONLY with a valid JSON object. No markdown, no backticks, no extra text.\n"
        "Use this exact structure:\n"
        "{\n"
        '  "top_courses": [\n'
        '    {"title":"<title>","platform":"<platform>","url":"<real url>","duration":"<e.g. 4 weeks>","level":"Beginner","why":"<one sentence>"},\n'
        '    {"title":"<title>","platform":"<platform>","url":"<real url>","duration":"<duration>","level":"Intermediate","why":"<one sentence>"},\n'
        '    {"title":"<title>","platform":"<platform>","url":"<real url>","duration":"<duration>","level":"Advanced","why":"<one sentence>"}\n'
        "  ],\n"
        '  "top_certifications": [\n'
        '    {"name":"<name>","issuer":"<issuer>","url":"<real url>","difficulty":"Entry","value":"<why it matters>"},\n'
        '    {"name":"<name>","issuer":"<issuer>","url":"<real url>","difficulty":"Associate","value":"<why it matters>"},\n'
        '    {"name":"<name>","issuer":"<issuer>","url":"<real url>","difficulty":"Professional","value":"<why it matters>"}\n'
        "  ],\n"
        '  "must_have_skills": [\n'
        '    {"skill":"<name>","category":"Technical","priority":"High","description":"<brief>"},\n'
        '    {"skill":"<name>","category":"Soft","priority":"High","description":"<brief>"},\n'
        '    {"skill":"<name>","category":"Domain","priority":"High","description":"<brief>"},\n'
        '    {"skill":"<name>","category":"Technical","priority":"Medium","description":"<brief>"},\n'
        '    {"skill":"<name>","category":"Soft","priority":"Medium","description":"<brief>"},\n'
        '    {"skill":"<name>","category":"Domain","priority":"Medium","description":"<brief>"}\n'
        "  ],\n"
        '  "salary_range": "<e.g. $70,000 - $130,000 per year>",\n'
        '  "job_market_outlook": "<1-2 sentences>",\n'
        '  "top_companies": ["<co1>","<co2>","<co3>","<co4>","<co5>"]\n'
        "}"
    )
    response = gemini_model.generate_content(prompt)
    raw = response.text.strip()
    raw = re.sub(r"```json|```", "", raw).strip()
    return json.loads(raw)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("""
    <div style="padding: 24px 8px 16px;">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:28px;">
            <div style="width:42px;height:42px;background:linear-gradient(135deg,#38bdf8,#6366f1);
                border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:1.3rem;">🚀</div>
            <div>
                <div style="font-family:'Syne',sans-serif;font-weight:800;font-size:1.1rem;
                    background:linear-gradient(90deg,#38bdf8,#a78bfa);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;">CareerAI</div>
                <div style="color:#475569;font-size:0.75rem;">Career Intelligence</div>
            </div>
        </div>
        <div style="color:#475569;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;
            font-weight:600;margin-bottom:12px;">Assessment Progress</div>
    </div>
    """, unsafe_allow_html=True)

    total_steps = len(categories)
    for i, cat in enumerate(categories):
        meta = CATEGORY_META[cat]
        is_done = i < st.session_state.step
        is_current = i == st.session_state.step and st.session_state.step < total_steps
        if is_done:
            r2, g2, b2 = (int(meta['color'].lstrip('#')[j:j+2], 16) for j in (0, 2, 4))
            bg = f"rgba({r2},{g2},{b2},0.15)"
            border = meta["color"]
            text_color = meta["color"]
            status = "✓"
        elif is_current:
            bg = "rgba(56,189,248,0.08)"
            border = "#38bdf8"
            text_color = "#e2e8f0"
            status = "→"
        else:
            bg = "transparent"
            border = "rgba(255,255,255,0.06)"
            text_color = "#475569"
            status = str(i + 1)

        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;padding:10px 12px;
            border-radius:10px;border:1px solid {border};background:{bg};margin-bottom:6px;">
            <div style="width:26px;height:26px;border-radius:8px;
                background:{'rgba(56,189,248,0.15)' if is_current else 'rgba(255,255,255,0.04)'};
                display:flex;align-items:center;justify-content:center;
                font-size:0.75rem;color:{text_color};font-weight:700;">{status}</div>
            <div style="font-size:1.1rem;">{meta['icon']}</div>
            <div>
                <div style="font-size:0.85rem;color:{text_color};font-weight:600;
                    font-family:'Syne',sans-serif;">{cat}</div>
                <div style="font-size:0.7rem;color:#475569;">{meta['desc']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    completed = min(st.session_state.step, total_steps)
    pct = int(completed / total_steps * 100)
    st.markdown(f"""
    <div style="margin-top:20px;padding:16px;background:rgba(255,255,255,0.03);
        border-radius:12px;border:1px solid rgba(255,255,255,0.06);">
        <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
            <span style="font-size:0.75rem;color:#64748b;">Completion</span>
            <span style="font-size:0.75rem;color:#38bdf8;font-weight:700;">{pct}%</span>
        </div>
        <div style="background:rgba(255,255,255,0.05);border-radius:99px;height:4px;">
            <div style="width:{pct}%;height:4px;border-radius:99px;
                background:linear-gradient(90deg,#38bdf8,#6366f1);
                box-shadow:0 0 8px rgba(56,189,248,0.5);"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ================================================================
# SCROLL TO TOP
# st.markdown re-executes every rerun. Embedding the step value
# in the script text ensures the browser sees new content and runs
# it again (avoids iframe caching). No 'key' arg needed.
# ================================================================
# SCROLL TO TOP - NUCLEAR OPTION
# ================================================================
components.html(
    f"""
    <script>
    (function(){{
        // This variable change is what forces Streamlit to re-run the iframe
        var _step = {st.session_state.step}; 

        function obliterateScroll() {{
            try {{
                var p = window.parent;
                if (!p) return;
                
                // 1. Force the main window itself to the top
                p.scrollTo(0, 0);
                
                // 2. Recursively find EVERY element on the page and force its scroll to 0
                function resetAllScrolls(el) {{
                    if (el && el.scrollTop > 0) {{
                        el.scrollTop = 0;
                    }}
                    if (el && el.children) {{
                        for (var i = 0; i < el.children.length; i++) {{
                            resetAllScrolls(el.children[i]);
                        }}
                    }}
                }}
                resetAllScrolls(p.document.body);
                
                // 3. Fallback: Force the entire App view to align top instantly
                var topBlock = p.document.querySelector('.stApp');
                if (topBlock) {{
                    topBlock.scrollIntoView(true);
                }}
            }} catch(e) {{
                console.error("Scroll to top failed:", e);
            }}
        }}

        // Run aggressively over 1.5 seconds to outlast React's layout updates
        obliterateScroll();
        for (let i = 1; i <= 15; i++) {{
            setTimeout(obliterateScroll, i * 100);
        }}
    }})();
    </script>
    """,
    height=0,
)



# ---------------- HEADER ----------------
st.markdown("""
<div style="display:flex;align-items:center;justify-content:space-between;
    padding:0 0 32px 0;border-bottom:1px solid rgba(255,255,255,0.06);margin-bottom:36px;">
    <div>
        <h1 style="font-family:'Syne',sans-serif;font-size:2.4rem;font-weight:800;
            background:linear-gradient(90deg,#e2e8f0 0%,#38bdf8 50%,#a78bfa 100%);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            line-height:1.1;margin-bottom:6px;">AI Career Intelligence</h1>
        <p style="color:#64748b;font-size:0.95rem;margin:0;">
            Discover your ideal career path through AI-powered psychometric analysis
        </p>
    </div>
    <div style="padding:8px 16px;background:rgba(56,189,248,0.08);
        border:1px solid rgba(56,189,248,0.2);border-radius:20px;
        font-size:0.8rem;color:#38bdf8;font-weight:600;">
        🟢 AI Online
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------- PROGRESS BAR ----------------
progress_val = st.session_state.step / len(categories)
st.progress(progress_val)
st.markdown(f"""
<div style="display:flex;justify-content:space-between;margin-top:6px;margin-bottom:32px;">
    <span style="font-size:0.75rem;color:#475569;">
        Step {min(st.session_state.step + 1, len(categories))} of {len(categories)}
    </span>
    <span style="font-size:0.75rem;color:#38bdf8;font-weight:600;">
        {int(progress_val * 100)}% Complete
    </span>
</div>
""", unsafe_allow_html=True)

# ================================================================
# QUESTIONNAIRE
# ================================================================
if st.session_state.step < len(categories):
    cat = categories[st.session_state.step]
    meta = CATEGORY_META[cat]
    color = meta["color"]
    r, g, b = (int(color.lstrip('#')[j:j+2], 16) for j in (0, 2, 4))

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba({r},{g},{b},0.12),rgba(0,0,0,0));
        border:1px solid rgba({r},{g},{b},0.2);border-radius:20px;
        padding:28px 32px;margin-bottom:28px;position:relative;overflow:hidden;">
        <div style="position:absolute;right:24px;top:50%;transform:translateY(-50%);
            font-size:5rem;opacity:0.07;filter:blur(2px);">{meta['icon']}</div>
        <div style="display:flex;align-items:center;gap:16px;">
            <div style="width:56px;height:56px;border-radius:16px;
                background:linear-gradient(135deg,{color}22,{color}44);
                border:1px solid {color}44;
                display:flex;align-items:center;justify-content:center;font-size:1.8rem;">
                {meta['icon']}</div>
            <div>
                <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.12em;
                    color:{color};font-weight:700;margin-bottom:4px;">
                    Category {st.session_state.step + 1}</div>
                <h2 style="font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:800;
                    color:#f1f5f9;margin:0;">{cat} Skills</h2>
                <p style="color:#64748b;font-size:0.85rem;margin-top:3px;">{meta['desc']}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    total = 0
    for idx, q in enumerate(questions[cat]):
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.07);
            border-left:3px solid {color};border-radius:14px;
            padding:20px 24px 12px;margin-bottom:6px;">
            <div style="display:flex;align-items:flex-start;gap:12px;">
                <div style="width:28px;height:28px;min-width:28px;
                    background:rgba({r},{g},{b},0.15);border-radius:8px;
                    display:flex;align-items:center;justify-content:center;
                    font-size:0.7rem;font-weight:700;color:{color};margin-top:1px;">Q{idx+1}</div>
                <p style="color:#cbd5e1;font-size:0.95rem;line-height:1.5;margin:0;">{q}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        ans = st.radio("", list(options.keys()), key=f"{cat}_{q}", horizontal=True, label_visibility="collapsed")
        total += options[ans]
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    st.session_state.scores[cat] = total
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.session_state.step > 0:
            if st.button("← Previous", use_container_width=True):
                st.session_state.step -= 1
                st.rerun()
    with col3:
        if st.session_state.step < len(categories) - 1:
            if st.button("Next →", use_container_width=True):
                st.session_state.step += 1
                st.rerun()
        else:
            if st.button("🚀 Analyse My Career", use_container_width=True):
                st.session_state.step += 1
                st.rerun()

# ================================================================
# RESULTS
# ================================================================
else:
    scores = st.session_state.scores
    input_data = [[scores[k] for k in categories]]
    probs = model.predict_proba(input_data)[0]
    confidence = dict(zip(model.classes_, probs * 100))
    sorted_scores = sorted(confidence.items(), key=lambda x: x[1], reverse=True)
    top_career = sorted_scores[0][0]

    # ---- Hero ----
    st.markdown("""
    <div style="text-align:center;padding:20px 0 40px;">
        <div style="display:inline-block;padding:6px 18px;
            background:rgba(34,197,94,0.1);border:1px solid rgba(34,197,94,0.3);
            border-radius:20px;font-size:0.8rem;color:#22c55e;font-weight:600;
            margin-bottom:16px;">✦ Analysis Complete</div>
        <h1 style="font-family:'Syne',sans-serif;font-size:2.8rem;font-weight:800;
            background:linear-gradient(90deg,#f1f5f9,#38bdf8,#a78bfa);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            margin-bottom:12px;">Your Career Blueprint</h1>
        <p style="color:#64748b;font-size:1rem;max-width:500px;margin:0 auto;">
            Based on your responses, our AI has identified your top career matches
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ---- Top 3 medals ----
    medals = ["🥇", "🥈", "🥉"]
    medal_labels = ["Best Match", "Strong Match", "Good Match"]
    medal_colors = ["#fbbf24", "#94a3b8", "#fb923c"]

    st.markdown("<h3 style='font-family:Syne,sans-serif;color:#94a3b8;font-size:0.8rem;"
                "text-transform:uppercase;letter-spacing:0.1em;margin-bottom:16px;'>"
                "🏆 Top Career Matches</h3>", unsafe_allow_html=True)

    cols = st.columns(3)
    for i, (career, score) in enumerate(sorted_scores[:3]):
        icon, color = get_career_icon(career)
        with cols[i]:
            st.markdown(f"""
            <div style="background:linear-gradient(160deg,rgba(255,255,255,0.04),rgba(0,0,0,0.2));
                border:1px solid rgba(255,255,255,0.08);border-top:2px solid {medal_colors[i]};
                border-radius:20px;padding:28px 20px 24px;text-align:center;
                position:relative;overflow:hidden;">
                <div style="position:absolute;top:-20px;right:-20px;font-size:6rem;opacity:0.04;">{icon}</div>
                <div style="font-size:2.2rem;margin-bottom:8px;">{medals[i]}</div>
                <div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;
                    color:{medal_colors[i]};font-weight:700;margin-bottom:10px;">{medal_labels[i]}</div>
                <div style="font-size:1.5rem;margin-bottom:10px;">{icon}</div>
                <h3 style="font-family:'Syne',sans-serif;font-size:1.05rem;font-weight:700;
                    color:#f1f5f9;margin-bottom:12px;">{career}</h3>
                <div style="background:rgba(255,255,255,0.05);border-radius:99px;height:6px;margin-bottom:8px;">
                    <div style="width:{min(score,100):.1f}%;height:6px;border-radius:99px;
                        background:linear-gradient(90deg,{color},{medal_colors[i]});
                        box-shadow:0 0 8px {color}66;"></div>
                </div>
                <div style="font-size:1.4rem;font-weight:800;color:{medal_colors[i]};
                    font-family:'Syne',sans-serif;">{score:.1f}%</div>
                <div style="font-size:0.72rem;color:#475569;">compatibility</div>
            </div>
            """, unsafe_allow_html=True)

    # ---- Charts ----
    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-family:Syne,sans-serif;color:#94a3b8;font-size:0.8rem;"
                "text-transform:uppercase;letter-spacing:0.1em;margin-bottom:16px;'>"
                "📊 Your Skill Profile</h3>", unsafe_allow_html=True)

    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        vals = [scores[k] for k in categories]
        N = len(categories)
        angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
        vals_plot = vals + [vals[0]]
        angles += angles[:1]
        cat_labels = [f"{CATEGORY_META[c]['icon']} {c}" for c in categories]

        fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
        fig.patch.set_facecolor('#0d1929')
        ax.set_facecolor('#0d1929')
        ax.fill(angles, vals_plot, alpha=0.18, color='#38bdf8')
        ax.plot(angles, vals_plot, color='#38bdf8', linewidth=2.5)
        for angle, val in zip(angles[:-1], vals):
            ax.plot(angle, val, 'o', color='#38bdf8', markersize=7,
                    markerfacecolor='#38bdf8', markeredgecolor='#0d1929', markeredgewidth=2)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(cat_labels, color='#94a3b8', fontsize=9)
        ax.set_yticks([5, 10, 15, 20, 25])
        ax.set_yticklabels(["5", "10", "15", "20", "25"], color='#334155', fontsize=7)
        ax.set_ylim(0, 25)
        ax.grid(color='#1e3a5f', linestyle='--', linewidth=0.8, alpha=0.6)
        ax.spines['polar'].set_color('#1e3a5f')
        fig.tight_layout(pad=1.5)
        st.pyplot(fig)
        plt.close()

    with col_chart2:
        fig2, ax2 = plt.subplots(figsize=(5, 4))
        fig2.patch.set_facecolor('#0d1929')
        ax2.set_facecolor('#0d1929')
        bar_colors = ['#38bdf8', '#6366f1', '#f472b6', '#22c55e', '#fb923c']
        bar_labels = [f"{CATEGORY_META[c]['icon']} {c}" for c in categories]
        bar_vals = [scores[k] for k in categories]
        bars = ax2.barh(bar_labels, bar_vals, color=bar_colors, height=0.55, edgecolor='none')
        for bar, val in zip(bars, bar_vals):
            ax2.text(val + 0.2, bar.get_y() + bar.get_height() / 2,
                     f'{val}/25', va='center', ha='left', color='#64748b', fontsize=9)
        ax2.set_xlim(0, 28)
        ax2.set_xlabel("Score", color='#475569', fontsize=9)
        ax2.tick_params(colors='#94a3b8', labelsize=9)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['bottom'].set_color('#1e3a5f')
        ax2.spines['left'].set_color('#1e3a5f')
        ax2.xaxis.label.set_color('#475569')
        fig2.tight_layout()
        st.pyplot(fig2)
        plt.close()

    # ---- Full compatibility list ----
    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-family:Syne,sans-serif;color:#94a3b8;font-size:0.8rem;"
                "text-transform:uppercase;letter-spacing:0.1em;margin-bottom:16px;'>"
                "📋 Full Career Compatibility</h3>", unsafe_allow_html=True)

    for career, score in sorted_scores:
        icon, color = get_career_icon(career)
        r2, g2, b2 = (int(color.lstrip('#')[j:j+2], 16) for j in (0, 2, 4))
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:16px;padding:14px 20px;
            background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);
            border-radius:12px;margin-bottom:8px;">
            <div style="font-size:1.5rem;min-width:32px;text-align:center;">{icon}</div>
            <div style="flex:1;">
                <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                    <span style="font-weight:600;font-size:0.9rem;color:#e2e8f0;">{career}</span>
                    <span style="font-size:0.85rem;color:{color};font-weight:700;">{score:.1f}%</span>
                </div>
                <div style="background:rgba(255,255,255,0.05);border-radius:99px;height:4px;">
                    <div style="width:{min(score,100):.1f}%;height:4px;border-radius:99px;
                        background:linear-gradient(90deg,rgba({r2},{g2},{b2},0.6),{color});"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ================================================================
    # RECOMMENDATION SYSTEM
    # ================================================================
    st.markdown("<div style='height:48px'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
        <div style="width:36px;height:36px;background:linear-gradient(135deg,#22c55e,#38bdf8);
            border-radius:10px;display:flex;align-items:center;justify-content:center;">🎯</div>
        <div>
            <h3 style="font-family:'Syne',sans-serif;font-size:1.1rem;color:#f1f5f9;margin:0;">Smart Recommendation Engine</h3>
            <p style="color:#475569;font-size:0.8rem;margin:0;">AI-curated courses, certifications &amp; skills for
                <strong style="color:#22c55e;">{top_career}</strong></p>
        </div>
    </div>
    <div style="background:rgba(34,197,94,0.04);border:1px solid rgba(34,197,94,0.15);
        border-radius:16px;padding:20px 24px;margin-bottom:20px;">
        <p style="color:#94a3b8;font-size:0.88rem;line-height:1.6;margin:0;">
            Get personalised course links, top certifications, and must-have skills based on
            your psychometric scores. Tailored specifically for
            <strong style="color:#22c55e;">{top_career}</strong>.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_rec1, col_rec2 = st.columns([1, 3])
    with col_rec1:
        gen_recs = st.button("🎯 Get Recommendations", use_container_width=True)

    if gen_recs:
        with st.spinner("Building your personalised recommendations..."):
            try:
                recs = get_recommendations(top_career, scores)
                st.session_state.recommendations = recs
            except Exception as e:
                st.error(f"Recommendation engine failed: {e}")

    if st.session_state.recommendations:
        recs = st.session_state.recommendations

        # Market overview
        salary = recs.get("salary_range", "N/A")
        outlook = recs.get("job_market_outlook", "")
        companies = recs.get("top_companies", [])
        company_tags = "".join([
            f'<span style="background:rgba(167,139,250,0.1);border:1px solid rgba(167,139,250,0.2);'
            f'color:#a78bfa;padding:4px 12px;border-radius:20px;font-size:0.8rem;font-weight:600;">{c}</span>'
            for c in companies
        ])

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,rgba(34,197,94,0.08),rgba(56,189,248,0.05));
            border:1px solid rgba(34,197,94,0.2);border-radius:16px;padding:24px;margin-bottom:28px;">
            <div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap;">
                <div style="flex:1;min-width:200px;">
                    <div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;
                        color:#22c55e;font-weight:700;margin-bottom:4px;">💰 Salary Range</div>
                    <div style="font-size:1.3rem;font-weight:800;color:#f1f5f9;
                        font-family:'Syne',sans-serif;">{salary}</div>
                </div>
                <div style="flex:2;min-width:280px;">
                    <div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;
                        color:#38bdf8;font-weight:700;margin-bottom:4px;">📈 Market Outlook</div>
                    <div style="font-size:0.88rem;color:#94a3b8;line-height:1.5;">{outlook}</div>
                </div>
            </div>
            <div style="margin-top:16px;padding-top:16px;border-top:1px solid rgba(255,255,255,0.06);">
                <div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;
                    color:#a78bfa;font-weight:700;margin-bottom:8px;">🏢 Top Hiring Companies</div>
                <div style="display:flex;flex-wrap:wrap;gap:8px;">{company_tags}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Top 3 Courses
        st.markdown("<h3 style='font-family:Syne,sans-serif;color:#94a3b8;font-size:0.8rem;"
                    "text-transform:uppercase;letter-spacing:0.1em;margin-bottom:16px;'>"
                    "📚 Top 3 Recommended Courses</h3>", unsafe_allow_html=True)

        course_colors = ["#38bdf8", "#6366f1", "#f472b6"]
        course_nums = ["01", "02", "03"]
        level_colors = {"Beginner": "#22c55e", "Intermediate": "#fbbf24", "Advanced": "#f87171"}

        for i, course in enumerate(recs.get("top_courses", [])[:3]):
            cc = course_colors[i]
            r3, g3, b3 = (int(cc.lstrip('#')[j:j+2], 16) for j in (0, 2, 4))
            lvl_color = level_colors.get(course.get("level", ""), "#94a3b8")
            url = course.get("url", "#")
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.025);
                border:1px solid rgba({r3},{g3},{b3},0.2);border-left:3px solid {cc};
                border-radius:16px;padding:22px 24px;margin-bottom:12px;
                position:relative;overflow:hidden;">
                <div style="position:absolute;right:20px;top:50%;transform:translateY(-50%);
                    font-size:4rem;opacity:0.06;font-family:'Syne',sans-serif;
                    font-weight:800;color:{cc};">{course_nums[i]}</div>
                <div style="flex:1;">
                    <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:6px;">
                        <span style="background:rgba({r3},{g3},{b3},0.15);color:{cc};
                            font-size:0.72rem;font-weight:700;padding:3px 10px;border-radius:20px;
                            border:1px solid rgba({r3},{g3},{b3},0.3);">
                            {course.get('platform', '—')}
                        </span>
                        <span style="background:rgba(255,255,255,0.04);color:{lvl_color};
                            font-size:0.72rem;font-weight:600;padding:3px 10px;border-radius:20px;
                            border:1px solid rgba(255,255,255,0.08);">
                            {course.get('level', '—')}
                        </span>
                        <span style="color:#475569;font-size:0.75rem;">⏱ {course.get('duration', '—')}</span>
                    </div>
                    <h4 style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;
                        color:#f1f5f9;margin:0 0 6px;">{course.get('title', '—')}</h4>
                    <p style="color:#64748b;font-size:0.85rem;margin:0 0 12px;line-height:1.5;">
                        {course.get('why', '')}</p>
                    <a href="{url}" target="_blank"
                        style="display:inline-flex;align-items:center;gap:6px;
                        background:linear-gradient(135deg,rgba({r3},{g3},{b3},0.15),rgba({r3},{g3},{b3},0.05));
                        border:1px solid rgba({r3},{g3},{b3},0.3);
                        color:{cc};text-decoration:none;padding:8px 18px;
                        border-radius:10px;font-size:0.82rem;font-weight:600;
                        font-family:'Syne',sans-serif;">
                        🔗 View Course →
                    </a>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Top 3 Certifications
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        st.markdown("<h3 style='font-family:Syne,sans-serif;color:#94a3b8;font-size:0.8rem;"
                    "text-transform:uppercase;letter-spacing:0.1em;margin-bottom:16px;'>"
                    "🏅 Top Certifications to Earn</h3>", unsafe_allow_html=True)

        cert_colors = ["#fbbf24", "#fb923c", "#34d399"]
        diff_colors = {"Entry": "#22c55e", "Associate": "#38bdf8", "Professional": "#a78bfa", "Expert": "#f87171"}

        cert_cols = st.columns(3)
        for i, cert in enumerate(recs.get("top_certifications", [])[:3]):
            cc = cert_colors[i]
            dc = diff_colors.get(cert.get("difficulty", ""), "#64748b")
            cert_url = cert.get("url", "#")
            with cert_cols[i]:
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.08);
                    border-top:2px solid {cc};border-radius:16px;padding:22px 18px;
                    display:flex;flex-direction:column;min-height:260px;">
                    <div style="font-size:1.8rem;margin-bottom:8px;">🏅</div>
                    <div style="margin-bottom:10px;">
                        <span style="background:rgba(255,255,255,0.06);color:{dc};
                            font-size:0.68rem;font-weight:700;padding:2px 8px;border-radius:20px;">
                            {cert.get('difficulty', '—')}
                        </span>
                    </div>
                    <h4 style="font-family:'Syne',sans-serif;font-size:0.95rem;font-weight:700;
                        color:#f1f5f9;margin:0 0 4px;">{cert.get('name', '—')}</h4>
                    <div style="font-size:0.78rem;color:{cc};font-weight:600;margin-bottom:10px;">
                        by {cert.get('issuer', '—')}
                    </div>
                    <p style="color:#64748b;font-size:0.82rem;line-height:1.5;
                        flex:1;margin:0 0 14px;">{cert.get('value', '')}</p>
                    <a href="{cert_url}" target="_blank"
                        style="display:block;text-align:center;
                        background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);
                        color:#94a3b8;text-decoration:none;padding:8px;
                        border-radius:8px;font-size:0.8rem;font-weight:600;">
                        View Certification →
                    </a>
                </div>
                """, unsafe_allow_html=True)

        # Must-Have Skills
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        st.markdown("<h3 style='font-family:Syne,sans-serif;color:#94a3b8;font-size:0.8rem;"
                    "text-transform:uppercase;letter-spacing:0.1em;margin-bottom:16px;'>"
                    "⚡ Must-Have Skills</h3>", unsafe_allow_html=True)

        skill_cat_colors = {
            "Technical": ("#38bdf8", "rgba(56,189,248,0.08)", "rgba(56,189,248,0.18)"),
            "Soft":      ("#f472b6", "rgba(244,114,182,0.08)", "rgba(244,114,182,0.18)"),
            "Domain":    ("#22c55e", "rgba(34,197,94,0.08)", "rgba(34,197,94,0.18)"),
        }
        priority_icon = {"High": "🔴", "Medium": "🟡"}

        skill_list = recs.get("must_have_skills", [])
        for j in range(0, len(skill_list), 2):
            row_skills = skill_list[j:j+2]
            sk_cols = st.columns(len(row_skills))
            for ci, skill in enumerate(row_skills):
                sc = skill.get("category", "Technical")
                tc, bg, border = skill_cat_colors.get(
                    sc, ("#94a3b8", "rgba(255,255,255,0.05)", "rgba(255,255,255,0.1)")
                )
                picon = priority_icon.get(skill.get("priority", "Medium"), "🟡")
                with sk_cols[ci]:
                    st.markdown(f"""
                    <div style="background:{bg};border:1px solid {border};
                        border-radius:12px;padding:16px 18px;margin-bottom:10px;">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                            <span style="font-size:0.72rem;color:{tc};font-weight:700;
                                text-transform:uppercase;letter-spacing:0.06em;">{sc}</span>
                            <span style="font-size:0.75rem;">{picon} {skill.get('priority','Medium')}</span>
                        </div>
                        <div style="font-family:'Syne',sans-serif;font-weight:700;
                            color:#f1f5f9;font-size:0.95rem;margin-bottom:4px;">{skill.get('skill','—')}</div>
                        <div style="color:#64748b;font-size:0.8rem;line-height:1.4;">{skill.get('description','')}</div>
                    </div>
                    """, unsafe_allow_html=True)

    # ================================================================
    # AI ROADMAP
    # ================================================================
    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;">
        <div style="width:36px;height:36px;background:linear-gradient(135deg,#38bdf8,#6366f1);
            border-radius:10px;display:flex;align-items:center;justify-content:center;">🧭</div>
        <div>
            <h3 style="font-family:'Syne',sans-serif;font-size:1.1rem;color:#f1f5f9;margin:0;">AI Skill Roadmap</h3>
            <p style="color:#475569;font-size:0.8rem;margin:0;">Personalised learning path for your top career</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("✦ Generate My Roadmap"):
        with st.spinner("Crafting your personalised roadmap..."):
            response = gemini_model.generate_content(
                f"Create a detailed, structured career roadmap for becoming a {top_career}. "
                f"Include: key skills to learn, recommended resources, timeline milestones, and certifications."
            )
            st.session_state.ai_roadmap = response.text

    if st.session_state.ai_roadmap:
        st.markdown(f"""
        <div style="background:rgba(56,189,248,0.04);border:1px solid rgba(56,189,248,0.15);
            border-radius:16px;padding:28px;margin-top:12px;line-height:1.8;
            color:#cbd5e1;font-size:0.92rem;">
            {st.session_state.ai_roadmap.replace(chr(10), '<br>')}
        </div>
        """, unsafe_allow_html=True)

    # ================================================================
    # AI CAREER COUNSELOR CHATBOT
    # ================================================================
    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;">
        <div style="width:36px;height:36px;background:linear-gradient(135deg,#6366f1,#f472b6);
            border-radius:10px;display:flex;align-items:center;justify-content:center;">🤖</div>
        <div>
            <h3 style="font-family:'Syne',sans-serif;font-size:1.1rem;color:#f1f5f9;margin:0;">AI Career Counselor</h3>
            <p style="color:#475569;font-size:0.8rem;margin:0;">Ask anything about your career path</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    for role, msg in st.session_state.chat_history:
        is_user = role == "You"
        align = "flex-end" if is_user else "flex-start"
        bg = "rgba(56,189,248,0.12)" if is_user else "rgba(255,255,255,0.04)"
        border = "rgba(56,189,248,0.25)" if is_user else "rgba(255,255,255,0.08)"
        avatar = "👤" if is_user else "🤖"
        st.markdown(f"""
        <div style="display:flex;justify-content:{align};margin-bottom:12px;">
            <div style="max-width:75%;background:{bg};border:1px solid {border};
                border-radius:16px;padding:14px 18px;font-size:0.9rem;color:#cbd5e1;line-height:1.6;">
                <span style="font-size:0.75rem;font-weight:700;color:#64748b;
                    display:block;margin-bottom:6px;">{avatar} {role}</span>
                {msg}
            </div>
        </div>
        """, unsafe_allow_html=True)

    user_question = st.text_input(
        "",
        placeholder="Ask about salaries, skills, companies, study paths...",
        label_visibility="collapsed",
        key="chat_input"
    )

    if st.button("Send Message →"):
        if user_question:
            with st.spinner("Thinking..."):
                response = gemini_model.generate_content(
                    f"You are a professional career counselor. Answer concisely and helpfully: {user_question}"
                )
            st.session_state.chat_history.append(("You", user_question))
            st.session_state.chat_history.append(("AI Counselor", response.text))
            st.rerun()

    # ================================================================
    # PDF REPORT + ACTIONS
    # ================================================================
    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
    st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.06);margin-bottom:28px;'>",
                unsafe_allow_html=True)

    def generate_pdf():
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("CareerAI — Your Personal Career Report", styles["Title"]))
        elements.append(Spacer(1, 20))

        elements.append(Paragraph("Top Career Matches:", styles["Heading2"]))
        elements.append(ListFlowable([
            ListItem(Paragraph(f"{c} — {s:.2f}% match", styles["Normal"]))
            for c, s in sorted_scores[:3]
        ]))
        elements.append(Spacer(1, 20))

        if st.session_state.recommendations:
            recs_pdf = st.session_state.recommendations

            elements.append(Paragraph("Recommended Courses:", styles["Heading2"]))
            elements.append(ListFlowable([
                ListItem(Paragraph(
                    f"{course.get('title','')} — {course.get('platform','')} "
                    f"({course.get('level','')}): {course.get('url','')}",
                    styles["Normal"]
                ))
                for course in recs_pdf.get("top_courses", [])
            ]))
            elements.append(Spacer(1, 12))

            elements.append(Paragraph("Top Certifications:", styles["Heading2"]))
            elements.append(ListFlowable([
                ListItem(Paragraph(
                    f"{cert.get('name','')} by {cert.get('issuer','')} "
                    f"[{cert.get('difficulty','')}]: {cert.get('url','')}",
                    styles["Normal"]
                ))
                for cert in recs_pdf.get("top_certifications", [])
            ]))
            elements.append(Spacer(1, 12))

            elements.append(Paragraph("Must-Have Skills:", styles["Heading2"]))
            elements.append(ListFlowable([
                ListItem(Paragraph(
                    f"{skill.get('skill','')} ({skill.get('category','')}, "
                    f"{skill.get('priority','')} priority): {skill.get('description','')}",
                    styles["Normal"]
                ))
                for skill in recs_pdf.get("must_have_skills", [])
            ]))
            elements.append(Spacer(1, 20))

        if st.session_state.ai_roadmap:
            elements.append(Paragraph("Your Personalised Roadmap:", styles["Heading2"]))
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(st.session_state.ai_roadmap, styles["Normal"]))

        doc.build(elements)
        buffer.seek(0)
        return buffer

    col_a, col_b = st.columns(2)
    with col_a:
        st.download_button(
            "📄 Download Full Report",
            data=generate_pdf(),
            file_name="career_report.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    with col_b:
        if st.button("🔄 Retake Assessment", use_container_width=True):
            st.session_state.step = 0
            st.session_state.scores = {}
            st.session_state.ai_roadmap = ""
            st.session_state.chat_history = []
            st.session_state.recommendations = None
            st.rerun()
