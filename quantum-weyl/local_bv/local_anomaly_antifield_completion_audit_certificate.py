#!/usr/bin/env python3
"""Emit or check the local anomaly antifield-completion audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

try:
    from .local_anomaly_antifield_completion_audit import evaluate
except ImportError:
    from local_anomaly_antifield_completion_audit import evaluate


HERE = Path(__file__).resolve().parent
OUTPUT = (
    HERE / "certificates/LOCAL_ANOMALY_ANTIFIELD_COMPLETION_AUDIT.json"
)
SOURCE_PATHS = (
    "local_anomaly_antifield_completion_audit.py",
    "local_anomaly_antifield_completion_audit_certificate.py",
    "verify_local_anomaly_antifield_completion_audit.py",
    "schema/local-anomaly-antifield-completion-audit-v1.schema.json",
    "tests/test_local_anomaly_antifield_completion_audit.py",
    "../reports/local-anomaly-antifield-completion-audit.md",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    value = evaluate()
    manifest = {path: _sha256(HERE / path) for path in SOURCE_PATHS}
    value["provenance"] = {
        "proof_type": "INDEPENDENT_EXACT_MULTI_ARTIFACT_COMPLETION_AUDIT",
        "source_manifest": manifest,
        "source_manifest_sha256": hashlib.sha256(
            json.dumps(
                manifest, sort_keys=True, separators=(",", ":")
            ).encode()
        ).hexdigest(),
    }
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(content, encoding="utf-8")
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != content):
        raise SystemExit(f"stale completion audit: {OUTPUT}")
    print("LOCAL ANOMALY ANTIFIELD COMPLETION AUDIT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
