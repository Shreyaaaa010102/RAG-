import streamlit as st
import requests
import uuid
from datetime import datetime

# Replace with your n8n webhook URL
WEBHOOK_URL = "https://amerjahmi.app.n8n.cloud/webhook/d6d1691e-cbbe-4df9-aa67-c62a0be585d5/chat"

# Hardcoded password
PASSWORD = "Master"

# Custom CSS for iMessage-like styling
st.markdown("""
    <style>
    /* General app background */
    .stApp {
        background-color: #0a192f;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Headings */
    .stApp h1 {
        color: white !important;
        text-align: center;
        font-weight: 600;
        padding: 1rem 0;
    }
    
    /* Chat messages container */
    .stChatMessage {
        background-color: transparent !important;
        padding: 0.5rem 1rem !important;
    }
    
    /* User messages - RIGHT aligned with BLUE background */
    [data-testid="stChatMessageContent"][data-testid*="user"] {
        background-color: #007bff !important;
        color: white !important;
        border-radius: 18px !important;
        padding: 10px 16px !important;
        max-width: 70% !important;
        margin-left: auto !important;
        margin-right: 0 !important;
        word-wrap: break-word;
    }
    
    div[data-testid="stChatMessage"]:has([data-testid="stChatMessageContent"]) {
        display: flex !important;
        justify-content: flex-end !important;
        margin-bottom: 8px !important;
    }
    
    /* Target user message specifically */
    div[data-testid="stChatMessage"]:has(.user-message) {
        justify-content: flex-end !important;
    }
    
    div[data-testid="stChatMessage"]:has(.assistant-message) {
        justify-content: flex-start !important;
    }
    
    /* Assistant messages - LEFT aligned with GRAY background */
    .assistant-message {
        background-color: #2d3748 !important;
        color: white !important;
        border-radius: 18px !important;
        padding: 10px 16px !important;
        max-width: 70% !important;
        margin-right: auto !important;
        margin-left: 0 !important;
        display: inline-block;
        word-wrap: break-word;
    }
    
    .user-message {
        background-color: #007bff !important;
        color: white !important;
        border-radius: 18px !important;
        padding: 10px 16px !important;
        max-width: 70% !important;
        margin-left: auto !important;
        margin-right: 0 !important;
        display: inline-block;
        word-wrap: break-word;
        text-align: right;
    }
    
    /* Hide avatars */
    .stChatMessage img {
        display: none !important;
    }
    
    /* Date divider */
    .date-divider {
        text-align: center;
        color: #8892a6;
        font-size: 0.75rem;
        font-weight: 500;
        letter-spacing: 0.5px;
        margin: 1.5rem 0 1rem 0;
        text-transform: uppercase;
    }
    
    /* Input area */
    .stChatInputContainer {
        background-color: #1a202c !important;
        border-top: 1px solid #2d3748 !important;
        padding: 1rem !important;
    }
    
    .stChatInput textarea {
        background-color: #2d3748 !important;
        color: white !important;
        border: 1px solid #4a5568 !important;
        border-radius: 20px !important;
        padding: 10px 15px !important;
    }
    
    .stChatInput textarea::placeholder {
        color: rgba(255, 255, 255, 0.5) !important;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #007bff;
        color: white;
        border-radius: 20px;
        border: none;
        padding: 8px 20px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #0056b3;
        transform: translateY(-1px);
    }
    
    /* Login form */
    .stTextInput > div > div > input {
        background-color: #1a202c;
        color: white;
        border: 1px solid #4a5568;
        border-radius: 10px;
        padding: 10px;
    }
    
    .stTextInput label {
        color: white !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #007bff !important;
    }
    
    .stSpinner {
    color: white !important;
    }       
    /* Clear button positioning */
    .clear-button-container {
        position: absolute;
        top: 1rem;
        right: 1rem;
        z-index: 999;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_date" not in st.session_state:
    st.session_state.show_date = True

# Function to send message to n8n webhook
def send_message_to_n8n(user_message, session_id):
    payload = {
        "chatInput": user_message,
        "sessionId": session_id
    }
    headers = {"Content-Type": "application/json"}
    for attempt in range(3):
        try:
            response = requests.post(WEBHOOK_URL, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get("output") or data.get("response") or str(data)
        except requests.exceptions.RequestException as e:
            if attempt < 2:
                continue
            return f"⚠️ Error connecting to chatbot: {str(e)}"

# Password protection
if not st.session_state.authenticated:
    st.markdown('<h1>🔐 Login to Assistant</h1>', unsafe_allow_html=True)
    with st.form(key="login_form"):
        password_input = st.text_input("Enter Password", type="password")
        submit = st.form_submit_button("Login")
        if submit:
            if password_input == PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Incorrect password")
else:
    # Main chat interface
    col1, col2, col3 = st.columns([1, 6, 1])
    
    with col2:
        st.markdown('<h1>💬 RAG Assistant</h1>', unsafe_allow_html=True)
    
    with col3:
        if st.button("🔄 Clear"):
            st.session_state.messages = []
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.show_date = True
            st.rerun()
    
    # Date divider
    if st.session_state.show_date and len(st.session_state.messages) > 0:
        st.markdown(f'<div class="date-divider">{datetime.now().strftime("%A").upper()}</div>', unsafe_allow_html=True)
        st.session_state.show_date = False
    
    # Display chat history
    for message in st.session_state.messages:
        if message["role"] == "user":
            # User message - RIGHT aligned
            st.markdown(f'<div style="display: flex; justify-content: flex-end; margin-bottom: 8px;"><div class="user-message">{message["content"]}</div></div>', unsafe_allow_html=True)
        else:
            # Assistant message - LEFT aligned
            st.markdown(f'<div style="display: flex; justify-content: flex-start; margin-bottom: 8px;"><div class="assistant-message">{message["content"]}</div></div>', unsafe_allow_html=True)
    
    # User input
    if prompt := st.chat_input("Message..."):
        # Add date divider if first message
        if len(st.session_state.messages) == 0:
            st.markdown(f'<div class="date-divider">{datetime.now().strftime("%A").upper()}</div>', unsafe_allow_html=True)
        
        # Append user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message immediately
        st.markdown(f'<div style="display: flex; justify-content: flex-end; margin-bottom: 8px;"><div class="user-message">{prompt}</div></div>', unsafe_allow_html=True)
        
        # Get bot response
        with st.spinner("Extracting Data..."):
            bot_response = send_message_to_n8n(prompt, st.session_state.session_id)
        
        # Append and display bot response
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        st.rerun()
