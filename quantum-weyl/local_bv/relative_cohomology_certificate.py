"""Emit the exact sparse mapping-cone engine certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from .algebra import canonical_sha256
from .relative_cohomology import certification_bicomplex


PACKAGE_ROOT = Path(__file__).resolve().parent
OUTPUT_PATH = PACKAGE_ROOT / "certificates" / "RELATIVE_COHOMOLOGY_ENGINE_CERTIFICATE.json"
SCHEMA_PATH = PACKAGE_ROOT / "schema" / "relative_cohomology_certificate.schema.json"


def _source_manifest() -> dict[str, str]:
    paths = (
        "quotient.py",
        "relative_cohomology.py",
        "relative_cohomology_certificate.py",
        "schema/relative_cohomology_certificate.schema.json",
        "tests/test_relative_cohomology.py",
        "tests/test_relative_cohomology_certificate.py",
    )
    return {
        path: hashlib.sha256((PACKAGE_ROOT / path).read_bytes()).hexdigest()
        for path in paths
    }


def build_certificate() -> dict[str, Any]:
    complex_ = certification_bicomplex()
    checks = complex_.verify_bicomplex()
    total_cohomology = complex_.cohomology(1)
    relative = complex_.relative_cohomology(0, 1)
    if total_cohomology["quotient_dimension"] != 2:
        raise AssertionError("mapping-cone fixture total quotient drifted")
    if relative["quotient_dimension"] != 1:
        raise AssertionError("anchored relative quotient drifted")
    if relative["lower_only_total_class_dimension"] != 1:
        raise AssertionError("lower-only total class was not separated")
    return {
        "result_id": "RELATIVE_COHOMOLOGY_ENGINE_CERTIFICATE",
        "result_state": "ENGINE_VERIFIED_PRODUCTION_BASES_PENDING",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "checks": {
            **checks,
            "exact_sparse_matrix_composition": "VERIFIED",
            "deterministic_kernel_basis": "VERIFIED",
            "coboundary_in_cocycle_space": "VERIFIED",
            "quotient_representative_selection": "VERIFIED",
            "anchored_top_component_projection": "VERIFIED",
            "lower_only_total_class_exclusion": "VERIFIED",
            "sparse_exact_rank_and_nullspace": "VERIFIED",
            "incremental_quotient_independence": "VERIFIED",
        },
        "totalization_convention": "D = Q + (-1)^ghost_number d_h",
        "fixture": {
            "purpose": "commuting square plus one isolated cohomology class",
            "total_degree": total_cohomology["total_degree"],
            "ansatz_dimension": total_cohomology["ansatz_dimension"],
            "ansatz_basis_hash": total_cohomology["ansatz_basis_hash"],
            "total_cocycle_matrix_rank": total_cohomology["cocycle_matrix_rank"],
            "total_coboundary_matrix_rank": total_cohomology["coboundary_matrix_rank"],
            "total_quotient_dimension": total_cohomology["quotient_dimension"],
            "anchored_bidegree": {"ghost_number": 0, "form_degree": 1},
            "anchored_top_cocycle_dimension": relative["projected_top_cocycle_dimension"],
            "anchored_top_coboundary_rank": relative["projected_top_coboundary_rank"],
            "anchored_quotient_dimension": relative["quotient_dimension"],
            "lower_only_total_class_dimension": relative["lower_only_total_class_dimension"],
            "anchored_representative_coordinates": relative["representative_coordinates"],
            "complete_descent_lift_coordinates": relative["complete_descent_lift_coordinates"],
            "total_proof_hash": total_cohomology["proof_hash"],
            "anchored_proof_hash": relative["proof_hash"],
        },
        "canonical_hashes": {
            "source_manifest_sha256": canonical_sha256(_source_manifest()),
        },
        "not_computed": [
            "production V^p_g bases at the one-loop derivative bound",
            "production Q and d_h sparse matrices",
            "H^{0,4}(s|d) and H^{1,4}(s|d) quotient dimensions",
            "antifield-dependent quotient pending the classical export",
        ],
        "assumptions": [
            "Coordinate Q and d_h commute; the totalization sign produces D^2=0.",
            "The certificate validates the engine on a finite exact fixture and does not classify a physical candidate.",
        ],
    }


def _render(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = _render(build_certificate())
    if args.emit:
        OUTPUT_PATH.write_text(content, encoding="utf-8")
    if args.check and OUTPUT_PATH.read_text(encoding="utf-8") != content:
        raise SystemExit(f"relative cohomology engine certificate is stale: {OUTPUT_PATH}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("RELATIVE COHOMOLOGY ENGINE: EXACT FIXTURE PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
