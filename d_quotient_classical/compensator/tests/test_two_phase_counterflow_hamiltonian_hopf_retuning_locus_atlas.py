from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ATLAS = ROOT / "residual_atlas/two-phase-counterflow-hamiltonian-hopf-retuning-locus-fragment-v1.json"


def test_retuning_atlas_row_is_fail_closed() -> None:
    entry = json.loads(ATLAS.read_text())["entries"][0]
    assert entry["descriptions"]["causal"] == "NO_CERTIFIED_MAP"
    assert entry["descriptions"]["symplectic"] == "CERTIFIED"
    assert entry["descriptions"]["quantum"] == "NO_CERTIFIED_MAP"
    assert entry["mode_data"]["dispersion"]["status"] == "OBSTRUCTED"
