# Ela

## Windows quick start

The project dependencies are installed in the local `venv` folder. To start Ela from PowerShell:

```powershell
.\venv\Scripts\python.exe main.py
```

To reinstall the declared dependencies later:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -m playwright install chromium firefox
```

Ela needs a Gemini API key in `config/api_keys.json`. Keep that file private and do not share it. Screen analysis is available when you ask Ela to inspect your screen; it uses the installed `mss` package. Browser automation uses the installed Playwright browsers.

The optional `pandas`, `pydub`, and `mediapipe` packages are not part of the base install. When wake-word mode is enabled, the app downloads the local `sherpa-onnx` keyword spotter and its model on first launch; audio conversion with `pydub` also needs FFmpeg. Wake-word listening can be turned off in Ela settings.

## Background assistant

After setup, Ela registers itself to start with your Windows user account. It listens locally for **“Ela”** or **“Hey Ela”**; the floating icon and Gemini session stay off while it sleeps. After the wake phrase, audio is buffered locally while Gemini connects so the same spoken request can be handled. Ela returns to local wake-word listening after her answer finishes, and also sleeps after two minutes if no request follows. The first run sets up the local wake-word package and model; an internet connection is needed for that one-time download.

Use the tray menu to open controls, wake or sleep Ela manually, or exit. The dashboard and audio device meters pause while the main window is hidden.

## Phone dashboard

Open ELA from the system tray, then open the settings drawer and choose **Connect phone · show QR**. You can also right-click the floating icon while ELA is awake. The phone and computer must be on the same Wi-Fi network, with Ela running on the computer. The phone page supports text and live voice. The first phone connection may ask you to accept Ela's local HTTPS certificate. A phone can wake Ela by sending a deliberate remote command.

Windows keeps the lock screen under its own sign-in security. Ela can lock the laptop, but it cannot collect or replay your Windows password to unlock it; unlock with Windows Hello or the normal Windows sign-in screen.

Ela's default voice is Kore, and the default HUD uses the reactor core without a face.
