"""Extend the exact 27-node shortfall artifact to the canonical 30 nodes.

The first 27 matrices remain valid literal-action evaluations even though they
were insufficient for interpolation uniqueness.  This producer verifies their
content hashes and input hashes byte-for-byte, derives the three missing
matrices, and emits the same artifact that a full ``produce_samples`` run
would emit.  The independent exhaustive replay still re-derives all 30 nodes.
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import sympy as sp

from black_hole_programme.phase3.axial_arbitrary_radius_current_conservation.produce_samples import (
    INPUTS,
    OUTPUT,
    RECEIPT,
    ROOT,
    matrix_hash,
    matrix_rows,
    sha256,
)
from black_hole_programme.phase3.axial_null_infinity_trace_preflight.current_dag import (
    derive_rational_radius_current,
)


HERE = Path(__file__).resolve().parent
PREFIX = HERE / "literal-samples-27-superseded.json"
EXPECTED_PREFIX_SHA256 = (
    "1e5a4167f5c182243d3a61f645d92fa6e52cfce8f67d0ec62c96386d3c65c56e"
)


def main() -> None:
    started = time.monotonic()
    if sha256(PREFIX) != EXPECTED_PREFIX_SHA256:
        raise SystemExit("27-node prefix artifact drift")
    prefix = json.loads(PREFIX.read_text())
    if prefix["radii"] != list(range(3, 30)) or len(prefix["samples"]) != 27:
        raise SystemExit("27-node prefix radius set drift")
    for name, item in prefix["imports"].items():
        if name not in INPUTS or item["path"] != INPUTS[name]:
            raise SystemExit(f"27-node prefix import set drift: {name}")
        if sha256(ROOT / item["path"]) != item["sha256"]:
            raise SystemExit(f"27-node prefix input drift: {item['path']}")
    for sample in prefix["samples"]:
        if matrix_hash(sample["matrix_without_pi_alpha"]) != sample["matrix_sha256"]:
            raise SystemExit(f"27-node prefix matrix hash drift at r={sample['radius']}")

    samples = list(prefix["samples"])
    for radius in range(30, 33):
        node_started = time.monotonic()
        rows = matrix_rows(derive_rational_radius_current(sp.Integer(radius)))
        samples.append({
            "radius": radius,
            "matrix_without_pi_alpha": rows,
            "matrix_sha256": matrix_hash(rows),
        })
        print(
            f"literal tail sample r={radius} "
            f"{time.monotonic() - node_started:.3f}s",
            flush=True,
        )
    document = {
        "schema": "phase3-black-hole-axial-literal-current-rational-samples-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "ring": "QQ(I)(omega)",
        "radii": list(range(3, 33)),
        "samples": samples,
        "imports": {
            name: {"path": path, "sha256": sha256(ROOT / path)}
            for name, path in INPUTS.items()
        },
        "status": "EXACT_LITERAL_ACTION_EVALUATIONS",
    }
    OUTPUT.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    elapsed = time.monotonic() - started
    receipt = {
        "schema": "phase3-black-hole-axial-literal-current-rational-samples-receipt-v1",
        "artifact": str(OUTPUT.relative_to(ROOT)),
        "artifact_sha256": sha256(OUTPUT),
        "producer": str(Path(__file__).relative_to(ROOT)),
        "producer_sha256": sha256(Path(__file__)),
        "command": "python3 -m black_hole_programme.phase3.axial_arbitrary_radius_current_conservation.extend_samples",
        "elapsed_seconds": round(elapsed, 3),
        "sample_count": 30,
        "reused_exact_prefix": {
            "path": str(PREFIX.relative_to(ROOT)),
            "sha256": EXPECTED_PREFIX_SHA256,
            "verified_sample_count": 27,
        },
        "new_exact_tail_radii": [30, 31, 32],
        "full_independent_replay_required": True,
        "status": "PASS",
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUTPUT} in {elapsed:.3f}s")


if __name__ == "__main__":
    main()
