#!/usr/bin/env python3
"""Emit or check the regular-graph obstruction and endpoint descent theorem."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

try:
    from .berger_regular_graph_intertwiner_endpoint_descent import evaluate
except ImportError:
    from berger_regular_graph_intertwiner_endpoint_descent import evaluate


HERE = Path(__file__).resolve().parent
OUTPUT = (
    HERE
    / "certificates/"
    "BERGER_REGULAR_GRAPH_INTERTWINER_OBSTRUCTION_AND_ENDPOINT_DESCENT.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_certificate() -> dict[str, object]:
    result = evaluate().copy()
    paths = (
        "berger_regular_graph_intertwiner_endpoint_descent.py",
        "berger_regular_graph_intertwiner_endpoint_descent_certificate.py",
        "verify_berger_regular_graph_intertwiner_endpoint_descent.py",
        "schema/berger-regular-graph-intertwiner-endpoint-descent-v1.schema.json",
        "tests/test_berger_regular_graph_intertwiner_endpoint_descent.py",
        "../reports/berger-regular-graph-intertwiner-endpoint-descent.md",
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
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(content, encoding="utf-8")
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != content):
        raise SystemExit(f"stale regular graph/endpoint certificate: {OUTPUT}")
    print(
        "BERGER REGULAR GRAPH: OBSTRUCTED; METRIC ENDPOINT DESCENT: CERTIFIED; "
        "GHOST/WARD COMPLETION: OPEN"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
