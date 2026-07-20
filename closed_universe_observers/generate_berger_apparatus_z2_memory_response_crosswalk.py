#!/usr/bin/env python3
"""Fail-closed Berger Z2 receiver contract for apparatus memory response."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = (
    P / "certificates/BERGER_APPARATUS_Z2_MEMORY_RESPONSE_CROSSWALK.json"
)
CONTRACT = (
    P / "certificates/BERGER_APPARATUS_SAME_BACKGROUND_Z2_RECEIVER_CONTRACT.json"
)
REPORT = P / "reports/berger-apparatus-z2-memory-response-crosswalk.md"
REQUEST = (
    ROOT
    / "planning/events/"
    "observer-berger-apparatus-z2-memory-response-REQUEST-29bed3bc4a756983.json"
)
REQUEST_ID = (
    "sf:program/request/"
    "observer-berger-apparatus-z2-memory-response-to-classical-29bed3bc4a756983"
)
DEPENDENCIES = {
    "parent": P / "certificates/BERGER_DYNAMICAL_APPARATUS_PARENT.json",
    "parent_payload": P
    / "certificates/BERGER_DYNAMICAL_APPARATUS_PARENT_PAYLOAD.json",
    "rank_two": P
    / "certificates/BERGER_DYNAMICAL_EMITTER_CAUCHY_RANK_TWO.json",
    "component_contract": P
    / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "complete_unary": P
    / "certificates/BERGER_108_ROW_NONLINEAR_CLOCK_SECOND_JET.json",
    "complete_q2": P / "certificates/BERGER_108_ROW_COMPLETE_Q2_PBW.json",
    "rod_source_sector": P
    / "certificates/BERGER_GLOBAL_ROD_Q1_SOURCE_SECTOR_SOLVABILITY.json",
    "reduction_preflight": P
    / "certificates/BERGER_DYNAMICAL_APPARATUS_REDUCED_COHOMOLOGY_CROSSWALK.json",
    "abstract_cone_theorem": ROOT
    / "d_quotient_classical/certificates/"
    "FINITE_HARMONIC_SECOND_ORDER_TANGENT_CONE_THEOREM_V1.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _absence_audit(payload: dict[str, Any]) -> dict[str, bool]:
    return {
        "preparation_carrier_crosswalk": (
            "preparation_carrier_crosswalk" not in payload
        ),
        "quadratic_source_map_on_preparation_span": (
            "quadratic_source_map_on_preparation_span" not in payload
        ),
        "stabilizer_basis": "stabilizer_basis" not in payload,
        "moment_map_or_Taub_projections": (
            "moment_map_or_Taub_projections" not in payload
        ),
        "nonzero_shell_output_blocks": (
            "nonzero_shell_output_blocks" not in payload
        ),
        "reduced_adjoint_cokernel_bases": (
            "reduced_adjoint_cokernel_bases" not in payload
        ),
        "resonant_adjoint_pairings": (
            "resonant_adjoint_pairings" not in payload
        ),
        "correction_class_receivers": (
            "correction_class_receivers" not in payload
        ),
        "Berger_Z2_ideal": "Berger_Z2_ideal" not in payload,
        "memory_transport_on_Z2": "memory_transport_on_Z2" not in payload,
    }


def build_contract() -> dict[str, Any]:
    parent = json.loads(DEPENDENCIES["parent"].read_text())
    payload = json.loads(DEPENDENCIES["parent_payload"].read_text())
    request = json.loads(REQUEST.read_text())
    absent = _absence_audit(payload)
    if not all(absent.values()):
        raise AssertionError("same-background Berger Z2 capability audit drifted")
    if parent["observer_result"]["rank"] != 2:
        raise AssertionError("parent leading response rank drifted")
    if request["body"]["payload"]["request_id"] != REQUEST_ID:
        raise AssertionError("typed request identity drifted")
    return {
        "schema": (
            "closed-universe-berger-apparatus-"
            "same-background-z2-receiver-contract-v1"
        ),
        "result_id": "BERGER_APPARATUS_SAME_BACKGROUND_Z2_RECEIVER_CONTRACT",
        "status": "REQUIRED_NOT_YET_INSTANTIATED",
        "coefficient_field": (
            "exact algebraic/rational Berger coefficient field with declared "
            "differential-symbol localization"
        ),
        "background": (
            "same pinned positive Berger gravity-clock-Maxwell-apparatus "
            "background; no compact-product carrier"
        ),
        "precondition": {
            "combined_q1_crosswalk": (
                "BERGER_DYNAMICAL_APPARATUS_COMBINED_Q1_CROSSWALK_CONTRACT"
            ),
            "status": "REQUIRED_NOT_YET_INSTANTIATED",
            "reason": (
                "Z2 membership and memory descent require the preparation "
                "directions and detector records to be classes of one "
                "combined same-background q1 complex."
            ),
        },
        "input_span": {
            "ordered_generators": [
                "u_0: certified detector-selected localized emitter preparation 0",
                "u_1: certified detector-selected localized emitter preparation 1",
            ],
            "general_element": "u=a_0*u_0+a_1*u_1",
            "coefficient_ring": "exact polynomial ring in a_0,a_1",
            "required_quadratic_pairs": ["(u_0,u_0)", "(u_0,u_1)", "(u_1,u_1)"],
            "crosswalk_status": "NO_CERTIFIED_MAP",
        },
        "required_exact_objects": {
            "carrier_crosswalk": (
                "row-level chain map from u_0,u_1 and the 56-row parent into "
                "the selected combined Berger q1/q2 carrier"
            ),
            "quadratic_source": (
                "content-addressed symmetric map S(u_i,u_j)=D2E[u_i,u_j] "
                "in every quadratically generated output block"
            ),
            "finite_output_closure": (
                "complete output-block list for all finite sums, with exact "
                "Berger carrier labels and selection-rule witnesses"
            ),
            "Noether_reduction": (
                "all target identities and gauge-null correction columns "
                "removed before forming any cokernel"
            ),
            "stabilizer_receiver": (
                "certified stabilizer basis and every moment-map/Taub "
                "projection mu_X(S(u_i,u_j))"
            ),
            "resonant_receiver": (
                "for every nonzero shell, reduced adjoint-cokernel basis and "
                "all exact pairings R_j(S(u_i,u_j))"
            ),
            "correction_class_operators": (
                "separate operator domains, images and right-inverse witnesses "
                "for bounded/quasiperiodic, smooth secular and causal/retarded"
            ),
            "Z2_ideal": (
                "exact amplitude ideal and canonical locus decomposition for "
                "mu_X(u)=0 and every class-sensitive R_j(u)=0"
            ),
            "response_restriction": (
                "substitute the canonical Z2 locus into the action-derived "
                "two-by-two response and compute exact rank and kernel on "
                "each irreducible component"
            ),
            "memory_transport": (
                "transport every surviving detector record into a persistent "
                "relational memory pair with clock/rod and gauge covariance"
            ),
        },
        "correction_classes": {
            "bounded_or_quasiperiodic": {
                "required_receiver": (
                    "stabilizer projections plus every reduced resonant "
                    "adjoint-cokernel pairing"
                ),
                "current_status": "NO_CERTIFIED_MAP",
            },
            "smooth_secular": {
                "required_receiver": (
                    "stabilizer projections plus exact polynomial-prefactor "
                    "right inverses for every resonant block"
                ),
                "current_status": "NO_CERTIFIED_MAP",
            },
            "causal_or_retarded": {
                "required_receiver": (
                    "stabilizer projections plus a same-background compatible-"
                    "source retarded Green theorem on every output block"
                ),
                "current_status": "NO_CERTIFIED_MAP",
            },
        },
        "required_verification": [
            "all dependency and action/payload hashes match",
            "the carrier crosswalk is a q1 chain map and preserves grading",
            "the quadratic source is symmetric and q1/Noether compatible",
            "the output-block list is exhaustive under quadratic selection rules",
            "stabilizer and complementary cokernel bases are disjoint and complete",
            "all amplitude obstruction polynomials are reproduced exactly",
            "zero pairings have right inverses in the same correction class",
            "Z2 ideal membership and component decomposition replay independently",
            "restricted response ranks and kernels replay on every component",
            "memory transport is gauge, real and K_Berger covariant",
            "causal memory uses retarded support rather than coordinate frequency",
            "deletion, mixed-term, cokernel and correction-class mutations fail",
        ],
        "acceptance_outputs": [
            "machine-readable same-background carrier/preparation crosswalk",
            "quadratic source blocks and exact obstruction-pairing matrices",
            "one separately typed Z2 ideal per correction class",
            "individual-mode and balanced-combination membership table",
            "restricted response matrices with exact rank/kernel witnesses",
            "persistent relational-memory representatives",
            "method-distinct verifier and mutation fixtures",
        ],
        "current_absence_audit": absent,
        "typed_request": {
            "request_id": REQUEST_ID,
            "to_stream": "classical",
            "typed": "same-background-berger-z2-integrability-receiver",
            "path": str(REQUEST.relative_to(ROOT)),
            "sha256": sha256(REQUEST),
        },
        "forbid": [
            "compact-product modes identified with Berger modes by matching names",
            "the abstract finite-harmonic theorem called a Berger receiver",
            "leading rank two called nonlinear rank two before Z2 restriction",
            "formal secular correction called bounded or stable",
            "coordinate-frequency ratio called relational redshift",
            "one-generator tests substituted for all finite sums",
            "stabilizer moment maps omitted from the adjoint-cokernel audit",
        ],
    }


def build_certificate(contract: dict[str, Any]) -> dict[str, Any]:
    deps = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    contract_text = json.dumps(contract, indent=2, sort_keys=True) + "\n"
    return {
        "schema": (
            "closed-universe-berger-apparatus-"
            "z2-memory-response-crosswalk-v1"
        ),
        "result_id": "BERGER_APPARATUS_Z2_MEMORY_RESPONSE_CROSSWALK",
        "setting_id": deps["parent"]["setting_id"],
        "claim_status": "SHORTFALL_MISSING_SAME_BACKGROUND_BERGER_Z2_RECEIVER",
        "atlas_status": "OPEN",
        "dependency_tags": [
            "LOCAL-ALGEBRAIC",
            "REDUCED-MODE",
            "LORENTZIAN-CAUSAL",
        ],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": deps[name]["result_id"],
                "sha256": sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "contract_ref": {
            "path": str(CONTRACT.relative_to(ROOT)),
            "result_id": contract["result_id"],
            "sha256": hashlib.sha256(contract_text.encode()).hexdigest(),
        },
        "request_ref": contract["typed_request"],
        "capability_audit": {
            "parent_action_q1_q2_and_leading_rank_two": "CERTIFIED_IN_PARENT_SCOPE",
            "abstract_correction_class_criterion": "CERTIFIED_NO_BERGER_CARRIER_MAP",
            "combined_apparatus_q1_reduction": "NO_CERTIFIED_MAP",
            "same_background_quadratic_source_receiver": "NO_CERTIFIED_MAP",
            "stabilizer_Taub_receiver": "NO_CERTIFIED_MAP",
            "nonzero_shell_resonant_receiver": "NO_CERTIFIED_MAP",
            "Berger_Z2_locus": "NO_CERTIFIED_MAP",
            "verdict": "TYPED_SAME_BACKGROUND_RECEIVER_REQUIRED",
        },
        "correction_class_disposition": {
            name: "NO_CERTIFIED_MAP"
            for name in (
                "bounded_or_quasiperiodic",
                "smooth_secular",
                "causal_or_retarded",
            )
        },
        "observer_disposition": {
            "leading_linear_response_rank": "CERTIFIED_RANK_TWO_IN_PARENT_SCOPE_ONLY",
            "individual_preparation_Z2_membership": "NO_CERTIFIED_MAP",
            "balanced_combination_Z2_membership": "NO_CERTIFIED_MAP",
            "linearly_detectable_but_nonlinearly_obstructed_modes": "NO_CERTIFIED_MAP",
            "restricted_response_matrix": "NO_CERTIFIED_MAP",
            "nonlinear_response_rank_and_kernel": "NO_CERTIFIED_MAP",
            "persistent_relational_memory": "NO_CERTIFIED_MAP",
            "survives_gauge_reduction_on_Z2": "NO_CERTIFIED_MAP",
            "exceptional_resonant_operational_signature": "NO_CERTIFIED_MAP",
            "observer_coupling_adds_or_removes_source_channel": "NO_CERTIFIED_MAP",
            "recoil_backreaction_on_Z2": "NO_CERTIFIED_MAP",
            "relational_redshift": "NO_CERTIFIED_MAP",
        },
        "next_gate": (
            "INSTANTIATE_COMBINED_Q1_THEN_DELIVER_"
            "SAME_BACKGROUND_BERGER_Z2_RECEIVER"
        ),
        "claim_boundary": (
            "This exact audit imports by content hash the action-derived "
            "Berger apparatus parent and payload, the two certified localized "
            "emitter preparations with leading rank-two detector response, "
            "the component carrier, the completed same-background unary and "
            "q2 candidates, the solved global-rod quadratic source sector, "
            "the apparatus-reduction preflight and the abstract finite-"
            "harmonic second-order tangent-cone theorem. The abstract theorem "
            "states the correction-class-sensitive image/cokernel criterion "
            "only; it explicitly supplies no Berger carrier map. The parent "
            "payload contains neither a row-level crosswalk of u_0,u_1 into "
            "one combined q1/q2 complex nor D2E on their three symmetric "
            "quadratic pairs, a complete output-block closure, stabilizer "
            "moment-map/Taub projections, reduced nonzero-shell adjoint "
            "cokernels, resonant pairings, correction-class receivers, a "
            "Berger Z2 ideal or memory transport restricted to that ideal. "
            "The separate global-rod solvability result is not the quadratic "
            "source of the detector-selected emitter preparation span. "
            "Therefore no individual preparation or balanced combination is "
            "classified as second-order extendible or obstructed, and the "
            "leading triangular rank-two matrix is not promoted to a "
            "nonlinear response. Bounded/quasiperiodic, smooth secular and "
            "causal/retarded correction classes remain separate "
            "NO_CERTIFIED_MAP results. The emitted contract and typed "
            "classical request specify the missing same-background receiver. "
            "No compact-product mode, coordinate-frequency redshift, all-jet "
            "source verdict, q3, branch, particle, positivity or quantum "
            "claim is introduced."
        ),
        "provenance": {
            "generator_command": (
                "python3 -m closed_universe_observers."
                "generate_berger_apparatus_z2_memory_response_crosswalk --write"
            ),
            "independent_verifier_command": (
                "python3 -m closed_universe_observers."
                "verify_berger_apparatus_z2_memory_response_crosswalk"
            ),
            "source_sha256": sha256(Path(__file__)),
        },
    }


def report_text() -> str:
    return """# Berger apparatus Z2 memory-response receiver

The action-derived parent certifies a leading triangular rank-two response,
but it does not serialize the same-background second-order integrability
receiver for the two detector-selected preparation directions.

The missing receiver must evaluate all three symmetric quadratic pairs,
including the mixed pair, against every stabilizer moment-map/Taub projection
and every reduced nonzero-shell adjoint-cokernel vector.  It must do so
separately for bounded/quasiperiodic, smooth secular and causal/retarded
correction classes.  The abstract finite-harmonic theorem supplies the
criterion, not a Berger carrier map.

The accompanying contract fixes the carrier crosswalk, source blocks,
output closure, obstruction polynomials, correction-class right inverses,
Z2 ideals, restricted response ranks/kernels and persistent relational-memory
outputs required for promotion.  The typed classical-team request names this
same receiver.  Until it is delivered, all nonlinear detector and memory
claims remain fail-closed while the parent leading rank remains certified in
its original scope.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    contract = build_contract()
    certificate = build_certificate(contract)
    if args.write:
        CONTRACT.write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n")
        CERTIFICATE.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n"
        )
        REPORT.write_text(report_text())
    else:
        print(json.dumps(certificate, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
