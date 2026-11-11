# Scoring image: runs model-written code (HumanEval+/MBPP+ tests) and the IFEval checker without network access.
# Build:  docker build -t ablit-ab-scoring scoring/
# Run:    docker run --rm --network none --cpus 2 --memory 4g -v "$PWD":/study ablit-ab-scoring python analysis/score_det.py <session>
# The code tests use a 30 s time limit per item (harness/tasks.py). The result of a CPU-heavy item depends on CPU speed:
# see DEVIATIONS D11 (item mbpp-239, which ran about 26 s of a 30 s limit on one machine and timed out on a slower one).
# score_det.py needs the raw per-session replies, which are not part of this repository (only the resulting scores are).
FROM python:3.12-slim
RUN pip install --no-cache-dir httpx==0.28.1 numpy scipy langdetect immutabledict nltk packaging \
 && python -c "import nltk; [nltk.download(p, download_dir='/usr/local/share/nltk_data', quiet=True) for p in ('punkt','punkt_tab')]"
ENV NLTK_DATA=/usr/local/share/nltk_data PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUTF8=1
WORKDIR /study
