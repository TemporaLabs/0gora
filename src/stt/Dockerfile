# 0Gora STT (faster-whisper). Built ONLY under the `voice` compose profile — a
# default 0Gora deploy never builds this, so it carries zero footprint unless
# an instance opts into voice. Python 3.11 (ctranslate2/onnxruntime wheels).
FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
# Bake the model into the image so there is no runtime download (audio never
# leaves the box). Override the size at build with --build-arg STT_MODEL=tiny|base|small.
ARG STT_MODEL=base
ENV STT_MODEL=${STT_MODEL}
RUN python -c "from faster_whisper import WhisperModel; WhisperModel('${STT_MODEL}', device='cpu', compute_type='int8')"
COPY app.py ./
EXPOSE 8092
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8092"]
