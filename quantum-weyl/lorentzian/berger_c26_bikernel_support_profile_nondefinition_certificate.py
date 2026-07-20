#!/usr/bin/env python3
"""Emit or check the retained C26 support-profile non-definition."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

try:
    from .berger_c26_bikernel_support_profile_nondefinition import evaluate
except ImportError:
    from berger_c26_bikernel_support_profile_nondefinition import evaluate


HERE = Path(__file__).resolve().parent
OUTPUT = (
    HERE
    / "certificates/BERGER_C26_BIKERNEL_SUPPORT_PROFILE_NONDEFINITION.json"
)
SOURCE_PATHS = (
    "berger_c26_bikernel_support_profile_nondefinition.py",
    "berger_c26_bikernel_support_profile_nondefinition_certificate.py",
    "verify_berger_c26_bikernel_support_profile_nondefinition.py",
    "schema/berger-c26-bikernel-support-profile-nondefinition-v1.schema.json",
    "tests/test_berger_c26_bikernel_support_profile_nondefinition.py",
    "../reports/berger-c26-bikernel-support-profile-nondefinition.md",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    value = evaluate()
    manifest = {path: _sha256(HERE / path) for path in SOURCE_PATHS}
    value["provenance"] = {
        "proof_type": (
            "PINNED_EXPORT_AUDIT_WITH_INDEPENDENT_NONDEFINITION_REPLAY"
        ),
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
        raise SystemExit(f"stale C26 support certificate: {OUTPUT}")
    print("BERGER C26 BIKERNEL SUPPORT PROFILE NONDEFINITION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
