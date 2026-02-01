import streamlit as st
import requests

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(
    page_title="RAG AI Assistant",
    page_icon="🤖",
    layout="wide"
)

API_URL = "http://localhost:8000"

# =============================
# SESSION STATE
# =============================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# =============================
# THEME SWITCH
# =============================
def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"

# =============================
# CSS THEMES
# =============================
DARK_THEME = """
<style>
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    font-family: 'Segoe UI', sans-serif;
}
h1, h2, h3 { color: #ffffff; }
.glass {
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(14px);
    border-radius: 22px;
    padding: 25px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.4);
    margin-bottom: 20px;
}
.user-msg {
    background: linear-gradient(135deg, #11998e, #38ef7d);
    padding: 14px;
    border-radius: 18px 18px 0 18px;
    color: black;
    margin: 10px 0;
}
.bot-msg {
    background: linear-gradient(135deg, #8e2de2, #4a00e0);
    padding: 14px;
    border-radius: 18px 18px 18px 0;
    color: white;
    margin: 10px 0;
}
button {
    background: linear-gradient(135deg, #00c6ff, #0072ff) !important;
    color: white !important;
    border-radius: 30px !important;
}
</style>
"""

LIGHT_THEME = """
<style>
.stApp {
    background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
    font-family: 'Segoe UI', sans-serif;
}
h1, h2, h3 { color: #111; }
.glass {
    background: rgba(255, 255, 255, 0.9);
    border-radius: 22px;
    padding: 25px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    margin-bottom: 20px;
}
.user-msg {
    background: #daf5e4;
    padding: 14px;
    border-radius: 18px 18px 0 18px;
    color: black;
    margin: 10px 0;
}
.bot-msg {
    background: #e6e8ff;
    padding: 14px;
    border-radius: 18px 18px 18px 0;
    color: black;
    margin: 10px 0;
}
button {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important;
    border-radius: 30px !important;
}
</style>
"""

st.markdown(DARK_THEME if st.session_state.theme == "dark" else LIGHT_THEME, unsafe_allow_html=True)

# =============================
# HEADER + SWITCH BUTTON
# =============================
header_col, switch_col = st.columns([6, 1])

with header_col:
    st.markdown("<h1>🤖 RAG AI Assistant</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='opacity:0.8;'>Assistant intelligent basé sur vos documents PDF</p>",
        unsafe_allow_html=True
    )

with switch_col:
    st.button(
        "🌙 Dark" if st.session_state.theme == "light" else "☀️ Light",
        on_click=toggle_theme
    )

# =============================
# MAIN LAYOUT
# =============================
left, right = st.columns([1, 2])

# =============================
# UPLOAD
# =============================
with left:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### 📄 Upload PDF")

    uploaded_file = st.file_uploader("Choisir un PDF", type=["pdf"])
    if uploaded_file:
        try:
            res = requests.post(f"{API_URL}/upload", files={"file": uploaded_file}, timeout=30)
            if res.status_code == 200:
                st.success("✅ PDF chargé")
            else:
                st.error("❌ Erreur upload")
        except:
            st.error("⚠️ Backend indisponible")

    st.markdown("</div>", unsafe_allow_html=True)

# =============================
# CHAT
# =============================
with right:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### 💬 Chat")

    for msg in st.session_state.messages:
        css = "user-msg" if msg["role"] == "user" else "bot-msg"
        st.markdown(f"<div class='{css}'>{msg['content']}</div>", unsafe_allow_html=True)

    question = st.text_input("Pose ta question…")

    if st.button("🚀 Envoyer"):
        if question.strip():
            st.session_state.messages.append({"role": "user", "content": question})
            try:
                r = requests.post(f"{API_URL}/ask", json={"question": question}, timeout=60)
                answer = r.json().get("answer", "Pas de réponse") if r.status_code == 200 else "Erreur serveur"
            except:
                answer = "⚠️ Backend indisponible"

            st.session_state.messages.append({"role": "bot", "content": answer})
            st.experimental_rerun()

    st.markdown("</div>", unsafe_allow_html=True)
