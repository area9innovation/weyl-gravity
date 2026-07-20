#!/usr/bin/env python3
"""Obstruct the diagonal-action eight-rod replacement at K equivariance."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers import generate_berger_global_detector_rods as rods


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = (
    P
    / "certificates/"
    "BERGER_REPLACEMENT_112_UNARY_THEORY_K_EQUIVARIANCE_OBSTRUCTION.json"
)
PAYLOAD = (
    P
    / "certificates/"
    "BERGER_REPLACEMENT_112_UNARY_THEORY_K_EQUIVARIANCE_PAYLOAD.json"
)
SCHEMA = (
    P
    / "schema/"
    "berger-replacement-112-unary-theory-k-equivariance-obstruction-v1.schema.json"
)
REPORT = P / "reports/berger-replacement-112-unary-theory-k-equivariance-obstruction.md"
DEPENDENCIES = {
    "four_row_obstruction": P
    / "certificates/"
    "BERGER_GLOBAL_ROD_TWO_DIRECTION_EXTENSION_OBSTRUCTION.json",
    "four_row_payload": P
    / "certificates/"
    "BERGER_GLOBAL_ROD_TWO_DIRECTION_EXTENSION_PAYLOAD.json",
    "global_rods": P / "certificates/BERGER_GLOBAL_DETECTOR_INDEXED_RODS.json",
    "complete_108_unary": P
    / "certificates/"
    "BERGER_108_ROW_NONLINEAR_CLOCK_SECOND_JET.json",
    "component_contract": P
    / "certificates/"
    "BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "apparatus_parent": P
    / "certificates/"
    "BERGER_DYNAMICAL_APPARATUS_PARENT.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _zero_mod_unit_circles(
    expression: sp.Expr,
    *,
    sa: sp.Symbol,
    ca: sp.Symbol,
    su: sp.Symbol,
    cu: sp.Symbol,
) -> bool:
    """Decide a rational identity on the two trigonometric unit circles."""

    numerator, _ = sp.together(expression).as_numer_denom()
    ideal = sp.groebner(
        [ca**2 + sa**2 - 1, cu**2 + su**2 - 1],
        ca,
        cu,
        sa,
        su,
        order="lex",
    )
    return sp.expand(ideal.reduce(sp.expand(numerator))[1]) == 0


def _symbolic_background_matrices() -> tuple[sp.Matrix, sp.Matrix]:
    """Return B and e0(B)/nu with double angles imposed algebraically."""

    sa, ca, su, cu = sp.symbols("sa ca su cu", nonzero=True, real=True)
    spatial_sine_2 = 2 * sa * ca
    spatial_cosine_2 = ca**2 - sa**2
    time_sine_2 = 2 * su * cu
    time_cosine_2 = cu**2 - su**2
    q = 3 * sp.sqrt(10) / 10
    profiles = [
        [-q * sa, 0, 0, q * ca],
        [0, 2 * ca, 2 * sa, 0],
        [0, -2 * sa, 2 * ca, 0],
        [-q * spatial_sine_2, 0, 0, q * spatial_cosine_2],
        [0, 2 * spatial_cosine_2, 2 * spatial_sine_2, 0],
        [0, -2 * spatial_sine_2, 2 * spatial_cosine_2, 0],
    ]
    current: list[list[sp.Expr]] = []
    derivatives: list[list[sp.Expr]] = []
    for index, profile in enumerate(profiles):
        cosine, sine = (
            (cu, su)
            if index < 3
            else (time_cosine_2, time_sine_2)
        )
        current.append(
            [cosine * value for value in profile]
            + [sine * value for value in profile]
        )
        derivatives.append(
            [sine * value for value in profile]
            + [-cosine * value for value in profile]
        )
    current_matrix = sp.Matrix(current)
    derivative_matrix = sp.Matrix(derivatives)
    basis = sp.Matrix.vstack(
        current_matrix, derivative_matrix[0, :], derivative_matrix[3, :]
    )
    differentiated = sp.Matrix.vstack(
        derivative_matrix, -current_matrix[0, :], -current_matrix[3, :]
    )
    return basis, differentiated


def _exact_audit() -> dict[str, Any]:
    basis, differentiated = _symbolic_background_matrices()
    sa, ca, su, cu = sp.symbols("sa ca su cu", nonzero=True, real=True)
    determinant = sp.factor(basis.det())
    expected_determinant = (
        sp.Rational(324, 25)
        * sa**2
        * su**2
        * (ca**2 + sa**2) ** 5
        * (cu**2 + su**2) ** 5
    )
    if sp.expand(determinant - expected_determinant) != 0:
        raise AssertionError("eight-rod basis determinant drifted")

    generator = differentiated * basis.inv()
    symmetric = (generator + generator.T).applyfunc(sp.factor)
    expected = sp.zeros(8)
    for index, sign in ((1, 1), (2, 1), (4, -1), (5, -1)):
        expected[index, index] = sign * 2 * cu / su
    for residual in symmetric - expected:
        if not _zero_mod_unit_circles(
            residual, sa=sa, ca=ca, su=su, cu=cu
        ):
            raise AssertionError("identity-kinetic symmetric defect drifted")

    skew_projection = (generator - generator.T) / 2
    background_defect = skew_projection * basis - differentiated
    # Since A B=D, this defect is -(A+A^T)B/2 on the unit-circle
    # quotient.  Certify the identity entrywise and use invertibility of B.
    for residual in background_defect + expected * basis / 2:
        if not _zero_mod_unit_circles(
            residual, sa=sa, ca=ca, su=su, cu=cu
        ):
            raise AssertionError("skew-projection defect identity drifted")

    return {
        "symbolic_variables": {
            "sa": "sin(sqrt(10)/12)",
            "ca": "cos(sqrt(10)/12)",
            "su": "sin(sqrt(58)/24)",
            "cu": "cos(sqrt(58)/24)",
            "relations": ["sa^2+ca^2=1", "su^2+cu^2=1"],
        },
        "basis_determinant_before_unit_circle_reduction": sp.sstr(determinant),
        "basis_determinant": "324*sa^2*su^2/25",
        "basis_rank": 8,
        "generator_symmetric_defect_over_nu": [
            [sp.sstr(expected[row, column]) for column in range(8)]
            for row in range(8)
        ],
        "generator_symmetric_defect_rank": expected.rank(),
        "skew_projection_background_closure_defect_rank": expected.rank(),
        "nonzero_proof": (
            "0<sqrt(10)/12<1 and 0<sqrt(58)/24<1 imply "
            "sa,su,cu are nonzero, so det(B)>0 and 2*cu/su>0"
        ),
    }


def _actual_background_generator(payload: dict[str, Any]) -> list[list[str]]:
    matrix = payload["background_completion"][
        "centered_background_K_matrix_over_nu"
    ]
    if len(matrix) != 8 or any(len(row) != 8 for row in matrix):
        raise AssertionError("imported background K matrix is not 8 by 8")
    actual = sp.Matrix([[sp.sympify(value) for value in row] for row in matrix])
    u = sp.sqrt(58) / 24
    expected = sp.zeros(8)
    for index, sign in ((1, 1), (2, 1), (4, -1), (5, -1)):
        expected[index, index] = sign * 2 / sp.tan(u)
    symmetric = actual + actual.T
    for row in range(8):
        for column in range(8):
            # Multiplication by sin(u) removes the cotangent denominator and
            # makes the double-angle identity exact for SymPy.
            residual = sp.simplify(
                sp.expand_trig(
                    (symmetric[row, column] - expected[row, column])
                    * sp.sin(u)
                )
            )
            if residual != 0:
                raise AssertionError("imported and reconstructed K defects differ")
    return matrix


def build_payload() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    four_row = values["four_row_payload"]
    if sha256(DEPENDENCIES["four_row_payload"]) != values["four_row_obstruction"][
        "payload_ref"
    ]["sha256"]:
        raise AssertionError("four-row payload hash is not the certified input")
    if four_row["background_completion"]["completed_rank"] != 8:
        raise AssertionError("imported eight-rod background ceased to close")
    if values["complete_108_unary"]["flags"][
        "COMPLETE_FIRST_BIDEGREE_UNARY_GATE"
    ] is not True:
        raise AssertionError("terminal 108-row unary input is not certified")

    audit = _exact_audit()
    generator = _actual_background_generator(four_row)
    symmetric = audit["generator_symmetric_defect_over_nu"]
    commutator = [
        [
            sp.sstr(-sp.sympify(symmetric[row][column]))
            for column in range(8)
        ]
        for row in range(8)
    ]
    old_rows = values["component_contract"]["carrier_contract"]["rows"]
    new_rows = [
        {"index": 108, "row_id": "R0_4", "degree": 0, "sector": "apparatus:rod"},
        {"index": 109, "row_id": "R1_4", "degree": 0, "sector": "apparatus:rod"},
        {
            "index": 110,
            "row_id": "R0_4_plus",
            "degree": 1,
            "sector": "apparatus:rod_antifield_density",
        },
        {
            "index": 111,
            "row_id": "R1_4_plus",
            "degree": 1,
            "sector": "apparatus:rod_antifield_density",
        },
    ]
    rows = old_rows + new_rows
    if [row["index"] for row in rows] != list(range(112)):
        raise AssertionError("replacement row table is incomplete")
    return {
        "schema": "closed-universe-berger-replacement-112-unary-k-obstruction-payload-v1",
        "result_id": "BERGER_REPLACEMENT_112_UNARY_THEORY_K_EQUIVARIANCE_PAYLOAD",
        "replacement_contract": {
            "interpretation": (
                "replacement action/carrier; no local 108-to-112 chain map"
            ),
            "row_count": 112,
            "rows": rows,
            "new_rows": new_rows,
            "new_pairing_entries": [
                [108, 110, "1"],
                [109, 111, "1"],
                [110, 108, "-1"],
                [111, 109, "-1"],
            ],
            "rod_action": (
                "S_R^(8)=-1/2 sum_i=1^8 integral dvol_g "
                "g^{-1}(dR_i,dR_i)"
            ),
            "rod_kinetic_matrix": "I_8",
            "real_involution": "identity on the four new real rows",
        },
        "background": {
            "generator_matrix_over_nu": generator,
            "closure_defect_count": 0,
            "eight_rod_stress_and_Phi2_status": "CERTIFIED",
            **audit,
        },
        "first_obstruction": {
            "identity": "[K_Berger,q1]=0",
            "sector": "eight scalar-rod wave Hessian and its cotangent lift",
            "field_generator_over_nu": "A",
            "cotangent_generator_over_nu": "-A^T",
            "wave_hessian": (
                "epsilon_R_squared*(-e0^2+e1^2+e2^2+e3^2)*I_8"
            ),
            "normalized_principal_commutator": (
                "-(A^T+A), after dividing by "
                "epsilon_R_squared*nu*Box_principal"
            ),
            "normalized_principal_commutator_matrix": commutator,
            "principal_commutator_rank": 4,
            "nonzero_diagonal_rows": [1, 2, 4, 5],
            "nonzero_diagonal_coefficients": [
                "-2*cot(sqrt(58)/24)",
                "-2*cot(sqrt(58)/24)",
                "2*cot(sqrt(58)/24)",
                "2*cot(sqrt(58)/24)",
            ],
            "action_invariance_equation": "A^T I_8+I_8 A=0",
            "action_invariance_status": "OBSTRUCTED",
        },
        "minimality_and_next_enlargement": {
            "remove_R0_4_pair_background_rank": 7,
            "remove_R1_4_pair_background_rank": 7,
            "both_pairs_background_rank": 8,
            "replace_A_by_skew_part_background_defect_rank": 4,
            "positive_diagonal_kinetic_repair": "OBSTRUCTED_BY_NONZERO_A_DIAGONAL",
            "smallest_unexcluded_repair": (
                "replace I_8 by a non-diagonal positive kinetic matrix H, "
                "then recompute stress, Phi2 and every changed-action unary row"
            ),
            "canonical_candidate": "H=B^(-T) B^(-1)",
            "candidate_positive_definite_proof": (
                "v^T H v=||B^(-1)v||^2>0 because det(B)>0"
            ),
            "candidate_invariance_proof": (
                "A=B J B^(-1), J^T=-J, hence "
                "A^T H+H A=B^(-T)(J^T+J)B^(-1)=0"
            ),
            "candidate_changes_certified_action": True,
            "candidate_stress_Phi2_and_unary_status": "NO_CERTIFIED_MAP",
        },
        "disposition": {
            "replacement_row_table_pairing_and_real_structure": "CERTIFIED",
            "eight_rod_background_K_closure": "CERTIFIED",
            "complete_112_row_q1": "NO_CERTIFIED_MAP",
            "q1_squared": "NO_CERTIFIED_MAP",
            "unary_cyclicity": "NO_CERTIFIED_MAP",
            "identity_kinetic_K_equivariance": "OBSTRUCTED",
            "background_quotient_closure": "NO_CERTIFIED_MAP",
            "cohomology_apparatus_memory_redshift": "NO_CERTIFIED_MAP",
        },
    }


def build_certificate(payload: dict[str, Any]) -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    payload_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    return {
        "schema": (
            "closed-universe-berger-replacement-112-unary-"
            "k-equivariance-obstruction-v1"
        ),
        "result_id": "BERGER_REPLACEMENT_112_UNARY_THEORY_K_EQUIVARIANCE_OBSTRUCTION",
        "setting_id": values["complete_108_unary"]["setting_id"],
        "claim_status": (
            "OBSTRUCTED_DIAGONAL_ACTION_REPLACEMENT_AT_"
            "K_BERGER_EQUIVARIANCE"
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
        "first_obstruction": payload["first_obstruction"],
        "minimality_and_next_enlargement": payload[
            "minimality_and_next_enlargement"
        ],
        "downstream_disposition": payload["disposition"],
        "next_gate": (
            "REPLACE_THE_DIAGONAL_ROD_ACTION_BY_AN_EXACT_INVARIANT_"
            "POSITIVE_KINETIC_MIXING_AND_RECOMPUTE_STRESS_PHI2_AND_Q1"
        ),
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE result tests the "
            "action-derived 112-row replacement selected by the prior local "
            "chain-map obstruction. The four new rows, signed odd pairing, "
            "real structure, rank-eight background basis, eight-rod stress "
            "and Phi2 primitives are retained in their certified scopes. "
            "The decisive new calculation reconstructs the unique linear "
            "background generator A on the eight centered rods. For the "
            "certified diagonal positive scalar action its symmetric part "
            "has exact rank four, with diagonal entries plus-or-minus "
            "2*cot(sqrt(58)/24). The cotangent lift acts by -A^T, so the "
            "scalar-wave Hessian has normalized K commutator -(A^T+A), also "
            "of rank four. No other unary row can cancel a principal defect "
            "on this isolated rod-wave block. Replacing A by its skew part "
            "loses background closure with rank-four defect; deleting either "
            "new pair leaves closure rank seven; and no positive diagonal "
            "kinetic rescaling can remove a nonzero diagonal of A. Thus the "
            "certified identity-kinetic eight-rod action does not define the "
            "required K_Berger-equivariant replacement unary theory. The "
            "same 112 rows admit the exact positive candidate "
            "H=B^(-T)B^(-1), but that is a changed action and its stress, "
            "Phi2, complete q1 and quotient are NO_CERTIFIED_MAP. No complete "
            "112-row nilpotency, cyclicity, cohomology, apparatus union, "
            "memory, redshift, tangent-cone, causal or quantum result is "
            "promoted."
        ),
        "provenance": {
            "generator_command": (
                "python3 -m closed_universe_observers."
                "generate_berger_replacement_112_unary_theory_obstruction "
                "--write"
            ),
            "independent_verifier_command": (
                "python3 -m closed_universe_observers."
                "verify_berger_replacement_112_unary_theory_obstruction"
            ),
            "source_sha256": sha256(Path(__file__)),
        },
    }


def report_text() -> str:
    return """# Berger replacement 112-row unary theory

The forced eight-rod background generator is not a symmetry of the certified
diagonal positive scalar action.  Its symmetric part has exact rank four and
diagonal entries plus or minus `2*cot(sqrt(58)/24)`.  With the canonical
cotangent lift, the scalar-wave Hessian therefore has a rank-four
`[K_Berger,q1]` principal defect.

Deleting either new rod/cotangent pair restores neither closure nor the old
theory: the background span drops to rank seven.  Projecting the generator to
its skew part instead loses background closure with rank-four defect.  A
non-diagonal positive kinetic matrix `H=B^(-T)B^(-1)` is an exact unexcluded
repair, but it changes the action and requires a fresh stress, Phi2 and unary
calculation.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    certificate = build_certificate(payload)
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)
    if args.write:
        PAYLOAD.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        CERTIFICATE.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n"
        )
        REPORT.write_text(report_text())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
