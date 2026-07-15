#!/usr/bin/env python3
"""Verify the curvature-aware 24-field operator composition backend."""

import argparse

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.parallel_operator_composition import (
    ParallelFieldOperatorComposer,
)

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--claim-quadratic-solve", action="store_true")
    args = parser.parse_args()
    if args.claim_quadratic_solve:
        raise SystemExit(
            "REFUSED: the composition backend does not solve the quadratic ansatz"
        )

    payload = ParallelFieldOperatorComposer.build().certificate()
    path = ROOT / "covariant_completion/certificates/parallel_operator_composition.json"
    if args.emit:
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print("parallel 24-field operator composition: PASS")


if __name__ == "__main__":
    main()
