# WGM — AI Personal Automation Assistant

> A cross-platform AI-powered automation assistant built in Python inspired by J.A.R.V.I.S-style interaction and workflow automation.

WGM is designed to help control and interact with your computer using natural commands, voice input, automation tools, and AI models. The project started as an experiment around combining conversational AI with real desktop control and gradually evolved into a larger personal assistant system.

Unlike normal chatbot projects, WGM focuses more on:

* desktop interaction,
* automation,
* workflow assistance,
* and practical daily-use tools.

The assistant is capable of handling both conversational AI tasks and real operating-system-level actions.

---

# What WGM Can Do

## 🤖 AI Conversations

WGM can answer questions, explain concepts, summarize topics, and hold natural conversations using OpenRouter AI models.

Example:

```bash id="0odnyg"
"Explain black holes"
"Give me a summary of quantum computing"
```

---

## 🎙️ Voice Command Support

The assistant supports microphone-based voice interaction for hands-free control.

Example:

```bash id="v0pz91"
"Open Spotify"
"Search latest AI news"
"Take screenshot"
```

---

## 🌐 Web Search + Information

WGM can search the web, fetch information, and provide quick responses from online sources.

Features include:

* AI-assisted web search
* Weather reports
* News fetching
* Wikipedia integration

---

## 📂 File Searching

Search local files directly through commands.

Example:

```bash id="u4ql06"
"Find all PDF files"
"Search for my resume"
```

---

## 💻 App + Website Launcher

Launch installed applications or websites quickly using commands.

Supported examples:

* VS Code
* Spotify
* Chrome
* YouTube
* GitHub
* Netflix
* Figma
* and many more

---

## 🔊 System Controls

WGM can interact with basic system functionality like:

* volume controls,
* screenshots,
* app launching,
* time/date access,
* and desktop automation tasks.

---

# AI Models Used

WGM uses OpenRouter for accessing multiple AI models with automatic fallback support.

The assistant tries models in sequence if one fails or becomes unavailable.

## Current Model Pipeline

```python id="90rfhl"
1. qwen/qwen3-8b:free
2. meta-llama/llama-3.3-70b-instruct:free
3. google/gemma-3-27b-it:free
4. mistralai/mistral-7b-instruct:free
5. openrouter/auto
```

---

# Model Overview

| Model           | Purpose                                             |
| --------------- | --------------------------------------------------- |
| Qwen 3 8B       | Primary fast-response conversational model          |
| Llama 3.3 70B   | Larger reasoning and instruction-following fallback |
| Gemma 3 27B     | Alternative balanced conversational model           |
| Mistral 7B      | Lightweight backup model                            |
| OpenRouter Auto | Final automatic routing fallback                    |

The fallback system helps keep the assistant functional even if specific providers are temporarily unavailable.

---

# Performance Notes

Performance depends heavily on:

* internet speed,
* API response times,
* and hardware capabilities.

The assistant was tested mainly on older hardware during development, so some larger AI responses may take longer depending on the selected model.

Voice recognition and automation speed can also vary across operating systems.

---

# Platforms Supported

| Platform | Support |
| -------- | ------- |
| macOS    | ✅       |
| Windows  | ✅       |
| Linux    | ✅       |

---

# Technologies Used

Main technologies used in the project:

* Python
* OpenRouter API
* Gradio
* SpeechRecognition
* pyttsx3
* PyAutoGUI
* Requests
* Wikipedia API

---

# How to Run WGM Locally

## 1️⃣ Clone the Repository

```bash id="vwjlwm"
git clone https://github.com/Hi-dot935/WGM-AI-PERSONAL-ASSISTANT.git
cd WGM-AI-PERSONAL-ASSISTANT
```

---

## 2️⃣ Install Dependencies

```bash id="yftm4u"
pip install -r requirements.txt
```

---

## 3️⃣ Add OpenRouter API Key

Get a free API key from:

[OpenRouter](https://openrouter.ai?utm_source=chatgpt.com)

Then add your API key inside the Python configuration section:

```python id="58r33e"
OPENROUTER_API_KEY = "your-api-key"
```

---

## 4️⃣ Run the Assistant

```bash id="vbxuvv"
python WGM-ALL-DEVICES.py
```

---

# Example Commands

```bash id="2z0y1k"
python WGM-ALL-DEVICES.py "open youtube"
python WGM-ALL-DEVICES.py "weather in Pune"
python WGM-ALL-DEVICES.py "find all pdf files"
python WGM-ALL-DEVICES.py "latest AI news"
python WGM-ALL-DEVICES.py "what time is it"
```

---

# Project Status

WGM is still actively evolving and being improved over time.

Current focus areas include:

* smarter automation,
* cleaner architecture,
* local AI integration,
* memory/context improvements,
* and more reliable cross-platform support.

The project is primarily experimental and focused on learning, automation, and AI integration workflows.
