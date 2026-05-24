"""
web/server.py — WGM Flask Web Server
Run this file: python3 web/server.py
Then open:     http://localhost:5000
"""

import sys
import os
import socket
import threading
import importlib.util

# ── Make sure wgm_all_devices.py (project root) is importable ─
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, _ROOT)

# ── Import the assistant brain from WGM-ALL-DEVICES.py ────────
# The filename contains hyphens so we must use importlib directly.
_wgm_path = os.path.join(_ROOT, "wgm_all_devices.py")
_spec = importlib.util.spec_from_file_location("wgm", _wgm_path)
if _spec is None or not os.path.exists(_wgm_path):
    print(f"\n  ✗ Cannot find wgm_all_devices.py")
    print(f"  ✗ Expected at: {_wgm_path}")
    print(f"  ✗ Make sure server.py is inside a 'web/' subfolder of your project root.\n")
    sys.exit(1)
_wgm = importlib.util.module_from_spec(_spec)
sys.modules["wgm"] = _wgm
_spec.loader.exec_module(_wgm)

handle          = _wgm.handle
wishme          = _wgm.wishme
speak           = _wgm.speak
_clean_for_speech = _wgm._clean_for_speech

# ── Thread-local storage so concurrent users don't mix ───────
_ctx = threading.local()


def _capture_speak(text: str, rate: int = None):
    """Replacement speak() that captures text instead of using TTS in web mode."""
    clean = _clean_for_speech(str(text))
    if not clean:
        return
    print(f"\n  ◆ WGM: {clean}\n")
    # Only capture when inside a web request
    if getattr(_ctx, "capturing", False):
        _ctx.response = getattr(_ctx, "response", "") + clean + " "


def _web_handle(query: str) -> str:
    """Run handle() with speak() captured, return the text response."""
    original_speak = _wgm.speak

    # Patch speak on the wgm module so every call inside handle() is captured
    _wgm.speak = _capture_speak

    _ctx.capturing = True
    _ctx.response = ""

    try:
        handle(query)
    except Exception as e:
        _ctx.response = f"Something went wrong: {e}"
    finally:
        _wgm.speak = original_speak
        _ctx.capturing = False

    result = _ctx.response.strip()
    _ctx.response = ""
    return result if result else "Done."


def _web_greet() -> str:
    """Run wishme() and capture the greeting text."""
    original_speak = _wgm.speak
    _wgm.speak = _capture_speak

    _ctx.capturing = True
    _ctx.response = ""

    try:
        wishme()
    except Exception:
        pass
    finally:
        _wgm.speak = original_speak
        _ctx.capturing = False

    result = _ctx.response.strip()
    _ctx.response = ""
    return result if result else "W.G.M. is online. How may I assist you?"


# ── Flask setup ───────────────────────────────────────────────
try:
    from flask import Flask, render_template, request, jsonify
    _FLASK_OK = True
except ImportError:
    _FLASK_OK = False


def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"


if _FLASK_OK:
    # Templates + static folders are one level up from this file
    _root = os.path.join(os.path.dirname(__file__))
    app = Flask(
        __name__,
        template_folder=os.path.join(_root, "templates"),
        static_folder=os.path.join(_root, "static"),
    )

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/greet")
    def greet():
        return jsonify({"reply": _web_greet()})

    @app.route("/chat", methods=["POST"])
    def chat():
        data = request.get_json(silent=True) or {}
        query = (data.get("query") or "").strip()
        if not query:
            return jsonify({"reply": "I didn't catch that — could you rephrase?"})
        reply = _web_handle(query.lower())
        return jsonify({"reply": reply})


if __name__ == "__main__":
    if not _FLASK_OK:
        print("\n  Flask is not installed.")
        print("  Run:  pip install flask\n")
        sys.exit(1)

    ip = get_local_ip()
    print("\n" + "═" * 54)
    print("  ◆ WGM Web UI")
    print(f"  ◆ Local   → http://localhost:5000")
    print(f"  ◆ Network → http://{ip}:5000")
    print("  ◆ Ctrl+C to stop")
    print("═" * 54 + "\n")

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
