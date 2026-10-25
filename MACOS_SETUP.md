# Ela — macOS setup

Ela selects the macOS implementation automatically when it runs on macOS.

## Install

```bash
cd /path/to/Ela
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-macos.txt
python -m app.main
```

Set `ELA_PIN` in your local `.env` before starting.

## Required macOS permissions

- Allow your terminal (or the Python IDE running Ela) in **Privacy & Security → Microphone**.
- Allow it in **Privacy & Security → Accessibility** for keyboard, mouse, and browser-tab controls.
- Allow it in **Privacy & Security → Screen Recording** for screenshots and on-screen text lookup.

The first Whisper run can download a model, so it needs an internet connection.
