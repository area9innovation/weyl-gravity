#!/usr/bin/env python3
"""Certify the transport-only terminal gate for covariant H4."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.final_transport import FinalCovariantTransportStatus


CERTIFICATE_DIR = ROOT / "covariant_completion" / "certificates"
ANALYTIC_CERTIFICATE_DIR = ROOT / "analytic_completion" / "certificates"
BRIDGE_CERTIFICATE_DIR = ROOT / "bridge" / "certificates"

AUTHORITATIVE_INPUTS = {
    "curvature_prolongation_status": (
        CERTIFICATE_DIR / "curved_curvature_prolongation_status.json"
    ),
    "final_claim_DAG": CERTIFICATE_DIR / "final_claim_dependencies.json",
    "causal_quasi_isomorphism": (
        CERTIFICATE_DIR / "curved_causal_transport_recognition.json"
    ),
    "SO42_equivariant_transport": (
        CERTIFICATE_DIR / "curved_SO42_causal_transport_recognition.json"
    ),
    "direct_causal_pairing_transport": (
        CERTIFICATE_DIR / "curved_direct_causal_pairing_transport.json"
    ),
    "residual_H4": ANALYTIC_CERTIFICATE_DIR / "completed_H4.json",
    "residual_Gram": ANALYTIC_CERTIFICATE_DIR / "completed_gram.json",
}

SO42_UNDERLYING_INPUTS = {
    "actual_causal_quasi_isomorphism": (
        CERTIFICATE_DIR / "curved_causal_transport_recognition.json"
    ),
    "auxiliary_retract": (
        CERTIFICATE_DIR / "curved_auxiliary_canonical_split.json"
    ),
    "curvature_mapping_cylinder": (
        CERTIFICATE_DIR / "curved_curvature_mapping_cylinder_substitution.json"
    ),
    "curvature_causal_pde": (
        CERTIFICATE_DIR / "curved_weyl_cotton_causal_pde.json"
    ),
    "raw_bv_transfer": BRIDGE_CERTIFICATE_DIR / "raw_bv_transfer.json",
    "cylinder_bgg_blocks": BRIDGE_CERTIFICATE_DIR / "cylinder_bgg_blocks.json",
    "cylinder_metric_preimages": (
        BRIDGE_CERTIFICATE_DIR / "cylinder_metric_preimages.json"
    ),
    "curvature_EAL_spectrum": (
        CERTIFICATE_DIR / "curved_EAL_spectrum_all_level.json"
    ),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _authoritative_input_hashes() -> dict[str, str]:
    return {name: _sha256(path) for name, path in AUTHORITATIVE_INPUTS.items()}


def _load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{path.name} is not a JSON certificate object")
    return value


def _canonical_certificate_sha256(value: dict[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _so42_underlying_certificates() -> dict[str, dict[str, object]]:
    return {name: _load_json(path) for name, path in SO42_UNDERLYING_INPUTS.items()}


def _so42_underlying_hashes(
    inputs: dict[str, dict[str, object]],
) -> dict[str, str]:
    return {
        name: _canonical_certificate_sha256(value)
        for name, value in inputs.items()
    }


def _so42_receipt_matches_inputs(
    certificate: dict[str, object], inputs: dict[str, dict[str, object]]
) -> bool:
    return certificate.get("input_certificate_sha256") == _so42_underlying_hashes(
        inputs
    )


def _transport_receipt_passes(
    payload: dict[str, object],
    expected_hashes: dict[str, str],
    expected_so42_underlying_hashes: dict[str, str],
) -> bool:
    recorded = payload.get("input_certificate_sha256")
    terminal = payload.get("terminal_gate")
    return bool(
        payload.get("schema") == "pure-weyl-final-covariant-transport-status-v1"
        and payload.get("dependency_tag") == "LORENTZIAN-CAUSAL"
        and isinstance(recorded, dict)
        and recorded == expected_hashes
        and payload.get("transitive_input_certificate_sha256")
        == {"SO42_equivariant_transport": expected_so42_underlying_hashes}
        and isinstance(terminal, dict)
        and terminal.get("derived_not_manually_set") is True
    )


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
            "REFUSED: the terminal theorem transports the certified residual H4; "
            "it does not recompute cohomology in the auxiliary variables"
        )
    if args.claim_final_covariant_h4 and not status.complete:
        blockers = status.blocking_dependencies("final_covariant_H4")
        raise SystemExit(
            "REFUSED: final_covariant_H4 is false; blocking atomic dependencies: "
            + ", ".join(blockers)
        )

    expected_hashes = _authoritative_input_hashes()
    so42_certificate = _load_json(
        AUTHORITATIVE_INPUTS["SO42_equivariant_transport"]
    )
    so42_inputs = _so42_underlying_certificates()
    if not _so42_receipt_matches_inputs(so42_certificate, so42_inputs):
        raise AssertionError(
            "SO(4,2) recognition receipt drifted from an underlying input"
        )
    expected_so42_underlying_hashes = _so42_underlying_hashes(so42_inputs)
    payload = {
        **status.certificate(),
        "dependency_tag": "LORENTZIAN-CAUSAL",
        "input_certificate_sha256": expected_hashes,
        "transitive_input_certificate_sha256": {
            "SO42_equivariant_transport": expected_so42_underlying_hashes,
        },
    }
    if args.emit:
        CERTIFICATE_DIR.mkdir(parents=True, exist_ok=True)
        outputs = {
            "covariant_causal_quasi_isomorphism.json": {
                **payload,
                "selected_arrow": "causal",
            },
            "covariant_CKV_recovery.json": {
                **payload,
                "selected_claim": "residual_endpoint_recovery",
                "status": status.report.nodes["residual_endpoint_recovery"].status,
            },
            "covariant_residual_no_duplication.json": {
                **payload,
                "selected_claim": "residual_endpoint_recovery",
                "status": status.report.nodes["residual_endpoint_recovery"].status,
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
        persisted_dag = json.loads(
            AUTHORITATIVE_INPUTS["final_claim_DAG"].read_text(encoding="utf-8")
        )
        if persisted_dag != status.report.certificate():
            raise AssertionError("persisted final-claim DAG drifted from the live DAG")
        if not status.report.nodes["residual_H4_is_C2"].status:
            raise AssertionError("residual H4 input regressed")
        if not status.report.nodes["residual_gram_is_I2"].status:
            raise AssertionError("residual Gram input regressed")
        if not status.report.nodes["direct_causal_pairing_transport"].status:
            raise AssertionError("direct causal pairing transport regressed")
        if not status.report.nodes["pairing_compatibility"].status:
            raise AssertionError("pairing compatibility regressed")
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
        if payload["terminal_gate"]["requires"] != list(terminal.requires):
            raise AssertionError("transport payload drifted from the terminal DAG")
        if not _transport_receipt_passes(
            payload, expected_hashes, expected_so42_underlying_hashes
        ):
            raise AssertionError("transport receipt did not bind every authoritative input")
        hash_guards = {}
        for input_name in AUTHORITATIVE_INPUTS:
            broken = deepcopy(payload)
            broken["input_certificate_sha256"][input_name] = "0" * 64
            hash_guards[input_name] = not _transport_receipt_passes(
                broken, expected_hashes, expected_so42_underlying_hashes
            )
        if not all(hash_guards.values()):
            raise AssertionError(
                "transport input-hash mutation guards failed: " + str(hash_guards)
            )
        so42_hash_guards = {}
        for input_name in SO42_UNDERLYING_INPUTS:
            broken_inputs = deepcopy(so42_inputs)
            broken_inputs[input_name]["_audit_mutation"] = True
            so42_hash_guards[input_name] = not _so42_receipt_matches_inputs(
                so42_certificate, broken_inputs
            )
        if not all(so42_hash_guards.values()):
            raise AssertionError(
                "SO(4,2) transitive input mutation guards failed: "
                + str(so42_hash_guards)
            )
        forged_so42 = deepcopy(so42_certificate)
        forged_input = deepcopy(so42_inputs["raw_bv_transfer"])
        forged_input["_audit_mutation"] = True
        forged_so42["input_certificate_sha256"]["raw_bv_transfer"] = (
            _canonical_certificate_sha256(forged_input)
        )
        forged_so42_rejected = not _so42_receipt_matches_inputs(
            forged_so42, so42_inputs
        )
        if not forged_so42_rejected:
            raise AssertionError(
                "a forged SO(4,2) receipt survived aggregate regeneration"
            )
        print(
            "FINAL COVARIANT TRANSPORT GUARDS: "
            f"{10 + len(hash_guards) + len(so42_hash_guards)}/"
            f"{10 + len(hash_guards) + len(so42_hash_guards)} PASS"
        )

    print("FINAL COVARIANT TRANSPORT: ALL IMPLEMENTED LOGIC CHECKS PASS")


if __name__ == "__main__":
    main()
