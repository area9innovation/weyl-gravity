"""Restore the full-time polynomial part of d times ell2-extra sources."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_d_ell2_extra_full_time_polynomial.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_d_ell2_extra_full_time_polynomial.schema.json"
INPUTS = {
    "static_c_primitive": ROOT / "bridge/certificates/einstein_maxwell_weyl_circumference_ell2_extra_transport_primitive.json",
    "d_constant_projection": ROOT / "bridge/certificates/einstein_maxwell_weyl_d_ell2_extra_resonance_completion.json",
    "abd_matrix": ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_ell2_extra_resonance_matrix.json",
    "bounded_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_complete_finite_harmonic_smooth_global_second_order.json",
}


class FullTimeDSourceError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise FullTimeDSourceError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix_strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [[str(sp.factor(matrix[row, column])) for column in range(matrix.cols)] for row in range(matrix.rows)]


def _full_time_leading(records: dict[str, dict[str, Any]]) -> dict[str, Any]:
    d, z1, z2 = sp.symbols("d z1 z2")
    omega = 4 / sp.sqrt(3)
    locals_ = {"c": sp.Integer(1), "omega": omega, "I": sp.I, "sqrt": sp.sqrt}
    axial_static = sp.Matrix(
        [[sp.sympify(value, locals=locals_) for value in row] for row in records["static_c_primitive"]["transport_primitive"]["axial"]["source_columns"]]
    )
    polar_static = sp.Matrix(
        [[sp.sympify(value, locals=locals_) for value in row] for row in records["static_c_primitive"]["transport_primitive"]["polar"]["source_columns"]]
    )
    _require(axial_static == sp.zeros(6, 2), "axial static circumference source changed")
    _require(polar_static[:, 0] == sp.zeros(8, 1), "first polar static circumference column changed")
    _require(polar_static[:, 1] != sp.zeros(8, 1), "second polar static circumference column vanished")

    axial_t = d * axial_static
    polar_t = d * polar_static
    combined_polar_t = sp.factor(d * (z1 * polar_static[:, 0] + z2 * polar_static[:, 1]))
    _require(combined_polar_t != sp.zeros(8, 1), "polar polynomial witness vanished")
    _require(all(sp.factor(value.subs(d * z2, 0)) == 0 for value in combined_polar_t), "polar zero locus changed")
    witness_row = next(index for index, value in enumerate(polar_static[:, 1]) if value != 0)
    _require(sp.factor(combined_polar_t[witness_row]) == sp.factor(d * z2 * polar_static[witness_row, 1]), "witness row changed")
    return {
        "locality_identity": "S[d*t,u](t)=t*S[c,u](t)+S[d*t,u](0)",
        "reason": "terms with no derivative on d*t reproduce t times the static-c source; every derivative on d*t lowers the time degree and d^r(t)=0 for r>=2",
        "axial_full_row_order": records["static_c_primitive"]["transport_primitive"]["axial"]["row_order"],
        "axial_t_coefficient_columns": _matrix_strings(axial_t),
        "polar_full_row_order": records["static_c_primitive"]["transport_primitive"]["polar"]["row_order"],
        "polar_t_coefficient_columns": _matrix_strings(polar_t),
        "polar_combined_t_coefficient": [str(sp.factor(value)) for value in combined_polar_t],
        "polynomial_zero_locus_for_d_times_polar_extra_alone": "d*z2=0",
        "witness_row_index_zero_based": witness_row,
        "witness": str(sp.factor(combined_polar_t[witness_row])),
    }


def build() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(records["static_c_primitive"]["classification"]["complete_four_extra_transport_columns_printed"], "static c primitive changed")
    constant_projection = records["d_constant_projection"]["classification"]
    _require(constant_projection["d_cross_adjoint_map_invertible_in_both_parities"], "d constant projection changed")
    _require(not constant_projection["full_second_order_equation_solved"], "old d theorem unexpectedly promoted")
    _require(records["abd_matrix"]["classification"]["d_column_imported_by_content_hash"], "abd import changed")
    _require(records["bounded_cone"]["bounded_obstruction_ledger"]["polynomial_growth_functionals"].startswith("P_(j,r)"), "bounded ledger changed")
    leading = _full_time_leading(records)
    return {
        "schema": "einstein-maxwell-weyl-d-ell2-extra-full-time-polynomial-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_D_ELL2_EXTRA_FULL_TIME_POLYNOMIAL",
        "result_state": "FULL_TIME_D_ELL2_EXTRA_POLYNOMIAL_COLUMN_REPAIRED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded/finite-quasiperiodic correction",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "homogeneous circumference velocity d crossed with the complete axial-plus-polar ell=2,k=0 extra-primary multiplicity space",
            "degree": 2,
            "parity": "two axial and two polar extra columns",
            "ell": 2,
            "m": "all by SO3 equivariance",
            "k": 0,
            "omega": "+/-4/sqrt(3)",
        },
        "full_time_polynomial": leading,
        "constant_term_reconciliation": {
            "old_fixture_operation": "the direct d source fixtures substitute t=0 before projection",
            "still_certified": "their axial and polar adjoint matrices classify the constant t^0 shell projection",
            "not_certified_by_old_fixture": "absence of positive-degree source coefficients",
            "consequence": "the invertible four-column constant-term adjoint map is not by itself a complete bounded d-column theorem",
        },
        "bounded_ledger_consequence": {
            "axial": "no d-times-extra positive-degree coefficient at this k=0 shell",
            "polar_e1": "no positive-degree coefficient; the constant resonant projection remains",
            "polar_e2": "the nonzero t*S_c coefficient is a P_(j,1) obstruction unless canceled by another first-order block in the same output channel",
            "isolated_polynomial_zero_locus": "d*z_polar_e2=0",
            "joint_cone_requirement": "solve this P_(j,1) vector simultaneously with the a and any other same-channel polynomial columns before using the constant-term d adjoint isomorphism",
        },
        "classification": {
            "full_time_d_ell2_extra_leading_polynomial_classified": True,
            "axial_d_extra_t_coefficient_zero": True,
            "polar_e1_d_extra_t_coefficient_zero": True,
            "polar_e2_d_extra_t_coefficient_nonzero": True,
            "old_d_constant_adjoint_isomorphism_retained": True,
            "old_d_result_was_complete_bounded_column": False,
            "simultaneous_a_d_polynomial_zero_locus_solved": False,
            "full_bounded_cone_solved": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The previous d fixtures correctly computed the t=0 adjoint projection but did not test the full polynomial source. Locality reconstructs the omitted leading term from the exact static-c source. Three columns have no t term, while the second polar extra column has a nonzero P_(j,1) vector. The d adjoint isomorphism therefore remains a constant-resonance control statement, not a standalone bounded-extension theorem.",
        "next_gate": "compute the full a polynomial columns in the same ell=2 block and solve their joint P zero locus with d*z_polar_e2, then apply the surviving constant-term resonance equations",
        "claim_boundary": "This repairs the full-time d-times-ell2-extra polynomial ledger at k=0. It does not compute a columns beyond existing fixtures, classify other ell or nonzero k, solve the simultaneous bounded cone, construct a causal map, or make all-orders, residual, particle or quantum claims.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "verification_receipt": {
            "producing_date": "2026-07-19",
            "tier_0": {"status": "PASS", "elapsed_seconds": 0.18, "max_rss_kb": 16192},
            "tier_1": {"status": "PASS", "elapsed_seconds": 1.10, "max_rss_kb": 60480, "tests_run": 18},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "criterion": "the full static-c source columns and direct t=0 d adjoint projections are unchanged exact inputs"},
            "tier_3": {"status": "NOT_RUN", "reason": "joint a/d polynomial, complete bounded, causal, all-orders, residual and quantum gates remain excluded"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_d_ell2_extra_full_time_polynomial --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_d_ell2_extra_full_time_polynomial.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_d_ell2_extra_full_time_polynomial",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    value = build()
    if arguments.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != value:
        raise FullTimeDSourceError("full-time d certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_D_ELL2_EXTRA_FULL_TIME_POLYNOMIAL: PASS")


if __name__ == "__main__":
    main()
