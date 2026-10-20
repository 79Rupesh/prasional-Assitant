# Ela Voice + Chrome Browser Patch

This patch is designed for your existing Windows project. It does **not** replace the whole project or `.env`, and it does not change your OpenRouter setup.

## What it changes

- Records until speech ends (about 1.4 seconds of silence), instead of cutting everything at exactly 5 seconds. Maximum utterance length is 25 seconds; after 12 seconds with no speech, that listening cycle is skipped.
- Keeps audio at 48 kHz during capture, chooses the clearer stereo channel, resamples it to the 16 kHz mono format Whisper expects, and writes `mic_test.wav` for inspection.
- Uses Whisper automatic detection first, keeps Hindi, and retries English when an unsupported language is guessed or when output looks like obvious repeated-text hallucination. English speech also gets a contextual refinement pass.
- Routes website commands such as `open Facebook`, `open example.com`, and `visit ChatGPT` through the browser task parser.
- Launches URLs and Google searches explicitly in Google Chrome rather than silently falling back to Microsoft Edge.
- Sends YouTube open/search/play URLs to Chrome as well.
- Makes a timestamped backup of every file it changes before applying the patch.

## Apply it on your computer

1. Stop Ela with `Ctrl+C`.
2. Extract the contents of this ZIP **directly into** `C:\Users\hp\Desktop\Ela` (not into a nested new folder). You should see `apply_ela_patch.py` beside your existing `app`, `actions`, `audio`, and `brain` folders.
3. In CMD, run:

   ```bat
   cd /d C:\Users\hp\Desktop\Ela
   python apply_ela_patch.py
   ```

4. If it reports success, run this syntax check:

   ```bat
   python -m compileall audio actions brain
   ```

5. Start Ela again:

   ```bat
   python -m app.main
   ```

## Voice behavior

The microphone starts a sentence when it detects speech and ends it after about 1.4 seconds of silence. A single utterance is capped at 25 seconds. If you pause longer than that in the middle of a sentence, Ela may treat the pause as the end of the utterance. Short, clear commands remain best for desktop automation.

## Browser behavior

- `Open Chrome` opens a new Chrome tab.
- `Open Facebook`, `Open YouTube`, `Open ChatGPT`, `Open GitHub`, and other mapped website names open their homepages in Chrome.
- A domain or URL such as `Open example.com` opens that domain in Chrome.
- For an unknown site name without a URL, Ela opens Google search results for that name in Chrome rather than guessing a potentially invalid URL.
- `Search for artificial intelligence in simple words` opens Google results in Chrome.
- `Search for lo-fi music on YouTube` should stay on the dedicated YouTube flow.

## Notes

Whisper cannot guarantee perfect transcription for every accent or noisy utterance. This patch reduces fixed-length cutoffs and avoids forcing the model's first language guess; it does not make speech recognition infallible. The script preserves the project's existing `WindowsBrowserController` methods other than `open()` and `search()`.
