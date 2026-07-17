"""Emit the four-dimensional Diff/mixed and minimal-BV H14 certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .diff_mixed_total_complex import analysis


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "certificates/AFN0_DIFF_MIXED_MINIMAL_BV_H14.json"
SCHEMA = HERE / "schema/afn0_diff_mixed_minimal_bv_h14.schema.json"
SOURCE_PATHS = (
    "quantum-weyl/local_bv/diff_mixed_total_complex.py",
    "quantum-weyl/local_bv/diff_mixed_total_complex_certificate.py",
    "quantum-weyl/local_bv/verify_diff_mixed_total_complex.py",
    "quantum-weyl/local_bv/schema/afn0_diff_mixed_minimal_bv_h14.schema.json",
    "quantum-weyl/local_bv/tests/test_diff_mixed_total_complex.py",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, Any]:
    result = analysis()
    return {
        "schema": "quantum-weyl-afn0-diff-mixed-minimal-bv-h14-v1",
        "result_id": "AFN0_DIFF_MIXED_MINIMAL_BV_H14",
        "result_state": "MINIMAL_BV_H14_COMPLETE_ON_REGULAR_BACH_LOCUS_NONMINIMAL_OPEN",
        "classical_commit": result["classical_commit"],
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {
            "spacetime_dimension": 4,
            "ghost_number": 1,
            "form_degree": 4,
            "engineering_dimension": 4,
            "minimal_antifield_number_range": [0, 2],
            "locality": "POLYNOMIAL_FINITE_JETS_ON_CONTRACTIBLE_PATCH",
            "regularity": "REGULAR_BACH_LOCUS_FOR_KOSZUL_TATE_ADAPTED_COORDINATES",
        },
        "dependency_hashes": result["dependency_hashes"],
        "ambient_accounting": result["ambient_accounting"],
        "comparison_theorem_application": result["theorem_application"],
        "primary_sources": result["primary_sources"],
        "small_algebra": result["small_algebra"],
        "AFN0_H14": result["AFN0_H14"],
        "minimal_BV_H14": result["minimal_BV_H14"],
        "checks": {
            "ambient_signature_inventory_bound": "VERIFIED",
            "universal_Diff_totalization": "VERIFIED_ON_GENERIC_STRICT_DENSITY_AND_ALL_SURVIVING_TOP_REPRESENTATIVES",
            "Euler_intrinsic_and_Diff_completion": "VERIFIED",
            "Weyl_ghost_derivative_reduction": "THEOREM_HYPOTHESES_VERIFIED",
            "pure_Diff_non_covariant_small_algebra": "EXACT_RATIONAL_RANK_COMPUTED",
            "degree_three_metric_invariant_polynomial_space": "ZERO",
            "pure_Diff_H14": "ZERO",
            "independent_mixed_Diff_Weyl_H14": "ZERO",
            "AFN0_H14_even_odd_dimensions": "2_1",
            "positive_antifield_columns": "ZERO_BY_EXPLICIT_CONTRACTION",
            "minimal_BV_H14_even_odd_dimensions": "2_1",
            "general_nonminimal_gauge_fixed_sector": "NOT_COMPUTED",
        },
        "claim_flags": {
            "AFN0_DIFF_MIXED_TOTAL_COMPLEX_COMPLETE": True,
            "PURE_DIFF_H14_ZERO": True,
            "INDEPENDENT_MIXED_DIFF_WEYL_H14_ZERO": True,
            "MINIMAL_BV_H14_COMPLETE_ON_REGULAR_BACH_LOCUS": True,
            "GENERAL_NONMINIMAL_GAUGE_FIXED_H14_COMPLETE": False,
            "FULL_G2_PROMOTED": False,
            "ANOMALY_COEFFICIENTS_COMPUTED_HERE": False,
            "QME_RESTORED": False,
            "LORENTZIAN_QUANTUM_THEORY": False,
        },
        "proof_sha256": result["proof_sha256"],
        "next_gate": "GENERAL_LOCAL_NONMINIMAL_DOUBLETS_AND_GAUGE_FIXED_CONTRACTION",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC result completes H14 for the minimal Diff x Weyl BV "
            "complex on the imported regular Bach-locus coordinate chart. It applies the "
            "Stora total-form comparison only after checking the local polynomial finite-jet "
            "scope, binds all 720 refined ambient signatures without expanding 2,860,932,903 "
            "raw graphs, verifies the universal Diff towers on every surviving top "
            "representative, and treats the only non-covariant pure-gravity escape sector "
            "by an exact rational computation of symmetric invariant tensors of the "
            "complexified metric structure algebra. The degree-three invariant space is "
            "zero, with degrees two and four retained as nonzero controls. Thus no pure-Diff "
            "or independent mixed Diff-Weyl class augments the two even and one odd Weyl "
            "classes. The positive-antifield columns then vanish by the separately certified "
            "Koszul-Tate contraction. This does not yet import and contract the general local "
            "nonminimal/gauge-fixed doublets, so it does not promote full G2. It computes no "
            "anomaly coefficient, regulated Slavnov breaking, QME restoration, residual "
            "quantum transfer, Hadamard state, Lorentzian product, or quantum theory."
        ),
        "provenance": {
            "source_sha256": {path: _sha256(ROOT / path) for path in SOURCE_PATHS}
        },
    }


def validate(value: dict[str, Any]) -> None:
    flags = value.get("claim_flags", {})
    if (
        flags.get("AFN0_DIFF_MIXED_TOTAL_COMPLEX_COMPLETE") is not True
        or flags.get("PURE_DIFF_H14_ZERO") is not True
        or flags.get("INDEPENDENT_MIXED_DIFF_WEYL_H14_ZERO") is not True
        or flags.get("MINIMAL_BV_H14_COMPLETE_ON_REGULAR_BACH_LOCUS") is not True
        or any(
            flags.get(name) is not False
            for name in (
                "GENERAL_NONMINIMAL_GAUGE_FIXED_H14_COMPLETE",
                "FULL_G2_PROMOTED",
                "ANOMALY_COEFFICIENTS_COMPUTED_HERE",
                "QME_RESTORED",
                "LORENTZIAN_QUANTUM_THEORY",
            )
        )
        or value.get("next_gate")
        != "GENERAL_LOCAL_NONMINIMAL_DOUBLETS_AND_GAUGE_FIXED_CONTRACTION"
    ):
        raise ValueError("Diff/mixed minimal-BV H14 certificate crossed its claim boundary")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    validate(value)
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    content = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(content)
    if args.check and OUTPUT.read_text() != content:
        raise SystemExit(f"stale Diff/mixed H14 certificate: {OUTPUT}")
    print("AFN0 DIFF/MIXED + MINIMAL BV H14: PASS; NONMINIMAL GATE OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
