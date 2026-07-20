#!/usr/bin/env python3
"""Independent replay of the two-rod construction and chain-map obstruction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator

from closed_universe_observers import generate_berger_global_detector_rods as rods
from closed_universe_observers import generate_berger_global_rod_q1_solvability as solve


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
C = P / "certificates/BERGER_GLOBAL_ROD_TWO_DIRECTION_EXTENSION_OBSTRUCTION.json"
X = P / "certificates/BERGER_GLOBAL_ROD_TWO_DIRECTION_EXTENSION_PAYLOAD.json"
SCHEMA = (
    P
    / "schema/"
    "berger-global-rod-two-direction-extension-obstruction-v1.schema.json"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def eight_rod_source_at_phase(phase: sp.Expr, harmonic: str) -> sp.Matrix:
    """Independently assemble the six old plus two sine-partner stresses."""

    signature = (-1, 1, 1, 1)
    stress = [[sp.S.Zero for _ in range(4)] for _ in range(4)]
    for profile_index, profile in enumerate(rods._profiles(phase)):
        derivatives = [profile] + [
            rods._frame_derivative(profile, axis) for axis in range(3)
        ]
        # A cosine/sine pair doubles its zero-frequency stress and cancels its
        # twice-frequency stress.  Only profile zero acquires that partner.
        multiplicity = (
            2
            if harmonic == "zero" and profile_index == 0
            else 0
            if harmonic == "positive" and profile_index == 0
            else 1
        )
        norm = sum(
            signature[axis]
            * multiplicity
            * solve._derivative_product(derivatives, axis, axis, harmonic)
            for axis in range(4)
        )
        for left in range(4):
            for right in range(4):
                stress[left][right] += (
                    multiplicity
                    * solve._derivative_product(
                        derivatives, left, right, harmonic
                    )
                )
                if left == right:
                    stress[left][right] -= signature[left] * norm / 2
    return sp.Matrix.vstack(
        *[
            (2 if left != right else 1)
            * signature[left]
            * signature[right]
            * solve._reduce_quadratic(stress[left][right])
            / 2
            for left, right in solve.PAIRS
        ]
    ).applyfunc(sp.simplify)


def eight_rod_source_basis(harmonic: str) -> sp.Matrix:
    cosine = eight_rod_source_at_phase(sp.S.Zero, harmonic)
    sine = eight_rod_source_at_phase(sp.pi / 2, harmonic)
    mixed = 2 * (
        eight_rod_source_at_phase(sp.pi / 4, harmonic)
        - (cosine + sine) / 2
    )
    return sp.Matrix.hstack(cosine, sine, mixed).applyfunc(sp.simplify)


def main() -> int:
    cert, payload = json.loads(C.read_text()), json.loads(X.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(cert)
    assert sha(X) == cert["payload_ref"]["sha256"]
    for ref in cert["dependency_refs"].values():
        assert sha(ROOT / ref["path"]) == ref["sha256"]

    global_rods = json.loads(
        (P / "certificates/BERGER_GLOBAL_DETECTOR_INDEXED_RODS.json").read_text()
    )
    for detector, row in zip(global_rods["global_rods"], payload[
        "background_completion"
    ]["new_rows"]):
        profile = sp.sympify(
            detector["spatial_profiles"][0],
            locals={str(x): x for x in rods.X},
        )
        center = sp.Rational(detector["physical_event_time"])
        field = sp.sin(rods.OMEGA * (rods.T - center)) * profile
        wave = -sp.diff(field, rods.T, 2) + sum(
            rods._frame_derivative(
                rods._frame_derivative(field, axis), axis
            )
            for axis in range(3)
        )
        assert sp.trigsimp(sp.expand_trig(wave)) == 0
        assert sp.sstr(field) == row["field"]

    completion = payload["background_completion"]
    assert completion["current_rank"] == 6
    assert completion["completed_rank"] == 8
    assert completion["K_closure_defect_count"] == 0
    assert len(completion["centered_background_K_matrix_over_nu"]) == 8

    retained = json.loads(
        (
            ROOT
            / "d_quotient_classical/certificates/"
            "BERGER_RETAINED_MINIMAL_OPERATOR.json"
        ).read_text()
    )["q1_blocks"]
    for harmonic, frequency in (
        ("zero", sp.S.Zero),
        ("positive", 2 * solve.OMEGA),
    ):
        block = payload["background_equation"]["exact_blocks"][harmonic]
        operator = solve._operator_matrix(retained["H_retained"], frequency)
        primitives = sp.zeros(100, 3)
        for column, sparse in enumerate(block["canonical_primitives_sparse"]):
            for row, value in sparse:
                primitives[row, column] = sp.sympify(value)
        source = eight_rod_source_basis(harmonic)
        assert (operator * primitives + source).applyfunc(
            sp.simplify
        ) == sp.zeros(100, 3)
        noether = solve._operator_matrix(
            retained["minus_K_spatial_sharp"], frequency
        )
        assert (noether * source).applyfunc(sp.simplify) == sp.zeros(30, 3)
        assert block["primitive_residual_nonzero_count"] == 0
        assert any(
            count > 0
            for count in block["old_to_new_primitive_delta_nonzero_counts"]
        )

    s, c = sp.symbols("s c", nonzero=True)
    # A polynomial P with -s^2 P=c s would require division by s.
    assert sp.cancel(-c * s / s**2) == -c / s
    assert sp.Poly(c * s, s).degree() < sp.Poly(s**2, s).degree()
    witnesses = payload["first_later_incompatibility"][
        "mixed_metric_to_new_rod_cotangent_witnesses"
    ]
    assert len(witnesses) == 2 and all(row["nonzero"] for row in witnesses)
    for detector, witness in zip(global_rods["global_rods"], witnesses):
        center = sp.Rational(detector["physical_event_time"])
        phase = sp.sympify(detector["hopf_phase"])
        profile = rods._profiles(phase)[0]
        field = sp.sin(rods.OMEGA * (rods.T - center)) * profile
        gradient = sp.simplify(
            sp.diff(field, rods.T).subs(
                {
                    rods.T: center,
                    rods.X[0]: 1,
                    rods.X[1]: 0,
                    rods.X[2]: 0,
                    rods.X[3]: 0,
                }
            )
        )
        assert gradient == sp.sympify(witness["background_time_gradient"])
        assert -gradient / 2 == sp.sympify(
            witness["K_Rh_temporal_principal_coefficient"]
        )
    assert payload["first_later_incompatibility"][
        "canonical_inclusion_chain_defect_count"
    ] == 2
    assert cert["downstream_disposition"]["complete_112_row_q1"] == (
        "NO_CERTIFIED_MAP"
    )
    print(
        "BERGER_GLOBAL_ROD_TWO_DIRECTION_EXTENSION_OBSTRUCTION "
        "independent verification: PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
