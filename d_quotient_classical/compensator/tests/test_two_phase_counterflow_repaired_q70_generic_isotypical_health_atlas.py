from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
GENERATOR = ROOT / "d_quotient_classical/atlas/generate_two_phase_counterflow_repaired_q70_generic_isotypical_health_atlas_fragment.py"
FRAGMENT = ROOT / "residual_atlas/two-phase-counterflow-repaired-q70-first-generic-isotypical-health-obstruction-fragment-v1.json"


def test_generic_q70_health_atlas_is_current_and_fail_closed() -> None:
    subprocess.run([sys.executable, str(GENERATOR), "--check"], cwd=ROOT, check=True)
    subprocess.run([sys.executable, "residual_atlas/validate_fragment.py", str(FRAGMENT.relative_to(ROOT))], cwd=ROOT, check=True)
    entry = json.loads(FRAGMENT.read_text())["entries"][0]
    assert entry["mode_data"]["dispersion"]["status"] == "OBSTRUCTED"
    assert entry["descriptions"]["causal"] == "CERTIFIED"
    assert entry["descriptions"]["quantum"] == "NO_CERTIFIED_MAP"
