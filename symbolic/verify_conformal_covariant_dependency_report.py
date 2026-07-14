#!/usr/bin/env python3
"""Generate and guard the fail-closed final covariant claim dependency DAG."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.dependencies import FinalClaimDependencyReport


CERTIFICATE = ROOT / "covariant_completion" / "certificates" / "final_claim_dependencies.json"
MARKDOWN = ROOT / "covariant_completion" / "generated" / "final_claim_dependencies.md"


CLAIM_FLAGS = {
    "claim_curved_operator": "curved_operator_identity",
    "claim_curved_retract": "curved_deformation_retract",
    "claim_curved_current": "curved_current_comparison",
    "claim_complete_green_hyperbolicity": "complete_bv_green_hyperbolicity",
    "claim_final_covariant_h4": "final_covariant_H4",
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    parser.add_argument("--claim-curved-operator", action="store_true")
    parser.add_argument("--claim-curved-retract", action="store_true")
    parser.add_argument("--claim-curved-current", action="store_true")
    parser.add_argument("--claim-complete-green-hyperbolicity", action="store_true")
    parser.add_argument("--claim-final-covariant-h4", action="store_true")
    args = parser.parse_args()

    report = FinalClaimDependencyReport.build()
    for argument_name, claim_name in CLAIM_FLAGS.items():
        if not getattr(args, argument_name):
            continue
        claim = report.nodes[claim_name]
        if not claim.status:
            blockers = report.certificate()["claims"][claim_name][
                "blocking_dependencies"
            ]
            raise SystemExit(
                f"REFUSED: {claim_name} is false; blocking atomic dependencies: "
                + ", ".join(blockers)
            )
        print(f"CERTIFIED: {claim_name}")

    if args.emit:
        CERTIFICATE.parent.mkdir(parents=True, exist_ok=True)
        MARKDOWN.parent.mkdir(parents=True, exist_ok=True)
        CERTIFICATE.write_text(
            json.dumps(report.certificate(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        MARKDOWN.write_text(report.markdown(), encoding="utf-8")
        print("wrote", CERTIFICATE.relative_to(ROOT))
        print("wrote", MARKDOWN.relative_to(ROOT))

    if args.guards:
        certificate = report.certificate()
        for name, node in report.nodes.items():
            dependency_statuses = [
                report.nodes[dependency].status for dependency in node.requires
            ]
            expected = (
                all(dependency_statuses)
                if node.dependency_mode == "all"
                else any(dependency_statuses)
            )
            if node.requires and node.status != expected:
                raise AssertionError(
                    f"derived claim {name} does not implement dependency mode "
                    f"{node.dependency_mode!r}"
                )
            blockers = certificate["claims"][name]["blocking_dependencies"]
            if node.status and blockers:
                raise AssertionError(f"true claim {name} still reports blockers")
        final = report.nodes["final_covariant_H4"]
        if bool(certificate["final_claim_atomic_blockers"]) == bool(final.status):
            raise AssertionError(
                "final atomic blockers must be present exactly while the theorem is false"
            )
        print("COVARIANT CLAIM DEPENDENCY GUARDS: 5/5 PASS")

    print("COVARIANT FINAL CLAIM DEPENDENCY REPORT: ALL LOGIC CHECKS PASS")


if __name__ == "__main__":
    main()
