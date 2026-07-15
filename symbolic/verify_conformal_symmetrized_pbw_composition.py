#!/usr/bin/env python3
"""Verify the exact symmetrized covariant-jet/PBW composition quotient."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.symmetrized_pbw_composition import (
    SymmetrizedPBWComposer,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--claim-quadratic-solve", action="store_true")
    args = parser.parse_args()
    if args.claim_quadratic_solve:
        raise SystemExit(
            "REFUSED: the PBW backend is exact, but no quadratic factor solve "
            "has been supplied"
        )

    payload = SymmetrizedPBWComposer.build().certificate()
    path = (
        ROOT
        / "covariant_completion/certificates/symmetrized_pbw_composition.json"
    )
    if args.emit:
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print("symmetrized covariant-jet/PBW composition: PASS")


if __name__ == "__main__":
    main()
