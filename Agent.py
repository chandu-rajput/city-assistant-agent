"""CityPulse Agent: weather and news tools, the agent, and a terminal chat.

Run in the terminal:  python agent.py
The Streamlit UI (app.py) imports build_agent() from this file.
"""

import os
import requests
from dotenv import load_dotenv

from langchain_mistralai import ChatMistralAI
from langchain.tools import tool
from langchain_core.messages import ToolMessage
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call
from tavily import TavilyClient
from rich import print
from rich.markup import escape  # stops [brackets] being read as colours

# Load API keys from the .env file
load_dotenv()


# =========================
# 1. Weather tool
# =========================

@tool
def get_weather(city: str) -> str:
    """Get the current weather of a city in India."""
    # The docstring above is what the AI reads to decide when to use this tool.

    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "Error: OpenWeather API key is missing."

    try:
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q": f"{city},IN", "appid": api_key, "units": "metric"},
            timeout=10,
        )

        # 404 means the city name was not recognised
        if response.status_code == 404:
            return f"Error: City '{city}' was not found."

        response.raise_for_status()
        data = response.json()

    except requests.RequestException:
        return "Error: Could not connect to the weather service."

    # data["weather"] is a list, so take the first item
    description = data["weather"][0]["description"]
    temp = data["main"]["temp"]
    feels_like = data["main"]["feels_like"]
    humidity = data["main"]["humidity"]
    wind = data["wind"]["speed"]

    return (
        f"Weather in {city}: {description}, {temp}°C "
        f"(feels like {feels_like}°C), humidity {humidity}%, wind {wind} m/s"
    )


# =========================
# 2. News tool
# =========================

# The client is created only if the key exists
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


# =========================
# 3. Human approval (terminal only)
# =========================

@wrap_tool_call
def human_approval(request, handler):
    """Ask for approval before any tool runs.

    LangChain calls this automatically and passes in:
      request = what the AI wants to do (tool name and arguments)
      handler = a function that runs the real tool
    """
    tool_name = request.tool_call["name"]
    tool_args = request.tool_call["args"]

    confirm = input(
        f"\nAgent wants to call '{tool_name}' with {tool_args}. Approve? (yes/no): "
    )

    if confirm.strip().lower() not in ("yes", "y"):
        # Return a "denied" message to the AI instead of running the tool
        return ToolMessage(
            content="Tool call denied by user.",
            tool_call_id=request.tool_call["id"],
            name=tool_name,
        )

    return handler(request)


# =========================
# 4. Build the agent
# =========================

def build_agent(require_approval: bool = True):
    """Create the agent.

    require_approval=True  -> asks in the terminal before each tool call
    require_approval=False -> no prompt (used by the Streamlit UI, because
                              input() cannot work inside a browser app)
    """
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
            "If a tool fails or is denied, explain that to the user."
        ),
        middleware=[human_approval] if require_approval else [],
    )


# =========================
# 5. Terminal chat
# =========================

def main():
    agent = build_agent(require_approval=True)

    # Full conversation history, so the bot remembers earlier messages
    messages = []

    print("[bold green]CityPulse Agent[/bold green]")
    print("Ask about weather or latest city news.")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        if not user_input:
            continue

        try:
            messages.append({"role": "user", "content": user_input})
            result = agent.invoke({"messages": messages})

            # The result holds the updated history; the last message is the answer
            messages = result["messages"]

            print("\n[bold cyan]Bot:[/bold cyan]")
            print(escape(messages[-1].content))
            print()

        except Exception as error:
            print(f"[bold red]Error:[/bold red] {escape(str(error))}")


# This runs only with "python agent.py", never when app.py imports this file
if __name__ == "__main__":
    main()