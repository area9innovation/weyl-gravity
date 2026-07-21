#!/usr/bin/env python3
"""Independent implication and provenance audit for the Phase-1 decision."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_PHASE1_VIABILITY_CLASSIFICATION_V1.json"


def main() -> int:
    c = json.loads(CERT.read_text())
    assert c["result_state"] == "OBSTRUCTED_NO_ROBUST_STATIONARY_SAME_FIELD_CLOCK"
    for item in c["imports"].values():
        p = ROOT / item["path"]
        assert hashlib.sha256(p.read_bytes()).hexdigest() == item["sha256"]
        assert json.loads(p.read_text())["result_id"] == item["result_id"]
    r = json.loads((ROOT / c["imports"]["retuning_locus"]["path"]).read_text())
    assert r["physical_quotient_summary"]["unstable_factor"] == "F2"
    assert r["physical_quotient_summary"]["unstable_factor_discriminant"] == "256*q^5*(9*q-8)"
    assert r["terminal_verdict"]["entire_component_Hamiltonian_Hopf"] is True
    assert c["decision"]["robust_stationary_retuning_exists"] is False
    assert c["downstream_activation"] == {
        "candidate_specific_nonlinear": False,
        "candidate_specific_observer": False,
        "candidate_specific_quantum": False,
        "phase1_classification_ending": True,
    }
    assert all(v.startswith("REJECTED_") for v in c["adversarial_mutations"].values())
    assert c["adversarial_mutations"]["unstable_sector_deleted_as_gauge"].endswith("INERTIA_4_4_0")
    print("PASS: independent Phase-1 provenance and branch-implication audit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
