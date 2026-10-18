# 🏙️ CityPulse Agent

An AI agent that provides **current weather and the latest news for Indian cities** through a chat interface.

Built using **LangChain, Mistral AI, OpenWeather API, Tavily API, and Streamlit**.

## 🖥️ UI Preview

![CityPulse Agent UI](assets)

## ✨ Features

- 💬 Chat-style web interface using Streamlit
- 🌦️ Retrieves current weather using the OpenWeather API
- 📰 Searches for the latest city news using the Tavily API
- 🧠 Maintains conversation history
- 🔧 Uses AI tools to retrieve information
- ✅ Includes terminal mode with human approval before tool execution

## 🛠️ Tech Stack

| Purpose | Technology |
|---|---|
| Programming language | Python |
| Agent framework | LangChain |
| Language model | Mistral AI |
| Weather data | OpenWeather API |
| News search | Tavily API |
| Web interface | Streamlit |

## 📁 Project Structure

```text
city_assistant-agent/
├── Agent.py
├── App.py
├── requirements.txt
├── README.md
└── assets/
    └── screenshot.png
```

**File descriptions:**
- `Agent.py` — Defines the AI agent, tools, and terminal chat functionality.
- `App.py` — Provides the Streamlit chat interface.
- `requirements.txt` — Lists the project's Python dependencies.
- `README.md` — Contains project documentation and setup instructions.

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- API keys for Mistral AI, OpenWeather, and Tavily

### 1. Clone the repository

Replace `YOUR-USERNAME` with your GitHub username.

```bash
git clone https://github.com/YOUR-USERNAME/city_assistant-agent.git
cd city_assistant-agent
```

### 2. Create and activate a virtual environment

If you're using `uv`, run:

```bash
uv sync
```

Alternatively, if you install dependencies using `requirements.txt`:

```bash
python -m venv .venv
```

On Windows:

```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure API keys

Create a `.env` file in the project folder and add your API keys:

```text
MISTRAL_API_KEY=your_key_here
OPENWEATHER_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
```

Get your keys from:

- **Mistral AI:** https://console.mistral.ai/
- **OpenWeather:** https://openweathermap.org/api
- **Tavily:** https://tavily.com/

Make sure `.env` is included in `.gitignore` so your API keys are not uploaded to GitHub.

### 4. Run the application

**Web interface:**

```bash
streamlit run App.py
```

**Terminal mode:**

```bash
python Agent.py
```

Terminal mode asks for approval before executing tools, while the web interface executes tools automatically.

## 💡 Example Questions

- What's the weather in Mumbai?
- What is the latest news in Pune?
- Give me the weather and latest news in Nagpur.

## ⚙️ How It Works

1. You enter a question in the chat interface or terminal.
2. The AI determines which tool or tools are needed.
3. The selected tool retrieves weather information or searches for news.
4. The AI uses the retrieved information to generate a response.

## 📝 Notes

- Run the project locally using your own API keys.
- API usage may be subject to provider limits or charges.
- Never upload your `.env` file or expose your API keys.
- The application requires a working internet connection to retrieve current information.
