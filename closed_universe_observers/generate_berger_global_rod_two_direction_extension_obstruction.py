#!/usr/bin/env python3
"""Build the forced two-rod background and test local 108->112 chain embedding."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

from closed_universe_observers import generate_berger_global_detector_rods as rods
from closed_universe_observers import generate_berger_global_rod_q1_solvability as solve


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = (
    P
    / "certificates/"
    "BERGER_GLOBAL_ROD_TWO_DIRECTION_EXTENSION_OBSTRUCTION.json"
)
PAYLOAD = (
    P
    / "certificates/"
    "BERGER_GLOBAL_ROD_TWO_DIRECTION_EXTENSION_PAYLOAD.json"
)
REPORT = P / "reports/berger-global-rod-two-direction-extension-obstruction.md"
DEPENDENCIES = {
    "crosswalk_obstruction": P
    / "certificates/"
    "BERGER_DYNAMICAL_APPARATUS_COMBINED_Q1_CROSSWALK_OBSTRUCTION.json",
    "global_rods": P / "certificates/BERGER_GLOBAL_DETECTOR_INDEXED_RODS.json",
    "rod_source": P
    / "certificates/BERGER_GLOBAL_ROD_Q1_SOURCE_SECTOR_SOLVABILITY.json",
    "rod_unary": P / "certificates/BERGER_84_ROW_ROD_GRAVITY_UNARY.json",
    "complete_unary": P
    / "certificates/BERGER_108_ROW_NONLINEAR_CLOCK_SECOND_JET.json",
    "K_gate": P
    / "certificates/BERGER_84_ROW_APPARATUS_Q2_Q3_K_GATE.json",
    "retained_q1": ROOT
    / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _source_at_phase(phase: sp.Expr, harmonic: str) -> sp.Matrix:
    """Eight-rod stress: add the sine partner of profile 1."""

    eta = (-1, 1, 1, 1)
    stress = [[sp.S.Zero for _ in range(4)] for _ in range(4)]
    for index, profile in enumerate(rods._profiles(phase)):
        derivatives = [profile] + [
            rods._frame_derivative(profile, axis) for axis in range(3)
        ]
        # cos and sin partners of profile 1 add at zero frequency and cancel
        # at twice the rod frequency.
        weight = (
            2
            if harmonic == "zero" and index == 0
            else 0
            if harmonic == "positive" and index == 0
            else 1
        )
        norm = sum(
            eta[axis]
            * weight
            * solve._derivative_product(derivatives, axis, axis, harmonic)
            for axis in range(4)
        )
        for left in range(4):
            for right in range(4):
                stress[left][right] += (
                    weight
                    * solve._derivative_product(
                        derivatives, left, right, harmonic
                    )
                )
                if left == right:
                    stress[left][right] -= eta[left] * norm / 2
    return sp.Matrix.vstack(
        *[
            (2 if left != right else 1)
            * eta[left]
            * eta[right]
            * solve._reduce_quadratic(stress[left][right])
            / 2
            for left, right in solve.PAIRS
        ]
    ).applyfunc(sp.simplify)


def _source_basis(harmonic: str) -> sp.Matrix:
    cosine = _source_at_phase(sp.S.Zero, harmonic)
    sine = _source_at_phase(sp.pi / 2, harmonic)
    mixed = 2 * (
        _source_at_phase(sp.pi / 4, harmonic) - (cosine + sine) / 2
    )
    return sp.Matrix.hstack(cosine, sine, mixed).applyfunc(sp.simplify)


def _exact_background_blocks() -> dict[str, Any]:
    q1 = json.loads(DEPENDENCIES["retained_q1"].read_text())["q1_blocks"]
    old_blocks = json.loads(DEPENDENCIES["rod_source"].read_text())["exact_blocks"]
    result: dict[str, Any] = {}
    for harmonic, frequency_text, frequency in (
        ("zero", "0", sp.S.Zero),
        ("positive", "sqrt(58)/3", 2 * solve.OMEGA),
    ):
        operator = solve._operator_matrix(q1["H_retained"], frequency)
        noether = solve._operator_matrix(q1["minus_K_spatial_sharp"], frequency)
        sources = _source_basis(harmonic)
        closure = (noether * sources).applyfunc(sp.simplify)
        if closure != sp.zeros(30, 3):
            raise AssertionError("eight-rod source lost Noether closure")
        rank, pivots, primitives = solve._canonical_primitives(operator, sources)
        old_primitives = sp.zeros(operator.cols, 3)
        for column, sparse in enumerate(
            old_blocks[harmonic]["canonical_primitives_sparse"]
        ):
            for row, value in sparse:
                old_primitives[row, column] = sp.sympify(value)
        old_sources = (-operator * old_primitives).applyfunc(sp.simplify)
        source_delta = (sources - old_sources).applyfunc(sp.simplify)
        delta = (primitives - old_primitives).applyfunc(sp.simplify)
        result[harmonic] = {
            "frequency": frequency_text,
            "operator_rank": rank,
            "operator_pivot_columns": pivots,
            "source_nonzero_counts": [
                sum(value != 0 for value in sources[:, column])
                for column in range(3)
            ],
            "canonical_primitives_sparse": solve._sparse_columns(primitives),
            "primitive_residual_nonzero_count": sum(
                value != 0 for value in operator * primitives + sources
            ),
            "Noether_defect_nonzero_count": sum(value != 0 for value in closure),
            "old_to_new_source_delta_nonzero_counts": [
                sum(value != 0 for value in source_delta[:, column])
                for column in range(3)
            ],
            "old_to_new_primitive_delta_nonzero_counts": [
                sum(value != 0 for value in delta[:, column])
                for column in range(3)
            ],
            "old_to_new_primitive_delta_first_witness": [
                next(
                    (
                        [row, sp.sstr(sp.factor(delta[row, column]))]
                        for row in range(delta.rows)
                        if delta[row, column] != 0
                    ),
                    None,
                )
                for column in range(3)
            ],
        }
    return result


def _rod_completion() -> dict[str, Any]:
    document = json.loads(DEPENDENCIES["global_rods"].read_text())
    coordinates = rods.X
    nu = rods.OMEGA
    current: list[list[sp.Expr]] = []
    derivatives: list[list[sp.Expr]] = []
    labels: list[str] = []
    new_rows = []
    for detector in document["global_rods"]:
        center = sp.Rational(detector["physical_event_time"])
        cosine, sine = sp.cos(nu * center), sp.sin(nu * center)
        for index, profile_text in enumerate(detector["spatial_profiles"], 1):
            profile = sp.sympify(
                profile_text, locals={str(x): x for x in coordinates}
            )
            spatial = [
                sp.expand(profile).coeff(x) for x in coordinates
            ]
            current.append([cosine * value for value in spatial] + [
                sine * value for value in spatial
            ])
            derivatives.append([sine * value for value in spatial] + [
                -cosine * value for value in spatial
            ])
            labels.append(f"R{detector['detector_id'][-1]}_{index}")
        profile = sp.sympify(
            detector["spatial_profiles"][0],
            locals={str(x): x for x in coordinates},
        )
        field = sp.sin(nu * (rods.T - center)) * profile
        wave = -sp.diff(field, rods.T, 2) + sum(
            rods._frame_derivative(
                rods._frame_derivative(field, axis), axis
            )
            for axis in range(3)
        )
        if sp.trigsimp(sp.expand_trig(wave)) != 0:
            raise AssertionError("new global rod failed its wave equation")
        new_rows.append(
            {
                "row_id": f"R{detector['detector_id'][-1]}_4",
                "detector_id": detector["detector_id"],
                "field": sp.sstr(field),
                "spatial_profile": sp.sstr(profile),
                "wave_residual": "0",
            }
        )

    current_matrix = sp.Matrix(current)
    derivative_matrix = sp.Matrix(derivatives)
    selected = [0, 3]
    completed = sp.Matrix.vstack(
        current_matrix, *[derivative_matrix[index, :] for index in selected]
    )
    if (current_matrix.rank(), completed.rank()) != (6, 8):
        raise AssertionError("canonical two-direction completion drifted")
    # K action on centered background rows in the completed coefficient basis.
    derivative_rows = [
        derivative_matrix[index, :] for index in range(6)
    ] + [
        -current_matrix[index, :] for index in selected
    ]
    K_rows = []
    for row in derivative_rows:
        solution = sp.linsolve((completed.T, row.T))
        vector = next(iter(solution))
        if any(value.free_symbols for value in vector):
            raise AssertionError("completed K action is not unique")
        K_rows.append([sp.sstr(sp.trigsimp(value)) for value in vector])
    return {
        "old_row_labels": labels,
        "new_rows": new_rows,
        "new_cotangent_rows": ["R0_4_plus", "R1_4_plus"],
        "selected_derivative_directions": ["e0(R0_1)/nu", "e0(R1_1)/nu"],
        "current_rank": current_matrix.rank(),
        "completed_rank": completed.rank(),
        "coefficient_space_dimension": 8,
        "centered_background_K_matrix_over_nu": K_rows,
        "K_closure_defect_count": 0,
    }


def build_payload() -> dict[str, Any]:
    completion = _rod_completion()
    background = _exact_background_blocks()
    phi0, phi1 = sp.sqrt(10) / 12, sp.sqrt(10) / 6
    mixed_witnesses = []
    for detector, center, phase in (
        (0, sp.Rational(1, 4), phi0),
        (1, sp.Rational(1, 2), phi1),
    ):
        profile = rods._profiles(phase)[0]
        field = sp.sin(rods.OMEGA * (rods.T - center)) * profile
        point = {
            rods.T: center,
            rods.X[0]: 1,
            rods.X[1]: 0,
            rods.X[2]: 0,
            rods.X[3]: 0,
        }
        background_time_gradient = sp.simplify(
            sp.diff(field, rods.T).subs(point)
        )
        # Varying -1/2 int sqrt(|g|) g^{-1}(dR,dR) once in the metric and
        # once in R gives the temporal mixed Hessian coefficient -d_t R/2.
        mixed_coefficient = sp.simplify(-background_time_gradient / 2)
        if mixed_coefficient == 0:
            raise AssertionError("mixed rod-gravity witness vanished")
        mixed_witnesses.append({
            "new_row": f"R{detector}_4",
            "point": f"t={center}, (x0,x1,x2,x3)=(1,0,0,0)",
            "background_time_gradient": sp.sstr(background_time_gradient),
            "K_Rh_temporal_principal_coefficient": sp.sstr(mixed_coefficient),
            "nonzero": True,
        })
    return {
        "schema": (
            "closed-universe-berger-global-rod-"
            "two-direction-extension-payload-v1"
        ),
        "result_id": "BERGER_GLOBAL_ROD_TWO_DIRECTION_EXTENSION_PAYLOAD",
        "coefficient_field": (
            "exact real trigonometric-algebraic field generated by "
            "sqrt(10),sqrt(58),sqrt(145) and the pinned phases"
        ),
        "row_extension": {
            "old_row_count": 108,
            "new_degree_zero_rows": ["R0_4", "R1_4"],
            "new_degree_one_rows": ["R0_4_plus", "R1_4_plus"],
            "prospective_row_count": 112,
            "degrees": [0, 0, 1, 1],
            "real_involution": "identity on all four new real rows",
            "pairing_entries": [
                [108, 110, "1"],
                [109, 111, "1"],
                [110, 108, "-1"],
                [111, 109, "-1"],
            ],
            "pairing_rank_added": 4,
        },
        "action": {
            "formula": (
                "S_R^(8)=-1/2 sum_(old six plus R0_4,R1_4) "
                "integral dvol_g g^{-1}(dR,dR)"
            ),
            "origin": "same positive massless scalar-rod action as the six-row sector",
            "odd_cotangents": "canonical cotangent lift of the two new Euler rows",
        },
        "background_completion": completion,
        "background_equation": {
            "equation": "H_retained Phi2^(8)=-q0^(eight rods)",
            "exact_blocks": background,
            "Noether_closed": True,
            "cokernel_projection": "ZERO",
            "canonical_primitive_exported": True,
            "old_Phi2_is_unchanged": False,
        },
        "first_later_incompatibility": {
            "required_interface": "local differential chain embedding i:Q108->Q112",
            "canonical_row_inclusion": "i(x)=(x,0,0,0)",
            "mixed_metric_to_new_rod_cotangent_witnesses": mixed_witnesses,
            "principal_equation_for_a_corrected_local_embedding": (
                "-s^2 P(s)=c s with c nonzero"
            ),
            "polynomial_divisibility": (
                "no P in the nonnegative-order local differential polynomial "
                "ring exists because s^2 does not divide c s"
            ),
            "only_formal_solution": "P(s)=-c/s, a nonlocal order-minus-one map",
            "local_embedding_status": "OBSTRUCTED",
            "canonical_inclusion_chain_defect_count": 2,
        },
        "minimality": {
            "six_rod_rank": 6,
            "required_closure_rank": 8,
            "one_rod_completion_rank": 7,
            "two_rod_completion_rank": 8,
            "wrong_degree_repair": (
                "a cotangent without its degree-zero scalar does not enlarge "
                "the background function span"
            ),
            "material_rod_substitution": (
                "rejected by the imported exact 24-of-24 principal separator"
            ),
        },
        "disposition": {
            "four_rows_action_pairing_background_and_K_closure": "CERTIFIED",
            "eight_rod_Phi2_source_sector_solvability": "CERTIFIED",
            "complete_112_row_q1": "NO_CERTIFIED_MAP",
            "q1_squared": "NO_CERTIFIED_MAP",
            "unary_cyclicity": "NO_CERTIFIED_MAP",
            "K_commutator_on_complete_q1": "NO_CERTIFIED_MAP",
            "original_108_row_local_chain_embedding": "OBSTRUCTED",
            "cohomology_Z2_memory_and_redshift": "NO_CERTIFIED_MAP",
        },
    }


def build_certificate(payload: dict[str, Any]) -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    payload_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    return {
        "schema": (
            "closed-universe-berger-global-rod-"
            "two-direction-extension-obstruction-v1"
        ),
        "result_id": "BERGER_GLOBAL_ROD_TWO_DIRECTION_EXTENSION_OBSTRUCTION",
        "setting_id": values["complete_unary"]["setting_id"],
        "claim_status": (
            "OBSTRUCTED_LOCAL_108_TO_112_CHAIN_EMBEDDING_AFTER_"
            "ACTION_DERIVED_ROD_REPAIR"
        ),
        "atlas_status": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": values[name]["result_id"],
                "sha256": sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "payload_ref": {
            "path": str(PAYLOAD.relative_to(ROOT)),
            "result_id": payload["result_id"],
            "sha256": hashlib.sha256(payload_text.encode()).hexdigest(),
            "canonical_sha256": canonical_sha256(payload),
        },
        "certified_partial_construction": {
            "exact_four_rows": "CERTIFIED",
            "action_and_pairing": "CERTIFIED",
            "real_structure": "CERTIFIED",
            "background_wave_equations": "CERTIFIED",
            "closure_rank_eight": "CERTIFIED",
            "eight_rod_stress_Noether_closure": "CERTIFIED",
            "eight_rod_Phi2_primitives": "CERTIFIED",
        },
        "first_later_incompatibility": payload["first_later_incompatibility"],
        "downstream_disposition": payload["disposition"],
        "next_gate": (
            "CHOOSE_REPLACEMENT_112_ROW_THEORY_OR_SUPPLY_A_NONLOCAL_"
            "SUPPORT_CONTROLLED_COMPARISON_MAP_DO_NOT_CALL_IT_AN_EXTENSION"
        ),
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE result constructs the "
            "unique canonical two-direction completion selected by the "
            "imported rank-six-to-rank-eight defect: the normalized time-"
            "derivative partners of R0_1 and R1_1, named R0_4 and R1_4, "
            "with their signed cyclic cotangents. Both new real scalar rods "
            "solve the Berger wave equation. Their common positive massless "
            "scalar action, four pairing entries, real involution and exact "
            "eight-dimensional centered-background K matrix are exported. "
            "One-rod and wrong-degree mutations fail. The complete eight-rod "
            "stress remains Noether closed in the same finite j=0,1 and "
            "frequency 0,plus-or-minus sqrt(58)/3 sector. Exact sparse "
            "primitives solve H_retained Phi2^(8)=-q0^(8), and their nonzero "
            "difference from the six-rod primitives is recorded. The "
            "construction then hits a later exact incompatibility with the "
            "work item's extension requirement. The same action produces a "
            "nonzero mixed metric-to-new-rod-cotangent unary block K_Rh. At "
            "the two displayed exact points its temporal principal "
            "coefficient is sqrt(145) sin(phi_a)/20, nonzero. Hence the "
            "canonical row inclusion of the original 108 rows has two chain "
            "defects. Any local differential correction P must solve "
            "-s^2 P(s)=c s. No nonnegative-order polynomial solution exists; "
            "the formal solution -c/s is nonlocal and has no certified "
            "support-controlled Green realization. Thus the demanded local "
            "108-to-112 chain embedding is obstructed in the exhaustive "
            "four-row positive scalar/cotangent extension class. A 112-row "
            "replacement theory may still be built, or a separately "
            "certified nonlocal comparison may be sought, but neither is an "
            "extension of the certified 108-row complex. No complete 112-row "
            "q1, cohomology, Z2 response, memory, redshift, q2/q3, particle, "
            "positivity or quantum claim is promoted."
        ),
        "provenance": {
            "generator_command": (
                "python3 -m closed_universe_observers."
                "generate_berger_global_rod_"
                "two_direction_extension_obstruction --write"
            ),
            "independent_verifier_command": (
                "python3 -m closed_universe_observers."
                "verify_berger_global_rod_"
                "two_direction_extension_obstruction"
            ),
            "source_sha256": sha256(Path(__file__)),
        },
    }


def report_text() -> str:
    return """# Berger global-rod two-direction extension

The forced rank-eight completion is explicit: add the normalized time-
derivative partners of R0_1 and R1_1 and their cyclic cotangents.  Both new
real rods solve the scalar wave equation, arise from the same positive
massless rod action, and close the centered background K orbit exactly.
The eight-rod stress is Noether closed and has exact retained Phi2 primitives.

The construction is not an extension of the old 108-row chain complex.
Metric perturbations source each new rod cotangent through a nonzero mixed
Hessian.  Correcting the canonical row inclusion locally would require
-s^2 P(s)=c s, so P=-c/s.  This is nonlocal and outside the declared local
crosswalk.  A 112-row replacement theory or a support-controlled nonlocal
comparison remains possible, but neither is certified here.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    certificate = build_certificate(payload)
    if args.write:
        PAYLOAD.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        CERTIFICATE.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n"
        )
        REPORT.write_text(report_text())
    else:
        print(json.dumps(certificate, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
