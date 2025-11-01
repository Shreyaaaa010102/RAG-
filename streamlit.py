import streamlit as st
import requests
import uuid  # For generating unique session IDs

# Replace with your n8n webhook URL
WEBHOOK_URL = "https://amerjahmi.app.n8n.cloud/webhook/d6d1691e-cbbe-4df9-aa67-c62a0be585d5/chat"

# Hardcoded password (change this; for production, use st.secrets or env vars)
PASSWORD = "Master"

# Custom CSS for Grok-like styling with dark blue theme
st.markdown("""
    <style>
    /* General chat container */
    .stApp {
        background-color: #0a192f;  /* Dark blue background */
        color: white;  /* Default text color white for contrast */
    }
    /* Headings and titles */
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
        color: white !important;
        text-align: center;  /* Center all titles */
    }
    /* Labels for inputs */
    .stApp .stTextInput label, .stApp .stButton label {
        color: white !important;  /* White labels for high contrast */
    }
    /* Message bubbles */
    .stApp .st-chat-message {
        border-radius: 15px;
        padding: 10px 15px;
        margin-bottom: 10px;
        max-width: 80%;
        color: white;  /* White text for messages */
    }
    /* User messages: right-aligned, blue bubble */
    .stApp div[data-testid="column"] > div > div > div > div > .st-chat-message.user {
        background-color: #007bff;  /* Blue bubble */
        color: white;
        margin-left: auto;
        text-align: right;
    }
    /* Assistant messages: left-aligned, darker bubble */
    .stApp div[data-testid="column"] > div > div > div > div > .st-chat-message.assistant {
        background-color: #2d3748;  /* Dark gray for assistant */
        color: white;
        margin-right: auto;
        text-align: left;
    }
    /* Avatars */
    .stApp .st-chat-message .st-avatar {
        border-radius: 50%;
    }
    /* Input area for password */
    .stApp .stTextInput > div > div > input {
        border-radius: 20px;
        padding: 10px;
        background-color: #1a202c;  /* Dark input background for password */
        color: white;  /* White text in input */
        border: 1px solid #4a5568;  /* Subtle border */
    }
    /* Buttons: clear and prominent */
    .stApp .stButton > button {
        background-color: #007bff;  /* Blue buttons */
        color: white;
        border-radius: 20px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;  /* Bold text for clarity */
    }
    .stApp .stButton > button:hover {
        background-color: #0056b3;  /* Darker blue on hover for interactivity */
        cursor: pointer;
    }
    /* Spinner */
    .stApp .stSpinner {
        text-align: center;
        color: white;
    }
    /* Ensure all text is clear within the app */
    .stApp p, .stApp div, .stApp span, .stApp label {
        color: white !important;  /* Override for high contrast within app */
    }
    /* Attempt to style the top toolbar */
    section[data-testid="stToolbar"] {
        background-color: #007bff !important;  /* Blue background for toolbar */
    }
    header[data-testid="stHeader"] {
        background-color: #007bff !important;  /* Blue for any header */
    }
    /* Style the bottom chat input bar */
    div.stChatFloatingInputContainer {
        background-color: #007bff !important;
        padding-bottom: 3rem !important;
        border-top: 1px solid #0056b3 !important;
    }
    div.stChatInput > div > div > input {
        background-color: #007bff !important;
        color: white !important;
        border: none !important;
    }
    div.stChatInput > div > div > input::placeholder {
        color: rgba(255, 255, 255, 0.6) !important;
    }
    /* Send button in chat input */
    div.stChatInput > div > div > button {
        background-color: #007bff !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())  # Generate unique ID once per session

if "messages" not in st.session_state:
    st.session_state.messages = []  # List to store chat history

# Function to send message to n8n webhook and get response
def send_message_to_n8n(user_message, session_id):
    payload = {
        "chatInput": user_message,   # must match n8n Chat Trigger key
        "sessionId": session_id
    }
    headers = {"Content-Type": "application/json"}
    for attempt in range(3):
        try:
            response = requests.post(WEBHOOK_URL, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            # Adjust to whatever key n8n returns ("output", "response", etc.)
            return data.get("output") or data.get("response") or str(data)
        except requests.exceptions.RequestException as e:
            if attempt < 2:
                continue
            return f"⚠️ Error connecting to chatbot: {str(e)}"


# Password protection
if not st.session_state.authenticated:
    st.markdown('<h1 style="color:white; text-align:center;">Login to Chatbot</h1>', unsafe_allow_html=True)
    password_input = st.text_input("Enter Password", type="password")
    if st.button("Login"):
        if password_input == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()  # Refresh to show chat
        else:
            st.error("Incorrect password")
else:
    # Streamlit app layout (Grok-like chat)
    st.markdown('<h1 style="color:white; text-align:center;">RAG Chatbot</h1>', unsafe_allow_html=True)  # Centered title

    # Clear chat button (Grok has reset options)
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())  # New session
        st.rerun()

    # Display chat history with avatars
    for message in st.session_state.messages:
        avatar = "🧑‍💻" if message["role"] == "user" else "🤖"  # Simple emojis; use URLs for images
        # For Grok logo: avatar = "https://example.com/grok-icon.png" for assistant
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # User input
    if prompt := st.chat_input("Ask me anything..."):  # Grok-like placeholder
        # Append user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)

        # Send to n8n and get response
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                bot_response = send_message_to_n8n(prompt, st.session_state.session_id)
            st.markdown(bot_response)

        # Append bot response to history
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
