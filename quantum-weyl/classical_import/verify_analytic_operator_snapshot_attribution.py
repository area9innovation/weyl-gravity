"""Independent verifier for analytic-producer classical-snapshot attribution."""

from __future__ import annotations

import hashlib
import json

from .analytic_operator_snapshot_attribution import OUTPUT, ROOT, build, validate_attribution


def verify() -> dict:
    checked = json.loads(OUTPUT.read_text())
    validate_attribution(checked)
    if checked != build():
        raise ValueError("analytic snapshot attribution does not reproduce")
    for path, digest in checked["provenance"]["source_sha256"].items():
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != digest:
            raise ValueError(f"analytic snapshot attribution source drifted: {path}")
    return checked


if __name__ == "__main__":
    verify()
    print("independent analytic snapshot attribution verifier: PASS")
