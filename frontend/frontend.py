"""
Aviory Frontend - Streamlit UI
Single-page application with 2-column layout (Upload + Chat)
Integrates with FastAPI backend
"""

import streamlit as st
import requests
import json
import os
import tempfile
import shutil
from datetime import datetime
import time
from frontend_styles import load_frontend_styles

# ==================== Page Configuration ====================
st.set_page_config(
    page_title="Aviory - Un assistant AI pour la recherche dans les documents",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== Styling ====================
load_frontend_styles(st)

# ==================== Configuration ====================
API_BASE_URL = "http://localhost:8000"
UPLOAD_ENDPOINT = f"{API_BASE_URL}/documents/reload"
UPLOAD_FILE_ENDPOINT = f"{API_BASE_URL}/documents/upload"
QUERY_ENDPOINT = f"{API_BASE_URL}/query"
STATUS_ENDPOINT = f"{API_BASE_URL}/status"

# ==================== Session State Initialization ====================
required_states = {
    "chat_history": [],
    "documents_status": None,
    "last_query_time": None,
    "clear_input_flag": False,
    "last_submitted_question": "",
    "uploaded_files": [],
    "upload_progress": 0,
    "temp_files": [],
    "current_folder_path": "documents"  # Dossier par défaut
}

for key, default_value in required_states.items():
    if key not in st.session_state:
        st.session_state[key] = default_value

# ==================== Helper Functions ====================

def check_api_health():
    """Check if FastAPI backend is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def get_system_status():
    """Fetch system status from API"""
    try:
        response = requests.get(STATUS_ENDPOINT, timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def save_file_to_documents_folder(file, folder_path):
    """Save uploaded file to documents folder"""
    try:
        # Créer le dossier s'il n'existe pas
        os.makedirs(folder_path, exist_ok=True)
        
        # Chemin complet du fichier
        file_path = os.path.join(folder_path, file.name)
        
        # Vérifier si le fichier existe déjà
        counter = 1
        base_name, extension = os.path.splitext(file.name)
        while os.path.exists(file_path):
            file_path = os.path.join(folder_path, f"{base_name}_{counter}{extension}")
            counter += 1
        
        # Sauvegarder le fichier
        with open(file_path, "wb") as f:
            f.write(file.getvalue())
        
        return file_path, True
    except Exception as e:
        return str(e), False

def upload_documents(folder_path: str):
    """Upload/reload documents from specified folder"""
    try:
        response = requests.post(
            UPLOAD_ENDPOINT,
            json={"documents_folder": folder_path},
            timeout=30
        )
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json().get("detail", "Upload failed")
    except Exception as e:
        return False, f"Error: {str(e)}"

def upload_files(files, folder_path):
    """Upload files to the documents folder and reload"""
    try:
        uploaded_files = []
        failed_files = []
        total_files = len(files)
        
        # Étape 1: Sauvegarder les fichiers localement
        for i, file in enumerate(files):
            try:
                file_path, success = save_file_to_documents_folder(file, folder_path)
                if success:
                    uploaded_files.append({
                        "name": file.name,
                        "path": file_path,
                        "size": file.size
                    })
                else:
                    failed_files.append(f"{file.name}: {file_path}")
                
                # Mettre à jour la progression
                st.session_state.upload_progress = ((i + 1) / total_files) * 0.5  # 50% pour sauvegarde
                st.rerun()
                
            except Exception as e:
                failed_files.append(f"{file.name}: {str(e)}")
        
        # Étape 2: Recharger les documents dans le système
        if uploaded_files:
            st.session_state.upload_progress = 0.75
            st.rerun()
            
            success, result = upload_documents(folder_path)
            if success:
                st.session_state.upload_progress = 1.0
                return uploaded_files, failed_files, True, result
            else:
                failed_files.append(f"Rechargement échoué: {result}")
                st.session_state.upload_progress = 1.0
                return uploaded_files, failed_files, False, result
        else:
            st.session_state.upload_progress = 1.0
            return [], failed_files, False, "Aucun fichier sauvegardé"
        
    except Exception as e:
        return [], [f"Erreur globale: {str(e)}"], False, str(e)

def ask_question(question: str, top_k: int = 5):
    """Query the RAG pipeline"""
    try:
        response = requests.post(
            QUERY_ENDPOINT,
            json={"question": question, "top_k": top_k},
            timeout=30
        )
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json().get("detail", "Query failed")
    except Exception as e:
        return False, f"Error: {str(e)}"

def format_timestamp():
    """Return current timestamp"""
    return datetime.now().strftime("%H:%M:%S")

def get_folder_stats(folder_path):
    """Get statistics about documents folder"""
    stats = {
        "total_files": 0,
        "total_size": 0,
        "file_types": {},
        "last_modified": None
    }
    
    try:
        if os.path.exists(folder_path):
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    stats["total_files"] += 1
                    
                    # Taille
                    try:
                        stats["total_size"] += os.path.getsize(file_path)
                    except:
                        pass
                    
                    # Type de fichier
                    ext = os.path.splitext(file)[1].lower()
                    stats["file_types"][ext] = stats["file_types"].get(ext, 0) + 1
                    
                    # Date de modification
                    try:
                        mod_time = os.path.getmtime(file_path)
                        if stats["last_modified"] is None or mod_time > stats["last_modified"]:
                            stats["last_modified"] = mod_time
                    except:
                        pass
    except:
        pass
    
    return stats

# ==================== Main UI ====================

# Header
st.markdown("""
<div class="header-container">
    <h1>Aviory</h1>
    <p>Un assistant AI pour la recherche dans les documents</p>
</div>
""", unsafe_allow_html=True)

# Check API connectivity
api_healthy = check_api_health()
if not api_healthy:
    st.error("⚠️ API Backend Not Running\n\nPlease start the FastAPI server")
    st.stop()

# Main layout: 2 columns
col_upload, col_chat = st.columns([1, 2])

# ==================== LEFT COLUMN: UPLOAD ====================
with col_upload:
    st.subheader("📁 Documents")
    
    # Onglets pour différentes méthodes d'upload
    tab_folder, tab_files = st.tabs(["📂 Dossier", "📄 Fichiers"])
    
    # Tab 1: Upload par dossier
    with tab_folder:
        st.write("**Configurer le dossier des documents:**")
        
        # Afficher le chemin actuel
        current_path = st.session_state.get("current_folder_path", "documents")
        
        folder_path = st.text_input(
            "Folder path",
            value=current_path,
            placeholder="e.g., documents, /path/to/docs",
            label_visibility="collapsed",
            key="folder_input"
        )
        
        # Mettre à jour le chemin dans l'état de session
        if folder_path != current_path:
            st.session_state.current_folder_path = folder_path
        
        # Vérifier si le dossier existe
        folder_exists = os.path.exists(folder_path) if folder_path else False
        
        if folder_path and not folder_exists:
            st.warning(f"⚠️ Le dossier '{folder_path}' n'existe pas.")
            if st.button("📁 Créer le dossier", use_container_width=True, key="create_folder_btn"):
                try:
                    os.makedirs(folder_path, exist_ok=True)
                    st.success(f"✅ Dossier créé: {folder_path}")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")
        
        # Reload button
        reload_disabled = not folder_exists
        reload_text = "🔄 Load Documents" if folder_exists else "⚠️ Dossier non valide"
        
        if st.button(reload_text, use_container_width=True, key="reload_btn", disabled=reload_disabled):
            with st.spinner("Loading documents..."):
                success, result = upload_documents(folder_path)
                if success:
                    st.success(f"✅ Chargé {result.get('num_chunks', 0)} chunks")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ Échec du chargement: {result}")
    
    # Tab 2: Upload de fichiers
    with tab_files:
        st.write("**Uploader des fichiers:**")
        
        # Afficher le dossier de destination
        dest_folder = st.session_state.get("current_folder_path", "documents")
        st.info(f"📁 Destination: `{dest_folder}`")
        
        # Zone de dépôt de fichiers
        uploaded_files = st.file_uploader(
            "Sélectionnez des fichiers",
            type=["pdf", "doc", "docx", "txt", "md", "csv", "xlsx", "pptx", "jpg", "png"],
            accept_multiple_files=True,
            label_visibility="collapsed",
            key="file_uploader"
        )
        
        if uploaded_files:
            # Calculer la taille totale
            total_size = sum(f.size for f in uploaded_files)
            st.info(f"✅ {len(uploaded_files)} fichier(s) sélectionné(s) - {total_size / 1024:.1f} KB")
            
            # Afficher la liste des fichiers
            with st.expander("📋 Voir les fichiers", expanded=False):
                for file in uploaded_files:
                    st.write(f"• {file.name} ({file.size / 1024:.1f} KB)")
        
        # Options d'upload
        col_options1, col_options2 = st.columns(2)
        with col_options1:
            overwrite = st.checkbox("Écraser les fichiers existants", value=False)
        with col_options2:
            auto_reload = st.checkbox("Recharger automatiquement", value=True)
        
        # Bouton d'upload
        upload_disabled = not uploaded_files or not dest_folder
        if st.button("📤 Upload Files", use_container_width=True, key="upload_files_btn", 
                    disabled=upload_disabled):
            
            with st.spinner("Upload en cours..."):
                # Réinitialiser la progression
                st.session_state.upload_progress = 0
                
                # Upload des fichiers
                uploaded, failed, reload_success, reload_result = upload_files(
                    uploaded_files, 
                    dest_folder
                )
                
                # Afficher les résultats
                if uploaded:
                    st.success(f"✅ {len(uploaded)} fichier(s) sauvegardé(s) dans `{dest_folder}`")
                    
                    if reload_success and auto_reload:
                        st.success(f"✅ Rechargé {reload_result.get('num_chunks', 0)} chunks")
                    elif auto_reload:
                        st.warning(f"⚠️ Fichiers sauvegardés mais rechargement échoué")
                
                if failed:
                    st.error(f"❌ {len(failed)} échec(s)")
                    for failure in failed[:3]:  # Afficher seulement les 3 premiers
                        st.error(failure)
                    if len(failed) > 3:
                        st.error(f"... et {len(failed) - 3} autres erreurs")
                
                # Réinitialiser l'uploader
                st.session_state.file_uploader = []
                st.rerun()
        
        # Barre de progression
        if st.session_state.upload_progress > 0:
            progress_text = ""
            if st.session_state.upload_progress < 0.6:
                progress_text = "Sauvegarde des fichiers..."
            elif st.session_state.upload_progress < 0.9:
                progress_text = "Rechargement dans l'IA..."
            else:
                progress_text = "Terminé !"
            
            st.progress(st.session_state.upload_progress)
            st.caption(f"{progress_text} {int(st.session_state.upload_progress * 100)}%")
    
    # Chat History
    st.write("**Historique du chat:**")
    # Bouton pour vider l'historique
    if st.button("🗑️ Vider l'historique", use_container_width=True, key="clear_history_btn"):
        st.session_state.chat_history = []
        st.success("✅ Historique vidé")
        st.rerun()

    # Affichage de l'historique
    if st.session_state.chat_history:
        for i, msg in enumerate(reversed(st.session_state.chat_history)):
            if msg["role"] == "user":
                # Échapper les apostrophes pour JavaScript
                escaped_content = msg['content'].replace("'", "\\'")
                st.markdown(f"""
                <div style="
                    background-color: #e0e0e0; 
                    padding: 0.8rem; 
                    border-radius: 0.5rem; 
                    margin-bottom: 0.5rem;
                    cursor: pointer;
                "
                onclick="document.querySelector('#question_input textarea').value = '{escaped_content}'">
                    {msg['content'][:100]}...
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("💬 Aucun historique de discussion pour le moment")

# ==================== RIGHT COLUMN: CHAT ====================
with col_chat:
    st.subheader("💬 Discussion")
    
    # Chat display area
    chat_container = st.container()
    
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="message-container user-message">
                    <strong>You:</strong> {msg['content']}
                    <div style="font-size: 0.8rem; color: #666; margin-top: 0.5rem;">{msg.get('timestamp', '')}</div>
                </div>
                """, unsafe_allow_html=True)
            elif msg["role"] == "assistant":
                st.markdown(f"""
                <div class="message-container assistant-message">
                    <strong> Aviory:</strong><br>{msg['content']}
                    <div style="font-size: 0.8rem; color: #666; margin-top: 0.5rem;">{msg.get('timestamp', '')}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Display sources if available
                if "sources" in msg:
                    with st.expander("📖 Sources", expanded=False):
                        for source in msg["sources"]:
                            relevance_pct = int(source.get("relevance", 0) * 100)
                            st.markdown(f"""
                            <div class="source-box">
                                <div class="source-name">{source.get('source', 'Unknown')}</div>
                                <div class="relevance">Relevance: {relevance_pct}%</div>
                                <div style="margin-top: 0.5rem; font-size: 0.85rem;">
                                    {source.get('text', 'N/A')[:200]}...
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
            elif msg["role"] == "error":
                st.markdown(f"""
                <div class="message-container error-message">
                    <strong>❌ Error:</strong> {msg['content']}
                </div>
                """, unsafe_allow_html=True)
            elif msg["role"] == "system":
                st.markdown(f"""
                <div class="message-container loading-message">
                    <strong>⏳ {msg['content']}</strong>
                </div>
                """, unsafe_allow_html=True)
    
    st.divider()
    
    # Input area - SOLUTION FONCTIONNELLE
    col_input, col_button = st.columns([5, 1])
    
    with col_input:
        # Créer une clé unique basée sur le flag de nettoyage
        input_key = f"question_input_{st.session_state.clear_input_flag}"
        
        # Utiliser un textarea avec gestion JavaScript
        question = st.text_area(
            "Posez une question...",
            placeholder="Quelle information recherchez-vous ?",
            label_visibility="collapsed",
            key=input_key 
        )
        
        # Ajouter JavaScript pour vider le champ si nécessaire
        if st.session_state.clear_input_flag:
            st.markdown("""
            <script>
            // Vider le textarea après le chargement
            document.addEventListener('DOMContentLoaded', function() {
                const textarea = document.querySelector('[data-testid="stTextArea"] textarea');
                if (textarea) {
                    textarea.value = '';
                    // Réinitialiser la hauteur si nécessaire
                    textarea.style.height = '100px';
                }
            });
            </script>
            """, unsafe_allow_html=True)
    
    with col_button:
        submit_button = st.button("Envoyer", use_container_width=True, key="submit_btn")
    
    # Process question
    if submit_button and question.strip():
        # Stocker la question pour usage ultérieur
        st.session_state.last_submitted_question = question
        
        # Add user message
        st.session_state.chat_history.append({
            "role": "user",
            "content": question,
            "timestamp": format_timestamp()
        })
        
        # Add loading indicator
        st.session_state.chat_history.append({
            "role": "system",
            "content": "Traitement de votre question..."
        })
        
        # Activer le flag pour vider l'input au prochain rendu
        st.session_state.clear_input_flag = not st.session_state.clear_input_flag
        
        # Rafraîchir immédiatement
        st.rerun()
    
    # Process API response if last message is loading
    if (st.session_state.chat_history and 
        st.session_state.chat_history[-1]["role"] == "system"):
        
        # Get the previous user message
        user_question = st.session_state.last_submitted_question
        
        if user_question:
            # Remove loading message
            st.session_state.chat_history.pop()
            
            # Query API
            success, result = ask_question(user_question)
            
            if success:
                # Add assistant response
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": result.get("answer", "Aucune réponse générée"),
                    "sources": result.get("sources", []),
                    "timestamp": format_timestamp()
                })
            else:
                # Add error message
                st.session_state.chat_history.append({
                    "role": "error",
                    "content": result,
                    "timestamp": format_timestamp()
                })
            
            # Clear the stored question
            st.session_state.last_submitted_question = ""
            st.session_state.last_query_time = time.time()
            st.rerun()

# ==================== Footer ====================
st.divider()
st.markdown("""
<div style="text-align: center; color: #6b7280; font-size: 0.85rem; padding: 1rem;">
    <p>Aviory © 2026 | Système de Q&A documentaire alimenté par RAG</p>
    <p>API: <span id="api-status">●</span> <code>localhost:8000</code></p>
</div>
""", unsafe_allow_html=True)