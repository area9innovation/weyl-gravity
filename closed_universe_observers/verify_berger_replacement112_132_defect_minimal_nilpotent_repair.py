#!/usr/bin/env python3
"""Independent verifier for the complete replacement-112 repair no-go."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
C = P / "certificates/BERGER_REPLACEMENT112_132_DEFECT_MINIMAL_NILPOTENT_REPAIR_NO_GO.json"
X = P / "certificates/BERGER_REPLACEMENT112_132_DEFECT_MINIMAL_NILPOTENT_REPAIR_NO_GO_PAYLOAD.json"
SCHEMA = P / "schema/berger-replacement112-132-defect-minimal-nilpotent-repair-no-go-v1.schema.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rank_pair(payload: dict[str, Any]) -> tuple[int, int]:
    equation = payload["nilpotency_equation"]
    rows = (equation["correction_only_equation"], equation["target_only_equation"])
    coefficient = sp.Matrix([[sp.Rational(row["correction_coefficient"])] for row in rows])
    augmented = sp.Matrix(
        [[sp.Rational(row["correction_coefficient"]), sp.Rational(row["right_hand_side"])] for row in rows]
    )
    return int(coefficient.rank()), int(augmented.rank())


def independent_k_defect_count(interface: dict[str, Any]) -> int:
    sa, ca, su, cu = sp.symbols("sa ca su cu", nonzero=True, real=True)
    local = {"sa": sa, "ca": ca, "su": su, "cu": cu}
    action = sp.Matrix(
        [[sp.sympify(value, locals=local) for value in row] for row in interface["K_Berger_interface"]["field_generator_A_over_nu"]]
    )
    hessian = sp.Matrix(
        [[sp.sympify(value, locals=local) for value in row] for row in interface["action_crosswalk"]["kinetic_matrix_H"]]
    )
    ideal = sp.groebner([ca**2 + sa**2 - 1, cu**2 + su**2 - 1], ca, cu, sa, su, order="lex")
    defects = 0
    for value in action.T * hessian + hessian * action:
        numerator = sp.together(value).as_numer_denom()[0]
        defects += int(ideal.reduce(sp.expand(numerator))[1] != 0)
    return defects


def validate_payload(payload: dict[str, Any]) -> None:
    ansatz = payload["complete_local_action_hessian_ansatz"]
    constraints = sp.Matrix(ansatz["integrability_constraint_matrix"])
    assert constraints.shape == (3, 4)
    assert constraints.rank() == ansatz["integrability_constraint_rank"] == 3
    nullspace = constraints.nullspace()
    assert len(nullspace) == ansatz["action_orbit_dimension"] == 1
    assert list(nullspace[0]) == ansatz["action_orbit_vector"] == [1, 1, 1, 1]
    assert ansatz["real_structure_defect_count"] == 0
    assert ansatz["K_Berger_invariance_defect_count"] == 0

    background = payload["background_preservation_gate"]
    background_matrix = sp.Matrix([[sp.Rational(background["specialized_anchor_coefficient"])]] )
    assert background_matrix.rank() == background["constraint_rank"] == 1
    assert background["admissible_dimension"] == 0

    coefficient_rank, augmented_rank = rank_pair(payload)
    equation = payload["nilpotency_equation"]
    assert coefficient_rank == equation["coefficient_matrix_rank"] == 1
    assert augmented_rank == equation["augmented_matrix_rank"] == 2
    correction_only = equation["correction_only_equation"]
    target_only = equation["target_only_equation"]
    assert sp.Rational(correction_only["correction_coefficient"]) != 0
    assert sp.Rational(target_only["correction_coefficient"]) == 0
    assert sp.Rational(target_only["right_hand_side"]) != 0
    determinant = sp.Rational(correction_only["correction_coefficient"]) * sp.Rational(target_only["right_hand_side"])
    assert str(determinant) == equation["canonical_two_equation_augmented_determinant"]
    assert (target_only["output_row_id"], target_only["input_row_id"]) == ("h_hat_star_00", "sigma")
    assert target_only["input_pbw_word"] == [] and target_only["time_mode"] == -2
    assert target_only["basis_monomial"] == {"x0": 2, "x1": 0, "x2": 0, "x3": 0, "r10": 0, "r58": 0, "j": 1}


def main() -> int:
    certificate = json.loads(C.read_text())
    payload = json.loads(X.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(certificate)
    assert sha(X) == certificate["payload_ref"]["sha256"]
    for reference in certificate["dependency_refs"].values():
        assert sha(ROOT / reference["path"]) == reference["sha256"]
    validate_payload(payload)

    interface_path = ROOT / certificate["dependency_refs"]["mixed_hessian_payload"]["path"]
    interface = json.loads(interface_path.read_text())
    assert independent_k_defect_count(interface) == 0
    audit = interface["formal_adjoint_and_hessian_audit"]
    assert audit["gauge_formal_adjoint_defect_count"] == 0
    assert audit["mixed_formal_adjoint_defect_count"] == 0
    assert audit["metric_hessian_symmetry_defect_count"] == 0

    material_path = ROOT / certificate["dependency_refs"]["material_parent_payload"]["path"]
    material = json.loads(material_path.read_text())
    assert material["complete_internal_q1"]["q1_squared_defect_count"] == 0
    assert material["detector_chain_map"]["rank"] == 2
    assert material["external_mixed_readout_interface"]["typing_status"] == "CERTIFIED_RELATIVE_INTERFACE_NOT_AN_INTERNAL_56_BY_56_ENTRY"
    assert payload["control_and_consumer_disposition"]["apparatus_160_pushout"] == "NONDEFINED"
    print("BERGER_REPLACEMENT112_132_DEFECT_MINIMAL_NILPOTENT_REPAIR_NO_GO independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
