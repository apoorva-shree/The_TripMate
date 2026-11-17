"""
TripMate AI - Main Streamlit Application
=========================================
A premium, conversational AI virtual assistant built with Google Gemini API
and Streamlit. Features dark-navy ChatGPT aesthetics, real-time streaming,
conversation memory, multi-session management, and specialized travel
intelligence capabilities.
"""

import os
import uuid
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

from config import (
    APP_NAME,
    TAGLINE,
    APP_ICON,
    WELCOME_TITLE,
    WELCOME_SUBTITLE,
    DEFAULT_MODEL,
    AVAILABLE_MODELS,
    SUGGESTED_PROMPTS,
    CUSTOM_CSS,
)
from chatbot import (
    TripMateChatbot,
    TripMateError,
    MissingAPIKeyError,
    AuthenticationError,
    RateLimitError,
    NetworkError,
)

# -----------------------------------------------------------------------------
# Page Configuration & Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title=f"{APP_NAME} | {TAGLINE}",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject Dark Navy & Cyan custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------------------------
def init_session_state():
    """Initializes chat sessions and settings in Streamlit session_state."""
    load_dotenv(override=True)

    # API Key initialization
    if "api_key" not in st.session_state:
        st.session_state.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""

    # Selected Gemini model
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = DEFAULT_MODEL

    # Pending prompt buffer for suggested prompts
    if "pending_prompt" not in st.session_state:
        st.session_state.pending_prompt = None

    # Multi-session chat storage
    if "chats" not in st.session_state:
        default_id = str(uuid.uuid4())[:8]
        st.session_state.chats = {
            default_id: {
                "id": default_id,
                "title": "New Chat",
                "messages": [],
                "created_at": datetime.now().strftime("%b %d, %H:%M"),
            }
        }
        st.session_state.current_chat_id = default_id

    # Validate active chat id
    if (
        "current_chat_id" not in st.session_state
        or st.session_state.current_chat_id not in st.session_state.chats
    ):
        first_id = list(st.session_state.chats.keys())[0]
        st.session_state.current_chat_id = first_id


init_session_state()

# Initialize Chatbot Engine with session key
chatbot = TripMateChatbot(api_key=st.session_state.api_key)


# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------
def get_current_chat():
    """Returns the current active chat session dictionary."""
    return st.session_state.chats[st.session_state.current_chat_id]


def create_new_chat():
    """Creates a new conversation session and switches to it."""
    new_id = str(uuid.uuid4())[:8]
    st.session_state.chats[new_id] = {
        "id": new_id,
        "title": "New Chat",
        "messages": [],
        "created_at": datetime.now().strftime("%b %d, %H:%M"),
    }
    st.session_state.current_chat_id = new_id
    st.session_state.pending_prompt = None


def clear_current_chat():
    """Empties messages in current chat and resets title."""
    chat = get_current_chat()
    chat["messages"] = []
    chat["title"] = "New Chat"


def auto_generate_title(prompt: str) -> str:
    """Generates a concise 3-5 word title from the user's initial prompt."""
    cleaned = prompt.strip().replace("\n", " ")
    words = cleaned.split()
    if len(words) <= 5:
        title = " ".join(words)
    else:
        title = " ".join(words[:5]) + "..."
    return title[:32]


def save_api_key_to_env(new_key: str):
    """Saves the user-provided API key to the .env file."""
    try:
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        lines = []
        key_found = False

        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

        new_lines = []
        for line in lines:
            if line.strip().startswith("GEMINI_API_KEY="):
                new_lines.append(f"GEMINI_API_KEY={new_key}\n")
                key_found = True
            else:
                new_lines.append(line)

        if not key_found:
            new_lines.append(f"GEMINI_API_KEY={new_key}\n")

        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        os.environ["GEMINI_API_KEY"] = new_key
        return True
    except Exception:
        return False


# -----------------------------------------------------------------------------
# Sidebar Navigation & Settings
# -----------------------------------------------------------------------------
with st.sidebar:
    # App Branding
    st.markdown(
        f"""
        <div style="padding: 0.5rem 0 1rem 0;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.8rem;">{APP_ICON}</span>
                <div>
                    <h2 style="margin: 0; font-size: 1.25rem; font-weight: 700; color: #FFFFFF;">{APP_NAME}</h2>
                    <p style="margin: 0; font-size: 0.72rem; color: #38BDF8; font-weight: 500;">{TAGLINE}</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # "New Chat" Action Button
    st.markdown('<div class="new-chat-btn">', unsafe_allow_html=True)
    if st.button("➕  New Chat", use_container_width=True, key="btn_new_chat"):
        create_new_chat()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<hr style='border-color: #1E293B; margin: 1rem 0;'>", unsafe_allow_html=True)

    # Conversation History List
    st.markdown(
        "<p style='font-size: 0.75rem; font-weight: 600; text-transform: uppercase; color: #64748B; letter-spacing: 0.05em; margin-bottom: 0.5rem;'>Recent Chats</p>",
        unsafe_allow_html=True,
    )

    chat_items = list(st.session_state.chats.items())
    # Display recent conversations in reverse chronological order
    for chat_id, chat_data in reversed(chat_items):
        is_active = chat_id == st.session_state.current_chat_id
        icon_prefix = "🔹" if is_active else "💬"
        btn_label = f"{icon_prefix} {chat_data['title']}"

        # Highlight active conversation
        if st.button(
            btn_label,
            key=f"chat_nav_{chat_id}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            st.session_state.current_chat_id = chat_id
            st.session_state.pending_prompt = None
            st.rerun()

    st.markdown("<hr style='border-color: #1E293B; margin: 1rem 0;'>", unsafe_allow_html=True)

    # Model Selection
    selected_model = st.selectbox(
        "AI Model",
        options=AVAILABLE_MODELS,
        index=AVAILABLE_MODELS.index(st.session_state.selected_model)
        if st.session_state.selected_model in AVAILABLE_MODELS
        else 0,
        help="Select the Google Gemini model for response generation.",
    )
    st.session_state.selected_model = selected_model

    # API Key Configuration Expander
    with st.expander("⚙️  Gemini API Configuration", expanded=not chatbot.is_configured()):
        is_ready = chatbot.is_configured()
        if is_ready:
            st.markdown(
                '<div style="color: #4ADE80; font-size: 0.85rem; margin-bottom: 0.5rem;">'
                '● API Key Active & Connected'
                '</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div style="color: #F87171; font-size: 0.85rem; margin-bottom: 0.5rem;">'
                '● No API Key Configured'
                '</div>',
                unsafe_allow_html=True,
            )

        entered_key = st.text_input(
            "Gemini API Key",
            value=st.session_state.api_key,
            type="password",
            placeholder="AIzaSy...",
            help="Your API key from Google AI Studio. Never shared or hardcoded.",
        )

        col_save, col_test = st.columns([1, 1])
        with col_save:
            if st.button("Save Key", use_container_width=True, key="btn_save_key"):
                if entered_key.strip():
                    st.session_state.api_key = entered_key.strip()
                    save_api_key_to_env(entered_key.strip())
                    chatbot.update_api_key(entered_key.strip())
                    st.success("API Key saved!")
                    st.rerun()
                else:
                    st.warning("Please enter a valid key.")

        with col_test:
            if st.button("Test", use_container_width=True, key="btn_test_key"):
                if entered_key.strip():
                    chatbot.update_api_key(entered_key.strip())
                    with st.spinner("Testing API connection..."):
                        ok, msg = chatbot.test_connection(model=selected_model)
                        if ok:
                            st.success("Connection verified!")
                        else:
                            st.error(msg)
                else:
                    st.error("Please provide a key to test.")

        st.markdown(
            """
            <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 0.5rem; line-height: 1.4;">
                Get a free key from <a href="https://aistudio.google.com/app/apikey" target="_blank" style="color: #38BDF8; text-decoration: underline;">Google AI Studio</a>.
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Chat Actions (Clear Current Chat)
    with st.expander("🛠️  Chat Options", expanded=False):
        if st.button("🗑️  Clear Current Chat", use_container_width=True, key="btn_clear_chat"):
            clear_current_chat()
            st.rerun()

        # Download conversation transcript as Markdown
        current_chat = get_current_chat()
        if current_chat["messages"]:
            md_transcript = f"# {APP_NAME} - Conversation Transcript\n"
            md_transcript += f"**Title:** {current_chat['title']}\n"
            md_transcript += f"**Date:** {current_chat['created_at']}\n\n---\n\n"
            for m in current_chat["messages"]:
                speaker = "User" if m["role"] == "user" else "TripMate AI"
                md_transcript += f"### {speaker}:\n{m['content']}\n\n"

            st.download_button(
                label="📥  Export Conversation (MD)",
                data=md_transcript,
                file_name=f"TripMate_{current_chat['title'][:20].replace(' ', '_')}.md",
                mime="text/markdown",
                use_container_width=True,
            )

    # Minimal About Section
    st.markdown(
        """
        <div style="margin-top: 1.5rem; padding: 0.75rem; background: #0F172A; border-radius: 8px; border: 1px solid #1E293B;">
            <p style="font-size: 0.75rem; font-weight: 600; color: #F1F5F9; margin-bottom: 0.25rem;">TripMate AI v2.0</p>
            <p style="font-size: 0.7rem; color: #94A3B8; margin: 0; line-height: 1.35;">
                General-purpose intelligence with travel & exploration superpowers. Powered by Google Gemini SDK.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# Main Chat Area & Welcome Interface
# -----------------------------------------------------------------------------
current_chat = get_current_chat()
messages = current_chat["messages"]

# If no messages in the current chat, display the Minimal Welcome Screen
if not messages:
    st.markdown(
        f"""
        <div class="welcome-container">
            <div class="badge-tag">{APP_ICON} {APP_NAME}</div>
            <div class="welcome-title">{WELCOME_TITLE}</div>
            <div class="welcome-subtitle">{WELCOME_SUBTITLE}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # If API key is missing, show a sleek setup card right on the welcome screen
    if not chatbot.is_configured():
        st.markdown(
            """
            <div class="info-box" style="max-width: 780px; margin: 0 auto 2rem auto;">
                <div style="font-weight: 600; font-size: 0.95rem; margin-bottom: 0.4rem; color: #38BDF8;">
                    🔑 Gemini API Key Setup Required
                </div>
                <div style="font-size: 0.85rem; color: #CBD5E1; line-height: 1.5;">
                    To chat with TripMate AI, configure your free Google Gemini API key:
                    <ol style="margin: 0.4rem 0 0.4rem 1.2rem; padding: 0;">
                        <li>Obtain your free API key at <a href="https://aistudio.google.com/app/apikey" target="_blank" style="color: #38BDF8; font-weight: 600;">Google AI Studio</a>.</li>
                        <li>Add it to your <code>.env</code> file (<code>GEMINI_API_KEY=your_key</code>) or enter it in the sidebar settings.</li>
                    </ol>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Suggested Prompts (2x2 grid)
    st.markdown(
        "<div style='max-width: 780px; margin: 0 auto 0.75rem auto; font-size: 0.85rem; font-weight: 600; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em;'>Suggested Topics</div>",
        unsafe_allow_html=True,
    )

    prompt_cols_1 = st.columns(2)
    prompt_cols_2 = st.columns(2)
    all_cols = prompt_cols_1 + prompt_cols_2

    for idx, item in enumerate(SUGGESTED_PROMPTS):
        col = all_cols[idx]
        with col:
            btn_text = f"{item['icon']}  {item['title']}\n\n_{item['description']}_"
            if st.button(
                btn_text,
                key=f"prompt_btn_{idx}",
                use_container_width=True,
            ):
                st.session_state.pending_prompt = item["prompt"]
                st.rerun()

    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

else:
    # Render Existing Chat Messages
    for msg in messages:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant", avatar=APP_ICON):
                st.markdown(msg["content"])


# -----------------------------------------------------------------------------
# Chat Input & Response Handling
# -----------------------------------------------------------------------------
user_prompt = st.chat_input("Ask TripMate AI anything (e.g., travel plans, coding, science, explanations)...")

# If user clicked a suggested prompt card, consume it as the active prompt
if not user_prompt and st.session_state.pending_prompt:
    user_prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None

# Process User Prompt
if user_prompt:
    # Check if API Key is configured before processing
    if not chatbot.is_configured():
        # Display user message first
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_prompt)

        with st.chat_message("assistant", avatar=APP_ICON):
            st.error(
                "🔑 **Gemini API Key Required**\n\n"
                "TripMate AI requires an active Google Gemini API key to generate responses.\n\n"
                "**How to configure:**\n"
                "1. Get your free key at [Google AI Studio](https://aistudio.google.com/app/apikey).\n"
                "2. Open the **⚙️ Gemini API Configuration** expander in the sidebar on the left.\n"
                "3. Paste your key and click **Save Key** (or add `GEMINI_API_KEY=your_key` to your `.env` file)."
            )
    else:
        # Auto-title conversation from first prompt if still named "New Chat"
        if current_chat["title"] == "New Chat":
            current_chat["title"] = auto_generate_title(user_prompt)

        # 1. Append User Message
        current_chat["messages"].append({"role": "user", "content": user_prompt})

        # 2. Render User Message
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_prompt)

        # 3. Stream AI Response
        with st.chat_message("assistant", avatar=APP_ICON):
            try:
                # Pass conversation history excluding the just-appended prompt
                history_for_model = current_chat["messages"][:-1]

                response_stream = chatbot.stream_response(
                    history=history_for_model,
                    new_prompt=user_prompt,
                    model=st.session_state.selected_model,
                )

                full_response = st.write_stream(response_stream)

                # Append assistant response to history
                current_chat["messages"].append({"role": "assistant", "content": full_response})

            except MissingAPIKeyError as e:
                st.error(f"🔑 **Missing API Key:** {str(e)}")
            except AuthenticationError as e:
                st.error(f"🚫 **Authentication Failed:** {str(e)}")
            except RateLimitError as e:
                st.warning(f"⏳ **Rate Limit Exceeded:** {str(e)}")
            except NetworkError as e:
                st.error(f"🌐 **Network Error:** {str(e)}")
            except TripMateError as e:
                st.error(f"⚠️ **Error:** {str(e)}")
            except Exception as e:
                st.error(f"❌ **Unexpected Error:** {str(e)}")
