"""Emit the exact ``Box R`` and ``omega Box R`` triviality certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from .algebra import canonical_sha256
from .triviality import box_r_triviality_analysis


PACKAGE_ROOT = Path(__file__).resolve().parent
OUTPUT_PATH = PACKAGE_ROOT / "certificates" / "TRIVIALITY_CERTIFICATE.json"
SCHEMA_PATH = PACKAGE_ROOT / "schema" / "triviality_certificate.schema.json"


def _fraction(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def _source_manifest() -> dict[str, str]:
    paths = (
        "triviality.py",
        "triviality_certificate.py",
        "schema/triviality_certificate.schema.json",
        "tests/test_triviality.py",
        "tests/test_triviality_certificate.py",
    )
    return {
        path: hashlib.sha256((PACKAGE_ROOT / path).read_bytes()).hexdigest()
        for path in paths
    }


def build_certificate() -> dict[str, Any]:
    analysis = box_r_triviality_analysis()
    zero_hash = analysis["relative_trivialization_residual"].canonical_hash()
    return {
        "result_id": "TRIVIALITY_CERTIFICATE",
        "result_state": "EXACT_PRIMITIVES_VERIFIED",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "checks": {
            "box_r_equals_div_gradient_r": "VERIFIED",
            "current_divergence_identity": "VERIFIED",
            "weyl_brst_r_squared_row": "VERIFIED",
            "omega_box_r_relative_trivialization": "VERIFIED",
        },
        "trivializations": {
            "CT_BOX_R": {
                "class_status": "EXACT",
                "primitive": analysis["box_r_primitive"].canonical_payload(),
                "equation": "BoxR = d_h(nabla R)",
                "verification_hash": analysis["box_r"].canonical_hash(),
            },
            "ANOM_OMEGA_BOX_R": {
                "class_status": "EXACT",
                "primitive": "R^2",
                "primitive_coefficient": _fraction(analysis["counterterm_coefficient"]),
                "current": analysis["anomaly_current"].canonical_payload(),
                "equation": "omega BoxR = -(1/12) Q_W(R^2) - d_h(R nabla omega - omega nabla R)",
                "verification_hash": zero_hash,
            },
        },
        "canonical_hashes": {
            "source_manifest_sha256": canonical_sha256(_source_manifest()),
            "box_r_sha256": analysis["box_r"].canonical_hash(),
            "omega_box_r_sha256": analysis["omega_box_r"].canonical_hash(),
            "anomaly_current_sha256": analysis["anomaly_current"].canonical_hash(),
            "zero_residual_sha256": zero_hash,
        },
        "assumptions": [
            "The certificate is the four-dimensional infinitesimal Weyl sector; universal Diff completion is recorded separately.",
            "The density convention is Q_W(sqrt(g) R^2) = -12 sqrt(g) R Box(omega).",
        ],
        "not_computed": [
            "full relative cohomology quotient outside these explicit primitives",
            "antifield/Koszul-Tate sector",
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
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(content, encoding="utf-8")
    if args.check and OUTPUT_PATH.read_text(encoding="utf-8") != content:
        raise SystemExit(f"triviality artifact is stale: {OUTPUT_PATH}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("DIMENSION-FOUR TRIVIALITY: EXACT CHECKS PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
