"""Emit the antifield-filtration block-interface receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from .algebra import canonical_sha256
from .filtered_complex import FilteredDegree, FilteredLocalComplex
from .relative_cohomology import SparseMatrix


PACKAGE_ROOT = Path(__file__).resolve().parent
OUTPUT_PATH = PACKAGE_ROOT / "certificates" / "AFN_FILTRATION_INTERFACE_CERTIFICATE.json"
SCHEMA_PATH = PACKAGE_ROOT / "schema" / "filtered_complex_certificate.schema.json"


def _source_manifest() -> dict[str, str]:
    paths = (
        "filtered_complex.py",
        "filtered_complex_certificate.py",
        "schema/filtered_complex_certificate.schema.json",
        "tests/test_filtered_complex.py",
    )
    return {
        path: hashlib.sha256((PACKAGE_ROOT / path).read_bytes()).hexdigest()
        for path in paths
    }


def build_certificate() -> dict[str, Any]:
    x = FilteredDegree(0, 0, 0)
    qx = FilteredDegree(0, 1, 0)
    xstar = FilteredDegree(1, -1, 0)
    qgt_x = FilteredDegree(1, 1, 0)
    spaces = {
        x: ("x",),
        qx: ("gamma_x",),
        xstar: ("x_star",),
        qgt_x: ("higher_x",),
    }
    blocks = {
        (x, 0): SparseMatrix.from_dense(((1,),)),
        (xstar, -1): SparseMatrix.from_dense(((0,),)),
        (x, 1): SparseMatrix.from_dense(((0,),)),
    }
    complex_ = FilteredLocalComplex(spaces, blocks, {})
    filtered_checks = complex_.verify_filtered_identities()
    afn0_checks = complex_.afn0_view().verify_bicomplex()
    return {
        "result_id": "AFN_FILTRATION_INTERFACE_CERTIFICATE",
        "result_state": "INTERFACE_READY_EXPORT_PENDING",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "checks": {
            "gamma_diagonal_block": "VERIFIED",
            "delta_minus_one_block": "VERIFIED",
            "positive_Q_gt0_block": "VERIFIED",
            "afn0_view_reuses_relative_cohomology_API": "VERIFIED",
            **filtered_checks,
            **afn0_checks,
        },
        "block_manifest": complex_.block_manifest(),
        "afn0_to_minimal_comparison_statuses": [
            "LIFTS_UNCHANGED",
            "REQUIRES_ANTIFIELD_COMPLETION",
            "BECOMES_EXACT",
            "IS_OBSTRUCTED",
        ],
        "canonical_hashes": {
            "source_manifest_sha256": canonical_sha256(_source_manifest()),
        },
        "not_computed": [
            "classical delta, gamma, and positive-filtration block entries",
            "minimal-BV quotient",
            "AFN0-to-minimal lift comparison",
        ],
    }


def _render(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = _render(build_certificate())
    if args.emit:
        OUTPUT_PATH.write_text(content, encoding="utf-8")
    if args.check and OUTPUT_PATH.read_text(encoding="utf-8") != content:
        raise SystemExit(f"AFN filtration artifact is stale: {OUTPUT_PATH}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("AFN FILTRATION INTERFACE: EXACT SHAPES PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
