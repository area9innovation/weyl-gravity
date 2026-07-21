#!/usr/bin/env python3
"""Independent verifier for repaired112 physical-reduction nonactivation."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
C = P / "certificates/BERGER_REPAIRED112_PHYSICAL_REDUCTION_AND_DETECTOR_RANK_NOT_ACTIVATED.json"
X = P / "certificates/BERGER_REPAIRED112_PHYSICAL_REDUCTION_AND_DETECTOR_RANK_NOT_ACTIVATED_PAYLOAD.json"
SCHEMA = P / "schema/berger-repaired112-physical-reduction-and-detector-rank-not-activated-v1.schema.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    certificate = json.loads(C.read_text())
    payload = json.loads(X.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(certificate)
    assert sha(X) == certificate["payload_ref"]["sha256"]
    for ref in certificate["dependency_refs"].values():
        assert sha(ROOT / ref["path"]) == ref["sha256"]
    pushout = json.loads((ROOT / certificate["dependency_refs"]["pushout_payload"]["path"]).read_text())
    repair = json.loads((ROOT / certificate["dependency_refs"]["repair_no_go_payload"]["path"]).read_text())
    assert pushout["category_of_complexes_gate"]["apparatus_pushout"] == "NONDEFINED"
    assert pushout["category_of_complexes_gate"]["derived_combined_row_count"] == "NO_CERTIFIED_MAP"
    equation = repair["nilpotency_equation"]
    a = sp.Rational(equation["correction_only_equation"]["correction_coefficient"])
    b = sp.Rational(equation["target_only_equation"]["right_hand_side"])
    minor = sp.Matrix([[a, 0], [0, b]])
    assert minor.rank() == 2
    assert str(minor.det()) == payload["method_distinct_obstruction_replay"]["canonical_augmented_determinant"]
    assert payload["activation_gate"]["verdict"] == "NOT_ACTIVATED"
    for sector in payload["sector_disposition"].values():
        assert set(sector.values()) == {"NO_CERTIFIED_MAP"}
    assert set(payload["contraction_and_pairing_disposition"].values()) == {"NO_CERTIFIED_MAP"}
    assert set(payload["observer_class_disposition"].values()) == {"NO_CERTIFIED_MAP"}
    assert payload["separate_material_fact"]["not_a_physical_combined_rank"] is True
    print("BERGER_REPAIRED112_PHYSICAL_REDUCTION_AND_DETECTOR_RANK_NOT_ACTIVATED independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
