import os

import requests
import streamlit as st
from dotenv import load_dotenv


# --------------------------------------------------
# Environment
# --------------------------------------------------

load_dotenv(override=True)

API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000/chat"
)
API_KEY = os.getenv("SMARTSHOP_API_KEY")


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="SmartShop AI",
    page_icon="🛍️",
    layout="centered"
)


# --------------------------------------------------
# Custom styling
# --------------------------------------------------

st.markdown(
    """
    <style>

    .block-container {
        max-width: 900px;
        padding-top: 2rem;
    }

    .smartshop-header {
        text-align: center;
        padding: 25px 10px 15px 10px;
    }

    .smartshop-header h1 {
        margin-bottom: 5px;
        font-size: 42px;
    }

    .smartshop-header p {
        font-size: 17px;
        color: #777;
    }

    .welcome-box {
        padding: 18px;
        border-radius: 12px;
        background-color: rgba(128,128,128,0.08);
        margin-bottom: 20px;
        text-align: center;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# Header
# --------------------------------------------------

st.markdown(
    """
    <div class="smartshop-header">
        <h1>🛍️ SmartShop AI</h1>
        <p>Your AI-powered shopping assistant</p>
    </div>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# Session state
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


if "suggested_prompt" not in st.session_state:
    st.session_state.suggested_prompt = None


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

with st.sidebar:

    st.title("SmartShop")

    st.caption(
        "AI-powered product recommendations, "
        "price comparisons, reviews and policies."
    )

    st.divider()

    st.subheader("Capabilities")

    st.write("💻 Product recommendations")
    st.write("💰 Price comparison")
    st.write("⭐ Product reviews")
    st.write("📦 Store policies")

    st.divider()

    if st.button(
        "🗑️ Clear conversation",
        use_container_width=True
    ):
        st.session_state.messages = []
        st.rerun()


# --------------------------------------------------
# Welcome area
# --------------------------------------------------

if not st.session_state.messages:

    st.markdown(
        """
        <div class="welcome-box">
            <h3>How can I help you today?</h3>
            <p>
                Search products, compare prices,
                check reviews or ask about store policies.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "💻 Find a laptop",
            use_container_width=True
        ):
            st.session_state.suggested_prompt = (
                "Find me the best laptop under $900 "
                "with at least 4 stars"
            )

        if st.button(
            "⭐ Check product reviews",
            use_container_width=True
        ):
            st.session_state.suggested_prompt = (
                "What do customers say about SP0001?"
            )

    with col2:

        if st.button(
            "💰 Compare prices",
            use_container_width=True
        ):
            st.session_state.suggested_prompt = (
                "Find smartphones under $800"
            )

        if st.button(
            "📦 Return policy",
            use_container_width=True
        ):
            st.session_state.suggested_prompt = (
                "Can I return my laptop after 20 days?"
            )


# --------------------------------------------------
# Display conversation history
# --------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# --------------------------------------------------
# User input
# --------------------------------------------------

typed_request = st.chat_input(
    "Ask SmartShop anything..."
)

user_request = (
    typed_request
    or st.session_state.suggested_prompt
)

st.session_state.suggested_prompt = None


# --------------------------------------------------
# FastAPI request
# --------------------------------------------------

if user_request:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_request
        }
    )

    with st.chat_message("user"):
        st.markdown(user_request)

    with st.chat_message("assistant"):

        with st.spinner(
            "SmartShop is finding the best answer..."
        ):

            try:

                api_response = requests.post(
                    API_URL,
                    json={
                        "message": user_request
                    },
                    headers={
                        "x-api-key": API_KEY
                    },
                    timeout=60
                )

                api_response.raise_for_status()

                data = api_response.json()

                response = data["response"]

            except requests.Timeout:

                response = (
                    "The request took longer than expected. "
                    "Please try again."
                )

            except requests.ConnectionError:

                response = (
                    "I can't connect to the SmartShop service "
                    "right now. Please try again shortly."
                )

            except requests.RequestException:

                response = (
                    "Something went wrong while processing "
                    "your request."
                )

        st.markdown(response)


    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )