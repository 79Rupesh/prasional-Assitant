"""Local, offline wake-phrase detection for ELA.

Uses sherpa-onnx's small English keyword-spotting model with custom keywords
"ELA" and "HEY ELA". Inference stays in a worker thread; the audio callback
only copies a short frame into a bounded queue.
"""
from __future__ import annotations

import importlib.util
import os
import queue
import shutil
import subprocess
import sys
import tarfile
import threading
from pathlib import Path
from typing import Callable
from urllib.request import Request, urlopen


WAKE_MODEL = "sherpa-onnx-kws-zipformer-gigaspeech-3.3M-2024-01-01"
MODEL_URL = (
    "https://github.com/k2-fsa/sherpa-onnx/releases/download/kws-models/"
    f"{WAKE_MODEL}.tar.bz2"
)
SAMPLE_RATE = 16000
WAKE_PHRASES = (("ELA", 0.40), ("HEY ELA", 0.32))

_MODEL_FILES = (
    "tokens.txt",
    "bpe.model",
    "encoder-epoch-12-avg-2-chunk-16-left-64.int8.onnx",
    "decoder-epoch-12-avg-2-chunk-16-left-64.int8.onnx",
    "joiner-epoch-12-avg-2-chunk-16-left-64.int8.onnx",
)


def _model_dir() -> Path:
    local = os.environ.get("LOCALAPPDATA")
    root = Path(local) if local else Path.home() / ".cache"
    return root / "ELA" / "models" / WAKE_MODEL


def is_installed() -> bool:
    """Return whether the wake detector and tokenizer dependencies are present."""
    try:
        return (importlib.util.find_spec("sherpa_onnx") is not None
                and importlib.util.find_spec("sentencepiece") is not None
                and importlib.util.find_spec("pypinyin") is not None)
    except Exception:
        return False


def _model_files_present(model_dir: Path) -> bool:
    return all((model_dir / name).is_file() for name in _MODEL_FILES)


def is_ready() -> bool:
    """Check runtime and downloaded model files without loading neural nets."""
    if not is_installed():
        return False
    model_dir = _model_dir()
    return _model_files_present(model_dir) and (model_dir / "keywords.txt").is_file()


def _write_keywords(model_dir: Path) -> None:
    """Tokenize the custom English wake phrases using this model's BPE vocab."""
    import sherpa_onnx

    encoded = sherpa_onnx.text2token(
        texts=[phrase for phrase, _threshold in WAKE_PHRASES],
        tokens=str(model_dir / "tokens.txt"),
        tokens_type="bpe",
        bpe_model=str(model_dir / "bpe.model"),
    )
    lines = [
        " ".join(tokens) + f" #{threshold:.2f}"
        for tokens, (_phrase, threshold) in zip(encoded, WAKE_PHRASES)
    ]
    if len(lines) != len(WAKE_PHRASES) or any(not line.strip() for line in lines):
        raise RuntimeError("Could not tokenize the ELA wake phrases.")
    (model_dir / "keywords.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def install_and_download(logger: Callable[[str], None] = print,
                         notify: Callable[[str], None] | None = None) -> tuple[bool, str]:
    """Install sherpa-onnx and download its small English KWS model once."""
    tell = notify or (lambda _msg: None)
    archive_path: Path | None = None
    try:
        if not is_installed():
            message = "Wake word: installing sherpa-onnx (one-time)…"
            logger(message)
            tell(message)
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "sherpa-onnx",
                 "sentencepiece", "pypinyin"],
                capture_output=True,
                text=True,
                timeout=600,
            )
            if result.returncode != 0:
                tail = (result.stderr or result.stdout or "").strip().splitlines()[-1:]
                return False, f"sherpa-onnx install failed: {(tail or [''])[0][:180]}"

        model_dir = _model_dir()
        model_dir.parent.mkdir(parents=True, exist_ok=True)
        if not _model_files_present(model_dir):
            message = "Wake word: downloading the small English ELA model…"
            logger(message)
            tell(message)
            archive_path = model_dir.parent / f"{WAKE_MODEL}.tar.bz2"
            request = Request(MODEL_URL, headers={"User-Agent": "ELA assistant"})
            with urlopen(request, timeout=60) as response, archive_path.open("wb") as out:
                shutil.copyfileobj(response, out)

            wanted = set(_MODEL_FILES)
            extracted: set[str] = set()
            with tarfile.open(archive_path, mode="r:bz2") as archive:
                for member in archive.getmembers():
                    parts = Path(member.name).parts
                    if (len(parts) != 2 or parts[0] != WAKE_MODEL
                            or parts[1] not in wanted or not member.isfile()):
                        continue
                    source = archive.extractfile(member)
                    if source is None:
                        continue
                    destination = model_dir / parts[1]
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    with source, destination.open("wb") as out:
                        shutil.copyfileobj(source, out)
                    extracted.add(parts[1])
            if extracted != wanted:
                return False, "The downloaded wake-word model is incomplete."

        if not (model_dir / "keywords.txt").is_file():
            _write_keywords(model_dir)
        if not is_ready():
            return False, "Wake-word setup finished, but the model is not ready."
        logger("Wake word: ready for 'Ela' and 'Hey Ela'.")
        return True, "Wake word installed and ready."
    except Exception as exc:
        return False, f"Wake-word setup error: {exc}"
    finally:
        if archive_path is not None:
            try:
                archive_path.unlink(missing_ok=True)
            except Exception:
                pass


class WakeWordDetector:
    """Feed microphone frames to a local sherpa-onnx keyword spotter."""

    def __init__(self, on_detect: Callable[[], None],
                 threshold: float = 0.5,
                 logger: Callable[[str], None] = print,
                 notify: Callable[[str], None] | None = None):
        self._on_detect = on_detect
        self._threshold = threshold
        self._logger = logger
        self._notify = notify or (lambda _msg: None)
        self._queue: queue.Queue = queue.Queue(maxsize=50)
        self._thread: threading.Thread | None = None
        self._running = False
        self._model = None
        self._stream = None
        self._ready = False

    def start(self) -> bool:
        """Load the model and start inference. Safe to call more than once."""
        if self._running:
            return True
        if not is_ready():
            self._logger("Wake word: sherpa-onnx model files are missing.")
            return False
        try:
            import sherpa_onnx

            model_dir = _model_dir()
            self._model = sherpa_onnx.KeywordSpotter(
                tokens=str(model_dir / "tokens.txt"),
                encoder=str(model_dir / _MODEL_FILES[2]),
                decoder=str(model_dir / _MODEL_FILES[3]),
                joiner=str(model_dir / _MODEL_FILES[4]),
                keywords_file=str(model_dir / "keywords.txt"),
                num_threads=1,
                sample_rate=SAMPLE_RATE,
                feature_dim=80,
                keywords_score=1.0,
                # Per-phrase thresholds live in keywords.txt. Keep a low global
                # floor so both the short and long phrases can be detected.
                keywords_threshold=min(0.25, self._threshold),
                provider="cpu",
            )
            self._stream = self._model.create_stream()
        except Exception as exc:
            self._logger(f"Wake word: could not load sherpa-onnx model — {exc}")
            self._notify("Wake word unavailable — use the WAKE NOW button.")
            self._model = None
            self._stream = None
            return False

        self._drain()
        self._running = True
        self._ready = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="WakeWordThread")
        self._thread.start()
        self._logger("Wake word: listening locally for 'Ela' or 'Hey Ela'.")
        return True

    def stop(self) -> None:
        self._running = False
        try:
            self._queue.put_nowait(None)
        except Exception:
            pass
        self._model = None
        self._stream = None
        self._ready = False

    @property
    def ready(self) -> bool:
        return self._ready

    def feed(self, frame_int16) -> None:
        """Copy a mic block into the bounded queue without blocking audio I/O."""
        if not self._running:
            return
        try:
            data = frame_int16[:, 0].copy() if getattr(frame_int16, "ndim", 1) > 1 else frame_int16.copy()
            self._queue.put_nowait(data)
        except queue.Full:
            pass
        except Exception:
            pass

    def _loop(self) -> None:
        import numpy as np

        model = self._model
        stream = self._stream
        if model is None or stream is None:
            return
        scale = np.float32(1.0 / 32768.0)
        while self._running:
            try:
                frame = self._queue.get()
                if frame is None or not self._running:
                    break
                samples = np.asarray(frame, dtype=np.int16).astype(np.float32) * scale
                stream.accept_waveform(SAMPLE_RATE, samples)
                while self._running and model.is_ready(stream):
                    model.decode_stream(stream)
                    if model.get_result(stream):
                        model.reset_stream(stream)
                        self._drain()
                        self._on_detect()
                        break
            except Exception as exc:
                self._logger(f"Wake word: inference error — {exc}")

    def _drain(self) -> None:
        try:
            while True:
                self._queue.get_nowait()
        except Exception:
            pass
