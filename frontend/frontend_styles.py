"""
Aviory Frontend Styles
Centralized CSS styling for Streamlit frontend
"""

FRONTEND_STYLES = """
<style>
    /* Main theme colors */
    :root {
        --primary-blue: #3b82f6;
        --dark-blue: #1e40af;
        --light-gray: #f9fafb;
        --border-gray: #e5e7eb;
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(90deg, #3b82f6 0%, #1e40af 100%);
        color: white;
        padding: 2rem 1rem;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .header-container h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: bold;
    }
    
    .header-container p {
        margin: 0.5rem 0 0 0;
        font-size: 1rem;
        opacity: 0.9;
    }
    
    /* Column containers */
    .column-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 0.75rem;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Upload area */
    .upload-area {
        border: 2px dashed #3b82f6;
        border-radius: 0.75rem;
        padding: 2rem;
        text-align: center;
        background: #f0f4ff;
        margin: 1rem 0;
    }
    
    .upload-area:hover {
        background: #e8edff;
        border-color: #1e40af;
    }
    
    /* Chat message styling */
    .message-container {
        margin: 1rem 0;
        padding: 1rem;
        border-radius: 0.5rem;
        animation: slideIn 0.3s ease-in;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .user-message {
        background: #dbeafe;
        border-left: 4px solid #3b82f6;
    }
    
    .assistant-message {
        background: #f0fdf4;
        border-left: 4px solid #22c55e;
    }
    
    .error-message {
        background: #fee2e2;
        border-left: 4px solid #ef4444;
    }
    
    .loading-message {
        background: #fef3c7;
        border-left: 4px solid #f59e0b;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #3b82f6 0%, #1e40af 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 0.5rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    }
    
    /* Input styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border: 1px solid #e5e7eb !important;
        border-radius: 0.5rem !important;
        padding: 0.75rem !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border: 2px solid #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    }
    
    /* Source styling */
    .source-box {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 0.5rem;
        padding: 0.75rem;
        margin: 0.5rem 0;
        font-size: 0.85rem;
    }
    
    .source-box .source-name {
        font-weight: 600;
        color: #3b82f6;
    }
    
    .source-box .relevance {
        color: #6b7280;
        font-size: 0.8rem;
    }
    
    /* Status indicators */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .status-success {
        background: #dcfce7;
        color: #166534;
    }
    
    .status-error {
        background: #fee2e2;
        color: #991b1b;
    }
    
    .status-loading {
        background: #fef3c7;
        color: #92400e;
    }
    
    /* History styling */
    .history-item {
        padding: 0.75rem;
        background: #f3f4f6;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.2s ease;
        border-left: 3px solid transparent;
    }
    
    .history-item:hover {
        background: #e5e7eb;
        border-left-color: #3b82f6;
    }
</style>
"""

def load_frontend_styles(st):
    """
    Load and apply frontend styles to Streamlit app
    
    Args:
        st: Streamlit module
    
    Example:
        from frontend_styles import load_frontend_styles
        load_frontend_styles(st)
    """
    st.markdown(FRONTEND_STYLES, unsafe_allow_html=True)
