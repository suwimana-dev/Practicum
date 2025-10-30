import streamlit as st
import requests
import re

# -----------------------------
# 🌞 Streamlit Page Setup
# -----------------------------
st.set_page_config(
    page_title="J.A.M.B.O. – JA AI Mentor Bot Operator",
    page_icon="💡",
    layout="centered"
)

# -----------------------------
# 🎨 Custom Light Theme CSS
# -----------------------------
st.markdown("""
    <style>
    body {
        background-color: #ffffff;
        color: #000000;
        font-family: 'Helvetica', sans-serif;
    }

    .chat-container {
        max-height: 550px;
        overflow-y: auto;
        padding: 15px;
        border-radius: 15px;
        border: 1px solid #ddd;
        background-color: #fafafa;
        box-shadow: 0px 0px 6px rgba(0,0,0,0.05);
    }

    .user-bubble {
        background-color: #e3f2fd; /* Light blue */
        color: #000;
        padding: 10px 15px;
        border-radius: 20px;
        margin: 8px 0;
        text-align: right;
        width: fit-content;
        margin-left: auto;
        font-size: 15px;
    }

    .bot-bubble {
        background-color: #f1f1f1;
        color: #000;
        padding: 10px 15px;
        border-radius: 20px;
        margin: 8px 0;
        text-align: left;
        width: fit-content;
        margin-right: auto;
        font-size: 15px;
    }

    .title {
        text-align: center;
        font-weight: bold;
        color: #1a73e8;
        font-size: 24px;
        margin-bottom: 20px;
    }

    .footer {
        text-align: center;
        font-size: 12px;
        color: #888;
        margin-top: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# 🤖 Title Section
# -----------------------------
st.markdown('<div class="title">💡 J.A.M.B.O. (JA AI Mentor Bot Operator)</div>', unsafe_allow_html=True)
st.write("Welcome! 👋 I’m here to assist you with the JA DEEP Entrepreneurship Program — ask me anything!")

# -----------------------------
# 🧠 Chat Logic
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat container
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-bubble">🙂 You: {msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-bubble">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# 💬 Input Field + Callback
# -----------------------------
def handle_message():
    """Handles message sending and bot response."""
    user_message = st.session_state.user_input.strip()
    if not user_message:
        return

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_message})

    try:
        response = requests.post(
            "http://localhost:5005/webhooks/rest/webhook",
            json={"sender": "user", "message": user_message}
        )

        if response.status_code == 200:
            rasa_replies = response.json()

            for r in rasa_replies:
                bot_reply = r.get("text", "")
                urls = re.findall(r'(https?://\S+)', bot_reply)

                if urls:
                    for url in urls:
                        pre_text = bot_reply.split(url)[0].strip()
                        if pre_text:
                            st.session_state.messages.append({"role": "bot", "content": pre_text})
                        st.session_state.messages.append({
                            "role": "bot",
                            "content": f"[🔗 Click here to open JA Registration Page]({url})"
                        })
                else:
                    st.session_state.messages.append({"role": "bot", "content": bot_reply})
        else:
            st.session_state.messages.append({
                "role": "bot",
                "content": "⚠️ The Rasa server returned an error. Please check the connection."
            })

    except requests.exceptions.ConnectionError:
        st.error("⚠️ Unable to connect to Rasa server. Please make sure it's running.")

    # Clear input field automatically after message
    st.session_state.user_input = ""


# Input box that triggers message send when Enter is pressed
st.text_input(
    "Type your message here:",
    key="user_input",
    on_change=handle_message,
)

# -----------------------------
# 🪶 Footer
# -----------------------------
st.markdown('<div class="footer">Powered by Rasa × Streamlit | JA DEEP Program</div>', unsafe_allow_html=True)
