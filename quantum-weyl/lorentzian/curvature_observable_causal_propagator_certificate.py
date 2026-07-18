#!/usr/bin/env python3
"""Emit or check the curvature observable causal-propagator certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .curvature_observable_causal_propagator import evaluate


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "certificates/CURVATURE_OBSERVABLE_CAUSAL_PROPAGATOR.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_certificate() -> dict[str, object]:
    result = evaluate().copy()
    paths = (
        "curvature_observable_causal_propagator.py",
        "curvature_observable_causal_propagator_certificate.py",
        "verify_curvature_observable_causal_propagator.py",
        "schema/curvature-observable-causal-propagator-v1.schema.json",
        "tests/test_curvature_observable_causal_propagator.py",
        "../reports/curvature-observable-causal-propagator.md",
    )
    manifest = {path: _sha256(HERE / path) for path in paths}
    result["provenance"] = {
        **result["provenance"],
        "source_manifest": manifest,
        "source_manifest_sha256": hashlib.sha256(
            json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    result = build_certificate()
    if args.emit:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(f"wrote {OUTPUT}")
        return 0
    if not OUTPUT.exists() or json.loads(OUTPUT.read_text()) != result:
        raise SystemExit(f"stale curvature observable propagator: {OUTPUT}")
    print("CURVATURE OBSERVABLE CAUSAL PROPAGATOR certificate: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
