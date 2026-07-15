#!/usr/bin/env python3
"""Generate and fail-closed verify the covariant H4 proof ledger."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.final_transport.proof_ledger import (  # noqa: E402
    DAG_PATH,
    JSON_PATH,
    MARKDOWN_PATH,
    ProofLedgerError,
    REPRODUCTION_COMMANDS,
    build_ledger,
    canonical_json,
    outputs_are_current,
    render_markdown,
    write_outputs,
)


def _load_dag() -> dict[str, object]:
    return json.loads(DAG_PATH.read_text(encoding="utf-8"))


def _expect_rejected(dag: dict[str, object], label: str) -> None:
    try:
        build_ledger(dag)
    except ProofLedgerError:
        return
    raise AssertionError(f"ledger accepted mutation: {label}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    payload = build_ledger()
    if args.emit:
        write_outputs(payload)
        print("wrote", JSON_PATH.relative_to(ROOT))
        print("wrote", MARKDOWN_PATH.relative_to(ROOT))
    if args.check or not args.emit:
        if not outputs_are_current(payload):
            raise AssertionError(
                "proof ledger drifted; regenerate with "
                "python3 symbolic/verify_conformal_covariant_H4_proof_ledger.py --emit"
            )

    if args.guards:
        dag = _load_dag()
        claims = dag["claims"]
        terminal = claims["final_covariant_H4"]

        broken = deepcopy(dag)
        broken["claims"]["final_covariant_H4"]["requires"].pop()
        _expect_rejected(broken, "missing terminal requirement")

        broken = deepcopy(dag)
        broken["claims"]["final_covariant_H4"]["requires"].append(
            broken["claims"]["final_covariant_H4"]["requires"][0]
        )
        _expect_rejected(broken, "duplicate terminal requirement")

        broken = deepcopy(dag)
        first = terminal["requires"][0]
        broken["claims"][first]["status"] = False
        _expect_rejected(broken, "false terminal requirement")

        broken = deepcopy(dag)
        evidence_claim = "scalar_wave_witness_no_go"
        broken["claims"][evidence_claim]["evidence"] = ["missing.json"]
        _expect_rejected(broken, "missing authoritative evidence")

        broken = deepcopy(dag)
        broken["claims"]["curved_operator_identity"]["requires"] = [
            "unknown_claim"
        ]
        _expect_rejected(broken, "unknown transitive claim")

        broken = deepcopy(dag)
        broken["claims"]["pairing_compatibility"]["requires"] = []
        broken["claims"]["pairing_compatibility"]["evidence"] = []
        _expect_rejected(broken, "derived claim with no evidence")

        mutated_payload = deepcopy(payload)
        first_path = next(iter(mutated_payload["evidence_inventory"]))
        mutated_payload["evidence_inventory"][first_path]["sha256"] = "0" * 64
        if canonical_json(mutated_payload) == canonical_json(payload):
            raise AssertionError("hash mutation was not observable")
        if outputs_are_current(mutated_payload):
            raise AssertionError("persisted ledger accepted a forged evidence hash")

        missing_commands = dict(REPRODUCTION_COMMANDS)
        missing_commands.pop(terminal["requires"][0])
        if set(missing_commands) == set(terminal["requires"]):
            raise AssertionError("command coverage mutation was not observable")

        if render_markdown(payload) != MARKDOWN_PATH.read_text(encoding="utf-8"):
            raise AssertionError("human-readable ledger drifted from JSON payload")
        print("COVARIANT H4 PROOF LEDGER GUARDS: 9/9 PASS")

    print("COVARIANT H4 PROOF LEDGER: ALL CHECKS PASS")


if __name__ == "__main__":
    main()
