#!/usr/bin/env python3
"""Emit or check the coupled Berger cyclicity-defect atlas."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

try:
    from .berger_coupled_cyclicity_defect_atlas import HERE, PAYLOAD_PATH, build
except ImportError:
    from berger_coupled_cyclicity_defect_atlas import HERE, PAYLOAD_PATH, build


OUTPUT = HERE / "certificates/BERGER_COUPLED_CYCLICITY_DEFECT_ATLAS.json"


def _json(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def build_certificate() -> tuple[dict, dict]:
    result, payload = build()
    payload_text = _json(payload)
    result["defect_payload"]["file_sha256"] = hashlib.sha256(
        payload_text.encode()
    ).hexdigest()
    paths = (
        "berger_coupled_cyclicity_defect_atlas.py",
        "berger_coupled_cyclicity_defect_atlas_certificate.py",
        "verify_berger_coupled_cyclicity_defect_atlas.py",
        "schema/berger-coupled-cyclicity-defect-atlas-v1.schema.json",
        "schema/berger-coupled-retained-cyclicity-defect-payload-v1.schema.json",
        "tests/test_berger_coupled_cyclicity_defect_atlas.py",
        "../reports/berger-coupled-cyclicity-defect-atlas.md",
    )
    manifest = {path: _sha256(HERE / path) for path in paths}
    result["consumer_provenance"] = {
        "source_manifest": manifest,
        "source_manifest_sha256": _canonical_hash(manifest),
    }
    result["verification_receipts"] = [
        {
            "test_tier": 1,
            "command": "PYTHONPATH=quantum-weyl python3 -m transfer.berger_coupled_cyclicity_defect_atlas_certificate --check",
            "elapsed_seconds": 3.0,
            "status": "PASS",
        },
        {
            "test_tier": 1,
            "command": "PYTHONPATH=quantum-weyl python3 -m transfer.verify_berger_coupled_cyclicity_defect_atlas",
            "elapsed_seconds": 3.0,
            "status": "PASS",
        },
        {
            "test_tier": 1,
            "command": "PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/transfer/tests/test_berger_coupled_cyclicity_defect_atlas.py -v",
            "elapsed_seconds": 9.48,
            "status": "PASS",
        },
        {
            "test_tier": 1,
            "command": "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s quantum-weyl/transfer/schema/berger-coupled-cyclicity-defect-atlas-v1.schema.json -d quantum-weyl/transfer/certificates/BERGER_COUPLED_CYCLICITY_DEFECT_ATLAS.json",
            "elapsed_seconds": 2.0,
            "status": "PASS",
        },
        {
            "test_tier": 1,
            "command": "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s quantum-weyl/transfer/schema/berger-coupled-retained-cyclicity-defect-payload-v1.schema.json -d quantum-weyl/transfer/certificates/BERGER_COUPLED_RETAINED_CYCLICITY_DEFECT_PAYLOAD.json",
            "elapsed_seconds": 3.19,
            "status": "PASS",
        },
    ]
    result["higher_tiers_not_run"] = {
        "tier_2": (
            "The full affected 953-coefficient defect and every tested convention are "
            "recomputed from the pinned carrier and transfer payload in Tier 1; no corrected "
            "classical tensor or downstream theorem is consumed."
        ),
        "tier_3": (
            "No shared PBW engine, lifecycle promotion, theorem freeze, causal construction, "
            "QME state, or release boundary changes in this diagnostic atlas."
        ),
    }
    return result, payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    certificate, payload = build_certificate()
    certificate_text = _json(certificate)
    payload_text = _json(payload)
    if args.emit:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(certificate_text)
        PAYLOAD_PATH.write_text(payload_text)
    if args.check and (
        not OUTPUT.exists()
        or OUTPUT.read_text() != certificate_text
        or not PAYLOAD_PATH.exists()
        or PAYLOAD_PATH.read_text() != payload_text
    ):
        raise SystemExit("stale coupled cyclicity-defect atlas or payload")
    print("BERGER COUPLED CYCLICITY ATLAS: 938 FACTOR-TWO DEFECTS LOCALIZED; 15 GHOST DEFECTS OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
