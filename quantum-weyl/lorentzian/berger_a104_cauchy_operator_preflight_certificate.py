#!/usr/bin/env python3
"""Emit or check the Berger A104 Cauchy-operator preflight."""

from __future__ import annotations

import argparse
import hashlib
import json

from .berger_a104_cauchy_operator_preflight import GENERATED, build


HERE = GENERATED.parent.parent
OUTPUT = HERE / "certificates/BERGER_A104_CAUCHY_OPERATOR_PREFLIGHT.json"


def _sha256(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _text(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def build_certificate() -> tuple[dict, dict[str, dict]]:
    result, artifacts = build()
    result = result.copy()
    sources = (
        "berger_a104_cauchy_operator_preflight.py",
        "berger_a104_cauchy_operator_preflight_certificate.py",
        "verify_berger_a104_cauchy_operator_preflight.py",
        "schema/berger-a104-cauchy-operator-preflight-v1.schema.json",
        "tests/test_berger_a104_cauchy_operator_preflight.py",
        "../reports/berger-a104-cauchy-operator-preflight.md",
        "metric_lower_by_two_biwave_import.py",
        "../transfer/berger_gauge_fixed_nonminimal_import.py",
        "../transfer/berger_retained_q1_import.py",
    )
    manifest = {path: _sha256(HERE / path) for path in sources}
    result["provenance"] = {
        **result["provenance"],
        "source_manifest": manifest,
        "source_manifest_sha256": hashlib.sha256(
            json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
    }
    return result, artifacts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result, artifacts = build_certificate()
    if args.emit:
        GENERATED.mkdir(parents=True, exist_ok=True)
        for name, payload in artifacts.items():
            (GENERATED / f"{name}.json").write_text(_text(payload))
        OUTPUT.write_text(_text(result))
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text() != _text(result):
            raise SystemExit(f"stale A104 Cauchy preflight: {OUTPUT}")
        for name, payload in artifacts.items():
            path = GENERATED / f"{name}.json"
            if not path.exists() or path.read_text() != _text(payload):
                raise SystemExit(f"stale A104 exact operator artifact: {name}")
    print("BERGER A104 CAUCHY PREFLIGHT: METRIC A80 EXACT, ENDPOINT A24 OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
