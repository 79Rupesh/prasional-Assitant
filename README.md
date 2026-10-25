# Ela

Ela is a Windows and macOS desktop voice assistant. The current application uses a
microphone recorder, Whisper speech recognition, a text wake-word gate, local
task classification, action handlers, local conversation responses, and an
optional LLM provider. Conversation and task context are held in memory for
the current process only.

## Run

From the project folder, use the matching environment:

```bat
.venv\Scripts\python.exe -m app.main
```

On macOS, see [MACOS_SETUP.md](MACOS_SETUP.md) and run:

```bash
.venv/bin/python -m app.main
```

Optional incoming phone control setup is documented in
[PHONE_CONTROL_SETUP.md](PHONE_CONTROL_SETUP.md). It requires a Twilio voice
number, an HTTPS tunnel, an allow-listed caller, a separate phone PIN, and
spoken approval for each task.

Configure `ELA_PIN` and the API key for the selected LLM provider in the local
`.env` file. Do not commit or include `.env` in a shared ZIP.

`LLM_PROVIDER` defaults to `gemini` and requires `GEMINI_API_KEY`; optionally
select the model with `GEMINI_MODEL`. For OpenAI, set `LLM_PROVIDER=openai`,
`OPENAI_API_KEY` (or legacy `LLM_API_KEY`), and optionally `OPENAI_MODEL`
(default `gpt-4o-mini`). For OpenRouter, set `LLM_PROVIDER=openrouter`,
`OPENROUTER_API_KEY`, and optionally `OPENROUTER_MODEL` (default is the
configured free model). Provider quota/rate-limit failures are logged with
exception details and returned as a retry/quota message instead of crashing.
Greetings, common conversational replies, the current date/time, and basic
capability questions are answered locally; the LLM is reserved for requests
that need more reasoning or knowledge.

The optional `ELA_WAKE_TIMEOUT_SECONDS` setting controls how long follow-up
speech is accepted after the wake word. It defaults to 45 seconds and must be
between 5 and 300 seconds.

## Microphone troubleshooting

Ela calibrates microphone noise automatically before each recording. To list
the available input devices without recording audio, run:

```bat
.venv\Scripts\python.exe -m audio.microphone.diagnostics
```

Set `ELA_MIC_DEVICE` to the selected device number only if the system default
is wrong. For a very quiet microphone, set `ELA_MIC_SENSITIVITY=1.5` in `.env`
to lower the speech threshold. Captured audio stays in memory by default. To
opt in to temporary microphone debugging, set `ELA_SAVE_MIC_DIAGNOSTIC=true`;
Ela then writes a WAV file in the operating system's temporary folder.
(allowed range: 0.5–3; higher means more sensitive).
The recorder requires repeated speech-level blocks to start and discards
short transients. Whisper additionally rejects low-level/noise-only audio and
trims silence. Set `ELA_WHISPER_LANGUAGE=auto`, `en`, or `hi` to choose automatic
language detection or pin English/Hindi; in auto mode, unsupported language
guesses are retried using both supported languages.

## Current voice and browser behavior

- Audio is recorded as 16 kHz, mono, 16-bit PCM, gated against calibrated room
  noise, and split on detected silence.
- Whisper output is quality-gated; only English and Hindi language results are
  accepted. Clear Hindi/Hinglish recognition is not guaranteed.
- Standby recognizes “Ela” and clear open/navigation commands addressed with a
  final “AI”. This uses recognized text rather than a dedicated audio wake-word
  detector, so it cannot guarantee immunity to Whisper hallucinations.
- Browser handlers request navigation in Chrome. YouTube falls back to the
  system default browser if Chrome is not installed. Ela cannot verify that a
  page finished loading, so it reports the launch request without claiming the
  page load was verified.
- Opening apps and websites, browser controls, searches, and ordinary desktop
  commands run from one instruction. Delete, move, and rename operations ask
  for approval after Ela resolves the exact file; WhatsApp asks once after the
  recipient and attachment are verified. Safe ordered commands run directly.
- File copy works between existing folders. WhatsApp document sending checks
  the selected contact and attachment on screen, then asks again before Send.
  Windows needs the Tesseract OCR application installed for this screen check.

Run the safe, focused tests and syntax check with:

```bat
venv\Scripts\python.exe -m pytest tests/test_voice_safety.py tests/test_speech_quality.py tests/test_microphone_thresholds.py tests/test_llm_resilience.py
venv\Scripts\python.exe -m unittest tests.test_task_state tests.test_browser_launch tests.test_explicit_task_routing tests.test_settings
venv\Scripts\python.exe -m compileall -q app actions audio brain core tests
```

The microphone, Whisper model, physical wake word, and real Chrome navigation
must still be validated on the target Windows machine.

## Roadmap

1. Complete and validate the V2 core: robust wake detection, reliable speech,
   browser state verification, cancellation, confirmation, and task recovery.
2. Add authorized desktop, window, keyboard/mouse, and document workflows.
3. Consider web research, multitasking, messaging, and remote-control features
   only after the core is stable.
