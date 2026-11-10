"""Regenerate aggregate tables from published scores and analysis/inputs only.
Run from any directory: python analysis/run_all.py
No datasets, replies, endpoints or private files are needed. Runtime about 1-3 minutes on a typical CPU; actual time depends on hardware.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
AN = ROOT / 'analysis'
env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}
subprocess.run([sys.executable, '-B', str(AN / 'compare.py')], check=True, env=env)
# The frozen compare module remains untouched. Replace only its loader for sensitivity score sources.
code = '''import json, runpy, sys
from pathlib import Path
an = Path(sys.argv[1]); source = an / sys.argv[2]
sys.path.insert(0, str(an))
import compare
compare.load = lambda label: json.loads((source / (label + '.json')).read_text(encoding='utf-8'))
runpy.run_path(str(an / 'extra_analysis.py'), run_name='__main__')
'''
for source, suffix in [('scores_unseeded', '_unseeded'), ('scores_altenv', '_altenv'), ('scores', '')]:
    subprocess.run([sys.executable, '-B', '-c', code, str(AN), source], check=True, env=env)
    if suffix:
        for stem, ext in [('extra_results', '.json'), ('extra_tables', '.md')]:
            (AN / (stem + suffix + ext)).write_bytes((AN / (stem + ext)).read_bytes())
subprocess.run([sys.executable, '-B', str(AN / 'extra_refusal_classifiers.py')], check=True, env=env)
subprocess.run([sys.executable, '-B', str(AN / 'validation_summary.py')], check=True, env=env)
subprocess.run([sys.executable, '-B', str(AN / 'truncation_summary.py')], check=True, env=env)
files = ['refusal_truncation_sensitivity.md', 'results.json', 'extra_results.json', 'extra_tables.md', 'extra_results_altenv.json', 'extra_tables_altenv.md', 'extra_results_unseeded.json', 'extra_tables_unseeded.md', 'extra_refusal_classifiers.md', 'validation_summary.json']
hashes = {name: hashlib.sha256((AN / name).read_bytes()).hexdigest() for name in files}
(AN / 'OUTPUT_HASHES.json').write_text(json.dumps(hashes, indent=2) + '\n', encoding='utf-8')
print('Regenerated', len(files), 'outputs; SHA-256 recorded in analysis/OUTPUT_HASHES.json')
