"""0Gora STT — self-hosted speech-to-text (faster-whisper).

OPTIONAL, opt-in voice transcription. This service lives in the framework but runs
ONLY under the `voice` Docker Compose profile, so a default 0Gora deploy never
builds or starts it — zero footprint unless an instance opts in (see
examples/0g/0gora.config.json `voice` + deploying with `--profile voice`).

Audio is transcribed on-box and never leaves the stack — unlike the browser Web
Speech API, which streams audio to Google. That keeps voice on-stack, in line with
0Gora's verifiable-compute theme. The transcription itself is not 0G-verified
(it's not the answer); the answer the user then asks still runs + verifies on 0G.
"""
from __future__ import annotations

import os
import tempfile

from fastapi import FastAPI, File, HTTPException, UploadFile

MODEL_SIZE = os.environ.get("STT_MODEL", "base")
# Empty => auto-detect language (handles multilingual dictation); set e.g. "en" to pin.
LANG = os.environ.get("STT_LANG", "").strip() or None

app = FastAPI(title="0Gora STT", version="0.2.2")
_model = None


def model():
    global _model
    if _model is None:
        from faster_whisper import WhisperModel

        # int8 on CPU — small RAM footprint, fast enough for short dictation clips.
        _model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
    return _model


@app.on_event("startup")
async def _warm() -> None:
    # Load the model once at startup so the first transcription isn't slow.
    model()


@app.get("/transcribe/health")
async def health():
    return {"status": "ok", "service": "0gora-stt", "model": MODEL_SIZE}


@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    """Multipart audio (webm/opus, mp4, wav…) → {text}. Decoded via ffmpeg."""
    data = await audio.read()
    if not data:
        raise HTTPException(status_code=400, detail="empty audio")
    # faster-whisper reads a path; ffmpeg (in the image) decodes whatever the
    # browser's MediaRecorder produced.
    with tempfile.NamedTemporaryFile(suffix=".audio", delete=True) as f:
        f.write(data)
        f.flush()
        try:
            segments, _info = model().transcribe(f.name, beam_size=1, language=LANG, vad_filter=True)
            text = "".join(s.text for s in segments).strip()
        except ValueError:
            # vad_filter raises on a clip with no detected speech (silence) — treat as
            # "nothing said" rather than a 500; the UI shows "didn't catch that".
            text = ""
    return {"text": text}
