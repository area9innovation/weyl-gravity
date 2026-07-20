#!/usr/bin/env python3
"""Independent exact replay for the dressed evanescent module preflight."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CERT = (
    ROOT
    / "quantum-weyl/anomalies/certificates/"
    "DRESSED_EVANESCENT_GEOMETRIC_BV_MODULE_PREFLIGHT.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def _matrix(values: list[list[dict[str, int]]]) -> list[list[Fraction]]:
    return [[_fraction(entry) for entry in row] for row in values]


def _mul(
    left: list[list[Fraction]], right: list[list[Fraction]]
) -> list[list[Fraction]]:
    return [
        [
            sum(
                (left[i][k] * right[k][j] for k in range(len(right))),
                Fraction(0),
            )
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def main() -> None:
    value = json.loads(CERT.read_text())
    assert value["dependency_tags"] == [
        "LOCAL-ALGEBRAIC",
        "EUCLIDEAN-SPECTRAL",
    ]
    for reference in value["input_pins"].values():
        path = ROOT / reference["path"]
        assert path.is_file()
        assert _sha256(path) == reference["sha256"]
        assert json.loads(path.read_text())["result_id"] == reference["result_id"]

    projection = value["four_dimensional_projection"]
    physical_from_raw = _matrix(
        projection["physical_definitions_from_raw_matrix"]
    )
    raw_from_physical = _matrix(projection["raw_from_physical_matrix"])
    identity = [
        [Fraction(int(i == j)) for j in range(4)] for i in range(4)
    ]
    assert _mul(physical_from_raw, raw_from_physical) == identity
    assert _mul(raw_from_physical, physical_from_raw) == identity
    assert _matrix(projection["left_composition"]) == identity
    assert _matrix(projection["right_composition"]) == identity

    # Differentiate the exact rational coefficients at d=4-epsilon.
    # -4/(2-epsilon) has derivative -1; and
    # 2/((3-epsilon)(2-epsilon)) has derivative
    # (1/3)(1/3+1/2)=5/18.
    raw_derivative = [
        Fraction(0),
        Fraction(-1),
        Fraction(1, 3) * (Fraction(1, 3) + Fraction(1, 2)),
        Fraction(0),
    ]
    stored_raw = [
        _fraction(entry)
        for entry in value["evanescent_continuations"][
            "C_d_squared_first_epsilon_raw_coordinates"
        ]
    ]
    assert raw_derivative == stored_raw == [
        Fraction(0),
        Fraction(-1),
        Fraction(5, 18),
        Fraction(0),
    ]
    projected = [
        sum(
            (
                raw_from_physical[row][column] * raw_derivative[row]
                for row in range(4)
            ),
            Fraction(0),
        )
        for column in range(4)
    ]
    stored_projected = [
        _fraction(entry)
        for entry in value["evanescent_continuations"][
            "C_d_squared_first_epsilon_physical_coordinates"
        ]
    ]
    assert projected == stored_projected == [
        Fraction(-1, 2),
        Fraction(1, 2),
        Fraction(-1, 18),
        Fraction(0),
    ]

    residue = _fraction(value["evanescent_continuations"]["Euler_residue"])
    witness = value["evanescent_continuations"][
        "minimal_subtraction_projection_commutator_witness"
    ]
    assert residue == Fraction(-87, 20)
    assert _fraction(witness["baseline_finite_C2"]) == 0
    assert _fraction(witness["shifted_finite_C2"]) == residue
    assert witness["difference_nonzero"] is True

    extended = json.loads(
        (
            ROOT / value["input_pins"]["extended_H04_H14"]["path"]
        ).read_text()
    )
    assert extended["H04"]["even_classes"] == [
        "C(g_hat)^2",
        "E4(g_hat)",
        "R(g_hat)^2",
    ]
    assert extended["H14"]["Weyl_and_mixed_quotient_dimension"] == 0

    quartet = json.loads(
        (
            ROOT / value["input_pins"]["quartet_cotangent_lift"]["path"]
        ).read_text()
    )["contractible_quartet"]
    assert quartet["QW_squared"] == [[0] * 4 for _ in range(4)]
    assert quartet["anticommutator"] == [
        [1 if i == j else 0 for j in range(4)] for i in range(4)
    ]

    obstruction = value["full_bv_obstruction"]
    assert obstruction["first_missing_object"] == (
        "ACTION_SELECTED_D_DIMENSIONAL_KOSZUL_TATE_DIFFERENTIAL"
    )
    assert obstruction["one_loop_mixing_map"] == "UNDEFINED_ACTION_INDEPENDENTLY"
    assert "epsilon/gamma5" in obstruction["parity_odd_independent_obstruction"]
    slots = value["selected_action_extension_receiver"]
    assert {
        slots["candidate_A_scalar"]["status"],
        slots["candidate_B_reducible_three_form"]["status"],
    } == {"UNFILLED_UNTIL_ACTION_SELECTION"}
    assert not any(value["claim_flags"].values())
    assert all(value["exact_checks"].values())
    expected = _canonical_hash(
        {key: entry for key, entry in value.items() if key != "proof_sha256"}
    )
    assert value["proof_sha256"] == expected
    print("Dressed evanescent geometric BV module preflight: PASS")


if __name__ == "__main__":
    main()
