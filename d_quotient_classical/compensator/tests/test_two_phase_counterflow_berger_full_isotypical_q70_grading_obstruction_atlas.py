from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
GENERATOR = ROOT / "d_quotient_classical/atlas/generate_two_phase_counterflow_berger_full_isotypical_q70_grading_obstruction_atlas_fragment.py"
FRAGMENT = ROOT / "residual_atlas/two-phase-counterflow-berger-full-isotypical-q70-grading-obstruction-fragment-v1.json"


def test_atlas_fragment_is_current_and_fail_closed() -> None:
    subprocess.run([sys.executable, str(GENERATOR), "--check"], cwd=ROOT, check=True)
    subprocess.run([sys.executable, "residual_atlas/validate_fragment.py", str(FRAGMENT.relative_to(ROOT))], cwd=ROOT, check=True)
    entry = json.loads(FRAGMENT.read_text())["entries"][0]
    assert entry["descriptions"]["causal"] == "OBSTRUCTED"
    assert entry["descriptions"]["symplectic"] == "OBSTRUCTED"
    assert entry["descriptions"]["quantum"] == "NO_CERTIFIED_MAP"
