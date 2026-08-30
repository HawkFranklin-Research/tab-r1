FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HUB_DISABLE_XET=1

RUN apt-get update && apt-get install -y --no-install-recommends git zstd libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace/tab-r1
COPY package ./package
COPY tabfm ./tabfm
COPY paper/analysis ./paper/analysis

RUN python -m pip install --upgrade pip \
    && python -m pip install ./package \
    && python -m pip install './tabfm[pytorch]' pyarrow huggingface-hub

ENTRYPOINT ["python", "paper/analysis/run_cloud_evaluation.py"]
