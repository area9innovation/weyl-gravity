"""Emit the exact minimal-BV Koszul--Tate collapse certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .minimal_bv_koszul_tate_collapse import analysis


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "certificates/MINIMAL_BV_KOSZUL_TATE_COLLAPSE.json"
SCHEMA = HERE / "schema/minimal_bv_koszul_tate_collapse.schema.json"
SOURCE_PATHS = (
    "quantum-weyl/local_bv/minimal_bv_koszul_tate_collapse.py",
    "quantum-weyl/local_bv/minimal_bv_koszul_tate_collapse_certificate.py",
    "quantum-weyl/local_bv/verify_minimal_bv_koszul_tate_collapse.py",
    "quantum-weyl/local_bv/schema/minimal_bv_koszul_tate_collapse.schema.json",
    "quantum-weyl/local_bv/tests/test_minimal_bv_koszul_tate_collapse.py",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, Any]:
    result = analysis()
    return {
        "schema": "quantum-weyl-minimal-bv-koszul-tate-collapse-v1",
        "result_id": "MINIMAL_BV_KOSZUL_TATE_COLLAPSE",
        "result_state": "MINIMAL_KT_COLLAPSE_PROVED_AFN0_WEYL_QUOTIENTS_LIFT_DIFF_MIXED_TOTAL_COMPLEX_OPEN",
        "classical_commit": result["classical_commit"],
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_hashes": result["dependency_hashes"],
        "scope": {
            "spacetime_dimension": 4,
            "engineering_dimension": 4,
            "form_degree": 4,
            "antifield_number_range": [0, 2],
            "coefficient_field": "Q",
            "locality": "SUPPORT_LOCAL_COVARIANT_POLYNOMIAL_JETS",
        },
        "contraction": {
            "contractible_pairs": result["contractible_pairs"],
            "pair_atom_count": result["pair_atom_count"],
            "base_atom_count": result["base_atom_count"],
            "positive_antifield_atom_count": result["positive_antifield_atom_count"],
            "generator_euler_identity": result["generator_euler_identity"],
            "regression_monomial_count": result["regression_monomial_count"],
            "regression_manifest_sha256": result["regression_manifest_sha256"],
            "proof_sha256": result["proof_sha256"],
        },
        "spectral_sequence": result["spectral_sequence"],
        "lift_ledger": result["lift_ledger"],
        "open_sectors": result["open_sectors"],
        "checks": {
            "all_nonzero_delta_rows_are_adapted_pairs": "VERIFIED",
            "all_positive_antifield_atoms_covered": "VERIFIED",
            "covariant_pair_tensor_types_match": "VERIFIED",
            "delta_sigma_plus_sigma_delta_equals_pair_Euler": "VERIFIED",
            "contracting_homotopy_regression": "VERIFIED",
            "positive_antifield_lower_forms_absent": "VERIFIED",
            "antifield_spectral_sequence_collapse": "VERIFIED",
            "AFN0_class_lift_ledger": "VERIFIED",
            "pure_Diff_and_mixed_total_complex": "NOT_COMPUTED",
        },
        "claim_flags": {
            "CLASSICAL_ANTIFIELD_EXPORT_IMPORTED": True,
            "MINIMAL_KOSZUL_TATE_POSITIVE_AFN_ACYCLIC": True,
            "H04_AFN0_CLASSES_LIFT_THROUGH_MINIMAL_KT": True,
            "H14_WEYL_AFN0_CLASSES_LIFT_THROUGH_MINIMAL_KT": True,
            "PURE_DIFF_H14_COMPUTED": False,
            "MIXED_DIFF_WEYL_H14_COMPUTED": False,
            "FULL_BV_G2_COMPLETE": False,
            "QME_RESTORED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "AFN0_DIFF_MIXED_TOTAL_COMPLEX_AND_MINIMAL_BV_H14",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC certificate proves the Koszul--Tate part of the minimal-BV "
            "extension. The six imported adapted-coordinate pairs admit an exact covariant "
            "contracting homotopy on the imported regular Bach-locus coordinate chart; every "
            "positive-antifield atom is covered, all such atoms "
            "already saturate horizontal form degree four, and the bounded antifield spectral "
            "sequence has no positive-antifield cohomology. Consequently the certified AFN0 "
            "covariant H04 candidate classes and the certified even/odd Weyl-ghost H14 candidate "
            "classes lift unchanged through the minimal Koszul--Tate sector, while explicit AFN0 "
            "trivializations remain exact. This does not complete the pure-diffeomorphism or "
            "mixed Diff--Weyl top/lower-form ambient quotient, so it does not promote the full "
            "minimal-BV H14 theorem or G2. It computes no anomaly coefficient, Slavnov breaking, "
            "QME restoration, residual quantum transfer, Hadamard state, Lorentzian products, "
            "particle interpretation, or quantum theory."
        ),
        "provenance": {
            "source_sha256": {path: _sha256(ROOT / path) for path in SOURCE_PATHS},
        },
    }


def validate(value: dict[str, Any]) -> None:
    flags = value.get("claim_flags", {})
    if (
        flags.get("MINIMAL_KOSZUL_TATE_POSITIVE_AFN_ACYCLIC") is not True
        or flags.get("H04_AFN0_CLASSES_LIFT_THROUGH_MINIMAL_KT") is not True
        or flags.get("H14_WEYL_AFN0_CLASSES_LIFT_THROUGH_MINIMAL_KT") is not True
        or any(
            flags.get(name) is not False
            for name in (
                "PURE_DIFF_H14_COMPUTED",
                "MIXED_DIFF_WEYL_H14_COMPUTED",
                "FULL_BV_G2_COMPLETE",
                "QME_RESTORED",
                "QUANTUM_CLAIM",
            )
        )
        or value.get("next_gate")
        != "AFN0_DIFF_MIXED_TOTAL_COMPLEX_AND_MINIMAL_BV_H14"
    ):
        raise ValueError("minimal KT collapse crossed its claim boundary")


def _text(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


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
    content = _text(value)
    if args.emit:
        OUTPUT.write_text(content)
    if args.check and OUTPUT.read_text() != content:
        raise SystemExit(f"stale minimal KT collapse certificate: {OUTPUT}")
    print("MINIMAL BV KOSZUL-TATE COLLAPSE: PASS; DIFF/MIXED TOTAL COMPLEX OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
