# WGM — AI Personal Automation Assistant

> A cross-platform AI-powered automation assistant built in Python, inspired by J.A.R.V.I.S-style interaction and workflow automation.

WGM is designed to help control and interact with your computer using natural commands, voice input, automation tools, and AI models. The project started as an experiment combining conversational AI with real desktop control and gradually evolved into a full personal assistant system.

Unlike normal chatbot projects, WGM focuses more on desktop interaction, automation, workflow assistance, and practical daily-use tools. The assistant handles both conversational AI tasks and real operating-system-level actions.

---

# What WGM Can Do

## AI Conversations

WGM can answer questions, explain concepts, summarize topics, and hold natural conversations using OpenRouter AI models.

```
"Explain black holes"
"Give me a summary of quantum computing"
"Give me a report on India GDP"
```

---

## Voice Command Support

The assistant supports microphone-based voice interaction for hands-free control.

```
"Open Spotify"
"Search latest AI news"
"Take screenshot"
```

---

## Web UI (Browser Interface)

WGM includes a cyberpunk-styled web interface you can open in any browser — on your laptop or any device on the same network.

```
python3 web/server.py
```

Then open: `http://localhost:5000`

Features of the web UI:
- Typewriter-style WGM responses
- Text-to-speech output in the browser
- Voice input via microphone
- Live clock and session HUD
- Quick command chips
- Works on mobile on the same Wi-Fi

---

## Web Search + Information

WGM can search the web, fetch information, and provide quick responses from online sources.

- AI-assisted web search via DuckDuckGo and Google
- Weather reports for any city
- News fetching
- Wikipedia integration

---

## File Searching

Search local files directly through commands.

```
"Find all PDF files"
"Search for my resume"
```

---

## App + Website Launcher

Launch installed applications or websites quickly using commands.

Supported examples: VS Code, Spotify, Chrome, YouTube, GitHub, Netflix, Figma, and many more.

---

## System Controls

WGM can interact with basic system functionality like volume controls, screenshots, app launching, time/date access, and desktop automation tasks.

---

# Project Structure

```
WGM-AI-PERSONAL-ASSISTANT/
├── wgm_all_devices.py     ← main assistant brain
├── requirements.txt
├── SETUP.txt
└── web/
    ├── server.py          ← Flask web server
    ├── static/
    │   ├── app.js
    │   └── style.css
    └── templates/
        └── index.html
```

---

# AI Models Used

WGM uses OpenRouter for accessing multiple AI models with automatic fallback support. The assistant tries models in sequence if one fails or becomes unavailable.

**Current Model Pipeline:**

```
1. qwen/qwen3-8b:free
2. meta-llama/llama-3.3-70b-instruct:free
3. google/gemma-3-27b-it:free
4. mistralai/mistral-7b-instruct:free
5. openrouter/auto
```

| Model           | Purpose                                              |
| --------------- | ---------------------------------------------------- |
| Qwen 3 8B       | Primary fast-response conversational model           |
| Llama 3.3 70B   | Larger reasoning and instruction-following fallback  |
| Gemma 3 27B     | Alternative balanced conversational model            |
| Mistral 7B      | Lightweight backup model                             |
| OpenRouter Auto | Final automatic routing fallback                     |

The fallback system keeps the assistant functional even if specific providers are temporarily unavailable.

---

# Platforms Supported

| Platform | Voice Mode | Web UI |
| -------- | ---------- | ------ |
| macOS    | ✅          | ✅      |
| Windows  | ✅          | ✅      |
| Linux    | ✅          | ✅      |

---

# Technologies Used

- Python 3.9+
- Flask (web UI server)
- OpenRouter API
- SpeechRecognition
- pyttsx3
- PyAutoGUI
- Requests
- Wikipedia API
- pyjokes

---

# How to Run WGM Locally

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/HI-dot935/WGM-AI-PERSONAL-ASSISTANT.git
cd WGM-AI-PERSONAL-ASSISTANT
```

---

## 2️⃣ Install Dependencies

**macOS** — run this first:
```bash
brew install portaudio
pip3 install -r requirements.txt
```

**Windows:**
```bash
pip install -r requirements.txt
```

**Linux:**
```bash
sudo apt install portaudio19-dev python3-pyaudio espeak ffmpeg
pip3 install -r requirements.txt
```

---

## 3️⃣ Add Your OpenRouter API Key

Get a free key at [openrouter.ai](https://openrouter.ai) → Keys → Create Key

Open `wgm_all_devices.py` and paste your key:

```python
OPENROUTER_API_KEY = "your-api-key-here"
```

---

## 4️⃣ Run the Assistant

**Voice mode (terminal):**
```bash
python3 wgm_all_devices.py
```

**Web UI (browser):**
```bash
python3 web/server.py
```
Then open `http://localhost:5000` in your browser.
To access from another device on the same Wi-Fi, use the Network URL printed in the terminal.

---

# Example Commands

```bash
# Quick test without mic
python3 wgm_all_devices.py "open youtube"
python3 wgm_all_devices.py "weather in Pune"
python3 wgm_all_devices.py "find all pdf files"
python3 wgm_all_devices.py "latest AI news"
python3 wgm_all_devices.py "what time is it"
```

---

# Performance Notes

Performance depends on internet speed, API response times, and hardware. The assistant was tested on older hardware, so some larger AI responses may take longer depending on the selected model. Voice recognition and automation speed can also vary across operating systems.

---

# Project Status

WGM is still actively evolving. Current focus areas include smarter automation, cleaner architecture, local AI integration, memory/context improvements, and more reliable cross-platform support. The project is primarily experimental and focused on learning, automation, and AI integration workflows.
