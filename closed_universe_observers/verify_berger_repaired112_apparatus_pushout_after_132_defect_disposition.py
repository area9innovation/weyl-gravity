#!/usr/bin/env python3
"""Independent verifier for the fresh post-repair apparatus nonactivation."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
C = P / "certificates/BERGER_REPAIRED112_APPARATUS_PUSHOUT_AFTER_132_DEFECT_DISPOSITION.json"
X = P / "certificates/BERGER_REPAIRED112_APPARATUS_PUSHOUT_AFTER_132_DEFECT_DISPOSITION_PAYLOAD.json"
SCHEMA = P / "schema/berger-repaired112-apparatus-pushout-after-132-defect-disposition-v1.schema.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    certificate = json.loads(C.read_text())
    payload = json.loads(X.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(certificate)
    assert sha(X) == certificate["payload_ref"]["sha256"]
    for ref in certificate["dependency_refs"].values():
        assert sha(ROOT / ref["path"]) == ref["sha256"]

    repair = json.loads((ROOT / certificate["dependency_refs"]["repair_no_go"]["path"]).read_text())
    repair_payload = json.loads((ROOT / certificate["dependency_refs"]["repair_no_go_payload"]["path"]).read_text())
    material = json.loads((ROOT / certificate["dependency_refs"]["material_parent"]["path"]).read_text())
    material_payload = json.loads((ROOT / certificate["dependency_refs"]["material_parent_payload"]["path"]).read_text())
    assert repair["atlas_status"] == "OBSTRUCTED"
    assert repair["gate_results"]["complete_repaired_replacement112_q1"] == "NO_CERTIFIED_MAP"
    assert material["gate_results"]["complete_executable_material_parent56_internal_q1"] == "CERTIFIED"
    assert material_payload["carrier"]["row_count"] == 56

    equation = repair_payload["nilpotency_equation"]
    a = sp.Rational(equation["correction_only_equation"]["correction_coefficient"])
    b = sp.Rational(equation["target_only_equation"]["right_hand_side"])
    augmented_minor = sp.Matrix([[a, 0], [0, b]])
    assert augmented_minor.rank() == 2
    assert str(augmented_minor.det()) == equation["canonical_two_equation_augmented_determinant"]
    assert equation["coefficient_matrix_rank"] == 1
    assert equation["augmented_matrix_rank"] == 2
    assert repair_payload["background_preservation_gate"]["admissible_dimension"] == 0

    gate = payload["category_of_complexes_gate"]
    assert gate["replacement_source_object"] == "NONEXISTENT_IN_DECLARED_REPLACEMENT_FAMILY"
    assert gate["apparatus_pushout"] == "NONDEFINED"
    assert gate["derived_combined_row_count"] == "NO_CERTIFIED_MAP"
    survivor = payload["material_parent_survivor"]
    assert survivor["row_count"] == 56 and survivor["detector_coordinate_rank"] == 2
    escape = payload["minimal_escape_signature"]
    assert escape["minimum_new_coefficient_image_dimension"] == 1
    assert escape["one_pair_route"]["minimum_new_rows"] == 2
    assert payload["nonactivation_disposition"]["physical_reduction"] == "NO_CERTIFIED_MAP"
    print("BERGER_REPAIRED112_APPARATUS_PUSHOUT_AFTER_132_DEFECT_DISPOSITION independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
