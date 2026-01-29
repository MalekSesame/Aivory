import streamlit as st
import os

# ---------------- CONFIGURATION PAGE ----------------
st.set_page_config(
    page_title="Mon Chatbot",
    page_icon="🤖",
    layout="centered"
)

# ---------------- LOGO ----------------
image_path = "logo.png"
if os.path.exists(image_path):
    col1, col2, col3 = st.columns([1.5, 1, 1.5])
    with col2:
        st.image(image_path, width=200)
else:
    st.warning(f"Image non trouvée: {image_path}")

# Phrase d'accueil
st.markdown("<h3 style='text-align: center; color: #666;'>Comment puis-je vous aider ?</h3>", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'show_file_uploader' not in st.session_state:
    st.session_state.show_file_uploader = False
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""

# ---------------- STYLE CSS (Style WhatsApp) ----------------
st.markdown("""
<style>
/* Boutons bleus */
.stButton > button {
    background-color: #1d4ed8 !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 20px !important;
    font-size: 18px !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    min-height: 50px !important;
}
.stButton > button:hover {
    background-color: #1e40af !important;
    transform: translateY(-2px) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
    background-color: #1e3a8a !important;
}

/* File uploader */
div[data-testid="stFileUploader"] > section > button {
    background-color: #1d4ed8 !important;
    color: white !important;
    border-radius: 10px !important;
    padding: 10px 20px !important;
}

/* Text input */
.stTextInput > div > div > input {
    border-radius: 10px;
    border: 2px solid #e5e7eb;
    padding: 12px;
    font-size: 16px;
}
.stTextInput > div > div > input:focus {
    border-color: #1d4ed8;
    box-shadow: 0 0 0 3px rgba(29, 78, 216, 0.1);
}

/* Conteneur principal du chat */
.chat-container {
    max-height: 500px;
    overflow-y: auto;
    padding: 10px;
    background-color: #f0f2f5;
    border-radius: 10px;
    background-image: url('https://user-images.githubusercontent.com/15075759/28719144-86dc0f70-73b1-11e7-911d-60d70fcded21.png');
    background-size: cover;
}

/* Style des bulles WhatsApp */
.message-bubble {
    max-width: 70%;
    margin: 8px 0;
    padding: 10px 14px;
    border-radius: 18px;
    position: relative;
    font-size: 15px;
    line-height: 1.4;
    word-wrap: break-word;
}

/* Messages utilisateur (droite) */
.user-message {
    background-color: #dcf8c6;
    margin-left: auto;
    border-bottom-right-radius: 4px;
    color: #000;
    text-align: left;
}

/* Messages bot (gauche) */
.bot-message {
    background-color: white;
    margin-right: auto;
    border-bottom-left-radius: 4px;
    color: #000;
    text-align: left;
    box-shadow: 0 1px 0.5px rgba(0, 0, 0, 0.13);
}

/* Heure des messages */
.message-time {
    font-size: 11px;
    color: #666;
    margin-top: 4px;
    text-align: right;
}

/* Supprime la flèche par défaut des bulles */
.user-message:after, .bot-message:after {
    display: none;
}
</style>
""", unsafe_allow_html=True)

# ---------------- CHAT WINDOW (Style WhatsApp) ----------------
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Afficher les messages dans le style WhatsApp
for sender, text in st.session_state.messages:
    if sender == 'user':
        st.markdown(f"""
        <div style='display: flex; justify-content: flex-end; margin: 8px 0;'>
            <div class='message-bubble user-message'>
                {text}
                <div class='message-time'>12:00</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style='display: flex; justify-content: flex-start; margin: 8px 0;'>
            <div class='message-bubble bot-message'>
                {text}
                <div class='message-time'>12:00</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- BARRE DE SAISIE ET BOUTONS ----------------
col1, col2, col3 = st.columns([0.8, 0.1, 0.1])
with col1:
    user_input = st.text_input("Message", placeholder="Tapez votre message ici...", label_visibility="collapsed", key="user_input")
with col2:
    attach_clicked = st.button("📎", help="Attacher un document", key="attach_btn")
with col3:
    send_clicked = st.button("➤", help="Envoyer le message", key="send_btn")

# ---------------- GESTION FICHIER ----------------
if attach_clicked:
    st.session_state.show_file_uploader = not st.session_state.show_file_uploader
    st.rerun()

if st.session_state.show_file_uploader:
    uploaded_file = st.file_uploader(
        "Choisir un fichier",
        type=['pdf', 'txt', 'docx', 'png', 'jpg', 'jpeg'],
        label_visibility="visible",
        key="file_uploader"
    )
    if uploaded_file is not None:
        st.session_state.uploaded_file = uploaded_file
        st.success(f"✅ Fichier attaché: {uploaded_file.name}")
        if st.button("❌ Supprimer le fichier", key="delete_btn"):
            st.session_state.uploaded_file = None
            st.session_state.show_file_uploader = False
            st.rerun()

if st.session_state.uploaded_file:
    st.info(f"📎 **Fichier attaché:** {st.session_state.uploaded_file.name}")

# ---------------- ENVOI MESSAGE ----------------
if send_clicked and user_input.strip():
    # Ajouter message utilisateur
    st.session_state.messages.append(('user', user_input))
    
    # Générer réponse (modifié selon votre demande)
    user_msg_lower = user_input.lower()
    
    if "bonjour" in user_msg_lower or "salut" in user_msg_lower or "coucou" in user_msg_lower:
        reply = "Bonjour comment puis-je vous aider !"
    elif "fichier" in user_msg_lower and st.session_state.uploaded_file:
        reply = f"J'ai bien reçu votre fichier '{st.session_state.uploaded_file.name}'."
    elif "merci" in user_msg_lower:
        reply = "Je vous en prie ! 😊"
    elif "ça va" in user_msg_lower or "comment vas-tu" in user_msg_lower:
        reply = "Je vais très bien, merci ! Et vous ?"
    elif "aide" in user_msg_lower or "aide-moi" in user_msg_lower:
        reply = "Je suis là pour vous aider ! Dites-moi ce dont vous avez besoin."
    elif "au revoir" in user_msg_lower or "bye" in user_msg_lower:
        reply = "Au revoir ! À bientôt ! 👋"
    else:
        reply = "J'ai bien reçu votre message. Je traite votre demande..."
    
    st.session_state.messages.append(('bot', reply))
    
    # Vider le champ
    st.session_state.user_input = ""
    
    st.rerun()

# ---------------- PIED DE PAGE ----------------
st.markdown("---")
st.markdown("<div style='text-align: center; color: #888; font-size: 0.8em;'>Chatbot créé avec Streamlit 🤖</div>", unsafe_allow_html=True)