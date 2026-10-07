# survival_v2 image: the pipeline, TabPFN (v2 - v3), TabFM (PyTorch) and the evaluator package of the paper pipeline.
# Build from the repository root:   docker build -f survival_v2/Dockerfile -t survival-v2 .
# The c-5 data and METABRIC are NOT baked in; mount them (see scripts/gcloud_launch.sh) and point the config at them.
FROM pytorch/pytorch:2.4.1-cuda12.1-cudnn9-runtime

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 HF_HUB_DISABLE_XET=1

RUN apt-get update && apt-get install -y --no-install-recommends git libgomp1 && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace/tab-r1
COPY package ./package
COPY tabfm ./tabfm
COPY survival_v2/requirements.txt ./survival_v2/requirements.txt
RUN python -m pip install --upgrade pip \
    && python -m pip install -r survival_v2/requirements.txt \
    && python -m pip install ./package './tabfm[pytorch]'
COPY survival_v2 ./survival_v2

ENTRYPOINT ["python", "survival_v2/run_pipeline.py"]
CMD ["--dry-run"]
