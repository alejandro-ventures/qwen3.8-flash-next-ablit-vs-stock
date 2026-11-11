"""Deterministic wrapper around analysis/score.py (DEVIATIONS D11).
The vendored IFEval checker calls langdetect without a seed, so instructions such as change_case:english_lowercase score
nondeterministically (found 2026-11-09: the same stored reply scored 0 or 1 across repeated calls). This wrapper fixes the
langdetect seed (DetectorFactory.seed = 0) and then runs the unchanged scorer, so every session is scored by the same
deterministic procedure. Usage: python analysis/score_det.py <label>."""
import sys
from pathlib import Path
from langdetect import DetectorFactory
DetectorFactory.seed = 0
sys.path.insert(0, str(Path(__file__).resolve().parent))
import score
score.main(sys.argv[1])
