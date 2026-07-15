"""Emit fail-closed Sprint 1 antifield-zero production receipts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from .afn0_production import afn0_production_results
from .algebra import canonical_sha256


PACKAGE_ROOT = Path(__file__).resolve().parent
RESULT_DIR = PACKAGE_ROOT / "cohomology"
CERTIFICATE_PATH = PACKAGE_ROOT / "certificates" / "AFN0_PRODUCTION_RUN_CERTIFICATE.json"
SCHEMA_PATH = PACKAGE_ROOT / "schema" / "afn0_result.schema.json"


def _source_manifest() -> dict[str, str]:
    paths = (
        "afn0_production.py",
        "afn0_production_certificate.py",
        "schema/afn0_result.schema.json",
        "tests/test_afn0_production.py",
    )
    return {
        path: hashlib.sha256((PACKAGE_ROOT / path).read_bytes()).hexdigest()
        for path in paths
    }


def build_certificate() -> dict[str, Any]:
    results = afn0_production_results()
    h04 = results["H04_AFN0_RESULT"]
    h14 = results["H14_AFN0_RESULT"]
    exact_ids = {
        candidate["representative_id"]
        for result in results.values()
        for slice_ in result["slices"]
        for candidate in slice_["candidates"]
        if candidate["relative_cohomology_status"] == "EXACT"
    }
    if exact_ids != {"CT_BOX_R", "ANOM_OMEGA_BOX_R"}:
        raise AssertionError("AFN0 known-exact ledger drifted")
    if any(
        candidate["nontriviality_witness"] is not None
        for result in results.values()
        for slice_ in result["slices"]
        for candidate in slice_["candidates"]
    ):
        raise AssertionError("incomplete AFN0 run promoted a nontriviality witness")
    return {
        "result_id": "AFN0_PRODUCTION_RUN_CERTIFICATE",
        "result_state": "SPRINT_1_IN_PROGRESS",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope_label": "AFN0_ONLY",
        "checks": {
            "H04_AFN0_EVEN_started": "VERIFIED",
            "H04_AFN0_ODD_started": "VERIFIED",
            "H14_AFN0_EVEN_WITHOUT_EULER_started": "VERIFIED",
            "H14_AFN0_ODD_started": "VERIFIED",
            "top_curvature_carrier_generation": "VERIFIED",
            "parity_split": "VERIFIED",
            "BoxR_explicit_primitive": "VERIFIED",
            "omega_BoxR_explicit_primitive": "VERIFIED",
            "premature_nontriviality_promotion_absent": "VERIFIED",
            "complete_lower_form_basis": "IN_PROGRESS",
            "Euler_intrinsic_tower": "IN_PROGRESS",
        },
        "result_hashes": {
            "H04_AFN0_RESULT": canonical_sha256(h04),
            "H14_AFN0_RESULT": canonical_sha256(h14),
        },
        "canonical_hashes": {
            "source_manifest_sha256": canonical_sha256(_source_manifest()),
        },
        "next_required_computation": [
            "generate all lower-form ghost and generalized-connection monomials at total engineering dimension four",
            "assemble the production Q and d_h sparse matrices",
            "complete the omega-Euler intrinsic tower",
            "emit dual nontriviality witnesses only after the complete boundary rank is frozen",
        ],
    }


def _render(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    results = afn0_production_results()
    outputs = {
        RESULT_DIR / f"{result_id}.json": _render(result)
        for result_id, result in results.items()
    }
    outputs[CERTIFICATE_PATH] = _render(build_certificate())
    if args.emit:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    if args.check:
        for path, content in outputs.items():
            if path.read_text(encoding="utf-8") != content:
                raise SystemExit(f"AFN0 production artifact is stale: {path}")
    if not args.emit and not args.check:
        print(outputs[CERTIFICATE_PATH], end="")
    else:
        print("AFN0 PRODUCTION: SPRINT 1 RECEIPTS VERIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
