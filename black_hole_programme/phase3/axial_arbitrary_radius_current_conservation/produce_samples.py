"""Freeze the 26 exact literal-action current samples used for interpolation."""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import sympy as sp

from black_hole_programme.phase3.axial_null_infinity_trace_preflight.current_dag import (
    derive_rational_radius_current,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "literal-samples.json"
RECEIPT = HERE / "literal-samples-receipt.json"
RADII = range(3, 33)
INPUTS = {
    "literal_action_current": "black_hole_programme/certificates/BH2A_FLUX_MATRIX.json",
    "repaired_system": "black_hole_programme/phase3/axial_complete_reconstruction_repair/certificate.json",
    "literal_current_dag": "black_hole_programme/phase3/axial_null_infinity_trace_preflight/current_dag.py",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def matrix_rows(matrix: sp.Matrix) -> list[list[str]]:
    return [[sp.sstr(sp.cancel(matrix[i, j])) for j in range(6)]
            for i in range(6)]


def matrix_hash(rows: list[list[str]]) -> str:
    payload = json.dumps(rows, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def build_document() -> dict:
    samples = []
    for index, radius in enumerate(RADII, start=1):
        started = time.monotonic()
        rows = matrix_rows(derive_rational_radius_current(sp.Integer(radius)))
        samples.append({
            "radius": radius,
            "matrix_without_pi_alpha": rows,
            "matrix_sha256": matrix_hash(rows),
        })
        print(
            f"literal sample r={radius} ({index}/30) "
            f"{time.monotonic() - started:.3f}s",
            flush=True,
        )
    return {
        "schema": "phase3-black-hole-axial-literal-current-rational-samples-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "ring": "QQ(I)(omega)",
        "radii": list(RADII),
        "samples": samples,
        "imports": {
            name: {"path": path, "sha256": sha256(ROOT / path)}
            for name, path in INPUTS.items()
        },
        "status": "EXACT_LITERAL_ACTION_EVALUATIONS",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    started = time.monotonic()
    document = build_document()
    elapsed = time.monotonic() - started
    if args.check:
        if document != json.loads(OUTPUT.read_text()):
            raise SystemExit("literal sample artifact drift")
        print(f"PASS: literal samples reproduced in {elapsed:.3f}s")
        return
    OUTPUT.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    receipt = {
        "schema": "phase3-black-hole-axial-literal-current-rational-samples-receipt-v1",
        "artifact": str(OUTPUT.relative_to(ROOT)),
        "artifact_sha256": sha256(OUTPUT),
        "producer": str(Path(__file__).relative_to(ROOT)),
        "producer_sha256": sha256(Path(__file__)),
        "command": "python3 -m black_hole_programme.phase3.axial_arbitrary_radius_current_conservation.produce_samples",
        "elapsed_seconds": round(elapsed, 3),
        "sample_count": 30,
        "status": "PASS",
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUTPUT} in {elapsed:.3f}s")


if __name__ == "__main__":
    main()
