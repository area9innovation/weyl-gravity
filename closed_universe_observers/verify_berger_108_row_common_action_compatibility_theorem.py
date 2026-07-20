#!/usr/bin/env python3
"""Independently verify the invariant common-action compatibility theorem."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from closed_universe_observers import berger_108_row_arity_replay as arity
from closed_universe_observers import berger_108_row_q1_pbw_replay as replay
from closed_universe_observers.berger_108_row_component_jet_contract import serialize
from closed_universe_observers.generate_berger_108_row_arity_two_obstruction import (
    _q1_source_parts,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = (
    PACKAGE
    / "certificates/BERGER_108_ROW_COMMON_ACTION_COMPATIBILITY_THEOREM.json"
)
SCHEMA = (
    PACKAGE
    / "schema/berger-108-row-common-action-compatibility-theorem-v1.schema.json"
)
PRIOR_WITNESS_KEY = (
    55,
    replay.word([1, 1, 0, 0]),
    84,
    replay.word([0, 0, 0, 0]),
)


def determinant3(matrix: list[list[int]]) -> int:
    return (
        matrix[0][0]
        * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1]
        * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2]
        * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )


def rank(matrix: list[list[int]]) -> int:
    work = [[Fraction(value) for value in row] for row in matrix]
    pivot_row = 0
    for column in range(len(work[0])):
        pivot = next(
            (row for row in range(pivot_row, len(work)) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        divisor = work[pivot_row][column]
        work[pivot_row] = [value / divisor for value in work[pivot_row]]
        for row in range(len(work)):
            if row == pivot_row or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [
                left - factor * right
                for left, right in zip(work[row], work[pivot_row], strict=True)
            ]
        pivot_row += 1
    return pivot_row


def evaluate(matrix: list[list[int]], vector: list[int]) -> list[int]:
    return [
        sum(coefficient * value for coefficient, value in zip(row, vector, strict=True))
        for row in matrix
    ]


def pairing_magnitude(document: dict, left: int, right: int) -> int:
    matches = [
        entry
        for entry in document["carrier_contract"]["pairing_entries"]
        if entry[0] == left and entry[1] == right
    ]
    assert len(matches) == 1
    assert matches[0][2][0][0] == [0, 0, 0, 0]
    return abs(int(matches[0][2][0][1]))


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)

    for reference in value["dependency_refs"].values():
        path = ROOT / reference["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == reference["sha256"]

    component = json.loads(
        (ROOT / value["dependency_refs"]["component_contract"]["path"]).read_text()
    )
    typed_pairing = json.loads(
        (ROOT / value["dependency_refs"]["typed_pairing"]["path"]).read_text()
    )
    typed_maxwell = json.loads(
        (ROOT / value["dependency_refs"]["typed_maxwell_q3"]["path"]).read_text()
    )
    physical = json.loads(
        (ROOT / value["dependency_refs"]["emitter_physical_q2"]["path"]).read_text()
    )
    diff = json.loads(
        (ROOT / value["dependency_refs"]["emitter_diff_q2"]["path"]).read_text()
    )
    assert physical["action_and_cyclicity_audit"]["q1_hessian_recovery"][
        "q1_hessian_recovery_defect_count"
    ] == 0
    assert "one component action" in physical["action_and_cyclicity_audit"][
        "cyclicity_generation"
    ]
    assert "three exact variational slots" in diff["action_and_cyclicity_audit"][
        "cyclicity_generation"
    ]
    assert typed_maxwell["typed_cyclic_presentation"]["lowered_tensor_identity"] == (
        "Omega_typed q2_typed=Omega_legacy q2_legacy"
    )

    ward = value["ward_derivation"]
    weights = ward["pairing_inputs"]
    tau_weight = pairing_magnitude(component, 3, 52)
    maxwell_weight = pairing_magnitude(component, 55, 59)
    emitter_weight = pairing_magnitude(component, 84, 96)
    typed_weight = typed_pairing["normalization"]["Maxwell_pairing_weight"]
    assert weights == {
        "canonical_tau_weight": tau_weight,
        "canonical_Maxwell_weight": maxwell_weight,
        "canonical_emitter_weight": emitter_weight,
        "typed_Maxwell_weight": typed_weight,
    }
    a = typed_weight * tau_weight // maxwell_weight
    b = maxwell_weight // emitter_weight
    c = emitter_weight // tau_weight
    matrix = [[1, 0, -a], [1, -b, 0], [0, 1, -c]]
    assert matrix == ward["matrix"]
    assert determinant3(matrix) == b * c - a == -1
    assert rank(matrix) == 3

    # Independent symbolic rescaling control, deliberately different from the
    # frozen factors. The transformed holonomy and rank must be unchanged.
    r_m, r_e, r_t = Fraction(3), Fraction(5), Fraction(7)
    a_prime = r_m * a / r_t
    b_prime = r_m * b / r_e
    c_prime = r_e * c / r_t
    assert a_prime / (b_prime * c_prime) == Fraction(a, b * c)
    scaled_matrix = [
        [Fraction(1), Fraction(0), -a_prime],
        [Fraction(1), -b_prime, Fraction(0)],
        [Fraction(0), Fraction(1), -c_prime],
    ]
    assert rank(scaled_matrix) == 3

    repairs = value["bounded_minimal_extension_ansatz"][
        "one_edge_action_normalizations"
    ]
    assert len(repairs) == 3
    for repair in repairs:
        assert determinant3(repair["matrix"]) == 0
        assert rank(repair["matrix"]) == 2
        assert evaluate(repair["matrix"], repair["null_vector"]) == [0, 0, 0]
        assert repair["original_q1_q2_substitution"].startswith("NOT_")

    for control in value["counterexample_strategy"]["dropped_orbit_controls"]:
        assert rank(control["matrix"]) == 2
        assert evaluate(control["matrix"], control["null_vector"]) == [0, 0]

    # Independent source-pair substitution into the original arity-two rail.
    q1 = _q1_source_parts()["emitter"]
    q2 = arity.load_q2(sources={"emitter_Diff_BV"})
    row = arity.arity_two_row(52, (0, 0), q1, q2, arity.parities())
    specialized = arity.specialize_bilinear_rows({52: row})[52]
    coefficient = specialized[PRIOR_WITNESS_KEY]
    expected = value["counterexample_strategy"]["persistent_original_q1_q2_witness"][
        "coefficient"
    ]
    assert serialize(coefficient) == expected

    extension = value["bounded_minimal_extension_ansatz"]
    assert extension["one_row_carrier_enlargement"]["target_dimension"] % 2 == 1
    assert extension["one_row_carrier_enlargement"]["status"] == "OBSTRUCTED"
    assert extension["surviving_physics_candidates"] == []
    assert not value["activation_disposition"]["conflux_preflight_authorized"]
    print("BERGER_108_ROW_COMMON_ACTION_COMPATIBILITY_THEOREM independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
