import streamlit as st
import os

# Configuration de la page
st.set_page_config(
    page_title="Mon Chatbot",
    page_icon="🤖",
    layout="centered"
)

# Vérifier si l'image existe
image_path = "logo.png"
if os.path.exists(image_path):
    # Centrer exactement le logo avec des colonnes proportionnées
    col1, col2, col3 = st.columns([1.5, 1, 1.5])  # Colonnes ajustées pour un centrage parfait
    with col2:
        st.image(image_path, width=200)
else:
    st.warning(f"Image non trouvée: {image_path}")

# Phrase d'accueil centrée
st.markdown("<h3 style='text-align: center; color: #666;'>Comment puis-je vous aider?</h3>", unsafe_allow_html=True)

# Initialisation de l'état de session pour la gestion des fichiers
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'show_file_uploader' not in st.session_state:
    st.session_state.show_file_uploader = False

# Style CSS pour les boutons bleus
st.markdown("""
<style>
    /* Style pour tous les boutons Streamlit */
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
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    /* Effet au survol */
    .stButton > button:hover {
        background-color: #1e40af !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(29, 78, 216, 0.3) !important;
    }
    
    /* Effet lors du clic */
    .stButton > button:active {
        transform: translateY(0) !important;
        background-color: #1e3a8a !important;
    }
    
    /* Style spécifique pour le bouton d'envoi */
    .send-button {
        background-color: #1d4ed8 !important;
    }
    
    /* Style spécifique pour le bouton de pièce jointe */
    .attach-button {
        background-color: #1d4ed8 !important;
    }
    
    /* Personnalisation du bouton de téléchargement de fichier */
    div[data-testid="stFileUploader"] > section > button {
        background-color: #1d4ed8 !important;
        color: white !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
    }
    
    /* Style pour le bouton de suppression */
    .delete-button {
        background-color: #dc2626 !important;
    }
    
    .delete-button:hover {
        background-color: #b91c1c !important;
    }
</style>
""", unsafe_allow_html=True)

# Barre de saisie et boutons sur la même ligne
col1, col2, col3 = st.columns([0.8, 0.1, 0.1])

with col1:
    user_input = st.text_input(
        "Message",
        placeholder="Tapez votre message ici...",
        label_visibility="collapsed",
        key="user_input"
    )

with col2:
    # Bouton pour attacher un document (bleu)
    attach_clicked = st.button("📎", help="Attacher un document", key="attach_btn")

with col3:
    # Bouton d'envoi (bleu)
    send_clicked = st.button("➤", help="Envoyer le message", key="send_btn")

# Gérer le clic sur le bouton d'attachement
if attach_clicked:
    st.session_state.show_file_uploader = not st.session_state.show_file_uploader
    st.rerun()

# Afficher le sélecteur de fichier si l'utilisateur a cliqué sur le bouton 📎
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
        
        # Bouton pour supprimer le fichier (en rouge pour la distinction)
        st.markdown("""
        <style>
            div[data-testid="column"]:nth-of-type(1) button {
                background-color: #dc2626 !important;
            }
        </style>
        """, unsafe_allow_html=True)
        
        if st.button("❌ Supprimer le fichier", key="delete_btn"):
            st.session_state.uploaded_file = None
            st.session_state.show_file_uploader = False
            st.rerun()

# Afficher le fichier actuellement attaché
if st.session_state.uploaded_file:
    st.info(f"📎 **Fichier attaché:** {st.session_state.uploaded_file.name}")

# Traitement du message quand le bouton d'envoi est cliqué
if send_clicked:
    if user_input.strip():
        # Afficher le message de l'utilisateur
        st.markdown("---")
        
        # Section utilisateur
        col_user1, col_user2 = st.columns([0.1, 0.9])
        with col_user1:
            st.markdown("**👤 Vous:**")
        with col_user2:
            st.markdown(f"{user_input}")
        
        # Afficher les informations sur le fichier attaché
        if st.session_state.uploaded_file:
            st.markdown("**📎 Pièce jointe:**")
            st.write(f"• **Nom:** {st.session_state.uploaded_file.name}")
            st.write(f"• **Type:** {st.session_state.uploaded_file.type}")
            st.write(f"• **Taille:** {st.session_state.uploaded_file.size / 1024:.2f} Ko")
        
        # Simuler une réponse du chatbot
        st.markdown("---")
        
        # Section chatbot
        col_bot1, col_bot2 = st.columns([0.1, 0.9])
        with col_bot1:
            st.markdown("**🤖 Chatbot:**")
        with col_bot2:
            # Exemple de réponse selon le type de message
            if "bonjour" in user_input.lower() or "salut" in user_input.lower():
                st.success("Bonjour ! Comment puis-je vous aider aujourd'hui ?")
            elif "fichier" in user_input.lower() and st.session_state.uploaded_file:
                st.success(f"J'ai bien reçu votre fichier '{st.session_state.uploaded_file.name}'. Je vais l'analyser.")
            elif "merci" in user_input.lower():
                st.success("Je vous en prie ! N'hésitez pas si vous avez d'autres questions.")
            else:
                st.success("J'ai bien reçu votre message. Je traite votre demande...")
                
        # Bouton pour effacer la conversation (optionnel, en bleu aussi)
        st.markdown("---")
        col_clear1, col_clear2, col_clear3 = st.columns([0.7, 0.15, 0.15])
        with col_clear2:
            if st.button("🗑️ Effacer", key="clear_btn"):
                st.session_state.uploaded_file = None
                st.session_state.show_file_uploader = False
                st.rerun()
            
    else:
        st.warning("⚠️ Veuillez entrer un message avant d'envoyer.")

# Style supplémentaire pour améliorer l'apparence
st.markdown("""
<style>
    /* Amélioration du champ de texte */
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
    
    /* Amélioration des messages */
    .message-box {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #1d4ed8;
    }
    
    /* Style pour les messages d'information */
    .stInfo {
        background-color: #dbeafe;
        border-left: 4px solid #1d4ed8;
        border-radius: 8px;
    }
    
    /* Style pour les messages de succès */
    .stSuccess {
        background-color: #dcfce7;
        border-left: 4px solid #16a34a;
        border-radius: 8px;
    }
    
    /* Style pour les messages d'avertissement */
    .stWarning {
        background-color: #fef3c7;
        border-left: 4px solid #d97706;
        border-radius: 8px;
    }
    
    /* Centrage parfait du logo */
    [data-testid="column"]:nth-of-type(2) {
        display: flex;
        justify-content: center;
        align-items: center;
    }
</style>
""", unsafe_allow_html=True)

# Pied de page
st.markdown("---")
st.markdown("<div style='text-align: center; color: #888; font-size: 0.8em;'>Chatbot créé avec Streamlit 🤖</div>", unsafe_allow_html=True)