"""Emit or check the complete coefficientwise Berger A104."""

from __future__ import annotations

import argparse
import json

from .berger_a104_endpoint_completion import (
    GENERATED,
    OUTPUT,
    REPORT,
    artifact_text,
    build,
)


def report_text(result: dict) -> str:
    ledger = result["endpoint_insertion_ledger"]
    return f"""# Berger A104 endpoint completion

The exact classical endpoint export closes the last two diagonal slots in the
frozen Cauchy ordering:

| block | coordinates | nonzero sparse entries |
| --- | ---: | ---: |
| `{ledger[0]['block_id']}` | {ledger[0]['inserted_coordinates']} | {ledger[0]['inserted_nonzero_sparse_entries']} |
| `{ledger[1]['block_id']}` | {ledger[1]['inserted_coordinates']} | {ledger[1]['inserted_nonzero_sparse_entries']} |

The global `104 x 104` operator now has all 10,816 coordinates determined and
{result['coverage']['known_nonzero_sparse_entries']} nonzero sparse entries.
All 10,528 previously certified coordinates are preserved.

This completes the finite coefficient table only.  The next gate is the
degree-plus-one companion/Cauchy BRST operator together with the nondegenerate
Cauchy/Krein form and real structure.  Closedness, the zero-frequency
Riesz/Jordan ledger and a Hadamard covariance remain open.

Verification uses the deterministic producer replay, completion replay,
independent sparse-entry verifier, strict Draft 2020-12 validation and the
ten scoped unit tests.  Tier 3 is not run because this closes one affected
finite carrier chain without promoting a Hadamard, QME, theorem-freeze or
release lifecycle.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result, operator = build()
    certificate = json.dumps(result, indent=2, sort_keys=True) + "\n"
    artifact = artifact_text(operator)
    report = report_text(result)
    artifact_path = GENERATED / "global_A104.json"
    if args.emit:
        GENERATED.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(certificate)
        artifact_path.write_text(artifact)
        REPORT.write_text(report)
    if args.check:
        if OUTPUT.read_text() != certificate:
            raise SystemExit("stale Berger A104 endpoint-completion certificate")
        if artifact_path.read_text() != artifact:
            raise SystemExit("stale full A104 operator artifact")
        if REPORT.read_text() != report:
            raise SystemExit("stale Berger A104 endpoint-completion report")
    if not args.emit and not args.check:
        print(certificate, end="")
    print("BERGER A104 ENDPOINT COMPLETION: 10816/10816 COORDINATES EXACT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
