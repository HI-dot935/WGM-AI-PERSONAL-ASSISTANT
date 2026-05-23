// ════════════════════════════════════════
// WGM WEB UI — APP.JS
// Cyberpunk + Voice + TTS
// ════════════════════════════════════════

const chat = document.getElementById("chat");
const input = document.getElementById("msg-input");

let currentMode = "text";
let audioEnabled = true;
let msgCounter = 0;

const speakOverlay = document.getElementById("speak-overlay");
const voiceOverlay = document.getElementById("voice-overlay");


// ───────────────────────────────────────
// CLOCK
// ───────────────────────────────────────

setInterval(() => {
    const now = new Date();
    document.getElementById("clock-display").textContent =
        now.toLocaleTimeString();
}, 1000);


// ───────────────────────────────────────
// GRID BACKGROUND
// ───────────────────────────────────────

const canvas = document.getElementById("grid-canvas");
const ctx = canvas.getContext("2d");

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
resizeCanvas();

window.addEventListener("resize", resizeCanvas);

function drawGrid() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.strokeStyle = "rgba(0,212,255,0.06)";
    ctx.lineWidth = 1;

    const size = 40;

    for (let x = 0; x < canvas.width; x += size) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, canvas.height);
        ctx.stroke();
    }

    for (let y = 0; y < canvas.height; y += size) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(canvas.width, y);
        ctx.stroke();
    }

    requestAnimationFrame(drawGrid);
}

drawGrid();


// ───────────────────────────────────────
// TYPEWRITER EFFECT
// ───────────────────────────────────────

async function typeText(el, text) {
    el.classList.add("typing-text");

    for (let i = 0; i < text.length; i++) {
        el.innerHTML += text[i];
        await new Promise(r => setTimeout(r, 12));
    }

    el.classList.remove("typing-text");
}


// ───────────────────────────────────────
// ADD MESSAGE
// ───────────────────────────────────────

async function addMessage(text, sender = "wgm") {

    msgCounter++;
    document.getElementById("msg-count").textContent =
        String(msgCounter).padStart(3, "0");

    const msg = document.createElement("div");
    msg.className = `msg ${sender}`;

    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.innerText = sender === "wgm" ? "WGM" : "YOU";

    const content = document.createElement("div");

    const bubble = document.createElement("div");
    bubble.className = "bubble";

    const time = document.createElement("div");
    time.className = "msg-time";
    time.innerText = new Date().toLocaleTimeString();

    content.appendChild(bubble);
    content.appendChild(time);

    msg.appendChild(avatar);
    msg.appendChild(content);

    chat.appendChild(msg);

    chat.scrollTop = chat.scrollHeight;

    if (sender === "wgm") {
        await typeText(bubble, text);

        if (audioEnabled) {
            speakText(text);
        }

    } else {
        bubble.innerText = text;
    }
}


// ───────────────────────────────────────
// SEND MESSAGE
// ───────────────────────────────────────

async function sendMessage() {

    const text = input.value.trim();

    if (!text) return;

    addMessage(text, "user");

    input.value = "";

    const typing = createTypingIndicator();

    try {

        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                query: text
            })
        });

        const data = await response.json();

        typing.remove();

        addMessage(data.reply, "wgm");

    } catch (err) {

        typing.remove();

        addMessage(
            "Connection to WGM core failed.",
            "wgm"
        );

        console.error(err);
    }
}


// ───────────────────────────────────────
// TYPING INDICATOR
// ───────────────────────────────────────

function createTypingIndicator() {

    const wrap = document.createElement("div");
    wrap.className = "msg wgm";

    wrap.innerHTML = `
        <div class="avatar">WGM</div>

        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;

    chat.appendChild(wrap);

    chat.scrollTop = chat.scrollHeight;

    return wrap;
}


// ───────────────────────────────────────
// ENTER KEY
// ───────────────────────────────────────

input.addEventListener("keydown", (e) => {

    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});


// ───────────────────────────────────────
// SPEECH SYNTHESIS (TTS)
// ───────────────────────────────────────

function speakText(text) {

    if (!window.speechSynthesis) return;

    speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);

    utterance.rate = 1;
    utterance.pitch = 0.9;
    utterance.volume = 1;

    const voices = speechSynthesis.getVoices();

    const selected =
        voices.find(v =>
            v.name.toLowerCase().includes("david")
        ) ||
        voices.find(v =>
            v.name.toLowerCase().includes("google")
        ) ||
        voices[0];

    if (selected) utterance.voice = selected;

    utterance.onstart = () => {
        speakOverlay.classList.add("active");
    };

    utterance.onend = () => {
        speakOverlay.classList.remove("active");
    };

    speechSynthesis.speak(utterance);
}


// ───────────────────────────────────────
// AUDIO TOGGLE
// ───────────────────────────────────────

function toggleAudio() {

    audioEnabled = !audioEnabled;

    const btn = document.getElementById("audio-toggle-btn");

    if (audioEnabled) {

        btn.classList.remove("muted");
        document.getElementById("audio-icon").innerText = "🔊";
        document.getElementById("audio-status").innerText = "ON";

    } else {

        speechSynthesis.cancel();

        btn.classList.add("muted");
        document.getElementById("audio-icon").innerText = "🔇";
        document.getElementById("audio-status").innerText = "OFF";
    }
}


// ───────────────────────────────────────
// MODE SWITCH
// ───────────────────────────────────────

function setMode(mode) {

    currentMode = mode;

    document
        .querySelectorAll(".mode-btn")
        .forEach(btn => btn.classList.remove("active"));

    if (mode === "text") {

        document
            .getElementById("text-mode-btn")
            .classList.add("active");

    } else {

        document
            .getElementById("voice-mode-btn")
            .classList.add("active");
    }
}


// ───────────────────────────────────────
// VOICE INPUT
// ───────────────────────────────────────

let recognition;

function activateMic() {

    if (!('webkitSpeechRecognition' in window)) {

        alert("Speech recognition not supported.");
        return;
    }

    recognition = new webkitSpeechRecognition();

    recognition.continuous = false;
    recognition.lang = "en-US";

    voiceOverlay.classList.add("active");

    document
        .getElementById("mic-btn")
        .classList.add("listening");

    recognition.start();

    recognition.onresult = (event) => {

        const transcript =
            event.results[0][0].transcript;

        input.value = transcript;

        cancelVoice();

        sendMessage();
    };

    recognition.onerror = () => {
        cancelVoice();
    };

    recognition.onend = () => {
        cancelVoice();
    };
}

function cancelVoice() {

    voiceOverlay.classList.remove("active");

    document
        .getElementById("mic-btn")
        .classList.remove("listening");

    if (recognition) {
        recognition.stop();
    }
}


// ───────────────────────────────────────
// QUICK FILL
// ───────────────────────────────────────

function fillInput(text) {
    input.value = text;
    input.focus();
}


// ───────────────────────────────────────
// STARTUP MESSAGE
// ───────────────────────────────────────

window.onload = async () => {
    try {
        const res = await fetch("/greet");
        const data = await res.json();
        addMessage(data.reply || "W.G.M. online. Systems initialized successfully.", "wgm");
    } catch {
        addMessage("W.G.M. online. Systems initialized successfully.", "wgm");
    }
};
