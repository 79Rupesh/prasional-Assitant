# Ela — Windows setup

This port keeps the existing project structure and task logic where possible, replacing direct macOS commands with Windows implementations. It is a first Windows port, so validate each feature on your machine before relying on it.

## 1. Requirements
- Windows 10/11, 64-bit
- Python 3.10 or 3.11 recommended
- A working microphone
- Internet connection for first-time Whisper model download
- Tesseract OCR is optional and required only for screen text recognition

## 2. Open the project folder
Open Command Prompt or PowerShell in the folder containing `main.py`'s parent package (`Ela`).

```powershell
cd path	o\Ela
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-windows.txt
```

If PowerShell blocks activation, use Command Prompt instead:

```bat
.venv\Scriptsctivate.bat
```

## 3. Configure `.env`
Copy `.env.example` to `.env` and set a PIN, for example:

```dotenv
ELA_ENV=development
ELA_PIN=choose-a-local-pin
LLM_API_KEY=
STT_API_KEY=
TTS_API_KEY=
```

Do not commit `.env` or share your PIN/API keys.

## 4. Run
From inside the `Ela` folder:

```powershell
python -m app.main
```

The current app asks for the PIN through its authenticator. On first launch, Whisper may download the `base` model and can take time to load.

## 5. Windows-specific notes
- TTS uses Windows PowerShell's `System.Speech` API.
- Mouse and keyboard actions use PyAutoGUI. They act on the real desktop, so test carefully.
- Browser navigation uses the default browser and keyboard shortcuts; it does not provide the same AppleScript-level browser introspection as macOS.
- Screen OCR requires installing the Tesseract OCR application separately and then `pytesseract`/Pillow in Python.
- Some existing tests explicitly test macOS classes and should remain macOS tests; run Windows-compatible tests selectively and add tests for the new Windows classes.
