#!/usr/bin/env python3
"""Record hashes for the rendered certificate-graph publication artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "certificate-graph-render-receipt.json"
ARTIFACTS = (
    "certificate-dag.dot",
    "certificate-dag.svg",
    "universe-building-dag.dot",
    "universe-building-dag.svg",
    "universe-building-dag.pdf",
    "universe-building-dag.png",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_receipt() -> dict[str, object]:
    missing = [name for name in ARTIFACTS if not (ROOT / name).is_file()]
    if missing:
        raise SystemExit("missing render artifacts: " + ", ".join(missing))
    return {
        "schema_version": "certificate-graph-render-receipt-v1",
        "claim_scope": "PRESENTATION-ONLY",
        "authoritative_inputs": [
            "certificate-dag.dot",
            "universe-building-dag.dot",
        ],
        "renderer": {
            "graphviz": "15.0.0",
            "interface": "@viz-js/viz 3.28.0",
            "pdf_conversion": "ps2pdf -dEPSCrop",
            "png_conversion": "pdftocairo -png -singlefile -r 120",
        },
        "artifacts": {
            name: {
                "sha256": sha256(ROOT / name),
                "bytes": (ROOT / name).stat().st_size,
            }
            for name in ARTIFACTS
        },
        "claim_boundary": (
            "Rendered files are publication views. The JSON/DOT graph and "
            "underlying certificates determine all scientific content."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    receipt = build_receipt()
    encoded = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != encoded:
            print("CERTIFICATE GRAPH RENDERS: FAIL (receipt is stale)")
            return 1
        print(f"CERTIFICATE GRAPH RENDERS: PASS artifacts={len(ARTIFACTS)}")
        return 0
    OUTPUT.write_text(encoded, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT.parent)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
