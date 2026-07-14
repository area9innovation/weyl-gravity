#!/usr/bin/env python3
"""Emit and guard the four terminal covariant-certification flags."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.dependencies import FinalClaimDependencyReport


CERTIFICATE = ROOT / "covariant_completion" / "certificates" / "four_flag_closure_status.json"
FLAG_NAMES = (
    "curved_operator_identity",
    "curved_deformation_retract",
    "curved_current_comparison",
    "final_covariant_H4",
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    parser.add_argument("--claim-complete", action="store_true")
    args = parser.parse_args()

    report = FinalClaimDependencyReport.build()
    report_certificate = report.certificate()
    flags = {name: report.nodes[name].status for name in FLAG_NAMES}
    final_requirements = report.nodes["final_covariant_H4"].requires
    expected_final = all(report.nodes[name].status for name in final_requirements)
    if flags["final_covariant_H4"] != expected_final:
        raise AssertionError("final_covariant_H4 is not the exact dependency conjunction")

    payload = {
        "schema": "pure-weyl-four-flag-closure-status-v1",
        "policy": "no flag is manually promoted",
        "flags": flags,
        "final_covariant_H4_requires": list(final_requirements),
        "final_covariant_H4_is_exact_conjunction": True,
        "atomic_blockers": list(report_certificate["final_claim_atomic_blockers"]),
        "curvature_propagation_gate": report_certificate[
            "curvature_propagation_gate"
        ],
        "complete": all(flags.values()),
        "honest_status": (
            "All four terminal flags are certified by the exact dependency DAG."
            if all(flags.values())
            else "The exact partial infrastructure is certified; terminal flags "
            "remain false exactly where curved atomic lemmas are still open."
        ),
    }

    if args.claim_complete and not payload["complete"]:
        raise SystemExit(
            "REFUSED: the curved operator, actual curved-Q retract, and complete "
            "curved current comparison remain dependency-blocked"
        )

    if args.emit:
        CERTIFICATE.parent.mkdir(parents=True, exist_ok=True)
        CERTIFICATE.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", CERTIFICATE.relative_to(ROOT))

    if args.guards:
        if flags != {
            name: report.nodes[name].status for name in FLAG_NAMES
        }:
            raise AssertionError("the emitted flags drifted from the dependency DAG")
        if payload["complete"] != all(flags.values()):
            raise AssertionError("the closure status is not the exact four-flag conjunction")
        if report.nodes["energy_H4_is_C2"].status is not True:
            raise AssertionError("the independent energy H4 input regressed")
        if report.nodes["energy_gram_is_I2"].status is not True:
            raise AssertionError("the independent energy Gram input regressed")
        if bool(payload["atomic_blockers"]) == bool(payload["complete"]):
            raise AssertionError(
                "atomic blockers must be present exactly while closure is incomplete"
            )
        print("FOUR-FLAG CLOSURE GUARDS: 4/4 PASS")

    print("FOUR-FLAG COVARIANT STATUS: ALL DEPENDENCY CHECKS PASS")


if __name__ == "__main__":
    main()
