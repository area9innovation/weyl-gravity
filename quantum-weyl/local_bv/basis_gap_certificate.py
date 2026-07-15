"""Emit the fail-closed AFN0 basis-gap report."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from .algebra import canonical_sha256
from .basis_gap import basis_gap_graph_bundle, basis_gap_report


PACKAGE_ROOT = Path(__file__).resolve().parent
OUTPUT_PATH = PACKAGE_ROOT / "certificates" / "BASIS_GAP_REPORT_AFN0.json"
SCHEMA_PATH = PACKAGE_ROOT / "schema" / "basis_gap_report_afn0.schema.json"
GRAPH_BUNDLE_DIR = PACKAGE_ROOT / "certificates" / "basis_graph_manifests"
GRAPH_BUNDLE_SCHEMA_PATH = PACKAGE_ROOT / "schema" / "basis_graph_bundle.schema.json"


def _source_manifest() -> dict[str, str]:
    paths = (
        "basis_exhaustiveness.py",
        "basis_gap.py",
        "basis_gap_certificate.py",
        "ambient_tensor_graphs.py",
        "ambient_tensor_graph_certificate.py",
        "lower_form_basis.py",
        "lower_form_basis_certificate.py",
        "lower_form_ambient.py",
        "lower_form_ambient_certificate.py",
        "tensor_graphs.py",
        "schema/afn0_lower_form_carrier_precertificate.schema.json",
        "schema/afn0_ambient_lower_form_signature.schema.json",
        "schema/afn0_ambient_tensor_graph_realization.schema.json",
        "schema/afn0_ambient_tensor_graph_bundle.schema.json",
        "schema/basis_gap_report_afn0.schema.json",
        "schema/basis_graph_bundle.schema.json",
        "tests/test_basis_exhaustiveness.py",
        "tests/test_basis_gap.py",
        "tests/test_lower_form_basis.py",
        "tests/test_lower_form_ambient.py",
        "tests/test_ambient_tensor_graphs.py",
        "tests/test_tensor_graphs.py",
    )
    return {
        path: hashlib.sha256((PACKAGE_ROOT / path).read_bytes()).hexdigest()
        for path in paths
    }


def build_certificate() -> dict[str, Any]:
    report = basis_gap_report()
    source_manifest = _source_manifest()
    payload = {
        **report,
        "canonical_hashes": {
            "source_manifest_sha256": canonical_sha256(source_manifest),
            "report_payload_sha256": report["report_hash"],
        },
    }
    return {**payload, "certificate_hash": canonical_sha256(payload)}


def _render(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    certificate = build_certificate()
    bundle = basis_gap_graph_bundle()
    bundle_path = GRAPH_BUNDLE_DIR / f"{bundle['bundle_hash']}.json"
    outputs = {
        OUTPUT_PATH: _render(certificate),
        bundle_path: _render(bundle),
    }
    if args.emit:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    if args.check:
        for path, content in outputs.items():
            if path.read_text(encoding="utf-8") != content:
                raise SystemExit(f"AFN0 basis-gap artifact is stale: {path}")
    if not args.emit and not args.check:
        print(outputs[OUTPUT_PATH], end="")
    else:
        print("AFN0 BASIS GAP: FAIL-CLOSED REPORT VERIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
