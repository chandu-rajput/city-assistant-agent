# =====================================================
# CITY ASSISTANT - STREAMLIT UI
# Run with:  streamlit run app.py
# =====================================================

import os
import requests
import streamlit as st   
from dotenv import load_dotenv

from langchain_mistralai import ChatMistralAI
from langchain.tools import tool
from langchain.agents import create_agent
from tavily import TavilyClient

# Read the .env file (API keys)
load_dotenv("Runnables\.env")

# =====================================================
# 1. TOOLS (same as before)
# =====================================================

@tool
def get_weather(city: str) -> str:
    """Get the current weather of a city in India."""

    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "Error: OpenWeather API key is missing."

    try:
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",  # API address
            params={"q": f"{city},IN", "appid": api_key, "units": "metric"},
            timeout=10,
        )

        # 404 = city not found
        if response.status_code == 404:
            return f"Error: City '{city}' was not found."

        response.raise_for_status()
        data = response.json()

    except requests.RequestException:
        return "Error: Could not connect to the weather service."

    # Pick the useful values out of the JSON
    description = data["weather"][0]["description"]
    temp = data["main"]["temp"]
    feels_like = data["main"]["feels_like"]
    humidity = data["main"]["humidity"]
    wind = data["wind"]["speed"]

    return (
        f"Weather in {city}: {description}, {temp}°C "
        f"(feels like {feels_like}°C), humidity {humidity}%, wind {wind} m/s"
    )


tavily_api_key = os.getenv("TAVILY_API_KEY")
tavily_client = TavilyClient(api_key=tavily_api_key) if tavily_api_key else None


@tool
def get_news(city: str) -> str:
    """Search the web for the latest news about a city."""

    if tavily_client is None:
        return "Error: Tavily API key is missing."

    try:
        response = tavily_client.search(
            query=f"latest news in {city}",
            topic="news",
            search_depth="basic",
            max_results=3,
        )
    except Exception:
        return "Error: Could not fetch news."

    results = response.get("results", [])
    if not results:
        return f"No news found for {city}."

    news_list = []
    for item in results:
        title = item.get("title", "No title")
        url = item.get("url", "")
        snippet = item.get("content", "")[:200]
        news_list.append(f"- {title}\n  Link: {url}\n  Summary: {snippet}")

    return f"Latest news about {city}:\n\n" + "\n\n".join(news_list)


# =====================================================
# 2. CREATE THE AGENT (only once)
# =====================================================

# @st.cache_resource = "build this once and reuse it".
# Streamlit re-runs the whole file on every click, so without this
# the agent would be rebuilt every time.
@st.cache_resource
def get_agent():
    llm = ChatMistralAI(model="ministral-14b-2512", temperature=0)

    return create_agent(
        model=llm,
        tools=[get_weather, get_news],
        system_prompt=(
            "You are a helpful city assistant. "
            "You can check weather and search for city news using tools. "
            "Use tools when needed. "
            "Answer clearly and concisely. "
            "Never invent weather data or news results. "
            "If a tool fails, explain that to the user."
        ),
    )


# =====================================================
# 3. PAGE SETUP
# =====================================================

st.set_page_config(page_title="City Assistant", page_icon="🏙️")
st.title("🏙️ City Assistant")
st.caption("Ask about the weather or the latest news of an Indian city.")

# Stop early with a clear message if the Mistral key is missing
if not os.getenv("MISTRAL_API_KEY"):
    st.error("MISTRAL_API_KEY is missing. Add it to your .env file.")
    st.stop()

agent = get_agent()


# =====================================================
# 4. MEMORY (session_state survives re-runs)
# =====================================================

# "messages" = history we send to the agent (needed for memory)
if "messages" not in st.session_state:
    st.session_state.messages = []

# "chat" = what we show on screen: {"role", "content", "tools"}
if "chat" not in st.session_state:
    st.session_state.chat = []

# Sidebar button to start a fresh conversation
with st.sidebar:
    st.header("Options")
    if st.button("🗑️ Clear chat"):
        st.session_state.messages = []
        st.session_state.chat = []
        st.rerun()
    st.markdown("**Try asking:**")
    st.markdown("- Weather in Mumbai?\n- News in Pune\n- Weather and news in Virar")


# =====================================================
# 5. SHOW THE OLD MESSAGES
# =====================================================

for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        # If tools were used for this answer, show them in a small box
        if msg.get("tools"):
            with st.expander("🔧 Tools used"):
                for t in msg["tools"]:
                    st.code(t)


# =====================================================
# 6. HANDLE A NEW QUESTION
# =====================================================

# st.chat_input shows the text box at the bottom.
# It gives the typed text, or None if nothing was sent.
user_input = st.chat_input("Ask about weather or news...")

if user_input:

    # Show the user's message right away
    st.session_state.chat.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Add it to the agent's history
    st.session_state.messages.append({"role": "user", "content": user_input})
    old_length = len(st.session_state.messages)

    with st.chat_message("assistant"):
        try:
            # Spinner = "loading..." animation while the agent works
            with st.spinner("Thinking..."):
                result = agent.invoke({"messages": st.session_state.messages})

            # Save the updated history (includes tool calls and results)
            st.session_state.messages = result["messages"]

            # The last message is the final answer
            answer = result["messages"][-1].content

            # Find which tools the AI called during THIS question
            tools_used = []
            for m in result["messages"][old_length:]:
                for call in getattr(m, "tool_calls", None) or []:
                    tools_used.append(f"{call['name']}({call['args']})")

            st.markdown(answer)

            if tools_used:
                with st.expander("🔧 Tools used"):
                    for t in tools_used:
                        st.code(t)

            # Save for display on the next re-run
            st.session_state.chat.append(
                {"role": "assistant", "content": answer, "tools": tools_used}
            )

        except Exception as error:
            st.error(f"Error: {error}")