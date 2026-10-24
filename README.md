# Ela

Ela is a Windows desktop voice assistant. The current application uses a
microphone recorder, Whisper speech recognition, a text wake-word gate, local
task classification, action handlers, local conversation responses, and an
optional LLM provider. Conversation and task context are held in memory for
the current process only.

## Run

From the project folder in Command Prompt:

```bat
venv\Scripts\python.exe -m app.main
```

Configure `ELA_PIN` and the API key for the selected LLM provider in the local
`.env` file. Do not commit or include `.env` in a shared ZIP.

The optional `ELA_WAKE_TIMEOUT_SECONDS` setting controls how long follow-up
speech is accepted after the wake word. It defaults to 45 seconds and must be
between 5 and 300 seconds.

## Current voice and browser behavior

- Audio is recorded as 16 kHz, mono, 16-bit PCM and split on detected silence.
- Whisper output is quality-gated; only English and Hindi language results are
  accepted. Clear Hindi/Hinglish recognition is not guaranteed.
- Standby activation currently depends on the recognized text beginning with
  “Ela” or a supported spelling. This is **not** a dedicated audio wake-word
  detector, so it cannot guarantee immunity to Whisper hallucinations.
- Browser handlers request navigation in Chrome. They currently cannot verify
  that a page finished loading, so Ela reports that limitation rather than
  claiming verified completion.
- `mic_test.wav` is overwritten with the latest captured utterance for
  troubleshooting.

Run the safe, focused tests and syntax check with:

```bat
venv\Scripts\python.exe -m unittest tests.test_voice_safety tests.test_task_state tests.test_browser_launch tests.test_explicit_task_routing tests.test_settings
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
