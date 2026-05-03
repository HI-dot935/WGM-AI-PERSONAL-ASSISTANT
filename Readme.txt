<div align="center">

# 🤖 W.G.M — AI Voice Assistant

### *Your personal J.A.R.V.I.S — powered by free AI*

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey?style=for-the-badge)
![AI](https://img.shields.io/badge/AI-OpenRouter%20Free-6C63FF?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)

<br/>

> **WGM** is a fully voice-controlled AI assistant that runs locally on your machine.  
> It listens to you, thinks, searches the web, controls your system, and talks back —  
> all for **completely free**, using OpenRouter's free AI tier.

<br/>

</div>

---

## ✨ Features

| Category | What it can do |
|---|---|
| 🧠 **AI Reasoning** | Answer anything — coding, maths, general knowledge, problem solving |
| 🌐 **Web Search** | DuckDuckGo instant answers + Google snippet scraping, no key needed |
| 📖 **Wikipedia** | Summarise any topic instantly |
| 🌤️ **Weather** | Live weather for any city (browser fallback if no API key) |
| 📰 **News** | Latest headlines via Google News |
| 🖥️ **App Launcher** | Open any app or website by voice — even specifically in Chrome |
| 🎵 **Music** | Play songs from your local Music folder |
| 📸 **Screenshot** | Capture screen and save to Desktop |
| 🔊 **Volume Control** | Up, down, max, mute, unmute |
| 📡 **WiFi Status** | Check which network you're connected to |
| 🎭 **Personality** | 80+ instant replies for casual chat, jokes, banter |
| 💬 **Memory** | Remembers your conversation within a session |
| 🔄 **Auto Fallback** | Tries 6 free AI models automatically if one is rate-limited |

---

## 🚀 Quick Start

### 1. Get a free OpenRouter API key
Go to [openrouter.ai](https://openrouter.ai) → Sign up → **Keys** → **Create Key**  
Copy the key — it looks like `sk-or-v1-xxxxxxxxxx`

### 2. Paste your key in `jarvis.py`
Open `jarvis.py` and find line ~73:
```python
OPENROUTER_API_KEY = "paste-your-key-here"
```

### 3. Install dependencies

**macOS:**
```bash
brew install portaudio
pip3 install -r requirements.txt
```

**Windows:**
```bash
pip install -r requirements.txt
pip install pycaw comtypes   # optional — for volume control
```

**Linux:**
```bash
sudo apt install portaudio19-dev python3-pyaudio espeak scrot
pip3 install -r requirements.txt
```

### 4. Run it
```bash
python3 jarvis.py         # macOS / Linux
python jarvis.py          # Windows
```

### 5. Quick test (no mic needed)
```bash
python3 jarvis.py "what time is it"
python3 jarvis.py "what is 1 + 1"
python3 jarvis.py "give me a report on India GDP"
```

---

## 🗣️ What You Can Say

### System & Info
```
what time is it
what's today's date
what's the wifi
take a screenshot
volume up / volume down / mute / unmute / max volume
```

### Search & Knowledge
```
search for quantum computing
google what is the best laptop 2026
wikipedia Elon Musk
what is machine learning
give me a report on India's GDP
summarise the news on AI
what happened with Apple today
```

### Weather
```
what's the weather
weather in Mumbai
how hot is it in London
will it rain in Pune today
```

### Open Apps & Websites
```
open spotify
open terminal
open youtube
open github in chrome
open instagram on chrome
open netflix
open google docs
launch vs code
go to stackoverflow
```

### YouTube & Chrome
```
search youtube for lo-fi music
search in chrome for best python tutorials
open chrome and search for iPhone 16
```

### Music & Media
```
play music
play some music
play song shape of you
```

### Casual Chat
```
hey / hello / what's up
how are you
tell me a joke
tell me something interesting
random fact
entertain me
```

### AI & Memory
```
write me a python function to sort a list
explain how neural networks work
calculate 15 percent of 3400
clear memory
```

---

## 🤖 AI Models — Full Breakdown

WGM uses **OpenRouter** to access free AI models. It automatically tries all 6 models in order if one is rate-limited or down.

> **Rate limits on free models:** ~20 requests/minute, ~200 requests/day per model.  
> With 6 models in rotation, you effectively get 6x that before hitting any wall.

---

### 🥇 `qwen/qwen3-8b:free` ← **THE BEST FREE MODEL RIGHT NOW**

| Property | Detail |
|---|---|
| **Made by** | Alibaba (Qwen Team) |
| **Size** | 8 billion parameters |
| **Context** | 128K tokens |
| **Strengths** | Exceptional reasoning, coding, maths, multilingual, fast |
| **Why it's #1** | Best overall quality-to-speed ratio among all free models. Handles everything from casual chat to complex analysis. Beats models 3x its size on benchmarks. Fast response time. Rarely rate-limited. |
| **Best for** | Everything — this should be your daily driver |

---

### 🥈 `deepseek/deepseek-chat:free`

| Property | Detail |
|---|---|
| **Made by** | DeepSeek AI (China) |
| **Size** | ~67B parameters (MoE architecture) |
| **Context** | 64K tokens |
| **Strengths** | Exceptional at coding, logic, maths, step-by-step reasoning |
| **Why it's #2** | One of the smartest free models available. DeepSeek V3 was the model that shocked the AI world in late 2024 by matching GPT-4 level performance at near-zero cost. Slightly slower than Qwen3 but more thorough on complex tasks. |
| **Best for** | Coding help, debugging, detailed analysis, reports |

---

### 🥉 `google/gemma-3-12b-it:free`

| Property | Detail |
|---|---|
| **Made by** | Google DeepMind |
| **Size** | 12 billion parameters |
| **Context** | 128K tokens |
| **Strengths** | Safe, reliable, good general knowledge, fast |
| **Why it's #3** | Google's open-source model. Very consistent — rarely gives weird or off-topic answers. Great for factual Q&A and general conversation. Not as sharp as DeepSeek on hard problems but very dependable. |
| **Best for** | General conversation, factual questions, casual use |

---

### 4️⃣ `meta-llama/llama-3.2-3b-instruct:free`

| Property | Detail |
|---|---|
| **Made by** | Meta (Facebook) |
| **Size** | 3 billion parameters |
| **Context** | 128K tokens |
| **Strengths** | Extremely fast, lightweight, conversational |
| **Why it's #4** | Meta's Llama 3 family is the backbone of open-source AI. The 3B version is tiny but surprisingly capable for simple tasks. It's the fastest model in the list — great when you just want a quick answer. |
| **Best for** | Quick replies, casual chat, simple questions |

---

### 5️⃣ `mistralai/mistral-small-3.1-24b-instruct:free`

| Property | Detail |
|---|---|
| **Made by** | Mistral AI (France) |
| **Size** | 24 billion parameters |
| **Context** | 128K tokens |
| **Strengths** | Great at instruction following, writing, structured responses |
| **Why it's #5** | Mistral is known for punching above its weight. The 24B model is genuinely impressive at following complex instructions and writing well-structured responses. Good fallback when the top models are busy. |
| **Best for** | Writing tasks, structured outputs, detailed instructions |

---

### 6️⃣ `microsoft/phi-3-mini-128k-instruct:free`

| Property | Detail |
|---|---|
| **Made by** | Microsoft Research |
| **Size** | 3.8 billion parameters |
| **Context** | 128K tokens (massive!) |
| **Strengths** | Incredibly long context window for its size, efficient |
| **Why it's #6** | Microsoft's Phi series proved that small models trained on quality data can compete with much larger ones. The 128K context window is the standout — it can handle very long conversations without forgetting. Used as the last resort fallback. |
| **Best for** | Long conversations, documents with lots of context |

---

### 🎯 Special: `openrouter/free` (what the code currently uses)

This is OpenRouter's smart auto-router — it randomly selects from available free models, intelligently filtering for models that support the features your request needs, such as image understanding, tool calling, and structured outputs.

It's like having all models at once. When you don't care which model answers, this is the simplest option. The code has it set as a fallback and also includes specific models so you can control exactly which one runs.

---

### 📊 Quick Comparison Table

| Model | Speed | Smarts | Coding | Chat | Best for |
|---|---|---|---|---|---|
| **Qwen3 8B** ⭐ | ⚡⚡⚡ | ★★★★★ | ★★★★★ | ★★★★★ | Everything |
| **DeepSeek Chat** | ⚡⚡ | ★★★★★ | ★★★★★ | ★★★★ | Code & analysis |
| **Gemma 3 12B** | ⚡⚡⚡ | ★★★★ | ★★★ | ★★★★★ | General use |
| **Llama 3.2 3B** | ⚡⚡⚡⚡ | ★★★ | ★★★ | ★★★★ | Quick replies |
| **Mistral Small** | ⚡⚡ | ★★★★ | ★★★★ | ★★★★ | Writing |
| **Phi-3 Mini** | ⚡⚡⚡ | ★★★ | ★★★ | ★★★ | Long context |

---

## 🔧 Changing the AI Model

Open `jarvis.py` and find the `OPENROUTER_MODELS` list near the top:

```python
OPENROUTER_MODELS = [
    "qwen/qwen3-8b:free",                              # ← Best overall (recommended)
    "deepseek/deepseek-chat:free",                     # ← Best for coding & reasoning
    "google/gemma-3-12b-it:free",                      # ← Most reliable
    "meta-llama/llama-3.2-3b-instruct:free",           # ← Fastest
    "mistralai/mistral-small-3.1-24b-instruct:free",   # ← Best writing
    "microsoft/phi-3-mini-128k-instruct:free",         # ← Longest context
]
```

The first model in the list is always tried first. Rearrange to change priority. All available free models: [openrouter.ai/models?q=free](https://openrouter.ai/models?q=free)

---

## 🎙️ Voice Settings

Open `jarvis.py` and find:

```python
VOICE_NAME  = "Samantha"   # Change this
VOICE_RATE  = 178          # Words per minute
```

**Best macOS voices for a Jarvis feel:**

| Voice | Style | Command to preview |
|---|---|---|
| `Daniel` | Deep British male — most JARVIS-like ✅ | `say -v Daniel "Hello sir"` |
| `Samantha` | Clear US female — current default | `say -v Samantha "Hello sir"` |
| `Alex` | US male, natural | `say -v Alex "Hello sir"` |
| `Victoria` | British female | `say -v Victoria "Hello sir"` |
| `Tom` | British male | `say -v Tom "Hello sir"` |

Run `say -v ?` in Terminal to see all voices installed on your Mac.

---

## 📁 Project Structure

```
WGM-Voice-Assistant/
│
├── jarvis.py           # Main assistant file — everything is here
├── requirements.txt    # Python dependencies
├── README.md           # This file
│
└── ~/.wgm_name         # Auto-created — stores your custom assistant name
```

---

## ⚙️ Optional: Weather API

For spoken weather (instead of opening browser):

1. Sign up free at [openweathermap.org](https://openweathermap.org/api)
2. Copy your API key
3. Paste it in `jarvis.py`:
```python
WEATHER_API_KEY = "your-openweathermap-key-here"
DEFAULT_CITY    = "Pune"   # your default city
```

---

## 🛠️ Requirements

```
SpeechRecognition~=3.10.4
requests~=2.31.0
wikipedia~=1.4.0
pyjokes==0.6.0
pyttsx3~=2.90
pyaudio~=0.2.14
```

**Windows only (volume control):**
```
pycaw==20230625
comtypes~=1.2.0
```

**Windows/Linux (screenshots):**
```
pyautogui~=0.9.54
```

---

## 🐛 Common Issues

**"Microphone unavailable"**
```bash
# macOS
brew install portaudio
pip3 install pyaudio

# Linux
sudo apt install portaudio19-dev
pip3 install pyaudio
```

**"AI is not configured"**  
→ You haven't pasted your OpenRouter key yet. Open `jarvis.py` line ~73.

**"All AI models unavailable"**  
→ All 6 free models hit rate limits simultaneously (rare). Wait 1-2 minutes and try again, or sign up for OpenRouter credits ($5 lasts months).

**Speech not recognised**  
→ Check your mic is set as default input in System Preferences → Sound → Input.

**`pyttsx3` errors on macOS**  
→ macOS uses the native `say` command, so `pyttsx3` is not needed and any errors from it can be ignored.

---

## 📝 License

MIT License — free to use, modify, and distribute.

---

## 🙏 Built With

- [OpenRouter](https://openrouter.ai) — free AI model access
- [DuckDuckGo API](https://duckduckgo.com) — free web search
- [Wikipedia Python](https://wikipedia.readthedocs.io) — encyclopaedia lookups
- [SpeechRecognition](https://github.com/Uberi/speech_recognition) — voice input
- [macOS `say` command](https://ss64.com/osx/say.html) — text to speech

---

<div align="center">

**Made with ❤️ — WGM Voice Assistant**

*Just speak. It listens.*

</div>