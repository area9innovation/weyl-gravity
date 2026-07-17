#!/usr/bin/env python3
"""Emit or check the canonical active quantum-frontier certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

try:
    from .active_frontier import HERE, build
except ImportError:
    from active_frontier import HERE, build


OUTPUT = HERE / "certificates/QUANTUM_WEYL_ACTIVE_FRONTIER.json"


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_certificate() -> dict:
    result = build()
    paths = (
        "active_frontier.py",
        "active_frontier_certificate.py",
        "verify_active_frontier.py",
        "schema/active-frontier-v1.schema.json",
        "tests/test_active_frontier.py",
        "reports/active-quantum-frontier.md",
    )
    manifest = {path: _hash(HERE / path) for path in paths}
    result["provenance"] = {
        "source_manifest": manifest,
        "source_manifest_sha256": hashlib.sha256(
            json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(content)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != content):
        raise SystemExit(f"stale active quantum frontier: {OUTPUT}")
    print("QUANTUM WEYL ACTIVE FRONTIER: SLAVNOV ASSEMBLY READY; ANALYTIC MATCH/QME OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
