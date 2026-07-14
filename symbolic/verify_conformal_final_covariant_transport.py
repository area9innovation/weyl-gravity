#!/usr/bin/env python3
"""Certify the transport-only terminal gate for covariant H4."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.final_transport import FinalCovariantTransportStatus


CERTIFICATE_DIR = ROOT / "covariant_completion" / "certificates"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    parser.add_argument("--claim-final-covariant-h4", action="store_true")
    parser.add_argument("--recompute-auxiliary-h4", action="store_true")
    args = parser.parse_args()

    status = FinalCovariantTransportStatus.build()
    if args.recompute_auxiliary_h4:
        raise SystemExit(
            "REFUSED: the terminal theorem transports the certified energy H4; "
            "it does not recompute cohomology in the auxiliary variables"
        )
    if args.claim_final_covariant_h4 and not status.complete:
        blockers = status.blocking_dependencies("final_covariant_H4")
        raise SystemExit(
            "REFUSED: final_covariant_H4 is false; blocking atomic dependencies: "
            + ", ".join(blockers)
        )

    payload = status.certificate()
    if args.emit:
        CERTIFICATE_DIR.mkdir(parents=True, exist_ok=True)
        outputs = {
            "covariant_causal_quasi_isomorphism.json": {
                **payload,
                "selected_arrow": "causal",
            },
            "covariant_CKV_recovery.json": {
                **payload,
                "selected_claim": "CKV_recovery",
                "status": status.report.nodes["CKV_recovery"].status,
            },
            "covariant_residual_no_duplication.json": {
                **payload,
                "selected_claim": "residual_no_duplication",
                "status": status.report.nodes["residual_no_duplication"].status,
            },
            "covariant_H4_transport.json": payload,
            "covariant_gram_transport.json": {
                **payload,
                "selected_claim": "pairing_compatibility",
                "status": status.report.nodes["pairing_compatibility"].status,
            },
        }
        for name, value in outputs.items():
            path = CERTIFICATE_DIR / name
            path.write_text(
                json.dumps(value, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            print("wrote", path.relative_to(ROOT))

    if args.guards:
        if not status.report.nodes["energy_H4_is_C2"].status:
            raise AssertionError("energy H4 input regressed")
        if not status.report.nodes["energy_gram_is_I2"].status:
            raise AssertionError("energy Gram input regressed")
        blockers = payload["terminal_gate"]["blocking_dependencies"]
        if bool(blockers) == bool(status.complete):
            raise AssertionError(
                "transport blockers must be present exactly while the gate is incomplete"
            )
        terminal = status.report.nodes["final_covariant_H4"]
        if terminal.status != all(
            status.report.nodes[name].status for name in terminal.requires
        ):
            raise AssertionError("terminal status is not derived from the live DAG")
        print("FINAL COVARIANT TRANSPORT GUARDS: 4/4 PASS")

    print("FINAL COVARIANT TRANSPORT: ALL IMPLEMENTED LOGIC CHECKS PASS")


if __name__ == "__main__":
    main()
