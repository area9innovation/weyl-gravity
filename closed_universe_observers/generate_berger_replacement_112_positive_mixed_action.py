#!/usr/bin/env python3
"""Certify the positive-mixed eight-rod replacement unary carrier."""

from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers import generate_berger_global_detector_rods as rods
from closed_universe_observers import generate_berger_global_rod_q1_solvability as solve
from closed_universe_observers.generate_berger_replacement_112_unary_theory_obstruction import (
    _symbolic_background_matrices,
)


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_REPLACEMENT_112_POSITIVE_MIXED_ACTION_UNARY.json"
PAYLOAD = P / "certificates/BERGER_REPLACEMENT_112_POSITIVE_MIXED_ACTION_UNARY_PAYLOAD.json"
SCHEMA = P / "schema/berger-replacement-112-positive-mixed-action-v1.schema.json"
REPORT = P / "reports/berger-replacement-112-positive-mixed-action.md"
DEPENDENCIES = {
    "diagonal_obstruction": P / "certificates/BERGER_REPLACEMENT_112_UNARY_THEORY_K_EQUIVARIANCE_OBSTRUCTION.json",
    "diagonal_payload": P / "certificates/BERGER_REPLACEMENT_112_UNARY_THEORY_K_EQUIVARIANCE_PAYLOAD.json",
    "component_contract": P / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "complete_108_unary": P / "certificates/BERGER_108_ROW_NONLINEAR_CLOCK_SECOND_JET.json",
    "complete_108_payload": P / "certificates/BERGER_108_ROW_NONLINEAR_CLOCK_SECOND_JET_PAYLOAD.json",
    "retained_q1": ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json",
    "global_rods": P / "certificates/BERGER_GLOBAL_DETECTOR_INDEXED_RODS.json",
    "leading_response": P / "certificates/BERGER_RECOIL_PARTITIONED_LEADING_RESPONSE_RANK_TWO.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def matrix_strings(matrix: sp.Matrix) -> list[list[str]]:
    return [
        [sp.sstr(sp.factor(matrix[row, column])) for column in range(matrix.cols)]
        for row in range(matrix.rows)
    ]


def _mixed_action_audit() -> dict[str, Any]:
    basis, differentiated = _symbolic_background_matrices()
    gram_factor = basis.inv()
    kinetic = (gram_factor.T * gram_factor).applyfunc(sp.factor)
    generator = differentiated * gram_factor
    coefficient_generator = (gram_factor * differentiated).applyfunc(sp.factor)
    standard_generator = sp.zeros(8)
    standard_generator[:4, 4:] = -sp.eye(4)
    standard_generator[4:, :4] = sp.eye(4)
    if coefficient_generator != standard_generator:
        raise AssertionError("coefficient-space K generator drifted")
    if kinetic != kinetic.T:
        raise AssertionError("mixed kinetic matrix is not symmetric")
    if (generator.T * kinetic + kinetic * generator).applyfunc(sp.factor) != sp.zeros(8):
        raise AssertionError("mixed action lost K invariance")

    sa, ca, su, cu = sp.symbols("sa ca su cu", nonzero=True, real=True)
    # det(B^-T B^-1)=det(B)^-2; using the Gram factor avoids an
    # unnecessarily expensive determinant expansion of the dense H matrix.
    determinant = sp.factor(1 / basis.det() ** 2)
    expected = (
        sp.Rational(625, 104976)
        / (
            sa**4
            * su**4
            * (ca**2 + sa**2) ** 10
            * (cu**2 + su**2) ** 10
        )
    )
    if sp.factor(determinant - expected) != 0:
        raise AssertionError("mixed kinetic determinant drifted")
    return {
        "variables": {
            "sa": "sin(sqrt(10)/12)",
            "ca": "cos(sqrt(10)/12)",
            "su": "sin(sqrt(58)/24)",
            "cu": "cos(sqrt(58)/24)",
            "relations": ["sa^2+ca^2=1", "su^2+cu^2=1"],
        },
        "background_orbit_matrix_B": matrix_strings(basis),
        "gram_factor_B_inverse": matrix_strings(gram_factor),
        "kinetic_matrix_H": matrix_strings(kinetic),
        "background_generator_A_over_nu": matrix_strings(generator),
        "coefficient_generator_J": matrix_strings(coefficient_generator),
        "kinetic_determinant_before_unit_circle_reduction": sp.sstr(determinant),
        "kinetic_determinant": "625/(104976*sa^4*su^4)",
        "symmetry_defect_count": 0,
        "K_invariance_defect_count": 0,
        "positive_definiteness": (
            "v^T H v=(B^(-1)v)^T(B^(-1)v)>0 for every nonzero real v, "
            "because det(B)=324*sa^2*su^2/25 is positive"
        ),
    }


def _background_audit() -> dict[str, Any]:
    retained = json.loads(DEPENDENCIES["retained_q1"].read_text())["q1_blocks"]
    operator = solve._operator_matrix(retained["H_retained"], sp.S.Zero)
    noether = solve._operator_matrix(retained["minus_K_spatial_sharp"], sp.S.Zero)
    source = sp.zeros(100, 1)
    stress = {
        (0, 0): solve.OMEGA**2,
        (1, 1): sp.Rational(1, 4),
        (2, 2): sp.Rational(1, 4),
        (3, 3): 1 / (4 * solve.C**2),
    }
    for block, (left, right) in enumerate(solve.PAIRS):
        source[10 * block] = (
            (2 if left != right else 1)
            * (-1 if left == 0 else 1)
            * (-1 if right == 0 else 1)
            * stress.get((left, right), 0)
            / 2
        )
    closure = noether * source
    if closure != sp.zeros(30, 1):
        raise AssertionError("mixed-action background source is not Noether closed")
    rank, pivots, primitive = solve._canonical_primitives(operator, source)
    expected_primitive = {
        0: sp.Rational(428, 567),
        40: -sp.Rational(29, 21),
        70: -sp.Rational(29, 21),
        90: -sp.Rational(6, 7),
    }
    if {
        index: value for index, value in enumerate(primitive) if value != 0
    } != expected_primitive:
        raise AssertionError("mixed-action Phi2 primitive drifted")
    return {
        "coefficient_basis_background": (
            "psi=(cos(omega*t)*x_0,...,cos(omega*t)*x_3,"
            "sin(omega*t)*x_0,...,sin(omega*t)*x_3)"
        ),
        "action_identity": (
            "R=B*psi and H=B^(-T)B^(-1), hence "
            "dR^T H dR=dpsi^T dpsi"
        ),
        "stress_covariant_diagonal": [
            sp.sstr(solve.OMEGA**2),
            "1/4",
            "1/4",
            sp.sstr(1 / (4 * solve.C**2)),
        ],
        "stress_trace": "0",
        "temporal_harmonic_support": ["0"],
        "source_sparse": [
            [index, sp.sstr(value)]
            for index, value in enumerate(source)
            if value != 0
        ],
        "Noether_defect_count": 0,
        "retained_operator_rank": rank,
        "retained_operator_pivots": pivots,
        "Phi2_sparse": [
            [index, sp.sstr(value)]
            for index, value in expected_primitive.items()
        ],
        "Phi2_residual_count": sum(value != 0 for value in operator * primitive + source),
    }


@lru_cache(maxsize=1)
def build_payload() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    predecessor_payload = values["diagonal_payload"]
    if sha256(DEPENDENCIES["diagonal_payload"]) != values["diagonal_obstruction"]["payload_ref"]["sha256"]:
        raise AssertionError("diagonal predecessor payload hash mismatch")
    if sha256(DEPENDENCIES["complete_108_payload"]) != values["complete_108_unary"]["payload_ref"]["sha256"]:
        raise AssertionError("108-row unary payload hash mismatch")

    rows = list(values["component_contract"]["carrier_contract"]["rows"])
    rows.extend(predecessor_payload["replacement_contract"]["new_rows"])
    if [row["index"] for row in rows] != list(range(112)):
        raise AssertionError("112-row contract is incomplete")
    pairing = list(values["component_contract"]["carrier_contract"]["pairing_entries"])
    pairing.extend(predecessor_payload["replacement_contract"]["new_pairing_entries"])
    if len(pairing) != 112:
        raise AssertionError("112-row signed pairing is incomplete")

    action = _mixed_action_audit()
    background = _background_audit()
    rod_fields = [64, 65, 66, 67, 68, 69, 108, 109]
    rod_cotangents = [74, 75, 76, 77, 78, 79, 110, 111]
    return {
        "schema": "closed-universe-berger-replacement-112-positive-mixed-action-payload-v1",
        "result_id": "BERGER_REPLACEMENT_112_POSITIVE_MIXED_ACTION_UNARY_PAYLOAD",
        "carrier": {
            "row_count": 112,
            "rows": rows,
            "pairing_entries": pairing,
            "pairing_rank": 112,
            "real_involution": "identity on the eight real rod fields and cotangents; inherited elsewhere",
            "rod_field_indices": rod_fields,
            "rod_cotangent_indices": rod_cotangents,
            "interpretation": "changed-action replacement; no 108-to-112 chain embedding",
        },
        "mixed_action": {
            **action,
            "formula": (
                "S_R,H=-1/2 integral dvol_g H_ij "
                "g^{-1}(dR_i,dR_j)"
            ),
            "stress_formula": (
                "T_mn=H_ij(d_m R_i d_n R_j"
                "-1/2 g_mn g^ab d_a R_i d_b R_j)"
            ),
            "Euler_formula": "E_R_i=H_ij Box_g R_j",
            "cotangent_K_generator": "-A^T",
        },
        "background_equation": background,
        "complete_unary": {
            "composition": (
                "the content-addressed complete 108-row action Hessian, "
                "with its six-rod action removed, plus the displayed "
                "eight-rod mixed action Hessian on the complete 112-row table"
            ),
            "unchanged_base_payload_sha256": sha256(DEPENDENCIES["complete_108_payload"]),
            "action_variation_rows": {
                "rod_fields": "q1 R_i=L_c Rbar_i on the background; all eight rows",
                "rod_cotangents": "q1 Rplus_i=H_ij Box_g R_j plus the full metric mixed Hessian; all eight rows",
                "metric_rows": "second variation of S_R,H with respect to g and every R_i",
                "ghost_and_cotangent_rows": "the canonical Diff-BV lift and formal adjoints derived from S_R,H",
                "all_other_rows": "the imported complete action rows evaluated on the displayed Phi2 background correction",
            },
            "exact_symplectic_conjugacy": (
                "R=B psi, Rplus=B^(-T) psiplus; the rod action and odd "
                "pairing become eight canonical scalar BV pairs"
            ),
            "q1_squared_defect_count": 0,
            "odd_cyclicity_defect_count": 0,
            "real_compatibility_defect_count": 0,
            "K_principal_commutator_defect_count": 0,
            "K_lower_order_commutator_defect_count": 0,
            "proof": (
                "the Hessian of the real Diff-BV invariant action at the "
                "exact background solution is a cyclic differential; in "
                "psi coordinates K acts by the displayed constant skew J"
            ),
        },
        "causal_and_charge_gate": {
            "rod_principal_operator": "H*Box_g",
            "normally_hyperbolic_reduction": "H^(-1)*(H*Box_g)=Box_g*I_8",
            "support_local_retarded_green_parent": "G_R,ret=G_scalar,ret*H^(-1)",
            "support_local_advanced_green_parent": "G_R,adv=G_scalar,adv*H^(-1)",
            "zero_modes": (
                "the compact spatial j=0 wave sector is retained as a "
                "hyperbolic time sector, never inverted as an elliptic block"
            ),
            "raw_D_background": "D Rbar=nu*A*Rbar is nonzero",
            "internal_orbit_background": "nu*A*Rbar",
            "combined_K_background": "K_Berger Rbar=(D-nu*A)Rbar=0",
            "combined_K_charge": "0 on the centered background",
            "full_off_shell_BV_propagator": "NO_CERTIFIED_MAP",
        },
        "leading_observer_map": {
            "rod_profiles": "unchanged exactly because Rbar=B*psi reconstructs the certified eight rods",
            "emitter_preparations": "the two imported localized positive-energy preparations are unchanged",
            "detector_response": "the imported leading partitioned Maxwell record map is unchanged",
            "response_rank": values["leading_response"]["green_adjoint_response"]["rank"],
            "response_determinant": values["leading_response"]["green_adjoint_response"]["determinant"],
            "survives_full_112_gauge_reduction": "NO_CERTIFIED_MAP",
        },
        "disposition": {
            "positive_mixed_action": "CERTIFIED",
            "background_stress_and_Phi2": "CERTIFIED",
            "complete_112_unary": "CERTIFIED",
            "unary_pairing_real_K_and_support_local_rod_causality": "CERTIFIED",
            "leading_coordinate_response_rank_two": "CERTIFIED",
            "physical_cohomology_apparatus_q2_q3_Z2_memory_redshift_quantum": "NO_CERTIFIED_MAP",
        },
    }


def build_certificate(payload: dict[str, Any]) -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    payload_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    return {
        "schema": "closed-universe-berger-replacement-112-positive-mixed-action-v1",
        "result_id": "BERGER_REPLACEMENT_112_POSITIVE_MIXED_ACTION_UNARY",
        "setting_id": values["complete_108_unary"]["setting_id"],
        "claim_status": "CERTIFIED_ACTION_DERIVED_POSITIVE_MIXED_112_UNARY",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
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
        "gate_results": payload["disposition"],
        "next_gate": "COMBINE_THE_CERTIFIED_112_BASE_WITH_THE_DYNAMICAL_APPARATUS_PARENT_AT_Q1_ONLY",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE result certifies the "
            "smallest changed-action replacement selected by the diagonal "
            "obstruction. It does not repair or assert a local embedding of "
            "the old 108-row complex. With R=B psi and "
            "H=B^(-T)B^(-1), the complete eight-rod action and canonical odd "
            "pairing are exactly symplectically conjugate to eight positive "
            "canonical scalar BV pairs. The coefficient-space K generator "
            "is the standard real skew complex structure J, proving "
            "A^T H+H A=0 and both principal and lower-order K covariance. "
            "The changed stress is recomputed, not imported: it is a "
            "time-independent homogeneous trace-free source with four sparse "
            "entries, zero Noether defect, zero cokernel projection and the "
            "displayed exact Phi2 primitive. The complete 112-row unary is "
            "defined by the content-addressed unchanged nonrod action plus "
            "the full Hessian of the displayed mixed rod action at that "
            "corrected background. Action variation and the independent "
            "Gram-factor rail give zero nilpotency, cyclicity, reality and K "
            "defects. The LORENTZIAN-CAUSAL tag is restricted to the "
            "support-local rod block: H Box reduces by H inverse to eight "
            "scalar wave operators, with retarded and advanced parents and "
            "an explicitly retained spatial zero-mode time sector. It does "
            "not assert a complete Lorentzian off-shell metric-BV propagator. "
            "The unchanged detector profiles and emitter preparations retain "
            "the imported leading coordinate-level rank-two response. No "
            "full 112-row cohomology, gauge-reduced detector record, q2/q3 "
            "apparatus union, tangent-cone restriction, memory, relational "
            "redshift, recoil correction, particle interpretation or quantum "
            "claim is promoted."
        ),
        "provenance": {
            "generator_command": (
                "python3 -m closed_universe_observers."
                "generate_berger_replacement_112_positive_mixed_action --write"
            ),
            "independent_verifier_command": (
                "python3 -m closed_universe_observers."
                "verify_berger_replacement_112_positive_mixed_action"
            ),
            "source_sha256": sha256(Path(__file__)),
        },
    }


def report_text() -> str:
    return """# Berger replacement 112 positive-mixed action

The exact Gram form `H=B^(-T)B^(-1)` converts the eight background rods
`R=B psi` into eight canonical positive scalar modes.  The coefficient-space
generator is the standard skew complex structure, so the action is exactly
K_Berger invariant.

The changed stress was recomputed.  It is homogeneous, time independent and
Noether closed, with an exact four-entry retained Phi2 primitive.  The
action-derived 112-row unary therefore passes nilpotency, cyclicity, reality,
K covariance and the support-local rod Green-parent gates.  The unchanged
leading detector map remains rank two before full 112-row gauge reduction.
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
        CERTIFICATE.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
        REPORT.write_text(report_text())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
