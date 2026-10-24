"""
Kalki Know — offline voice input using Vosk.
Records from the mic, transcribes locally. No internet needed.
"""

import os
import json
import queue

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "vosk_model")

_model = None  # lazy-loaded once


def _ensure_model():
    """Download + load the Vosk English model once, cache it on disk."""
    global _model
    if _model is not None:
        return _model

    try:
        from vosk import Model, SetLogLevel
        SetLogLevel(-1)  # silence Vosk's own logging
    except ImportError:
        raise RuntimeError(
            "Vosk not installed. Run this in your terminal:\n"
            "    pip install vosk sounddevice"
        )

    # If a model folder exists next to this file, use it.
    if os.path.isdir(MODEL_DIR):
        _model = Model(MODEL_DIR)
    else:
        # This downloads the small English model (~40 MB) on first call
        _model = Model(lang="en-us")
    return _model


def transcribe_from_mic(max_seconds=8):
    """
    Listen once from the default microphone, transcribe offline.
    Returns (text, error). error is None on success.
    """
    try:
        import sounddevice as sd
        from vosk import KaldiRecognizer
    except ImportError:
        return None, ("Voice input needs Vosk and sounddevice.\n\n"
                      "Run:  pip install vosk sounddevice")

    try:
        model = _ensure_model()
    except Exception as e:
        return None, f"Could not load Vosk model:\n{e}"

    samplerate = 16000
    q = queue.Queue()

    def _callback(indata, frames, time_info, status):
        if status:
            pass  # ignore stream status warnings
        q.put(bytes(indata))

    try:
        rec = KaldiRecognizer(model, samplerate)
        rec.SetWords(False)

        with sd.RawInputStream(
            samplerate=samplerate,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=_callback,
        ):
            # Collect for up to max_seconds, stop early if silence
            import time
            start = time.time()
            silence_frames = 0
            got_audio = False

            while time.time() - start < max_seconds:
                try:
                    data = q.get(timeout=0.5)
                except queue.Empty:
                    silence_frames += 1
                    if got_audio and silence_frames > 4:  # ~2s of silence → stop
                        break
                    continue

                got_audio = True
                silence_frames = 0
                if rec.AcceptWaveform(data):
                    break

            result = json.loads(rec.FinalResult())
            text = (result.get("text") or "").strip()
            if not text:
                return None, "Didn't hear anything. Try again."
            return text, None

    except OSError:
        return None, ("No microphone detected, or access was denied.\n"
                      "Please type your question instead.")
    except Exception as e:
        return None, f"Microphone error: {e}"