#!/usr/bin/env python3
"""Emit the fail-closed all-jet temporal-curl capability disposition."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = (
    PACKAGE
    / "certificates/BERGER_TEMPORAL_CURL_ALL_JET_DISPOSITION_SHORTFALL.json"
)
REPORT = (
    PACKAGE
    / "reports/berger-temporal-curl-all-jet-disposition-shortfall.md"
)
PREDECESSOR = (
    PACKAGE
    / "certificates/BERGER_TEMPORAL_MAXWELL_COTANGENT_MAPPING_CONE_CONSTRUCTION.json"
)
PREDECESSOR_PAYLOAD = (
    PACKAGE
    / "certificates/BERGER_TEMPORAL_MAXWELL_COTANGENT_MAPPING_CONE_CONSTRUCTION_PAYLOAD.json"
)
PREDECESSOR_CLOSEOUT = (
    ROOT
    / "reports/observer-temporal-maxwell-cotangent-mapping-cone-construction-closeout-2026-07-20.md"
)
REQUEST = (
    ROOT
    / "planning/forge-requests/observer-differential-pbw-module-membership.json"
)
SOURCE_FILES = [Path(__file__), REQUEST]

FORGE_SNAPSHOT = {
    "repository": "tango/forge",
    "commit": "404110a9338862959d7960b707dd6e1fb248f54d",
    "declared_capability_ledger": {
        "path": "lib/math/COMPLETENESS.md",
        "sha256": "9c13c3e51bbc160bc2b403c9d108edda1b469963199a07546af65209af33eb57",
    },
    "differential_pbw_work_item": {
        "path": "tools/science-forge/program/M10b-differential-pbw.json",
        "sha256": "cf1bc06924cb63e657f1aa2bffd122851d7543d9c958939ff181c779e6502510",
        "state": "PROPOSED",
    },
    "commutative_groebner_layer": {
        "path": "lib/math/groebner.forge",
        "sha256": "5efa4cbaf4083d0ca294933cdb765e01343e7e07cd00d95eb650df9376aded71",
    },
    "pbw_straightening_layer": {
        "path": "lib/math/wordpoly.forge",
        "sha256": "e686a974df8da72b34213f1151b1b21041cc7c81aadb14c3b2fb96152075742b",
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dependency_ref(path: Path, result_id: str) -> dict[str, str]:
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": result_id,
        "sha256": sha256(path),
    }


def build() -> dict[str, Any]:
    predecessor = json.loads(PREDECESSOR.read_text())
    request = json.loads(REQUEST.read_text())
    if predecessor["claim_status"] != (
        "OBSTRUCTED_COMPLETE_FILTERED_SECOND_JET_CURL_MAPPING_CONE"
    ):
        raise AssertionError("all-jet branch is not activated")
    for audit in predecessor["filtered_second_jet_theorem"][
        "per_emitter_audits"
    ].values():
        if (
            audit["full_action_image_rank"],
            audit["source_augmented_rank"],
        ) != (2641, 2642):
            raise AssertionError("predecessor rank disposition drifted")
    if request["body"]["state"] not in {"REQUESTED", "ACCEPTED"}:
        raise AssertionError("the missing-capability request is no longer open")

    return {
        "schema": (
            "closed-universe-berger-temporal-curl-all-jet-"
            "disposition-shortfall-v1"
        ),
        "result_id": "BERGER_TEMPORAL_CURL_ALL_JET_DISPOSITION_SHORTFALL",
        "setting_id": predecessor["setting_id"],
        "claim_status": (
            "SHORTFALL_MISSING_EXACT_DIFFERENTIAL_PBW_MODULE_MEMBERSHIP"
        ),
        "atlas_status": "OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {
            "predecessor_certificate": dependency_ref(
                PREDECESSOR,
                "BERGER_TEMPORAL_MAXWELL_COTANGENT_MAPPING_CONE_CONSTRUCTION",
            ),
            "predecessor_payload": dependency_ref(
                PREDECESSOR_PAYLOAD,
                "BERGER_TEMPORAL_MAXWELL_COTANGENT_MAPPING_CONE_CONSTRUCTION_PAYLOAD",
            ),
            "predecessor_closeout": dependency_ref(
                PREDECESSOR_CLOSEOUT,
                "observer-temporal-maxwell-cotangent-mapping-cone-closeout",
            ),
            "forge_request": dependency_ref(
                REQUEST,
                "sf:forge-request/observer-differential-pbw-module-membership",
            ),
        },
        "predecessor_lifecycle": {
            "science_commit": "ff64296e7074b90565a7c9673c5c7716fda415c4",
            "lifecycle_commit": "a991ad8290b31a96e61c2a45628ea8983d93dd40",
            "terminal_state": "OBSTRUCTED",
            "branch_selected": "ALL_JET_FINITE_PRESENTATION",
            "reason": (
                "Both source-labelled filtered second-jet action images have "
                "rank 2641 and acquire rank 2642 when the source is adjoined."
            ),
        },
        "capability_audit": {
            "forge_snapshot": FORGE_SNAPSHOT,
            "available_exact_layers": [
                "selected noncommutative word-polynomial PBW straightening",
                "commutative polynomial Groebner bases and ideal membership over QExt",
                "finite exact matrices and second-jet U(1)-kernel computation",
            ],
            "missing_required_layers": [
                "differential/cotangent generator metadata with jet-valued coefficients",
                "normal-order to component crosswalk with confluence certificate",
                "filtered PBW submodule Groebner or equivalent finite presentation",
                "generating module syzygies over Q(sqrt(10))",
                "certified associated-graded to filtered membership lift after IBP",
            ],
            "why_available_layers_do_not_close_gate": (
                "A commutative associated-graded ideal calculation cannot "
                "control lower-filtration Berger commutator corrections or "
                "prove that all invariant IBP classes lift. Finite-order rank "
                "stabilization supplies neither Noetherian completeness nor "
                "a source membership/non-membership witness at every finite "
                "derivative order."
            ),
            "audit_verdict": "MISSING_REQUIRED_EXACT_MODULE_MACHINERY",
        },
        "all_jet_disposition": {
            "declared_module": (
                "all finite-order local B_plus/tau/K_b action Hessians on "
                "the four-row temporal Maxwell-cotangent curl cone, modulo "
                "IBP, restricted to connected Berger-U(1) invariants, over "
                "the Berger differential-symbol PBW ring and Q(sqrt(10))"
            ),
            "finite_presentation": "NO_CERTIFIED_MAP",
            "hilbert_series": "NO_CERTIFIED_MAP",
            "groebner_or_equivalent_normal_form": "NO_CERTIFIED_MAP",
            "syzygies": "NO_CERTIFIED_MAP",
            "source_membership_at_any_finite_order": "NO_CERTIFIED_MAP",
            "irreducible_cokernel_generator": "NO_CERTIFIED_MAP",
            "minimal_excluded_enlargement": "NO_CERTIFIED_MAP",
            "completeness_category": "NO_CERTIFIED_MAP",
            "status": "SHORTFALL",
        },
        "controls": {
            "predecessor_second_jet_replay": "IMPORTED_CERTIFIED_BY_HASH",
            "blind_third_jet": "NOT_RUN_FORBIDDEN_BY_WORK_ITEM",
            "finite_order_extrapolation": "NOT_USED",
            "all_jet_deletion_mutations": (
                "NOT_RUN_MISSING_FINITE_PRESENTATION_ENGINE"
            ),
            "commutator_sign_mutation": (
                "SPECIFIED_IN_FORGE_REQUEST_NOT_YET_RUN"
            ),
        },
        "downstream_contract": {
            "blocking_request": (
                "sf:forge-request/observer-differential-pbw-module-membership"
            ),
            "activation_gate": (
                "LANDED_EXACT_FILTERED_PBW_MODULE_PRESENTATION_AND_"
                "INDEPENDENT_MEMBERSHIP_VERIFIER"
            ),
            "required_inputs": [
                "content-addressed Berger PBW commutator table",
                "B_plus integration-by-parts relations",
                "connected Berger-U(1) generator",
                "2641-dimensional predecessor Hessian image",
                "two explicit 42-coordinate source representatives",
            ],
            "required_outputs": [
                "finite module presentation over Q(sqrt(10))",
                "Hilbert-series or equivalent completeness certificate",
                "generating syzygies and filtered lifting certificate",
                "source membership witness or non-membership separator",
                "irreducible cokernel and minimal excluded enlargement",
                "independent replay and decisive mutations",
            ],
            "success_branch": (
                "If the source enters the exact all-jet image, construct only "
                "the smallest same-action q3 required by the master identity."
            ),
            "obstruction_branch": (
                "If a complete non-membership certificate survives, publish "
                "the scoped all-jet obstruction and keep q3 and observables closed."
            ),
        },
        "downstream_disposition": {
            "K_Berger_covariance": "NO_CERTIFIED_MAP",
            "raw_D_descent": "NO_CERTIFIED_MAP",
            "same_action_q3": "NO_CERTIFIED_MAP",
            "detector_response_and_rank": "NO_CERTIFIED_MAP",
            "redshift_memory_recoil": "NO_CERTIFIED_MAP",
            "tangent_cone_observer_restriction": "NO_CERTIFIED_MAP",
            "branch_and_quantum": "NO_CERTIFIED_MAP",
        },
        "assumption_ledger": [
            (
                "The complete filtered second-jet obstruction and lifecycle "
                "are imported by exact content and commit hashes."
            ),
            (
                "The Forge capability audit is a declared-capability snapshot "
                "at one exact external commit, not a proof that no possible "
                "software implementation exists."
            ),
            (
                "The requested all-jet category remains the same-background "
                "four-row connected Berger-U(1) differential-symbol module."
            ),
        ],
        "missing_object_ledger": [
            "exact finite presentation of the all-jet IBP/PBW Hessian module",
            "filtered module syzygies and associated-graded lifting theorem",
            "all-finite-order source membership or non-membership witness",
            "irreducible cokernel and minimal excluded enlargement",
            "all-jet deletion and commutator-sign mutation receipts",
        ],
        "next_gate": (
            "WAIT_FOR_FORGE_DIFFERENTIAL_PBW_MODULE_MEMBERSHIP_ENGINE_"
            "THEN_REPLAY_THE_ALL_JET_SOURCE_CLASS"
        ),
        "claim_boundary": (
            "This result is a machine-readable SHORTFALL, not an all-jet "
            "obstruction theorem. It imports the exact finite filtered "
            "second-jet result 2641<2642 for both labelled emitters and "
            "therefore selects the all-jet branch. The audited Forge snapshot "
            "has exact commutative Groebner membership, selected PBW "
            "straightening and finite exact linear algebra, but its declared "
            "capability ledger leaves the differential-PBW/component "
            "crosswalk and syzygy layers open. Those missing layers are "
            "required to lift associated-graded relations through Berger "
            "commutator corrections, integration by parts and the connected "
            "U(1)-invariant restriction. No third-jet computation, numerical "
            "rank extrapolation, finite presentation, Hilbert series, all-jet "
            "source verdict, irreducible cokernel, q3, K_Berger covariance, "
            "detector response, redshift, recoil, tangent-cone, branch or "
            "quantum claim is made."
        ),
        "provenance": {
            "source_files": [
                {
                    "path": str(path.relative_to(ROOT)),
                    "sha256": sha256(path),
                }
                for path in SOURCE_FILES
            ],
            "generator_command": (
                "python3 -m closed_universe_observers."
                "generate_berger_temporal_curl_all_jet_disposition_shortfall "
                "--write"
            ),
            "independent_verifier_command": (
                "python3 -m closed_universe_observers."
                "verify_berger_temporal_curl_all_jet_disposition_shortfall"
            ),
        },
    }


def report_text(value: dict[str, Any]) -> str:
    return rf"""# Berger temporal-curl all-jet disposition

## Result

The predecessor forces the all-jet branch: both exact filtered second-jet
images have rank \(2641\), and adjoining the corresponding source raises the
rank to \(2642\).  The work item forbids a blind third-jet enlargement.

The available exact substrate does not close the replacement gate.  At Forge
commit `{FORGE_SNAPSHOT["commit"]}`, exact commutative Groebner membership
over algebraic extensions and selected PBW straightening are present, but the
declared completeness ledger still leaves differential/cotangent PBW
metadata, jet-valued coefficient crosswalks, confluence and module syzygies
open.  A commutative associated-graded calculation would not certify the
filtered lift through Berger commutators and integration by parts.

The required capability is now tracked by
`sf:forge-request/observer-differential-pbw-module-membership`.  Its stop
condition requires a finite presentation over \(\mathbb Q(\sqrt{{10}})\), an
exact invariant-submodule construction, syzygies, a filtered lifting
certificate, source membership or non-membership evidence, and independent
mutation checks.

## Fail-closed boundary

This is `SHORTFALL`, with atlas status `OPEN`.  It is not evidence that the
source survives at every derivative order.  No third-jet rank, Hilbert series,
all-jet cokernel, \(K_{{\rm Berger}}\), \(q_3\), detector, redshift, recoil or
tangent-cone observable is promoted.

Next gate:
`{value["next_gate"]}`.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.write:
        CERTIFICATE.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
        REPORT.write_text(report_text(value))
    else:
        print(json.dumps(value, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
