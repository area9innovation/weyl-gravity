from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
GENERATOR = ROOT / "d_quotient_classical/atlas/generate_two_phase_counterflow_repaired_q70_low_j_stabilizer_health_atlas_fragment.py"
FRAGMENT = ROOT / "residual_atlas/two-phase-counterflow-repaired-q70-low-j-stabilizer-health-fragment-v1.json"


def test_low_j_atlas_is_current_complete_and_fail_closed() -> None:
    subprocess.run([sys.executable, str(GENERATOR), "--check"], cwd=ROOT, check=True)
    subprocess.run([sys.executable, "residual_atlas/validate_fragment.py", str(FRAGMENT.relative_to(ROOT))], cwd=ROOT, check=True)
    entries = json.loads(FRAGMENT.read_text())["entries"]
    assert len(entries) == 4
    assert sum(entry["mode_data"]["dispersion"]["status"] == "OBSTRUCTED" for entry in entries) == 2
    assert all(entry["descriptions"]["quantum"] == "NO_CERTIFIED_MAP" for entry in entries)
    assert all(entry["descriptions"]["observational"] == "NO_CERTIFIED_MAP" for entry in entries)
