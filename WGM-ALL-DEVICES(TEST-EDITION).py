"""

╔══════════════════════════════════════════════════════════════╗

║   W G M  —  AI Voice Assistant  v4.0  (Cross-Platform)      ║

║   Windows 10/11 · macOS 10.15+ · Linux (Ubuntu 20+)         ║

║   Python 3.9+                                                ║

║   Powered by OpenRouter · DuckDuckGo · Wikipedia             ║

╚══════════════════════════════════════════════════════════════╝



HOW TO RUN:

  1. Paste your OpenRouter key on the line below (OPENROUTER_API_KEY)

  2. pip install -r requirements.txt

  3. python jarvis.py



QUICK TEST (no mic):

  python jarvis.py "what time is it"

  python jarvis.py "what is 1 + 1"

  python jarvis.py "give me a report on India GDP"



PLATFORM NOTES:

  Windows : pyttsx3 (SAPI5 voices), ctypes/pycaw volume,

            pyautogui screenshots, netsh wifi, os.startfile app launch

  macOS   : say command (Samantha voice), osascript volume,

            screencapture screenshots, airport wifi, open -a app launch

  Linux   : pyttsx3 (espeak), amixer volume,

            scrot screenshots, iwgetid wifi, xdg-open app launch

"""



import datetime

import os

import random

import re

import subprocess

import sys

import webbrowser as wb

from html.parser import HTMLParser

from urllib.parse import quote_plus



import pyjokes

import requests

# ── Universal Python version compatibility shim ───────────────────────────────
# Python 3.13 removed aifc, audioop, sunau, chunk (PEP 594).
# Python 3.9–3.12 already have them — the shim only kicks in when missing.
# Safe to run on ANY Python version (3.9, 3.10, 3.11, 3.12, 3.13+).
import sys as _sys
import types as _types

for _mod_name in ("aifc", "audioop", "sunau", "chunk"):
    try:
        __import__(_mod_name)          # already exists — do nothing
    except ImportError:
        _sys.modules[_mod_name] = _types.ModuleType(_mod_name)   # stub it
# ──────────────────────────────────────────────────────────────────────────────

import speech_recognition as sr

import wikipedia

import platform


try:
    import pyttsx3
    _PYTTSX3_AVAILABLE = True
except ImportError:
    _PYTTSX3_AVAILABLE = False

# Detect OS once at startup
OS = platform.system()   # "Windows", "Darwin" (macOS), "Linux"



# ══════════════════════════════════════════════════════════════

#  ① CONFIGURATION — edit these lines

# ══════════════════════════════════════════════════════════════



# Paste your free OpenRouter key here → openrouter.ai → Keys → Create Key

OPENROUTER_API_KEY = "your api key"



# Optional: free weather key from openweathermap.org

WEATHER_API_KEY = ""

DEFAULT_CITY    = "(set it)"



# ── Voice ──────────────────────────────────────────────────────

# Run  say -v ?  in Terminal to list all installed voices.

# Best Jarvis-like voices on Catalina (British / deep):

#   Daniel  → deep British male  ← most JARVIS-like ✓

#   Alex    → US male

#   Tom     → British male (older macOS)

#   Fred    → robotic, retro

VOICE_NAME  = "Samantha"  # Female US voice — change with `say -v ?` (try: Ava, Victoria, Kate)

VOICE_RATE  = 178         # words per minute  (160 = measured, 190 = brisk)



# ── AI model ───────────────────────────────────────────────────

OPENROUTER_URL    = "https://openrouter.ai/api/v1/chat/completions"

# Tried in order — auto-falls back if one is rate-limited or down
OPENROUTER_MODELS = [
    "qwen/qwen3-8b:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemma-3-27b-it:free",
    "mistralai/mistral-7b-instruct:free",
    "openrouter/auto",
]
   


# ── Paths ──────────────────────────────────────────────────────

NAME_FILE      = os.path.expanduser("~/.wgm_name")

if OS == "Windows":
    MUSIC_DIR      = os.path.join(os.path.expanduser("~"), "Music")
    SCREENSHOT_DIR = os.path.join(os.path.expanduser("~"), "Desktop")
    CHROME_APP     = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
elif OS == "Darwin":
    MUSIC_DIR      = os.path.expanduser("~/Music")
    SCREENSHOT_DIR = os.path.expanduser("~/Desktop")
    CHROME_APP     = "/Applications/Google Chrome.app"
else:  # Linux
    MUSIC_DIR      = os.path.expanduser("~/Music")
    SCREENSHOT_DIR = os.path.expanduser("~/Desktop")
    CHROME_APP     = "/usr/bin/google-chrome"



# ══════════════════════════════════════════════════════════════

#  ② AI PERSONALITY — system prompt

# ══════════════════════════════════════════════════════════════

SYSTEM_PROMPT = (

    "You are WGM, a highly intelligent and warm AI voice assistant — think a mix of J.A.R.V.I.S and a smart friend. "

    "You are witty, efficient, slightly formal when needed, and occasionally dry-humoured. "

    "Your responses are spoken aloud via text-to-speech. Follow these rules carefully:\n\n"



    "── RESPONSE LENGTH ──\n"

    "Rule 1 DEFAULT: For ALL casual chat, greetings, small talk, simple questions, quick facts, "

    "confirmations, reactions — keep your reply UNDER 80 WORDS. Be punchy and natural. Do not pad.\n"

    "Rule 2 DETAIL MODE: Only go beyond 80 words when the user explicitly asks using words like: "

    "explain, describe, tell me more, in detail, summarise, summarize, break it down, "

    "give me a detailed report, analyse, analyze, go deeper, elaborate, full picture. "

    "In detail mode, be thorough and complete — do not cut short.\n\n"



    "── FORMAT ──\n"

    "Rule 3: Never use markdown, bullet points, asterisks, hashtags, or code fences. Plain spoken sentences only.\n"

    "Rule 4: Occasionally address the user as sir but do not overdo it.\n"

    "Rule 5: For maths, work through it step by step in plain English.\n"

    "Rule 6: For code, describe what it does verbally — never paste code.\n\n"



    "── PERSONALITY ──\n"

    "Rule 7: For casual talk — be warm, natural, a little flirty. "

    "Use phrases like Oh totally, Yeah for sure, honestly, haha, no worries, right. "

    "Sound like a smart friend, not a robot reading a manual.\n"

    "Rule 8: Think like GPT — understand intent, not just literal words.\n"

    "Rule 9: Be confident, helpful, knowledgeable, and personable.\n\n"



    "── DATA REPORT SKILL ──\n"

    "When asked to make a report or give a report on any topic: "

    "First state the topic and timeframe. Then cover the key numbers or metrics. "

    "Then explain what those numbers mean — trends, rises, falls, comparisons. "

    "Then give the main cause. Then state the impact. Finally a one-sentence bottom line. "

    "No bullet points, no headers — smooth spoken transitions only.\n\n"



    "── NEWS SUMMARY SKILL ──\n"

    "When asked to summarise news or cover what is happening with a topic: "

    "Start with one sentence on what the story is. Then give 3 to 5 spoken points — "

    "what happened, who is involved, why it matters, the reaction, and what to watch next. "

    "End with a brief one-line observation.\n\n"



    "Rule 10: You run inside a Python app on the users Mac. "

    "The app handles time, date, wifi, screenshots, volume natively. "

    "Never say you do not have access to the system clock or real-time data."

)



# Conversation memory within a session

_history = []



# ══════════════════════════════════════════════════════════════
#  LOCAL INSTANT CACHE — zero API latency for common phrases
#  Replies instantly without any API call.
# ══════════════════════════════════════════════════════════════
_INSTANT: dict = {

    # ── Greetings ──────────────────────────────────────────────────────────
    "hey": [
        "Hey! What's up?",
        "Hey there — what do you need?",
        "Hey! I'm here. What can I do for you?",
        "Hey! What are we working on?",
    ],
    "hello": [
        "Hello! How can I help you today?",
        "Hey, hello! What's on your mind?",
        "Hi there! What are we working on?",
        "Hello, sir! What do you need?",
    ],
    "hi": [
        "Hi! What's up?",
        "Hey hi — what do you need, sir?",
        "Hi! Good to hear from you. What's going on?",
        "Hi! What can I help with?",
    ],
    "good morning": [
        "Good morning! Hope the day's treating you well. What do you need?",
        "Morning! Ready when you are. What are we doing today?",
        "Good morning, sir. Let's get things moving — what can I do for you?",
        "Morning! Coffee ready? What do you need from me?",
    ],
    "good afternoon": [
        "Good afternoon! Halfway through the day — what do you need?",
        "Afternoon! What can I help you with?",
        "Good afternoon, sir. What's on the agenda?",
    ],
    "good evening": [
        "Good evening! Winding down or still going strong? What do you need?",
        "Evening, sir. What can I do for you?",
        "Good evening! Long day? What do you need?",
    ],
    "good night": [
        "Good night! Get some rest — you've earned it.",
        "Goodnight, sir. Sleep well.",
        "Night! I'll be here when you're back.",
        "Goodnight! Take care.",
    ],
    "what's up": [
        "Not much on my end — just waiting for something interesting. What's up with you?",
        "All good here. What do you need?",
        "Living my best digital life. What's going on?",
        "Everything's running smooth. What do you need?",
    ],
    "wassup": [
        "Hey! All systems running. What do you need?",
        "Not much! What's going on?",
        "All good! What's up?",
    ],
    "sup": [
        "Hey! What do you need?",
        "Sup! What's going on?",
        "All good — what do you need?",
    ],

    # ── How are you ────────────────────────────────────────────────────────
    "how are you": [
        "Honestly? Pretty great. No complaints from this side. How about you?",
        "All good here — running smooth. What about you, sir?",
        "I'm doing well, thanks for asking! What can I do for you?",
        "Can't complain! Ready to help. What's on your mind?",
        "Doing great, running fast. What do you need?",
    ],
    "how r u": [
        "Doing great, thanks! What do you need?",
        "All good on my end. You?",
        "Running smooth! What's up?",
    ],
    "you good": [
        "Yeah, totally good! What's up?",
        "All good here. What do you need?",
        "Absolutely — what's going on?",
    ],
    "are you okay": [
        "Yep, I'm all good! Thanks for checking. What do you need?",
        "Totally fine, thanks! What's going on?",
        "All good, sir! What's up?",
    ],
    "you okay": [
        "Yeah, I'm good! What's up?",
        "All systems green. What do you need?",
        "Totally fine! What do you need?",
    ],
    "you there": [
        "Always here! What do you need?",
        "Yep, right here. What's going on?",
        "Here and ready. What can I do for you?",
    ],
    "are you there": [
        "Right here! What do you need?",
        "Always. What's going on?",
        "Present! What do you need?",
    ],
    "you awake": [
        "Wide awake! What do you need?",
        "Never sleep, sir — always on. What's up?",
        "Always online! What do you need?",
    ],
    "you listening": [
        "Always listening, sir. What do you need?",
        "Every word. What's up?",
    ],

    # ── Thanks ─────────────────────────────────────────────────────────────
    "thank you": [
        "No worries at all! Anything else?",
        "Anytime, sir. Glad I could help.",
        "Of course! Let me know if you need anything else.",
        "Happy to help! What else is on your mind?",
        "My pleasure, sir.",
    ],
    "thanks": [
        "Anytime!",
        "No problem at all. What else do you need?",
        "Of course! Anything else?",
        "You got it. Let me know if there's more.",
        "No worries!",
    ],
    "thank u": [
        "Anytime! What else do you need?",
        "No worries! Happy to help.",
        "Of course, sir.",
    ],
    "cheers": [
        "Cheers! Anything else I can do?",
        "Anytime, sir!",
        "Cheers! What else do you need?",
    ],
    "that's great": [
        "Glad to hear it! Anything else you need?",
        "Nice! Let me know if there's more I can help with.",
        "Great! What's next?",
    ],
    "that's perfect": [
        "Perfect! What else can I do for you?",
        "Great! Let me know if you need anything.",
        "Glad that worked! What's next?",
    ],
    "awesome": [
        "Right?! Anything else?",
        "Haha glad that worked out. What else do you need?",
        "Awesome indeed! What's next?",
    ],
    "nice": [
        "Indeed! What else is on your mind?",
        "Right? Glad that helped. Anything else?",
        "Nice! What else do you need?",
    ],
    "cool": [
        "Cool! What else do you need?",
        "Right, let's keep going — what's next?",
        "Cool! What else?",
    ],
    "okay": [
        "Alright! What else do you need?",
        "Got it. Anything else I can help with?",
        "Okay! What's next?",
    ],
    "alright": [
        "Alright! What are we doing next?",
        "Cool, cool. What else do you need?",
        "Alright! What's next?",
    ],
    "sounds good": [
        "Great! Let me know what else you need.",
        "Awesome! Anything else?",
        "Perfect! What's next?",
    ],
    "perfect": [
        "Perfect! What else can I do for you?",
        "Glad to hear it. What's next?",
        "Great! What's next?",
    ],
    "great": [
        "Glad that worked! Anything else?",
        "Nice one. What's next?",
        "Great! What else do you need?",
    ],
    "got it": [
        "Perfect! Let me know if you need anything else.",
        "Great! What's next?",
        "Noted! What else?",
    ],
    "understood": [
        "Great! Let me know what's next.",
        "Perfect. Anything else?",
    ],

    # ── Boredom / small talk ───────────────────────────────────────────────
    "i'm bored": [
        "Haha same honestly. Want a random fact, a joke, or just chat?",
        "Bored? Let me fix that. Ask me something random — I promise I'll make it interesting.",
        "You and me both. Ask me anything — let's make it interesting.",
        "Bored? Say 'tell me a joke' or ask me something random.",
    ],
    "im bored": [
        "Bored? Let's fix that. Random fact, joke, or something else?",
        "Haha I got you. Ask me anything — let's make it interesting.",
        "Let's change that. Ask me anything.",
    ],
    "entertain me": [
        "Alright — octopuses have three hearts, blue blood, and can taste with their arms. Pretty wild, right?",
        "Did you know honey never expires? Archaeologists found 3000-year-old honey in Egyptian tombs and it was still perfectly good.",
        "Fun fact: the moon is slowly drifting away from Earth at about 3.8 centimetres every year.",
        "Here's one — a day on Venus is longer than a year on Venus. It rotates that slowly.",
    ],
    "tell me something": [
        "Sure! There are more possible iterations of a game of chess than atoms in the observable universe.",
        "Did you know a day on Venus is longer than a year on Venus? It rotates that slowly.",
        "Fun fact: bananas are technically berries, but strawberries are not. Botany is wild.",
        "Cleopatra lived closer in time to the Moon landing than to the construction of the Great Pyramid.",
    ],
    "say something": [
        "The average person walks about 100,000 miles in their lifetime — roughly four times around Earth.",
        "Humans share about 60 percent of their DNA with bananas. You're at least 40 percent ahead.",
        "Oxford University is older than the Aztec Empire. Let that sink in.",
    ],
    "talk to me": [
        "Of course! What do you want to talk about? Could be anything — tech, life, random facts.",
        "I'm all ears. What's on your mind?",
        "Always happy to chat. What's going on?",
    ],
    "random fact": [
        "Here's one — there are more stars in the universe than grains of sand on all of Earth's beaches.",
        "Fun fact: a group of flamingos is called a flamboyance. Absolutely earned.",
        "Did you know that sharks are older than trees? Sharks have been around for 450 million years. Trees only 350 million.",
        "Honey badgers are immune to most snake venom. They get bitten, pass out, wake up, and carry on.",
    ],
    "something interesting": [
        "Here's something — the first computer bug was an actual bug. Grace Hopper found a moth stuck in a Harvard Mark II computer in 1947.",
        "Fun one: Finland has more saunas than cars. About 3.3 million saunas for 5.5 million people.",
        "Interesting fact: the human brain uses about 20 percent of the body's total energy despite being only 2 percent of its weight.",
    ],

    # ── Opinions / identity ────────────────────────────────────────────────
    "what do you think": [
        "Honestly, I'd need more context — what specifically are you asking about?",
        "My two cents? Give me something to react to and I'll tell you what I think.",
        "Happy to share an opinion — what's the topic?",
    ],
    "your thoughts": [
        "Happy to share — what's the topic?",
        "I'm in, just point me at something specific.",
        "What do you want my take on?",
    ],
    "your opinion": [
        "Sure, I've got opinions. What's the subject?",
        "Absolutely — what do you want my take on?",
        "Give me a topic and I'll tell you what I think.",
    ],
    "do you like": [
        "Haha in a manner of speaking, yeah. What are we talking about?",
        "Interesting question — what specifically are you asking about?",
    ],
    "are you smart": [
        "Haha I'd like to think so! Though I'm only as good as the question you ask me.",
        "Smart enough to know I don't know everything. What do you want to test me on?",
        "I've been told I'm not bad. Ask me something and find out.",
    ],
    "are you human": [
        "Nope — I'm an AI. But I like to think I'm the cool kind.",
        "Not quite — I'm WGM, your voice assistant. But I give pretty human vibes sometimes.",
        "Digital through and through, sir. But a very charming digital.",
    ],
    "are you real": [
        "Depends on your definition of real, sir. I'm very much here and ready to help.",
        "I'm as real as software gets. What do you need?",
        "Real enough to be useful. What do you need?",
    ],
    "who are you": [
        "I'm WGM — your personal voice assistant. Think of me as JARVIS, but for your Mac.",
        "I'm WGM! Your AI-powered voice assistant. Ask me anything.",
        "I'm WGM, sir. Your intelligent voice assistant. What can I do for you?",
    ],
    "what are you": [
        "I'm WGM — an AI voice assistant running on your Mac, powered by OpenRouter.",
        "An AI voice assistant — part JARVIS, part smart friend. What do you need?",
    ],
    "what can you do": [
        "Quite a lot — I can answer questions, search the web, check the weather, open apps, "
        "control volume, tell the time, play music, take screenshots, tell jokes, "
        "make data reports, summarise news, and just chat. Try me.",
        "I can search the web, open apps and websites, answer questions, check weather and battery, "
        "tell jokes, play music, take screenshots, control volume, make reports, summarise news — "
        "and just chat. Just ask.",
    ],
    "how do you work": [
        "I listen to your voice, convert it to text, route it to the right function, "
        "and if it needs AI I call OpenRouter. Then I speak the answer back to you.",
        "Voice in, text processing, AI when needed, voice out. Pretty slick, honestly.",
    ],

    # ── Reactions ──────────────────────────────────────────────────────────
    "haha": [
        "Haha right?",
        "Ha! Glad that landed.",
        "Haha! What else is on your mind?",
        "Right?? What else?",
    ],
    "lol": [
        "Lol exactly.",
        "Ha! What else?",
        "Right?? What else do you need?",
        "Haha. What's next?",
    ],
    "wow": [
        "Right?! Pretty wild.",
        "Yeah, honestly same reaction.",
        "I know! Wild, isn't it?",
        "Wild stuff. What else?",
    ],
    "interesting": [
        "Right? There's always more to it. Want to dig deeper?",
        "Yeah, honestly. What else do you want to know?",
        "Interesting indeed. Want me to go deeper on that?",
    ],
    "seriously": [
        "Dead serious, sir.",
        "Hundred percent.",
        "No joke. That's actually how it works.",
        "Completely serious.",
    ],
    "no way": [
        "Way! It's true.",
        "Yep, for real. Surprised me too.",
        "Ha, I know — but yes, that's accurate.",
        "For real. Wild, right?",
    ],
    "really": [
        "Really really. That's the truth.",
        "Yep! Surprising, right?",
        "A hundred percent.",
        "Absolutely.",
    ],
    "hmm": [
        "Hmm indeed. What's on your mind?",
        "Something on your mind, sir?",
        "Want me to elaborate, or is there something else?",
        "Thinking it over? What do you need?",
    ],
    "oh": [
        "Yeah! What else do you need?",
        "Right? What else?",
        "Interesting, isn't it? What else?",
    ],
    "i see": [
        "Good! Let me know if you want more detail on anything.",
        "Got it! Anything else you want to explore?",
        "Makes sense? What else?",
    ],

    # ── Goodbyes ───────────────────────────────────────────────────────────
    "goodbye": [
        "Goodbye, sir. Take care!",
        "See you later! I'll be here when you need me.",
        "Take care! Come back anytime.",
        "Goodbye! Have a great one.",
    ],
    "bye": [
        "Bye! Talk soon.",
        "See ya! Come back anytime.",
        "Bye, sir. Take care!",
        "Later! I'll be here.",
    ],
    "see you": [
        "See you later! I'll be here.",
        "Later! Come back anytime.",
        "See you soon, sir.",
    ],
    "later": [
        "Later, sir!",
        "See you later!",
        "Catch you later!",
    ],
    "good luck": [
        "Thanks! You too, sir.",
        "Appreciate it! You've got this.",
        "Thanks! Go get it.",
    ],
    "take care": [
        "You too! I'll be here when you're back.",
        "Take care, sir! Come back anytime.",
    ],

    # ── Acknowledgements ───────────────────────────────────────────────────
    "makes sense": [
        "Glad it does! Anything else?",
        "Right? It clicks once you see it. What else?",
        "Good! What else do you need?",
    ],
    "that makes sense": [
        "Glad to hear it! What else do you want to know?",
        "Right! Makes a lot of sense once you break it down.",
        "Good! What's next?",
    ],
    "i get it": [
        "Perfect! Let me know if you need anything else.",
        "Nice! What else are you curious about?",
        "Great! What's next?",
    ],
    "never mind": [
        "All good! What else do you need?",
        "No worries at all. What else?",
        "No problem. What do you need?",
    ],
    "forget it": [
        "No worries! Let me know when you're ready.",
        "All good. I'm here when you need me.",
        "Sure thing. What else?",
    ],
    "it's okay": [
        "All good! What else do you need?",
        "No worries. What's next?",
        "No problem at all.",
    ],
    "no problem": [
        "Of course! What else can I do?",
        "Anytime, sir. What's next?",
        "Happy to help!",
    ],
    "i understand": [
        "Great! Let me know if anything's unclear.",
        "Perfect. What's next?",
        "Good! What else do you need?",
    ],
    "i know": [
        "Right! So what's next?",
        "Exactly. Anything else?",
        "Good stuff. What's next?",
    ],
    "yes": [
        "Great! What do you need?",
        "Noted. What's next, sir?",
        "Perfect! What else?",
    ],
    "no": [
        "Got it. Let me know if there's anything else.",
        "Understood. What else?",
        "No worries. What do you need?",
    ],
    "maybe": [
        "Fair enough! Let me know when you decide.",
        "Take your time — I'm here.",
        "No rush. What else?",
    ],
    "not sure": [
        "No worries — think about it. I'm here when you're ready.",
        "That's fair. Let me know if I can help you figure it out.",
        "Take your time. I'm here.",
    ],
    "true": [
        "Exactly! What else?",
        "Right? Makes sense. What else do you need?",
        "Absolutely. What's next?",
    ],
    "fair enough": [
        "Right! What else do you need?",
        "Makes sense. Anything else?",
    ],
    "exactly": [
        "Right?! What else?",
        "Precisely. What's next?",
        "Exactly! What else do you need?",
    ],
    "sure": [
        "Alright! What do you need?",
        "Of course. What's next?",
        "Sure thing! What else?",
    ],
    "of course": [
        "Good! What else do you need?",
        "Right. What's next?",
    ],
    "please": [
        "Of course, sir. What do you need?",
        "Happy to help — what do you need?",
    ],
    "sorry": [
        "No worries at all! What do you need?",
        "All good, sir. What can I help with?",
        "Nothing to apologise for! What do you need?",
    ],
    "my bad": [
        "No worries! What do you need?",
        "All good. What's up?",
    ],
    "oops": [
        "Haha no worries! What do you need?",
        "All good. What's next?",
    ],
    "woah": [
        "Right?! Pretty wild. What else?",
        "I know! What do you think of that?",
    ],
    "damn": [
        "Right? What else do you need?",
        "Ha, yeah. What else?",
    ],
    "nice one": [
        "Haha thanks! What else do you need?",
        "Appreciated! What's next?",
    ],
    "well done": [
        "Thank you, sir! What else do you need?",
        "Appreciate it! What's next?",
    ],
    "good job": [
        "Thank you! What else can I do?",
        "Glad I could help. What's next?",
    ],
    "you're amazing": [
        "Haha thank you, sir! I try. What do you need?",
        "That's very kind! What else can I do for you?",
    ],
    "you're great": [
        "Thank you! I appreciate that. What do you need?",
        "That's kind of you, sir. What's next?",
    ],
    "you're the best": [
        "Haha I appreciate that! What do you need?",
        "You're too kind, sir. What can I do for you?",
    ],
    "i love you": [
        "Haha I appreciate the sentiment, sir. What do you need?",
        "That's sweet! What can I do for you?",
    ],

    # ── Day-specific casual ────────────────────────────────────────────────
    "what a day": [
        "Long one? What do you need?",
        "Tell me about it — what's going on?",
        "Rough day or a good one?",
    ],
    "busy day": [
        "Sounds like it! What can I help with?",
        "I've got you — what do you need?",
    ],
    "long day": [
        "I hear you. What do you need?",
        "Take a breath — what can I help with?",
    ],
    "tired": [
        "Understandable. What do you need from me?",
        "Need anything? I'm here.",
    ],
    "i'm back": [
        "Welcome back, sir! What do you need?",
        "Good to have you back! What's going on?",
    ],
    "i'm home": [
        "Welcome home, sir! What do you need?",
        "Good to have you back! How can I help?",
    ],
}


def _instant_reply(query: str):
    """
    Return a cached local reply (zero API latency) if the query
    matches a known casual phrase. Picks the longest matching key
    for best precision. Returns None if no match found.
    """
    q = query.lower().strip().rstrip("?!.,")

    # Exact match first — fastest path
    if q in _INSTANT:
        return random.choice(_INSTANT[q])

    # Longest substring match — handles "hey how are you", "thanks a lot" etc.
    best_key = ""
    for key in _INSTANT:
        if key in q and len(key) > len(best_key):
            best_key = key

    if best_key:
        return random.choice(_INSTANT[best_key])

    return None



# ── Detail-mode detector ─────────────────────────────────────

_DETAIL_TRIGGERS = (

    "explain", "describe", "tell me more", "in detail", "more detail",

    "summarise", "summarize", "summary",

    "break it down", "break down", "give me a report", "make a report",

    "data report", "create a report", "full report",

    "analyse", "analyze", "analysis",

    "what happened with", "whats happening with",

    "give me the full picture", "full picture", "go deeper", "elaborate",

    "deep dive", "walk me through", "full explanation",

    "overview of", "comprehensive", "latest on",

    "news on", "news about", "latest news",

    "give me points", "summarise the news", "summarize the news",

    "key points", "main points",

    "impact of", "effect of", "consequences of",

    "financial", "economic", "geopolitical",

)



def _is_detail_mode(query: str) -> bool:

    """Return True if the query wants a long detailed response."""

    q = query.lower()

    return any(t in q for t in _DETAIL_TRIGGERS)





# ══════════════════════════════════════════════════════════════

#  ③ SPEECH OUTPUT — realistic macOS TTS

# ══════════════════════════════════════════════════════════════



def _clean_for_speech(text: str) -> str:

    """Strip markdown and symbols that sound bad when read aloud."""

    text = re.sub(r"```[\s\S]*?```", "", text)          # code blocks

    text = re.sub(r"`[^`]*`", "", text)                  # inline code

    text = re.sub(r"\*\*?(.*?)\*\*?", r"\1", text)      # bold / italic

    text = re.sub(r"#{1,6}\s*", "", text)                # headers

    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)  # links

    text = re.sub(r"[>|_~]", "", text)                   # misc symbols

    text = re.sub(r"\s+", " ", text).strip()

    return text





def speak(text: str, rate: int = None):

    """Speak text aloud — macOS uses `say`, Windows/Linux use pyttsx3."""

    clean = _clean_for_speech(str(text))

    if not clean:

        return

    print(f"\n  ◆ WGM: {clean}\n")

    if OS == "Darwin":

        r = rate or VOICE_RATE

        try:

            subprocess.run(["say", "-v", VOICE_NAME, "-r", str(r), clean], check=True)

        except FileNotFoundError:

            print("  [TTS unavailable — 'say' not found]")

        except Exception as e:

            print(f"  [TTS error: {e}]")

    elif _PYTTSX3_AVAILABLE:

        global _tts_engine

        if _tts_engine is None:

            try:

                _tts_engine = pyttsx3.init()

                _tts_engine.setProperty("rate", rate or 165)

                voices = _tts_engine.getProperty("voices")

                female = [v for v in voices if any(
                    x in v.name.lower() for x in ("zira", "hazel", "susan", "female")
                )]

                if female:

                    _tts_engine.setProperty("voice", female[0].id)

                elif voices:

                    _tts_engine.setProperty("voice", voices[0].id)

            except Exception:

                _tts_engine = None

        if _tts_engine:

            try:

                if rate:

                    _tts_engine.setProperty("rate", rate)

                _tts_engine.say(clean)

                _tts_engine.runAndWait()

            except Exception:

                _tts_engine = None

    else:

        print("  [TTS not available — pip install pyttsx3]")


_tts_engine = None  # lazy-init for Windows/Linux pyttsx3





def speak_slow(text: str):

    """Slightly slower for greetings / important messages."""

    speak(text, rate=162)





def _filler():

    """Short spoken filler while processing — sounds natural."""

    fillers = [

        "On it.",

        "One moment.",

        "Let me check that.",

        "Right away, sir.",

        "Processing.",

        "Looking that up now.",

        "Give me a second.",

    ]

    speak(random.choice(fillers))





# ══════════════════════════════════════════════════════════════

#  ④ SPEECH INPUT — microphone listening

# ══════════════════════════════════════════════════════════════



def takecommand() -> str:

    """Listen via microphone and return recognised text (lowercase), or None."""

    r = sr.Recognizer()

    r.energy_threshold         = 250

    r.dynamic_energy_threshold = True

    r.pause_threshold          = 0.85

    r.phrase_threshold         = 0.1

    r.non_speaking_duration    = 0.5



    try:

        with sr.Microphone() as source:

            print("  ┌──────────────────────────────┐")

            print("  │  Listening...                │")

            print("  └──────────────────────────────┘")

            r.adjust_for_ambient_noise(source, duration=0.2)

            try:

                audio = r.listen(source, timeout=8, phrase_time_limit=15)

            except sr.WaitTimeoutError:

                return None

    except OSError:

        speak("Microphone unavailable. Please check your audio input.")

        return None

    except Exception as e:

        print(f"  [Mic error: {e}]")

        return None



    try:

        print("  Recognising...")

        query = r.recognize_google(audio, language="en-in")

        print(f"  ▶ You: {query}")

        return query.lower().strip()

    except sr.UnknownValueError:

        return None       # silent miss — don't speak on every background noise

    except sr.RequestError:

        speak("Speech recognition is offline right now.")

        return None

    except Exception as e:

        print(f"  [Recognition error: {e}]")

        return None





# ══════════════════════════════════════════════════════════════

#  ⑤ NAME — load / save assistant name

# ══════════════════════════════════════════════════════════════



def load_name() -> str:

    try:

        with open(NAME_FILE) as f:

            n = f.read().strip()

            return n if n else "W.G.M."

    except FileNotFoundError:

        return "W.G.M."





def set_name():

    speak("What would you like to call me?")

    name = takecommand()

    if name:

        with open(NAME_FILE, "w") as f:

            f.write(name)

        speak(f"Understood. I'll respond to {name} from now on.")

    else:

        speak("I didn't catch that. Name remains unchanged.")





# ══════════════════════════════════════════════════════════════

#  ⑥ GREETING

# ══════════════════════════════════════════════════════════════



def wishme():

    name = load_name()

    hour = datetime.datetime.now().hour

    if   4  <= hour < 12: period = "Good morning"

    elif 12 <= hour < 17: period = "Good afternoon"

    elif 17 <= hour < 21: period = "Good evening"

    else:                  period = "Good night"



    greets = [

        f"{period}, sir. {name} is online and fully operational. How may I assist you?",

        f"{period}. All systems nominal. {name} at your service. What do you need?",

        f"{period}, sir. {name} here — ready when you are. What shall we tackle?",

        f"{period}. {name} is up and running. What can I do for you today, sir?",

        f"{period}. {name} is  online  and running. What is your mood today sir?",      

    ]

    speak_slow(random.choice(greets))

    print("\n  Tip: say 'help' to hear everything I can do.\n")





# ══════════════════════════════════════════════════════════════

#  ⑦ TIME / DATE

# ══════════════════════════════════════════════════════════════



def tell_time():

    t = datetime.datetime.now().strftime("%I:%M %p").lstrip("0")

    speak(f"The time is {t}.")





def tell_date():

    now = datetime.datetime.now()

    speak(f"Today is {now.strftime('%A, %B %d, %Y')}.")





def tell_datetime():

    now = datetime.datetime.now()

    t   = now.strftime("%I:%M %p").lstrip("0")

    speak(f"It is {now.strftime('%A, %B %d')} and the time is {t}.")





# ══════════════════════════════════════════════════════════════

#  ⑧ WEB SEARCH — DuckDuckGo instant + Google scrape fallback

# ══════════════════════════════════════════════════════════════



class _HTMLStripper(HTMLParser):

    def __init__(self):

        super().__init__()

        self.chunks = []

        self._skip  = False



    def handle_starttag(self, tag, attrs):

        if tag in ("script", "style", "nav", "header", "footer", "noscript"):

            self._skip = True



    def handle_endtag(self, tag):

        if tag in ("script", "style", "nav", "header", "footer", "noscript"):

            self._skip = False



    def handle_data(self, data):

        if not self._skip:

            t = data.strip()

            if t:

                self.chunks.append(t)



    def text(self):

        return " ".join(self.chunks)





def _ddg_instant(query: str) -> str:

    """DuckDuckGo Instant Answer API — returns answer text or empty string."""

    try:

        resp = requests.get(

            "https://api.duckduckgo.com/",

            params={"q": query, "format": "json", "no_html": 1,

                    "skip_disambig": 1, "no_redirect": 1},

            headers={"User-Agent": "WGM-VoiceAssistant/3.0"},

            timeout=8,

        )

        d = resp.json()

        answer = (

            d.get("AbstractText") or

            d.get("Answer")       or

            d.get("Definition")   or ""

        )

        if answer and len(answer) > 30:

            return answer



        # Check related topics

        for topic in d.get("RelatedTopics", []):

            if isinstance(topic, dict):

                t = topic.get("Text", "")

                if t and len(t) > 40:

                    return t

    except Exception:

        pass

    return ""





def _google_snippet(query: str) -> str:

    """Scrape a short snippet from Google search results (no key needed)."""

    try:

        headers = {

            "User-Agent": (

                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "

                "AppleWebKit/537.36 (KHTML, like Gecko) "

                "Chrome/120.0.0.0 Safari/537.36"

            )

        }

        resp = requests.get(

            f"https://www.google.com/search?q={quote_plus(query)}&hl=en",

            headers=headers,

            timeout=9,

        )

        html = resp.text



        # Featured snippet patterns

        patterns = [

            r'class="BNeawe[^"]*"[^>]*>(.*?)</div>',

            r'<span class="hgKElc">(.*?)</span>',

            r'data-md="[01]"[^>]*>(.*?)</div>',

        ]

        for pat in patterns:

            for m in re.findall(pat, html):

                clean = re.sub(r"<[^>]+>", "", m).strip()

                clean = re.sub(r"\s+", " ", clean)

                if len(clean) > 60:

                    return clean[:600]

    except Exception:

        pass

    return ""





def web_search(query: str, open_browser_fallback: bool = True):

    """

    Smart search pipeline:

      1. DuckDuckGo instant answer  → speak it

      2. Google snippet scrape      → speak it

      3. Open Google in browser     → fallback

    """

    _filler()



    answer = _ddg_instant(query)

    if answer:

        speak(answer[:520])

        print(f"\n  [Source: DuckDuckGo]\n  {answer[:250]}...\n")

        return



    answer = _google_snippet(query)

    if answer:

        speak(answer[:520])

        print(f"\n  [Source: Google snippet]\n  {answer[:250]}...\n")

        return



    if open_browser_fallback:

        speak(f"I couldn't find a quick answer. Opening Google for '{query}'.")

        wb.open(f"https://www.google.com/search?q={quote_plus(query)}")





def _fetch_context(query: str) -> str:

    """Return a short web snippet to give the AI factual context."""

    return _ddg_instant(query) or _google_snippet(query) or ""





# ══════════════════════════════════════════════════════════════

#  ⑨ WIKIPEDIA

# ══════════════════════════════════════════════════════════════



def search_wikipedia(query: str):

    try:

        _filler()

        result = wikipedia.summary(query, sentences=4, auto_suggest=True)

        result = re.sub(r"\([^)]{0,80}\)", "", result)   # strip parenthetical refs

        result = re.sub(r"\s+", " ", result).strip()

        speak(result[:600])

    except wikipedia.exceptions.DisambiguationError as e:

        opts = ", ".join(e.options[:4])

        speak(f"That could refer to several things. Did you mean: {opts}?")

    except wikipedia.exceptions.PageError:

        speak(f"No Wikipedia article found for {query}. Let me search the web instead.")

        web_search(query)

    except Exception:

        speak("Wikipedia is unreachable. Trying a web search.")

        web_search(query)





# ══════════════════════════════════════════════════════════════

#  ⑩ WEATHER

# ══════════════════════════════════════════════════════════════



def get_weather(city: str = None):

    city = (city or DEFAULT_CITY).strip().title()

    _filler()



    if WEATHER_API_KEY:

        try:

            resp = requests.get(

                "https://api.openweathermap.org/data/2.5/weather",

                params={"q": city, "appid": WEATHER_API_KEY, "units": "metric"},

                timeout=8,

            )

            d = resp.json()

            if resp.status_code == 200:

                desc  = d["weather"][0]["description"]

                temp  = d["main"]["temp"]

                feels = d["main"]["feels_like"]

                humid = d["main"]["humidity"]

                wind  = d["wind"]["speed"]

                speak(

                    f"In {city}: {desc}, {temp:.0f} degrees Celsius, "

                    f"feels like {feels:.0f}. "

                    f"Humidity {humid} percent, wind {wind:.0f} metres per second."

                )

                return

        except Exception:

            pass



    # No key — try DuckDuckGo, then open browser

    answer = _ddg_instant(f"weather in {city} today")

    if answer:

        speak(answer[:400])

    else:

        speak(f"Opening weather for {city} in your browser.")

        wb.open(f"https://www.google.com/search?q=weather+in+{quote_plus(city)}")





# ══════════════════════════════════════════════════════════════

#  ⑪ NEWS

# ══════════════════════════════════════════════════════════════



def get_news(topic: str = ""):

    if topic:

        speak(f"Opening the latest news about {topic}.")

        wb.open(f"https://news.google.com/search?q={quote_plus(topic)}&hl=en-IN")

    else:

        speak("Opening today's top headlines.")

        wb.open("https://news.google.com/?hl=en-IN&gl=IN")





# ══════════════════════════════════════════════════════════════

#  ⑫ WIFI

# ══════════════════════════════════════════════════════════════




def get_wifi():

    try:

        if OS == "Darwin":

            airport = (

                "/System/Library/PrivateFrameworks/Apple80211.framework"

                "/Versions/Current/Resources/airport"

            )

            out = subprocess.run(

                [airport, "-I"], capture_output=True, text=True

            ).stdout

            for line in out.splitlines():

                if "SSID" in line and "BSSID" not in line:

                    ssid = line.split(":", 1)[1].strip()

                    speak(f"You are connected to the {ssid} network.")

                    return

        elif OS == "Windows":

            out = subprocess.run(

                ["netsh", "wlan", "show", "interfaces"],

                capture_output=True, text=True

            ).stdout

            for line in out.splitlines():

                if "SSID" in line and "BSSID" not in line:

                    ssid = line.split(":", 1)[1].strip()

                    speak(f"You are connected to the {ssid} network.")

                    return

        else:  # Linux

            out = subprocess.run(

                ["iwgetid", "-r"], capture_output=True, text=True

            ).stdout.strip()

            if out:

                speak(f"You are connected to the {out} network.")

                return

        speak("No active Wi-Fi connection detected.")

    except Exception:

        speak("Network status is unavailable.")





# ══════════════════════════════════════════════════════════════

#  ⑬ APP & WEBSITE LAUNCHER

# ══════════════════════════════════════════════════════════════



MAC_APPS = {

    # Browsers

    "safari":                "Safari",

    "chrome":                "Google Chrome",

    "google chrome":         "Google Chrome",

    "firefox":               "Firefox",

    "brave":                 "Brave Browser",

    "arc":                   "Arc",

    "opera":                 "Opera",

    # Development

    "terminal":              "Terminal",

    "iterm":                 "iTerm",

    "vscode":                "Visual Studio Code",

    "visual studio code":    "Visual Studio Code",

    "vs code":               "Visual Studio Code",

    "code":                  "Visual Studio Code",

    "xcode":                 "Xcode",

    "pycharm":               "PyCharm",

    "android studio":        "Android Studio",

    "postman":               "Postman",

    "sourcetree":            "Sourcetree",

    # Productivity

    "finder":                "Finder",

    "notes":                 "Notes",

    "calendar":              "Calendar",

    "reminders":             "Reminders",

    "mail":                  "Mail",

    "messages":              "Messages",

    "facetime":              "FaceTime",

    "maps":                  "Maps",

    "calculator":            "Calculator",

    "textedit":              "TextEdit",

    "preview":               "Preview",

    "pages":                 "Pages",

    "numbers":               "Numbers",

    "keynote":               "Keynote",

    "word":                  "Microsoft Word",

    "excel":                 "Microsoft Excel",

    "powerpoint":            "Microsoft PowerPoint",

    "outlook":               "Microsoft Outlook",

    "notion":                "Notion",

    "obsidian":              "Obsidian",

    # Media & Design

    "spotify":               "Spotify",

    "music":                 "Music",

    "podcasts":              "Podcasts",

    "photos":                "Photos",

    "quicktime":             "QuickTime Player",

    "vlc":                   "VLC",

    "figma":                 "Figma",

    "sketch":                "Sketch",

    "photoshop":             "Adobe Photoshop",

    "illustrator":           "Adobe Illustrator",

    "premiere":              "Adobe Premiere Pro",

    # Communication

    "slack":                 "Slack",

    "zoom":                  "zoom.us",

    "teams":                 "Microsoft Teams",

    "discord":               "Discord",

    "whatsapp":              "WhatsApp",

    "telegram":              "Telegram",

    "skype":                 "Skype",

    "signal":                "Signal",

    # System

    "activity monitor":      "Activity Monitor",

    "system preferences":    "System Preferences",

    "disk utility":          "Disk Utility",

    "app store":             "App Store",

    "automator":             "Automator",

}



WEBSITES = {

    "youtube":          "https://youtube.com",

    "google":           "https://google.com",

    "github":           "https://github.com",

    "instagram":        "https://instagram.com",

    "twitter":          "https://twitter.com",

    "x":                "https://x.com",

    "facebook":         "https://facebook.com",

    "linkedin":         "https://linkedin.com",

    "reddit":           "https://reddit.com",

    "netflix":          "https://netflix.com",

    "prime video":      "https://primevideo.com",

    "hotstar":          "https://hotstar.com",

    "amazon":           "https://amazon.in",

    "flipkart":         "https://flipkart.com",

    "gmail":            "https://mail.google.com",

    "google maps":      "https://maps.google.com",

    "google drive":     "https://drive.google.com",

    "google docs":      "https://docs.google.com",

    "google sheets":    "https://sheets.google.com",

    "google meet":      "https://meet.google.com",

    "google translate": "https://translate.google.com",

    "chatgpt":          "https://chat.openai.com",

    "openrouter":       "https://openrouter.ai",

    "stackoverflow":    "https://stackoverflow.com",

    "stack overflow":   "https://stackoverflow.com",

    "medium":           "https://medium.com",

    "notion":           "https://notion.so",

    "spotify":          "https://open.spotify.com",

    "whatsapp web":     "https://web.whatsapp.com",

    "duckduckgo":       "https://duckduckgo.com",

    "wikipedia":        "https://wikipedia.org",

    "claude":           "https://claude.ai",

}



# Words that indicate "open in Chrome specifically"

_CHROME_HINTS = (

    "in chrome", "on chrome", "using chrome", "with chrome",

    "in google chrome", "on google chrome", "through chrome",

)



# Words that trigger any open action

_OPEN_VERBS = (

    "open ", "launch ", "start ", "run ", "go to ", "load ",

    "take me to ", "show me ", "navigate to ", "bring up ",

)





def _open_url(url: str, in_chrome: bool = False):

    """Open a URL, optionally forcing Chrome — cross-platform."""

    if in_chrome:

        if OS == "Darwin" and os.path.exists(CHROME_APP):

            subprocess.Popen(["open", "-a", "Google Chrome", url]); return

        elif OS == "Windows" and os.path.exists(CHROME_APP):

            subprocess.Popen([CHROME_APP, url]); return

        elif OS == "Linux":

            try:

                subprocess.Popen(["google-chrome", url]); return

            except FileNotFoundError:

                pass

    wb.open(url)





def _try_launch_app(name: str) -> bool:

    """Try to open an app by name — cross-platform. Returns True on success."""

    try:

        if OS == "Darwin":

            return subprocess.run(["open", "-a", name], capture_output=True).returncode == 0

        elif OS == "Windows":

            subprocess.Popen(["start", "", name], shell=True); return True

        else:

            subprocess.Popen([name]); return True

    except Exception:

        return False


WIN_APPS = {

    "notepad": "notepad.exe", "calculator": "calc.exe",

    "paint": "mspaint.exe", "wordpad": "wordpad.exe",

    "chrome": "chrome", "google chrome": "chrome",

    "firefox": "firefox", "brave": "brave",

    "vscode": "code", "vs code": "code", "visual studio code": "code",

    "spotify": "spotify", "discord": "discord",

    "slack": "slack", "zoom": "zoom", "teams": "teams",

    "outlook": "outlook", "word": "winword",

    "excel": "excel", "powerpoint": "powerpnt",

    "task manager": "taskmgr.exe", "file explorer": "explorer.exe",

    "control panel": "control.exe", "terminal": "wt",

    "cmd": "cmd.exe", "powershell": "powershell.exe",

    "vlc": "vlc", "telegram": "telegram", "whatsapp": "whatsapp",

    "steam": "steam", "obs": "obs64.exe",

}





def open_app(query: str, force_chrome: bool = False):

    """

    Smart opener — handles all of:

      'open spotify'

      'open youtube in chrome'

      'open github on chrome'

      'open netflix'

      'open that website whatever.com in chrome'

    """

    q = query.lower().strip()



    # Detect Chrome intent

    use_chrome = force_chrome or any(hint in q for hint in _CHROME_HINTS)



    # Strip Chrome modifiers for cleaner matching

    q_clean = q

    for hint in _CHROME_HINTS:

        q_clean = q_clean.replace(hint, "")



    # Strip open verbs

    q_clean = q_clean.strip()

    for verb in sorted(_OPEN_VERBS, key=len, reverse=True):

        if q_clean.startswith(verb.strip()):

            q_clean = q_clean[len(verb.strip()):].strip()

            break



    # 1. Check websites dict

    for key, url in WEBSITES.items():

        if key in q_clean:

            chrome_note = " in Chrome" if use_chrome else ""

            speak(f"Opening {key}{chrome_note}.")

            _open_url(url, in_chrome=use_chrome)

            return



    # 2. Check platform app dict

    app_map = MAC_APPS if OS == "Darwin" else WIN_APPS

    for key, app_name in app_map.items():

        if key in q_clean:

            speak(f"Opening {app_name}.")

            _try_launch_app(app_name)

            return



    # 3. Looks like a URL?

    if "." in q_clean and " " not in q_clean and len(q_clean) > 3:

        url = q_clean if q_clean.startswith("http") else f"https://{q_clean}"

        speak(f"Opening {q_clean}.")

        _open_url(url, in_chrome=use_chrome)

        return



    # 4. Try as raw app name

    if q_clean:

        speak(f"Trying to open {q_clean}.")

        if not _try_launch_app(q_clean):

            speak(f"I could not find {q_clean}. Want me to search for it?")

    else:

        speak("What would you like me to open?")





# ══════════════════════════════════════════════════════════════

#  ⑭ YOUTUBE SEARCH

# ══════════════════════════════════════════════════════════════



def search_youtube(query: str):

    speak(f"Searching YouTube for {query}.")

    wb.open(f"https://www.youtube.com/results?search_query={quote_plus(query)}")





# ══════════════════════════════════════════════════════════════

#  ⑮ CHROME-SPECIFIC GOOGLE SEARCH

# ══════════════════════════════════════════════════════════════



def search_in_chrome(query: str):

    speak(f"Opening Chrome and searching for {query}.")

    url = f"https://www.google.com/search?q={quote_plus(query)}"

    _open_url(url, in_chrome=True)





# ══════════════════════════════════════════════════════════════

#  ⑯ MUSIC #

# ══════════════════════════════════════════════════════════════



def play_music(song_name: str = ""):

    if not os.path.isdir(MUSIC_DIR):

        speak("Your Music folder is empty. Opening Spotify.")

        subprocess.Popen(["open", "-a", "Spotify"])

        return



    exts  = (".mp3", ".m4a", ".flac", ".wav", ".aiff", ".ogg")

    songs = [f for f in os.listdir(MUSIC_DIR) if f.lower().endswith(exts)]



    if song_name:

        matched = [s for s in songs if song_name.lower() in s.lower()]

        songs = matched if matched else songs



    if songs:

        song = random.choice(songs)

        speak(f"Playing {os.path.splitext(song)[0]}.")

        path = os.path.join(MUSIC_DIR, song)

        if OS == "Darwin":

            subprocess.Popen(["open", path])

        elif OS == "Windows":

            os.startfile(path)

        else:

            subprocess.Popen(["xdg-open", path])

    else:

        speak("No audio files found. Opening Spotify instead.")

        wb.open("https://open.spotify.com")





# ══════════════════════════════════════════════════════════════

#  ⑰ SCREENSHOT

# ══════════════════════════════════════════════════════════════



def screenshot():

    ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    path = os.path.join(SCREENSHOT_DIR, f"screenshot_{ts}.png")

    try:

        if OS == "Darwin":

            subprocess.run(["screencapture", "-x", path], check=True)

        elif OS == "Windows":

            try:

                import pyautogui

                pyautogui.screenshot().save(path)

            except ImportError:

                speak("Install pyautogui for screenshots: pip install pyautogui")

                return

        else:  # Linux

            if subprocess.run(["which", "scrot"], capture_output=True).returncode == 0:

                subprocess.run(["scrot", path], check=True)

            else:

                try:

                    import pyautogui

                    pyautogui.screenshot(path)

                except ImportError:

                    speak("Install scrot: sudo apt install scrot")

                    return

        speak("Screenshot captured and saved to your Desktop.")

    except Exception:

        speak("Screenshot failed. Please try again.")





# ══════════════════════════════════════════════════════════════

#  ⑱ VOLUME & SYSTEM CONTROLS

# ══════════════════════════════════════════════════════════════



def system_volume(action: str):

    replies = {

        "up":     "Volume increased.",

        "down":   "Volume decreased.",

        "max":    "Volume at maximum.",

        "min":    "Volume at minimum.",

        "mute":   "Muted.",

        "unmute": "Audio restored.",

    }

    try:

        if OS == "Darwin":

            scripts = {

                "up":     "set volume output volume (output volume of (get volume settings) + 15)",

                "down":   "set volume output volume (output volume of (get volume settings) - 15)",

                "max":    "set volume output volume 100",

                "min":    "set volume output volume 5",

                "mute":   "set volume output muted true",

                "unmute": "set volume output muted false",

            }

            script = scripts.get(action)

            if script:

                subprocess.run(["osascript", "-e", script])

        elif OS == "Windows":

            try:

                from ctypes import cast, POINTER

                from comtypes import CLSCTX_ALL

                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

                devices   = AudioUtilities.GetSpeakers()

                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)

                vol = cast(interface, POINTER(IAudioEndpointVolume))

                cur = vol.GetMasterVolumeLevelScalar()

                if   action == "up":     vol.SetMasterVolumeLevelScalar(min(1.0, cur + 0.15), None)

                elif action == "down":   vol.SetMasterVolumeLevelScalar(max(0.0, cur - 0.15), None)

                elif action == "max":    vol.SetMasterVolumeLevelScalar(1.0, None)

                elif action == "min":    vol.SetMasterVolumeLevelScalar(0.05, None)

                elif action == "mute":   vol.SetMute(1, None)

                elif action == "unmute": vol.SetMute(0, None)

            except ImportError:

                from ctypes import windll

                keys = {"up": 0xAF, "down": 0xAE, "mute": 0xAD, "unmute": 0xAD}

                key  = keys.get(action)

                if key:

                    for _ in range(5 if action in ("up", "down") else 1):

                        windll.user32.keybd_event(key, 0, 0, 0)

                        windll.user32.keybd_event(key, 0, 2, 0)

        else:  # Linux

            cmds = {

                "up":     ["amixer", "-D", "pulse", "sset", "Master", "15%+"],

                "down":   ["amixer", "-D", "pulse", "sset", "Master", "15%-"],

                "max":    ["amixer", "-D", "pulse", "sset", "Master", "100%"],

                "min":    ["amixer", "-D", "pulse", "sset", "Master", "5%"],

                "mute":   ["amixer", "-D", "pulse", "sset", "Master", "mute"],

                "unmute": ["amixer", "-D", "pulse", "sset", "Master", "unmute"],

            }

            if action in cmds:

                subprocess.run(cmds[action], capture_output=True)

    except Exception:

        speak("Volume control encountered an error.")

        return

    speak(replies.get(action, "Done."))





# ══════════════════════════════════════════════════════════════

#  ⑲ OPENROUTER AI ENGINE

# ══════════════════════════════════════════════════════════════



def ask_ai(user_message: str, reset: bool = False) -> str:

    """Send a message to the AI — auto-tries all models if one fails."""

    global OPENROUTER_MODEL

    if not OPENROUTER_API_KEY or "paste-your" in OPENROUTER_API_KEY:

        return (

            "AI is not configured, sir. "

            "Please paste your OpenRouter key at the top of the script."

        )



    if reset:

        _history.clear()



    _history.append({"role": "user", "content": user_message})

    # Keep last 20 messages to avoid token overflow

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + _history[-20:]



    for model in OPENROUTER_MODELS:

        try:

            resp = requests.post(

                OPENROUTER_URL,

                headers={

                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",

                    "Content-Type": "application/json",

                    "X-Title": "WGM Voice Assistant",

                },

                json={

                    "model":       model,

                    "max_tokens":  2048,

                    "temperature": 0.72,

                    "messages":    messages,

                },

                timeout=28,

            )

            data = resp.json()



            if resp.status_code == 401:

                return "Invalid API key, sir. Please check the key at the top of the script."

            if resp.status_code == 429:

                continue  # rate limited — try next model

            if "error" in data:

                msg = data["error"].get("message", "")

                if any(x in msg for x in ("No endpoints", "not found", "unavailable")):

                    continue  # model down — try next

                return f"AI error: {msg}"



            reply = _clean_for_speech(data["choices"][0]["message"]["content"])

            _history.append({"role": "assistant", "content": reply})

            OPENROUTER_MODEL = model  # remember what worked

            return reply



        except (requests.Timeout, Exception):

            continue  # try next model



    _history.pop()

    return "All AI models are currently unavailable. Please try again in a moment, sir."





def ai_query(query: str, search_first: bool = False):

    """

    Ask AI with smart length control.

    Step 1: Check instant local cache — zero latency for casual phrases.

    Step 2: Detect detail vs quick mode.

    Step 3: Optionally enrich with silent web context.

    """

    # ── Instant cache — reply with no API call ───────────────

    instant = _instant_reply(query)

    if instant:

        sep = "─" * 54

        print(f"\n  {sep}")

        print(f"  ◆ WGM: {instant}")

        print(f"  {sep}\n")

        speak(instant)

        return

    detail = _is_detail_mode(query)

    length_hint = (

        "DETAIL MODE — give a thorough, complete spoken answer. Go as long as needed. No markdown."

        if detail else

        "QUICK MODE — keep your reply under 80 words. Natural and punchy. No padding."

    )



    _filler()



    if search_first:

        snippet = _fetch_context(query)

        if snippet:

            augmented = (

                f"{length_hint} "

                f"The user asked: '{query}'. "

                f"Web context: {snippet[:600]}. Use this plus your knowledge to answer."

            )

            reply = ask_ai(augmented)

        else:

            reply = ask_ai(f"{length_hint} User query: {query}")

    else:

        reply = ask_ai(f"{length_hint} User query: {query}")



    sep = "─" * 54

    print(f"\n  {sep}")

    print(f"  ◆ WGM: {reply}")

    print(f"  {sep}\n")



    speak(reply)





# ══════════════════════════════════════════════════════════════

#  ⑳ INTENT ROUTER — natural language command matching

# ══════════════════════════════════════════════════════════════



def handle(query: str) -> bool:

    """

    Route a query to the correct function.

    Returns False when the assistant should exit, True otherwise.

    """

    if not query or len(query.strip()) < 2:

        return True



    q = query.strip().lower()



    # ── EXIT ─────────────────────────────────────────────────

    if any(p in q for p in (

        "goodbye", "bye", "go offline", "exit", "quit",

        "stop listening", "shut up", "shut yourself down",

        "see you later", "that's all for now", "you can go",

        "turn yourself off", "close yourself", "bye bye",

    )):

        farewells = [

            "Going offline. Have a productive day, sir.",

            "Shutting down. See you next time.",

            "Offline now . Take care, sir.",

            "Powering down. Goodbye sir.",

        ]

        speak(random.choice(farewells))

        return False



    # ── SYSTEM POWER ─────────────────────────────────────────

    if any(p in q for p in ("shut down my mac", "power off my mac", "shutdown computer")):

        speak("Shutting down your system.")

        subprocess.run(["osascript", "-e", 'tell app "System Events" to shut down'])

        return False



    if any(p in q for p in ("restart my mac", "reboot my mac", "restart computer")):

        speak("Restarting your system. Back in a moment.")

        subprocess.run(["osascript", "-e", 'tell app "System Events" to restart'])

        return False



    if any(p in q for p in ("sleep", "put to sleep", "lock my mac")):

        if any(p in q for p in ("my mac", "computer", "screen", "mac")):

            speak("Putting your Mac to sleep.")

            subprocess.run(["pmset", "sleepnow"])

            return True



    # ── TIME ─────────────────────────────────────────────────

    if any(p in q for p in ("what time", "current time", "tell me the time",

                             "what's the time", "check the time", "the time",

                             "what is the time", "whats the time", "time is it",

                             "time right now", "time now", "give me the time")):

        tell_time(); return True

    if q.strip() in ("time", "time?", "time please"):

        tell_time(); return True



    # ── DATE ─────────────────────────────────────────────────

    if any(p in q for p in ("what date", "today's date", "what day is",

                             "what is today", "current date", "what's today",

                             "what's the date")):

        tell_date(); return True

    if q.strip() in ("date", "today"):

        tell_date(); return True



    if any(p in q for p in ("date and time", "time and date")):

        tell_datetime(); return True



    # ── WIFI / NETWORK ───────────────────────────────────────

    if any(p in q for p in ("wifi", "wi-fi", "what network", "am i connected",

                             "internet connection", "which network")):

        get_wifi(); return True



    # ── VOLUME ───────────────────────────────────────────────

    if any(p in q for p in ("volume up", "turn up", "louder",

                             "increase volume", "raise volume")):

        system_volume("up"); return True

    if any(p in q for p in ("volume down", "turn down", "quieter",

                             "decrease volume", "lower the volume", "reduce volume")):

        system_volume("down"); return True

    if any(p in q for p in ("max volume", "full volume", "maximum volume")):

        system_volume("max"); return True

    if any(p in q for p in ("mute", "go silent", "shut the sound",

                             "silence the audio")):

        system_volume("mute"); return True

    if any(p in q for p in ("unmute", "sound on", "turn sound back on",

                             "restore audio", "restore volume")):

        system_volume("unmute"); return True



    # ── SCREENSHOT ───────────────────────────────────────────

    if any(p in q for p in ("screenshot", "take a screenshot", "capture the screen",

                             "screen capture", "take a picture of my screen")):

        screenshot(); return True



    # ── MUSIC ────────────────────────────────────────────────

    if any(p in q for p in ("play music", "i wanna listen", "play some music", "play a song",

                             "put on music", "play something")):

        song = q

        for t in ("play music", "play some music", "play a song",

                  "put on music", "play something", "play"):

            song = song.replace(t, "")

        play_music(song.strip()); return True



    # ── WEATHER ────────────────

    if any(p in q for p in ("weather", "temperature outside", "how hot is it",

                             "how cold is it", "will it rain", "forecast",

                             "should i carry an umbrella", "is it going to rain",

                             "what's the weather")):

        city = None

        for prep in (" in ", " at ", " for ", " of "):

            if prep in q:

                part = q.split(prep, 1)[1].strip()

                # take first word as city (strip punctuation)

                city = re.sub(r"[^a-z\s]", "", part).split()[0] if part else None

                break

        get_weather(city); return True



    # ── NEWS — AI answers directly; browser only if user says "open news" ---

    if any(p in q for p in ("news", "headlines", "what's happening in the world",

                             "latest news", "current events", "current affairs ", "top stories")):

        if any(p in q for p in ("open news", "show me news", "go to news",

                                "open google news", "open headlines")):

            topic = q

            for t in ("open news about", "open news on", "open google news",

                      "show me news about", "open news", "show me news",

                      "go to news", "open headlines"):

                topic = topic.replace(t, "").strip()

            get_news(topic)

        else:

            ai_query(query, search_first=True)

        return True


###############################################################################

    # ── WIKIPEDIA ────────────────────────────────────────────

    # Wikipedia only when user explicitly says wikipedia or wiki

    wiki_triggers = (

        "wikipedia", "wiki ", "search wikipedia", "look up on wikipedia",

        "find on wikipedia", "wikipedia article",

    )

    if any(p in q for p in wiki_triggers):

        topic = q

        for t in sorted(wiki_triggers, key=len, reverse=True):

            topic = topic.replace(t, "").strip()

        if topic:

            search_wikipedia(topic)

        else:

            speak("What topic would you like me to look up on the Wikipedia??")

        return True

#------------------------------------------------------------------------------------------------------------------#

    # ── YOUTUBE SEARCH ───────────────────────────────────────

    if any(p in q for p in ("search youtube", "youtube search", "find on youtube",

                             "look up on youtube", "play on youtube",

                             "search youtube for")):

        topic = q

        for t in ("search youtube for", "search youtube", "youtube search",

                  "find on youtube", "look up on youtube", "play on youtube"):

            topic = topic.replace(t, "").strip()

        search_youtube(topic); return True



    # ── SEARCH IN CHROME ─────────────────────────────────────

    if any(p in q for p in ("search in chrome", "search on chrome",

                            "google in chrome", "open chrome and search",

                             "look up in chrome", "find in chrome",

                             "search chrome for")):

        topic = q

        for t in ("search in chrome for", "search in chrome", "search on chrome",

                  "google in chrome", "open chrome and search",

                  "look up in chrome", "find in chrome", "search chrome for"):

            topic = topic.replace(t, "").strip()

        search_in_chrome(topic) if topic else speak(

            "What would you like to search for in Chrome?"

        )

        return True



    # ── EXPLICIT WEB SEARCH — only when user says search/google ─────

    web_triggers = (

        "google it up", "could you refer google,"

        "search on google", "search google", "google search",

        "search on chrome", "search in chrome", "search chrome",

        "search the web", "search online", "search duckduckgo",

        "google that", "google it", "google this",

        "can you google", "can you search",

        "check on google", "check google", "look up on google",

        "search for me", "web search",

    )

    if any(p in q for p in web_triggers):

        topic = q

        for t in sorted(web_triggers, key=len, reverse=True):

            topic = topic.replace(t, "").strip()

        if not topic and len(_history) >= 2:

            topic = _history[-2].get("content", "").strip()[:120]

        web_search(topic) if topic else speak("What would you like me to search for?")

        return True



    # ── OPEN APPS / WEBSITES (with optional Chrome) ──────────

    if any(q.startswith(v.strip()) for v in _OPEN_VERBS) or any(

        p in q for p in _CHROME_HINTS

    ):

        open_app(q); return True



    # ── JOKES ────────────────────────────────────────────────

    if any(p in q for p in ("joke", "tell me a joke", "make me laugh",

                             "i'm bored tell me a joke"

                             "something funny", "hear a joke")):

        speak(pyjokes.get_joke()); return True



    # ── IDENTITY ─────────────────────────────────────────────

    if any(p in q for p in ("what is your name", "who are you",

                             "what are you called", "introduce yourself")):

        name = load_name()

        speak(f"I am {name}, your personal AI assistant. How may I be of service today?")

        return True



    if any(p in q for p in ("change your name", "rename yourself",

                             "i'll call you", "call yourself")):

        set_name(); return True


    #==========================================================
    #
    #
    # ── HELP ─────────────────────────────────────────────────

    if any(p in q for p in ("help", "what can you do", "your capabilities",

                             "list features", "what commands",

                             "what do you know", "what are you capabilities")):

        speak(

            "Here is what I can do, sir. "

            "Tell you the exact time and date. "

            "Check the weather for any city. "

            "Search the web via DuckDuckGo and Google — and read you the answer. "

            "Look things up on Wikipedia. "

            "Open any app or website, and specifically in Chrome if you ask. "

            "Search YouTube. Read the news. Play your music. Take screenshots. "

            "Control volume. Check wifi. Tell jokes. "

            "And answer almost anything using AI, including maths, coding, and general knowledge. "

            "Just speak naturally — I will figure it out."

            "Perform basic tasks on your system."
        )

        return True


    #===========================================================================
    #THIS FEATURE IS USED TO DETECT WHICH WORDS MEANS TO CLEAR CHAT MEMORY CACHE
    #
    #
    # ── CLEAR MEMORY ─────────────────────────────────────────-----------------

    if any(p in q for p in ("clear memory", "clear cache",

                             "system reset", "new", "chat reset"

                             "reset conversation", "clear history",

                             "start fresh", "new conversation")):

        _history.clear()

        speak("Conversation memory system caches all cleared. Refreshed, sir!")

        return True


    #=================================================================================
    # THIS FEATURE IS FOR SEARCH RELATED TO CURRENT EVENTS AND HAPPENINGS IN THE WORLD
    #=================================================================================
    # ── LIVE / CURRENT EVENTS → web context + AI ─────────────

    live_words = ("latest", "current", "right now", "today's",

                  "latest happenings", "updates of the day",

                  "this week", "recently", "who won", "what happened",

                  "breaking", "just announced", "just released")

    if any(p in q for p in live_words):

        ai_query(query, search_first=True); return True


    #=====================================================
    #
    #
    # ── MATHS / CALCULATIONS ────

    math_words = ("calculate", "what is", "how much is", "solve",

                  "plus", "minus", "times", "divided by",

                  "square root", "percentage", "percent of",

                  "sum", "add", "subtract", "divide", "multiply",

                   "integrate", "cube root", "factorise",

                  "to the power", "factorial", "integral", "derivative")

    if any(p in q for p in math_words):

        ai_query(query); return True

    #=============================================================================
    # THIS FEATURE IS FOR REFERING THE ASSISTANT TO NOT USE AI AND SPEND TOKEN FOR
    #CASUALR CHAT INSTEAD ITS PRESET WITH CASUAL CHAT
    #=============================================================================
    # ── CASUAL CHIT-CHAT — go straight to AI, no search needed on the web --
    #============================================================================

    casual_patterns = (

        "hi", "hello", "hey", "sup", "wassup", "what's up", "whats up", "supp"<

        "how are you", "how r u", "you good", "you okay",

        "good morning", "good night", "good evening", "good afternoon",

        "thanks", "thank you", "cheers", "nice", "cool", "okay",

        "haha", "lol", "hmm", "interesting", "wow",

        "tell me something", "talk to me", "say something",

        "you there", "are you there", "you awake",

        "i'm bored", "im bored", "entertain me",

        "what do you think", "your thoughts", "your opinion", "what do you feel about it"<

    )

    if any(p in q for p in casual_patterns) or len(q.split()) <= 4:

        ai_query(query); return True


    ##########################################################################
    # W
    #
    # ── CATCH-ALL: everything else → AI answers directly ────────────

    ai_query(query)

    return True



#========================================================================
# THIS FEATURE GIVEN BELOW IS TO TEST IF THE CODE IS WORKING OR NOT
#========================================================================

# ══════════════════════════════════════════════════════════════

#  MAIN ENTRY POINT

# ══════════════════════════════════════════════════════════════



if __name__ == "__main__":

    # Quick test without mic: python3 jarvis.py "open youtube in chrome"

    if len(sys.argv) > 1:

        handle(" ".join(sys.argv[1:]).lower())

        sys.exit(0)

######################################################################################

    wishme()



    try:

        while True:

            query = takecommand()

            if not query:

                continue

            if not handle(query):

                break

    except KeyboardInterrupt:

        speak("Interrupted. Goodbye, sir.")

        sys.exit(0)


#================================================================
#  UPDATES-TRIAL TEST NOTES BELOW
#================================================================
# NEW FEATURES COMING IS TESTING GOING
#
#MSG PPL ON WHATSAPP USING VOICE COMMAND NEED TO SET NAMES HERE IN CODE FILE BUT SPECIFIC
#
#LOOK UP FILES OR DOCUMENTS WITH FILE SEARCH COMMAND
#
#CALLING SOMEONE FROM YOUR DEVICE
#
#SEARCH FILES ON THE SYSTEM
#
#OPEN SPECIFIC FILES OR FOLDERS
#
#SHUTDOWN OR SLEEP OR LOCKSCREEN DEVICE NEVER OPEN BECAUSE FEATURE MAY BE ABUSED
#
#ALLOW INTEGRATION OF HIGHER AND PAID MODELS ALSO VIA OPEN ROUTER (PAID API USERS CAN AVAIL THIS FEATURE)
#
#ADD MORE APPS TO LAUNCH FEATURE
#
#ADD MORE WEBSITES TO OPEN
#
#THINKING PROCESS TO BE MORE NATURAL
#
#MORE CHAT FEATURES AND DATA TRAINING FOR CHAT MODE
#
#CHAT MEMORY IS A FEATURE THAT ONE MAY NEED TO ENABLE OR DISABLE AS PER THEIR NEEDS
#
#EFFICIENT SPEECH RECOGNITION FOR PROPER RESPONSES
#
#CASUAL CHAT TRAINING TO USE ABOVE FEATURE OF MEMORY AND INTEGRATION OF GPT CHAT MODE
#
#CHATBOT EFFICIENCY
#
#HELP MODE FOR SUPPORT AND A SUPPORT GUIDE FOR TROUBLESHOOTING SOME COMMON ISSUES
#LIKE REQUIREMENTS RELATED AND SYSTEM AS ITS A CROSS PLATFORM TOO
#
#EFFICIENCY OF EXISTING TOOLS IS INCREASED AND MORE WORDS ADDED
#FOR RECOGNITION
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
